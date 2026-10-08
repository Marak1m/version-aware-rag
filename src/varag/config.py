"""Project paths and configuration loading.

Version strings come only from ``configs/libraries.yaml``. Nothing in the code
hardcodes one.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILES = ("libraries.yaml", "canaries.yaml", "models.yaml", "experiment.yaml")
SIDES = ("old", "new")


def project_root() -> Path:
    """The repo root: VARAG_ROOT if set, else the first parent holding pyproject.toml and configs/."""
    override = os.environ.get("VARAG_ROOT")
    if override:
        return Path(override).resolve()
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "configs").is_dir():
            return parent
    raise RuntimeError("cannot locate the project root (no pyproject.toml + configs/ above varag/)")


def configs_dir() -> Path:
    return project_root() / "configs"


def load_yaml(name: str) -> dict[str, Any]:
    with open(configs_dir() / name, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data or {}


def load_libraries() -> dict[str, Any]:
    return load_yaml("libraries.yaml")


def load_canaries() -> dict[str, Any]:
    return load_yaml("canaries.yaml")


def load_models() -> dict[str, Any]:
    return load_yaml("models.yaml")


def load_experiment() -> dict[str, Any]:
    return load_yaml("experiment.yaml")


def config_hash() -> str:
    """sha256 over the four config files, in a fixed order."""
    h = hashlib.sha256()
    for name in CONFIG_FILES:
        h.update(name.encode())
        h.update((configs_dir() / name).read_bytes())
    return h.hexdigest()


def library_names() -> list[str]:
    return list(load_libraries()["libraries"].keys())


def env_name(library: str, side: str) -> str:
    return f"{library}_{side}"


def env_names() -> list[str]:
    return [env_name(lib, side) for lib in library_names() for side in SIDES]


def env_spec(name: str) -> dict[str, Any]:
    """Library, side, pinned version, extra pins and module for one environment name."""
    library, _, side = name.rpartition("_")
    libs = load_libraries()["libraries"]
    if library not in libs or side not in SIDES:
        raise KeyError(f"unknown environment {name!r}")
    entry = libs[library][side]
    return {
        "name": name,
        "library": library,
        "side": side,
        "module": libs[library].get("module", library),
        "version": str(entry["version"]),
        "extra_pins": list(entry.get("extra_pins", [])),
    }


def other_side(side: str) -> str:
    return "new" if side == "old" else "old"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
