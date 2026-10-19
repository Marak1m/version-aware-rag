"""Threshold sweep and the freeze (handoff: tuned on dev clue instances, frozen before any test run)."""

import pytest

from varag.pipeline.infer import thresholds
from varag.pipeline.thresholds import Point, clue_instances, frozen, sweep


def test_thresholds_are_frozen_at_the_dev_point():
    stamp = frozen()
    assert stamp is not None and stamp["frozen_split"] == "dev"
    assert thresholds() == (3.0, 1.5)


@pytest.mark.envs
def test_dev_sweep_commits_every_clue_instance_at_the_frozen_point():
    instances = clue_instances("dev")
    assert instances and all(i.split == "dev" and i.condition == "clue" for i in instances)
    (point,) = sweep(instances, commit_grid=(3.0,), noise_grid=(1.5,))
    assert point.committed == point.instances and point.wrong == 0


def test_point_counts():
    p = Point(3.0, 1.5, instances=10, committed=8, correct=7)
    assert (p.wrong, p.uncommitted) == (1, 2)


def test_test_split_run_refuses_unfrozen_thresholds(monkeypatch):
    import varag.pipeline.thresholds as t
    from varag.eval import run as run_module

    monkeypatch.setattr(t, "frozen", lambda: None)
    monkeypatch.setattr(run_module, "require_verified", lambda *a, **k: None)
    with pytest.raises(RuntimeError, match="not frozen"):
        run_module.run("plain_rag", "mock_ref", "test")
