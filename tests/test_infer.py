"""The decision rule at its thresholds, the question templates and the simulated user."""

import pytest

from varag.pipeline.extract import Signal, Signals
from varag.pipeline.infer import CONTEXT_CONFLICT, INFER, UNCERTAIN, infer
from varag.pipeline.questions import conflict_question, parse_version, uncertain_question
from varag.pipeline.user import SimulatedUser
from varag.pipeline.values import GoldRef, match_value, parse_gold, rejected_values, sides_of_value

VERSIONS = {"old": "1.5.3", "new": "3.0.6"}


def signals(old=0.0, new=0.0, d_old=False, d_new=False):
    out = Signals("pandas")
    if old:
        out.signals.append(Signal("context", "symbol", "a", "old", old))
    if new:
        out.signals.append(Signal("context", "symbol", "b", "new", new))
    if d_old:
        out.signals.append(Signal("context", "pin", "p", "old", 0.0, decisive=True))
    if d_new:
        out.signals.append(Signal("context", "pin", "q", "new", 0.0, decisive=True))
    return out


@pytest.mark.parametrize("old,new,d_old,d_new,kind,side", [
    (3.0, 0.0, False, False, INFER, "old"),          # at tau_commit
    (2.9, 0.0, False, False, UNCERTAIN, None),       # just under
    (3.0, 1.5, False, False, INFER, "old"),          # other side at tau_noise is still weak
    (3.0, 1.6, False, False, CONTEXT_CONFLICT, None),
    (0.0, 4.0, False, False, INFER, "new"),
    (0.0, 0.0, True, False, INFER, "old"),           # decisive alone
    (0.0, 1.6, True, False, CONTEXT_CONFLICT, None), # decisive against non-weak evidence
    (0.0, 0.0, True, True, CONTEXT_CONFLICT, None),  # two decisive signals, opposite sides
    (1.5, 1.5, False, False, UNCERTAIN, None),
])
def test_decision_rule(old, new, d_old, d_new, kind, side):
    decision = infer(signals(old, new, d_old, d_new), tau_commit=3.0, tau_noise=1.5)
    assert (decision.kind, decision.side) == (kind, side)
    assert decision.margin == old - new


def test_questions_and_reply_parsing():
    q = uncertain_question("pandas", VERSIONS)
    assert "1.x or 3.x" in q and "import pandas; print(pandas.__version__)" in q and "say so" in q
    c = conflict_question("pandas", VERSIONS, "pandas<2", "pandas.DataFrame.map", "new")
    assert c.startswith("Your requirements say pandas<2, but your code uses pandas.DataFrame.map, which only exists in pandas 3.x.")
    assert parse_version("I'm on pandas 3.0.6.", VERSIONS) == "new"
    assert parse_version("1.x", VERSIONS) == "old"
    assert parse_version("I'm not sure.", VERSIONS) is None
    assert parse_version("something else", VERSIONS) is None
    assert parse_version("1 or 3, both", VERSIONS) is None


def test_simulated_user_arms_and_relevance():
    knows = SimulatedUser("knows", "pandas", VERSIONS)
    assert knows.reply(uncertain_question("pandas", VERSIONS), "new").text == "I'm on pandas 3.0.6."
    assert knows.reply("Which version are you on?", "old").relevant
    irrelevant = knows.reply("What colour is the sky?", "old")
    assert irrelevant.text == "I'm not sure what you're asking." and not irrelevant.relevant
    unsure = SimulatedUser("unsure", "pandas", VERSIONS)
    assert unsure.reply(uncertain_question("pandas", VERSIONS), "new").text == "I'm not sure."
    with pytest.raises(ValueError):
        SimulatedUser("oracle", "pandas", VERSIONS)


def test_gold_parsing_and_value_matching():
    assert parse_gold("pandas.DataFrame.applymap") == GoldRef("pandas.DataFrame.applymap")
    assert parse_gold("pydantic.Field(regex)") == GoldRef("pydantic.Field", "regex")
    ref = parse_gold('pandas.date_range(freq="M")')
    assert ref == GoldRef("pandas.date_range", "freq", "M", True) and ref.keyword_symbol == "pandas.date_range(freq)"
    assert parse_gold("numpy.array(copy=None)").value is None and parse_gold("numpy.array(copy=None)").has_value
    index = {("pandas.date_range", "freq"): ({"value": "M", "side": "old", "anchored": False, "replacement": "ME"},
                                             {"value": "Q", "side": "old", "anchored": True, "replacement": "QE"},
                                             {"value": "ME", "side": "new", "anchored": False, "replacement": "M"})}
    assert match_value(index, "pandas.date_range", "freq", "M")["side"] == "old"
    assert match_value(index, "pandas.date_range", "freq", "Q-JUN")["replacement"] == "QE"
    assert match_value(index, "pandas.date_range", "freq", "ME-JUN") is None
    assert match_value(index, "pandas.date_range", "freq", "h") is None
    assert sides_of_value(index, "ME") == {"new"}
    assert rejected_values(index, "ValueError: Invalid frequency: ME. Failed to parse") == [("ME", "old", "Invalid frequency: ME")]
    assert rejected_values(index, "ValueError: Invalid frequency: M. Failed") == [("M", "new", "Invalid frequency: M")]
    assert rejected_values(index, "ValueError: Invalid frequency: h") == []
