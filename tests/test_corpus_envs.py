"""M4 acceptance on the built corpus (marked ``envs``)."""

import json

import pytest

from varag.bench.instances import build_instances
from varag.bench.schema import load_concepts
from varag.config import SIDES, project_root
from varag.corpus.retrieve import PROVENANCE_FIELDS, check_gold_chunks, chunk_for, load_corpus, versions_for
from varag.eval.run import library_versions, retrieval_for

pytestmark = pytest.mark.envs
LIBRARIES = ("pandas", "numpy", "pydantic")


def all_chunks():
    for library in LIBRARIES:
        for side, version in versions_for(library).items():
            yield from load_corpus(library, version)


def test_every_chunk_has_complete_provenance_and_fits_the_cap():
    count = 0
    for chunk in all_chunks():
        count += 1
        assert all(chunk["provenance"].get(f) for f in PROVENANCE_FIELDS), chunk["chunk_id"]
        assert chunk["source"].get("sha256"), chunk["chunk_id"]
        assert chunk["n_tokens"] <= 350, chunk["chunk_id"]
        if chunk["source"]["type"] == "docs":
            assert {"tag", "commit", "path"} <= set(chunk["source"]), chunk["chunk_id"]
    assert count > 4000


def test_every_kept_example_ran_clean_in_its_tagged_environment():
    for chunk in all_chunks():
        if chunk["parts"]["example"]:
            check = chunk["example_check"]
            assert check["status"] == "ok", chunk["chunk_id"]
            assert check["discriminative"] == (check["other_status"] == "error"), chunk["chunk_id"]
        else:
            assert chunk["example_dropped"], chunk["chunk_id"]


@pytest.mark.parametrize("concept_id", ["pd-001", "np-001", "pyd-001", "ctl-np-001"])
def test_step7_passes_for_every_seed_concept(concept_id):
    concept = next(c for c in load_concepts() if c.id == concept_id)
    result = check_gold_chunks(concept)
    assert result["problems"] == [], result


@pytest.mark.parametrize("library,version_side,symbol", [
    ("pandas", "old", "pandas.DataFrame.applymap"), ("pandas", "new", "pandas.DataFrame.map"),
    ("numpy", "old", "numpy.trapz"), ("numpy", "new", "numpy.trapezoid"),
])
def test_symbol_gold_examples_are_discriminative(library, version_side, symbol):
    chunk = chunk_for(library, versions_for(library)[version_side], symbol)
    assert chunk["example_check"]["discriminative"], chunk["chunk_id"]


def test_conflict_true_for_concepts_false_for_control_with_uniform_distractors():
    concepts = {c.id: c for c in load_concepts()}
    instances = build_instances(list(concepts.values()), library_versions())
    retrieved = retrieval_for(instances, concepts)
    for inst in instances:
        rs = retrieved[inst.instance_id]
        assert rs.conflict == (not concepts[inst.concept_id].is_control), (inst.instance_id, rs.conflict_reason)
    # Distractors depend on the task text only: identical across a concept's instances.
    by_concept = {}
    for inst in instances:
        ids = tuple(sorted(r.chunk_id for r in retrieved[inst.instance_id].items if r.role == "distractor"))
        by_concept.setdefault(inst.concept_id, set()).add(ids)
    assert all(len(v) == 1 for v in by_concept.values()), by_concept
    # Exactly half of each concept's targeted instances put the target's gold chunk first.
    for cid, concept in concepts.items():
        if concept.is_control:
            continue
        flags = [retrieved[i.instance_id].target_gold_first for i in instances if i.concept_id == cid]
        assert sum(flags) * 2 == len(flags), (cid, flags)
        for inst in (i for i in instances if i.concept_id == cid):
            first = retrieved[inst.instance_id].items[0]
            assert first.role == "gold" and (first.side == inst.target) == retrieved[inst.instance_id].target_gold_first


def test_example_cache_is_keyed_by_current_locks():
    manifest = json.loads((project_root() / "envs" / "manifest.json").read_text(encoding="utf-8"))
    locks = {e["lock_sha256"] for e in manifest.values()}
    for library in LIBRARIES:
        path = project_root() / "data" / "corpus" / library / "example_checks.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert rows and all(r["lock_sha256"] in locks for r in rows)
