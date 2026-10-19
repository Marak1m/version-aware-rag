"""Threshold sweep and freeze (handoff, "Decision rule": thresholds are tuned on dev clue instances
only and frozen before any test-split run).

``sweep`` runs the decision rule over the dev clue instances for a grid of (tau_commit, tau_noise)
and reports, per point, the commits, the wrong commits and the clue instances left uncommitted.
The frozen point lives in configs/experiment.yaml under ``thresholds`` with ``frozen_on`` (a date)
and ``frozen_split: dev``; ``varag run`` refuses a test-split run while ``frozen_on`` is missing.
"""

from __future__ import annotations

from dataclasses import dataclass

from varag.bench.instances import Instance, build_instances
from varag.bench.schema import load_concepts
from varag.config import load_experiment
from varag.pipeline.extract import extract_signals
from varag.pipeline.infer import CONTEXT_CONFLICT, INFER, infer

TAU_COMMIT_GRID = (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0)
TAU_NOISE_GRID = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)


@dataclass
class Point:
    tau_commit: float
    tau_noise: float
    instances: int
    committed: int
    correct: int

    @property
    def wrong(self) -> int:
        return self.committed - self.correct

    @property
    def uncommitted(self) -> int:
        return self.instances - self.committed


def clue_instances(split: str = "dev") -> list[Instance]:
    from varag.eval.run import library_versions

    return [i for i in build_instances(load_concepts(split=split), library_versions()) if i.condition == "clue"]


def sweep(instances: list[Instance], commit_grid=TAU_COMMIT_GRID, noise_grid=TAU_NOISE_GRID) -> list[Point]:
    signals = [(inst, extract_signals(inst.query, inst.context, inst.library)) for inst in instances]
    points = []
    for tc in commit_grid:
        for tn in noise_grid:
            if tn >= tc:
                continue
            decisions = [(inst, infer(sig, tc, tn)) for inst, sig in signals]
            committed = [(inst, d) for inst, d in decisions if d.kind == INFER]
            points.append(Point(tc, tn, len(instances), len(committed), sum(1 for inst, d in committed if d.side == inst.target)))
    return points


def contradiction_instances(split: str = "dev") -> list[Instance]:
    from varag.eval.run import library_versions

    return [i for i in build_instances(load_concepts(split=split), library_versions()) if i.condition == "contradiction"]


def contradiction_sweep(instances: list[Instance], tau_commit: float, noise_grid=TAU_NOISE_GRID) -> list[tuple[float, int, int]]:
    """(tau_noise, instances detected as CONTEXT_CONFLICT, total) at a fixed tau_commit: the check
    of tau_noise that the clue instances cannot give (prompt review, 2026-10-19)."""
    signals = [extract_signals(inst.query, inst.context, inst.library) for inst in instances]
    return [(tn, sum(infer(sig, tau_commit, tn).kind == CONTEXT_CONFLICT for sig in signals), len(instances))
            for tn in noise_grid if tn < tau_commit]


def frozen() -> dict | None:
    """The thresholds block when it carries a freeze stamp, else None."""
    block = load_experiment().get("thresholds", {})
    return block if block.get("frozen_on") else None


def format_sweep(points: list[Point], current: tuple[float, float]) -> str:
    lines = ["tau_commit tau_noise  committed  wrong  uncommitted"]
    for p in points:
        mark = "  <- configured" if (p.tau_commit, p.tau_noise) == current else ""
        lines.append(f"{p.tau_commit:10g} {p.tau_noise:9g}  {p.committed:4}/{p.instances:<4} {p.wrong:5}  {p.uncommitted:11}{mark}")
    return "\n".join(lines)
