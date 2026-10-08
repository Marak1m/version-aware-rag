import re

from varag import config


def test_libraries_have_two_sides():
    libs = config.load_libraries()["libraries"]
    assert set(libs) == {"pandas", "numpy", "pydantic"}
    for lib, entry in libs.items():
        assert entry["old"]["version"] != entry["new"]["version"], lib
        assert entry["inventory_roots"], lib


def test_env_names_and_specs():
    names = config.env_names()
    assert len(names) == 6
    spec = config.env_spec("pandas_old")
    assert spec["library"] == "pandas" and spec["side"] == "old"
    assert spec["extra_pins"] == ["numpy==1.26.4"]
    assert config.env_spec("numpy_new")["extra_pins"] == []


def test_canaries_cover_every_env():
    canaries = config.load_canaries()
    for name in config.env_names():
        lib, _, side = name.rpartition("_")
        assert side in canaries[lib], name
        assert {"present", "absent"} <= set(canaries[lib][side])


def test_models_and_experiment_load():
    models = config.load_models()
    assert {"mock_ref", "mock_wrong", "vllm_qwen7b"} <= set(models["backends"])
    assert models["sampling"]["repetition_penalty"] == 1.0
    exp = config.load_experiment()
    assert exp["thresholds"]["tau_commit"] == 3.0
    assert "va_rag" in exp["methods"]


def test_config_hash_is_sha256():
    assert re.fullmatch(r"[0-9a-f]{64}", config.config_hash())
