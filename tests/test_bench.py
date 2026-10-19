import shutil

import pytest

from varag.bench.instances import build_instances, rotated_clue_type
from varag.bench.schema import ConceptError, concept_sha256, lint_version_mentions, load_concept, load_concepts
from varag.config import project_root

VERSIONS = {"pandas": {"old": "1.5.3", "new": "3.0.6"}, "numpy": {"old": "1.26.4", "new": "2.4.6"}, "pydantic": {"old": "1.10.13", "new": "2.13.4"}}


def test_lint_catches_versions_in_prose():
    assert lint_version_mentions("I use pandas 1.5 here") == ["pandas 1.5"]
    assert lint_version_mentions("pin numpy>=2.4 please")
    assert lint_version_mentions("on pydantic v2") and lint_version_mentions("version 2 only")
    assert lint_version_mentions("release 3.0.6 broke it")
    assert lint_version_mentions("multiply every cell by 0.5 and keep 3 decimals") == []
    assert lint_version_mentions("match ^[A-Z]{3}-\\d{4}$") == []


def test_seed_concepts_load():
    concepts = load_concepts()
    ids = {c.id for c in concepts}
    assert {"pd-001", "np-001", "pyd-001", "ctl-np-001"} <= ids
    pyd = next(c for c in concepts if c.id == "pyd-001")
    assert pyd.change_type == "param_rename" and pyd.portable_alternative == "guard_only" and pyd.has_portable
    assert pyd.ref_path("wrong").name == "wrong.py" and pyd.ref_path("wrong").exists()
    assert {c.type for c in pyd.clues["old"]} == {"pin", "code"}
    ctl = next(c for c in concepts if c.id == "ctl-np-001")
    assert ctl.is_control and ctl.has_portable


def test_instances_counts_and_rotation():
    concepts = [c for c in load_concepts() if c.id in {"pd-001", "np-001", "pyd-001", "ctl-np-001"}]
    instances = build_instances(concepts, VERSIONS)
    ids = {i.instance_id for i in instances}
    assert "pd-001/old/no-clue" in ids and "pd-001/new/stated" in ids and "ctl-np-001/control" in ids
    clue = [i for i in instances if i.condition == "clue"]
    assert len(clue) == 6 and all(i.context and i.clue_type for i in clue)
    stated = next(i for i in instances if i.instance_id == "np-001/new/stated")
    assert stated.query.endswith("I am using numpy 2.4.6.") and stated.context == ""
    assert len(instances) == 3 * 6 + 1


def test_rotation_balances_types():
    picks = [rotated_clue_type(["pin", "code", "error"], i, s) for i in range(3) for s in (0, 1)]
    assert sorted(picks) == ["code", "code", "error", "error", "pin", "pin"]
    assert rotated_clue_type(["code", "pin"], 0, 1) == "code"
    assert rotated_clue_type([], 0, 0) is None


def test_concept_lint_rejects_version_in_query(tmp_path):
    src = project_root() / "data" / "tasks" / "numpy" / "np-001"
    dst = tmp_path / "np-001"
    shutil.copytree(src, dst)
    text = (dst / "concept.yaml").read_text(encoding="utf-8")
    (dst / "concept.yaml").write_text(text.replace("Return a plain float.", "Return a plain float. This is numpy 1.26."), encoding="utf-8")
    with pytest.raises(ConceptError, match="names a version"):
        load_concept(dst)


def test_concept_sha_changes_with_content_but_not_validation(tmp_path):
    src = project_root() / "data" / "tasks" / "numpy" / "ctl-np-001"
    dst = tmp_path / "ctl-np-001"
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("validation.json"))
    before = concept_sha256(dst)
    (dst / "validation.json").write_text("{}", encoding="utf-8")
    assert concept_sha256(dst) == before
    (dst / "ref_portable.py").write_text("x = 1\n", encoding="utf-8")
    assert concept_sha256(dst) != before


# --- one_directional concepts (user decision 2026-10-15) -----------------------------------


def test_one_directional_loads_without_ref_new(make_one_directional):
    concept = load_concept(make_one_directional())
    assert concept.one_directional and concept.has_portable
    assert concept.target_sides == ("new",)
    assert (concept.native_ref("old"), concept.native_ref("new")) == ("old", "portable")


def test_one_directional_rejects_ref_new_and_needs_a_plain_portable(make_one_directional):
    with pytest.raises(ConceptError, match="no ref_new.py"):
        load_concept(make_one_directional(concept_id="np-od-901", ref_new=True))
    with pytest.raises(ConceptError, match="portable_alternative: plain"):
        load_concept(make_one_directional(concept_id="np-od-902", portable="none"))


def test_concept_needs_a_wrong_answer(make_one_directional):
    directory = make_one_directional(concept_id="np-od-903")
    (directory / "wrong.py").unlink()
    with pytest.raises(ConceptError, match="wrong.py missing"):
        load_concept(directory)


def test_one_directional_instances_target_new_only(make_one_directional):
    concept = load_concept(make_one_directional())
    ids = [i.instance_id for i in build_instances([concept], VERSIONS)]
    # With and without a clue, new target only; no version-stated instance even though control_eligible.
    assert ids == ["np-od-900/new/no-clue", "np-od-900/new/clue-code"]


def test_class_caps(make_one_directional):
    from varag.bench.schema import class_cap_problems, class_counts

    one = load_concept(make_one_directional())
    concepts = load_concepts()                                               # pd-001, np-001, pyd-001 and a control
    np001 = next(c for c in concepts if c.id == "np-001")
    assert class_counts([one, np001])["numpy"] == {"one_directional": 1, "removal": 1}
    # one_directional is capped at a third of the whole benchmark, not of each library.
    assert class_cap_problems([one, np001]) == ["benchmark: 1 of 2 concepts are one_directional; the cap is 1/3"]
    assert class_cap_problems([one, *concepts]) == []                        # 1 of 4, though numpy alone is 1 of 2
    # behavior: 15% of each library, pandas and NumPy exempt.
    def behavior(c):
        return type(c)(**{**c.__dict__, "id": c.id + "-b", "exclusivity": "behavior"})
    pyd = next(c for c in concepts if c.id == "pyd-001")
    pd001 = next(c for c in concepts if c.id == "pd-001")
    assert class_cap_problems([pyd, behavior(pyd)]) == ["pydantic: 1 of 2 concepts are behavior; the cap is 3/20"]
    assert class_cap_problems([pd001, behavior(pd001), np001, behavior(np001)]) == []
    assert class_cap_problems(concepts) == []


def test_mocks_return_native_references(make_one_directional):
    from varag.llm.client import ChatRequest
    from varag.llm.mock import MockBackend

    directory = make_one_directional()
    meta = {"concept_dir": str(directory), "target": "new"}
    ref = MockBackend("mock_ref", "ref").complete(ChatRequest([], {}, meta)).text
    wrong = MockBackend("mock_wrong", "wrong").complete(ChatRequest([], {}, meta)).text
    assert "method='lower'" in ref and "interpolation='lower'" in wrong
