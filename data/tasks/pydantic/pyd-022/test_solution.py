import pytest
from pydantic import ValidationError

from solution import AppConfig, load_config


def test_reads_the_file(tmp_path):
    path = tmp_path / "app.json"
    path.write_text('{"name": "api", "port": 8080}', encoding="utf-8")
    config = load_config(str(path))
    assert isinstance(config, AppConfig)
    assert config.name == "api"
    assert config.port == 8080


def test_invalid_content_is_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"name": "api", "port": "high"}', encoding="utf-8")
    with pytest.raises(ValidationError):
        load_config(str(path))
