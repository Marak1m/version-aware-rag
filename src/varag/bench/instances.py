"""Instances (handoff, "Instances"): a concept run for one target version under one clue
condition, plus version-stated and no-conflict controls.

  {id}/{old|new}/no-clue      ambiguous, no context
  {id}/{old|new}/clue-{type}  ambiguous, one clue; the type rotates over pin, code, error
  {id}/{old|new}/stated       control: one sentence names the version, no context
  {id}/control                no-conflict control: no target

A one_directional concept gets new/no-clue and new/clue-{type} only (user decision 2026-10-15).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from varag.bench.schema import CLUE_TYPES, Concept
from varag.config import SIDES


@dataclass
class Instance:
    instance_id: str
    concept_id: str
    library: str
    split: str
    kind: str                 # ambiguous | stated | control
    target: str | None        # old | new | None
    condition: str            # no-clue | clue | stated | control
    query: str
    context: str = ""
    clue_type: str | None = None
    overlap: str | None = None
    concept_dir: str = ""

    @property
    def targeted(self) -> bool:
        return self.target is not None

    def to_dict(self) -> dict:
        return asdict(self)


def stated_sentence(library: str, version: str) -> str:
    return f"I am using {library} {version}."


def rotated_clue_type(available: list[str], concept_index: int, side_index: int) -> str | None:
    """Rotate over pin, code, error so the three are balanced within a library and across targets."""
    ordered = [t for t in CLUE_TYPES if t in available]
    if not ordered:
        return None
    return ordered[(2 * concept_index + side_index) % len(ordered)]


def build_instances(concepts: list[Concept], versions: dict[str, dict[str, str]]) -> list[Instance]:
    """``versions`` maps library -> {old: version, new: version} (from the environment manifest)."""
    out: list[Instance] = []
    by_library: dict[str, list[Concept]] = {}
    for c in sorted(concepts, key=lambda c: (c.library, c.id)):
        by_library.setdefault(c.library, []).append(c)

    for library, group in by_library.items():
        index = 0             # concepts with the full clue rotation
        behaviour_index = 0   # behaviour concepts: pin and code only (user decision 2026-10-18)
        for concept in group:
            base = {"concept_id": concept.id, "library": library, "split": concept.split, "concept_dir": str(concept.directory)}
            if concept.is_control:
                out.append(Instance(f"{concept.id}/control", kind="control", target=None, condition="control", query=concept.query, **base))
                continue
            for side in concept.target_sides:
                side_index = SIDES.index(side)
                out.append(Instance(f"{concept.id}/{side}/no-clue", kind="ambiguous", target=side, condition="no-clue", query=concept.query, **base))
                rotation = behaviour_index if concept.exclusivity == "behavior" else index
                clue_type = rotated_clue_type([c.type for c in concept.clues.get(side, [])], rotation, side_index)
                if clue_type:
                    clue = concept.clue(side, clue_type)
                    out.append(Instance(
                        f"{concept.id}/{side}/clue-{clue_type}", kind="ambiguous", target=side, condition="clue",
                        query=concept.query, context=clue.text, clue_type=clue_type, overlap=clue.overlap, **base,
                    ))
                if concept.control_eligible and not concept.one_directional:
                    sentence = stated_sentence(library, versions[library][side])
                    out.append(Instance(
                        f"{concept.id}/{side}/stated", kind="stated", target=side, condition="stated",
                        query=f"{concept.query}\n\n{sentence}", **base,
                    ))
            if concept.exclusivity == "behavior":
                behaviour_index += 1
            else:
                index += 1
    return out
