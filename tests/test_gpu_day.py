"""gpu-day pieces that need no GPU: the noise subset, the estimate and the plan text."""

from varag.gpu_day import format_plan, noise_ids, seconds_per_answer


def test_noise_subset_is_twenty_dev_instances():
    ids = noise_ids()
    assert len(ids) == 20 == len(set(ids))
    assert all(i.split("/")[0].split("-")[0] in ("pd", "np", "pyd", "ctl") for i in ids)


def test_estimate_falls_back_to_the_config(monkeypatch):
    import varag.gpu_day as g

    monkeypatch.setattr(g, "_finished_runs", lambda model: [])
    per, source = seconds_per_answer("primary")
    assert per > 0 and source == "configs/models.yaml"


def test_plan_text_names_every_model():
    p = {"split": "dev", "concepts": 16, "instances": 83, "methods": 11, "arms": ["knows", "unsure"], "total_min": 3.0,
         "models": [{"model": "primary", "answers": 10, "seconds_per_answer": 0.6, "estimate_min": 0.1, "source": "x"},
                    {"model": "vllm_large", "answers": 10, "seconds_per_answer": 1.5, "estimate_min": 0.3, "source": "y"}]}
    text = format_plan(p)
    assert "primary" in text and "vllm_large" in text and "total about 3.0 min" in text
