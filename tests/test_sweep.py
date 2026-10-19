"""sweep pieces that need no GPU: the noise subset, the estimate and the plan text."""

from varag.sweep import format_plan, noise_ids, seconds_per_answer


def test_noise_subset_is_twenty_dev_instances():
    ids = noise_ids()
    assert len(ids) == 20 == len(set(ids))
    assert all(i.split("/")[0].split("-")[0] in ("pd", "np", "pyd", "ctl") for i in ids)


def test_estimate_falls_back_to_the_config(monkeypatch):
    import varag.sweep as g

    monkeypatch.setattr(g, "_finished_runs", lambda model: [])
    per, source = seconds_per_answer("small")
    assert per > 0 and source == "configs/models.yaml"


def test_plan_text_names_every_model():
    p = {"split": "dev", "concepts": 16, "instances": 83, "methods": 11, "arms": ["knows", "unsure"], "total_min": 3.0,
         "models": [{"model": "small", "answers": 10, "seconds_per_answer": 0.6, "estimate_min": 0.1, "source": "x"},
                    {"model": "large", "answers": 10, "seconds_per_answer": 1.5, "estimate_min": 0.3, "source": "y"}]}
    text = format_plan(p)
    assert "small" in text and "large" in text and "total about 3.0 min" in text


def test_test_split_is_refused_while_it_has_no_concepts():
    from varag.sweep import refusals, sweep

    assert any("no concepts in split 'test'" in r for r in refusals("test"))
    record = sweep("test", dry_run=True, log=lambda _: None)
    assert not record["ok"] and "no concepts" in record["error"]


def test_dev_split_is_not_refused():
    from varag.sweep import refusals

    assert refusals("dev") == []
