"""The decision rule (handoff, "Decision rule") and validation step 6.

    strong(v) = D[v] or S[v] >= tau_commit
    weak(v)   = not D[v] and S[v] <= tau_noise
    INFER(old) if strong(old) and weak(new); INFER(new) if strong(new) and weak(old);
    CONTEXT_CONFLICT if neither side is weak; else UNCERTAIN.
    margin = S[old] - S[new], logged with D[old] and D[new].

Thresholds live in configs/experiment.yaml, are tuned on dev clue instances only and are frozen
before any test-split run. Weights are not tuned in M5 (fitting them is L17).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from varag.bench.schema import Concept
from varag.config import SIDES, env_name, load_experiment, other_side
from varag.pipeline.extract import Signals, extract_signals

INFER, UNCERTAIN, CONTEXT_CONFLICT = "INFER", "UNCERTAIN", "CONTEXT_CONFLICT"


@dataclass
class Decision:
    kind: str                 # INFER | UNCERTAIN | CONTEXT_CONFLICT
    side: str | None          # old | new when INFER
    S: dict                   # non-decisive weight per side
    D: dict                   # decisive signal present per side
    margin: float             # S[old] - S[new]
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


def thresholds() -> tuple[float, float]:
    t = load_experiment().get("thresholds", {})
    return float(t.get("tau_commit", 3.0)), float(t.get("tau_noise", 1.5))


def infer(signals: Signals, tau_commit: float | None = None, tau_noise: float | None = None) -> Decision:
    commit, noise = thresholds()
    tau_commit = commit if tau_commit is None else tau_commit
    tau_noise = noise if tau_noise is None else tau_noise
    S = {side: signals.S(side) for side in SIDES}
    D = {side: signals.D(side) for side in SIDES}
    strong = {side: D[side] or S[side] >= tau_commit for side in SIDES}
    weak = {side: (not D[side]) and S[side] <= tau_noise for side in SIDES}
    margin = S["old"] - S["new"]
    for side in SIDES:
        if strong[side] and weak[other_side(side)]:
            why = "decisive signal" if D[side] else f"S[{side}]={S[side]:g} >= {tau_commit:g}"
            return Decision(INFER, side, S, D, margin, f"{why}; other side weak")
    if not weak["old"] and not weak["new"]:
        return Decision(CONTEXT_CONFLICT, None, S, D, margin, "both sides have evidence above the noise threshold")
    return Decision(UNCERTAIN, None, S, D, margin, "no side is strong while the other is weak")


# --- validation step 6 ----------------------------------------------------------------------


def reproduce_error_clue(concept: Concept, clue) -> str | None:
    """Re-run the clue's snippet in its side's environment and compare the traceback's last line
    with the recorded one. Returns a problem string, or None."""
    from varag.bench.schema import error_clue_snippet
    from varag.corpus.examples import run_checks

    snippet = error_clue_snippet(clue.text).rstrip()
    recorded = [line for line in clue.text.splitlines() if line.strip()]
    if not snippet.strip() or not recorded:
        return f"{clue.file}: empty snippet or traceback"
    last = recorded[-1].strip()
    result = run_checks(env_name(concept.library, clue.side), concept.library, [("clue", snippet)], timeout=30, log=lambda _: None)["clue"]
    if result.status != "error":
        return f"{clue.file}: snippet did not fail in {clue.side} ({result.status})"
    observed = (result.error or "").strip().splitlines()[-1].strip() if result.error else ""
    if observed.split(":")[0] != last.split(":")[0]:
        return f"{clue.file}: traceback last line changed: recorded {last[:80]!r}, observed {observed[:80]!r}"
    return None


def check_clues(concept: Concept) -> dict:
    """Validation step 6: each clue alone infers its side; each error clue's traceback reproduces.
    Returns {"problems", "info", "record"} like step 7."""
    if concept.is_control:
        return {"problems": [], "info": "controls carry no clues", "record": {}}
    problems: list[str] = []
    info: list[str] = []
    decisions: dict[str, dict] = {}
    for side, clues in concept.clues.items():
        for clue in clues:
            signals = extract_signals("", clue.text, concept.library)
            decision = infer(signals)
            decisions[clue.file] = {"kind": decision.kind, "side": decision.side, "margin": decision.margin, "S": decision.S, "D": decision.D}
            if decision.kind != INFER or decision.side != side:
                problems.append(f"{clue.file} ({clue.type}, {side}): {decision.kind}" + (f"({decision.side})" if decision.side else "")
                                + f" S={decision.S} D={decision.D}")
            else:
                info.append(f"{clue.file}: INFER({side}) margin {decision.margin:+g}" + (" decisive" if decision.D[side] else ""))
            if clue.type == "error":
                problem = reproduce_error_clue(concept, clue)
                if problem:
                    problems.append(problem)
                else:
                    info.append(f"{clue.file}: traceback reproduces in {side}")
    return {"problems": problems, "info": "; ".join(info), "record": {"clue_decisions": decisions}}
