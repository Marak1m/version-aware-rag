import pytest

from varag.config import project_root


def pytest_collection_modifyitems(config, items):
    """Skip tests marked ``envs`` until the six library environments are built."""
    if (project_root() / "envs" / "manifest.json").exists():
        return
    skip = pytest.mark.skip(reason="envs/manifest.json missing: run `varag env build` first")
    for item in items:
        if "envs" in item.keywords:
            item.add_marker(skip)
