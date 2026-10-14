"""``varag inventory build``: run the extractor in all six environments, write inventories
with provenance, dump the rule tables the new-side packages ship, and write the diffs."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable

from varag.config import SIDES, env_name, load_libraries
from varag.envs.build import read_manifest
from varag.envs.runner import run_script
from varag.envs.verify import require_verified
from varag.inventory import rules as rules_mod
from varag.inventory.diff import build_diff
from varag.inventory.schema import diff_path, inventory_path, read_inventory, write_inventory

SHIPPED_RULES = {"numpy": "expired_attrs_2_0.json", "pydantic": "migration.json"}


def rule_names_by_root(library: str) -> dict[str, list[str]]:
    """Names the rule sets mention, grouped by owner, so hidden members get probed too."""
    out: dict[str, set[str]] = {}
    for rule in rules_mod.load_rules(library):
        for symbol in (rule.symbol, rule.replacement):
            if not symbol or "(" in symbol or not symbol.startswith(library + "."):
                continue
            owner, _, name = symbol.rpartition(".")
            out.setdefault(owner, set()).add(name)
    return {owner: sorted(names) for owner, names in out.items()}


def extract_side(library: str, side: str, cfg: dict, manifest: dict, log: Callable[[str], None]) -> tuple[str, list[dict]]:
    name = env_name(library, side)
    version = manifest[name]["library_version"]
    extra = rule_names_by_root(library)
    roots = [{**root, "extra_names": extra.get(root["public"], [])} for root in cfg["inventory_roots"]]
    spec = {"library": library, "version": version, "roots": roots}
    if cfg.get("config_keys"):
        spec["config_keys"] = {"public": cfg["config_keys"]["public"], **cfg["config_keys"][side]}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "inventory.jsonl"
        diagnostics = run_script(name, "inventory_extract.py", [str(out)], stdin_text=json.dumps(spec), timeout=900)
        entries = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    for root, error in diagnostics.get("roots_failed", {}).items():
        log(f"[{name}] root unavailable: {root}: {error}")
    write_inventory(inventory_path(library, version), entries, library, version, manifest[name]["lock_sha256"], f"inventory_extract.py in {name}")
    log(f"[{name}] {len(entries)} entries from {len(diagnostics.get('roots_ok', []))} roots -> {inventory_path(library, version).name}")
    return version, entries


def dump_shipped_rules(library: str, manifest: dict, log: Callable[[str], None]) -> None:
    filename = SHIPPED_RULES.get(library)
    if not filename:
        return
    name = env_name(library, "new")
    data = run_script(name, "dump_rules.py", [library])
    provenance = {"library": library, "version": data["version"], "lock_sha256": manifest[name]["lock_sha256"], "source": f"dump_rules.py in {name}"}
    field_kwargs = data.pop("field_v1_kwargs", None)
    data.update(provenance)
    path = rules_mod.rules_dir(library) / filename
    rules_mod._write_json(path, data)
    log(f"[{name}] rule tables -> {path.relative_to(path.parents[3])}")
    if field_kwargs is not None:
        field_kwargs.update(provenance)
        path = rules_mod.rules_dir(library) / "field_v1_kwargs.json"
        rules_mod._write_json(path, field_kwargs)
        log(f"[{name}] Field() V1 keywords -> {path.relative_to(path.parents[3])}: " + ", ".join(f"{k}={v['handling']}" for k, v in field_kwargs["keywords"].items()))


def build_inventories(libraries: list[str] | None = None, log: Callable[[str], None] = print) -> None:
    config = load_libraries()
    libraries = libraries or list(config["libraries"])
    require_verified([env_name(lib, side) for lib in libraries for side in SIDES])
    manifest = read_manifest()
    generic = set(config.get("generic_method_names", []))
    for library in libraries:
        cfg = config["libraries"][library]
        dump_shipped_rules(library, manifest, log)
        versions, entries = {}, {}
        for side in SIDES:
            versions[side], entries[side] = extract_side(library, side, cfg, manifest, log)
        provenance = {
            side: {"version": versions[side], "lock_sha256": manifest[env_name(library, side)]["lock_sha256"]}
            for side in SIDES
        }
        diff = build_diff(
            library, versions["old"], versions["new"], entries["old"], entries["new"],
            generic, rules_mod.deprecated_symbols(library), provenance,
            rule_kept_keywords=rules_mod.deprecated_kept_symbols(library),
            rule_listed=rules_mod.rule_listed_symbols(library),
        )
        path = diff_path(library)
        path.write_text(json.dumps(diff, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        rules_mod.write_replacements(library)
        log(f"[{library}] diff: " + ", ".join(f"{k}={v}" for k, v in diff["counts"].items()))


def load_diff(library: str) -> dict:
    return json.loads(diff_path(library).read_text(encoding="utf-8"))


def load_inventories(library: str) -> dict[str, list[dict]]:
    """Both sides' entries, each checked against the current manifest lock."""
    manifest = read_manifest()
    out = {}
    for side in SIDES:
        entry = manifest[env_name(library, side)]
        _, entries = read_inventory(inventory_path(library, entry["library_version"]), entry["lock_sha256"])
        out[side] = entries
    return out
