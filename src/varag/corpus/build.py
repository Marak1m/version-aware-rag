"""``varag corpus build``: one chunk per API symbol per version, with provenance.

pandas and NumPy chunks come from the installed docstrings (read inside the verified
environment, so the version tag is true by construction); pydantic chunks come from the docs
markdown at the release tag, falling back to the docstring. Examples are checked by execution
(varag.corpus.examples). See docs/plans/M4.md for the decisions.
"""

from __future__ import annotations

import json
import statistics
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.bench.schema import load_concepts
from varag.config import SIDES, env_name, load_experiment, load_libraries, other_side, project_root, sha256_text
from varag.corpus import pydantic_docs
from varag.corpus.chunks import Composed, Parts, deprecation_note, description_from_summary, fit, with_example
from varag.corpus.examples import CheckCache, CheckResult, example_sha, extract_doctest_example, fenced_blocks, pick_block, run_checks, ANY
from varag.corpus.tokens import count_tokens, tokenizer_provenance
from varag.envs.build import read_manifest
from varag.envs.runner import run_script
from varag.envs.verify import require_verified
from varag.inventory.build import load_diff, load_inventories

# config_key chunks (pydantic.Config.<key>) carry the config docs section that mentions the key, so
# config-key concepts have gold chunks (seed pyd-002 and pyd-003, 2026-10-19).
CHUNK_KINDS = ("function", "method", "class", "attribute", "config_key")
EXCLUDED_OWNERS = ()


def corpus_dir(library: str) -> Path:
    return project_root() / "data" / "corpus" / library


def corpus_path(library: str, version: str) -> Path:
    return corpus_dir(library) / f"{version}.jsonl"


def gold_keywords(library: str) -> dict[str, dict[str, tuple]]:
    """side -> owner symbol -> (keyword, value), for concepts whose gold is a keyword (decision D5)
    or a value (decision D-b: the example should pass the gold value, freq="M" in 1.5.3)."""
    from varag.pipeline.values import parse_gold

    out: dict[str, dict[str, tuple]] = {side: {} for side in SIDES}
    for concept in load_concepts(library):
        for side in SIDES:
            for symbol in list(concept.gold.get(side, [])) + list(concept.gold.get("shared", [])):
                ref = parse_gold(symbol)
                if ref.param:
                    out[side][ref.owner] = (ref.param, ref.value if ref.has_value else ANY)
    return out


def exclusive_params(diff: dict, owner: str) -> set[str]:
    out = set()
    for bucket in ("old_only", "new_only", "deprecated_in_new"):
        for symbol in diff[bucket]:
            if symbol.startswith(owner + "(") and symbol.endswith(")"):
                out.add(symbol[len(owner) + 1:-1])
    return out


def read_docstrings(env: str, roots: list[dict], symbols: list[str]) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "docs.json"
        run_script(env, "docstring_extract.py", [str(out)], stdin_text=json.dumps({"roots": roots, "symbols": symbols}), timeout=1800)
        return json.loads(out.read_text(encoding="utf-8"))


def _source_example(library: str, symbol: str, entry: dict, doc: dict, keyword: str | None, value: object = ANY) -> tuple[str | None, bool]:
    name = symbol.rsplit(".", 1)[-1]
    examples = doc.get("examples", "")
    code, kw_met = extract_doctest_example(examples, name, keyword, value=value) if ">>>" in examples else (None, False)
    if code is None:
        code, kw_met = pick_block(fenced_blocks(examples + "\n" + doc.get("summary_region", "")), name, keyword, value)
    return code, kw_met


def compose_side(library: str, side: str, version: str, entries: list[dict], diff: dict, docs: dict,
                 keywords: dict[str, tuple], sections: list | None, docs_manifest: dict | None) -> list[dict]:
    """Chunk drafts for one version: parts fitted to the cap and a candidate example (not yet checked)."""
    params_by_owner: dict[str, list[dict]] = {}
    for e in entries:
        if e["kind"] == "param":
            params_by_owner.setdefault(e["owner"], []).append({"name": e["name"], "default": e.get("default")})
    all_blocks = [(s, b) for s in sections for b in s.blocks] if sections else []
    drafts = []
    for entry in entries:
        if entry["kind"] not in CHUNK_KINDS or entry["owner"].startswith(EXCLUDED_OWNERS):
            continue
        symbol = entry["symbol"]
        name = entry["name"]
        title = symbol[len(library) + 1:]
        doc = docs.get(symbol, {})
        keyword, value = keywords.get(symbol, (None, ANY))
        section = pydantic_docs.section_for(symbol, version, sections) if sections else None
        if section is not None:
            description = pydantic_docs.first_sentence(section.body) or description_from_summary(doc.get("summary_region", ""))
            note = None
            example, kw_met = pick_block(section.blocks, name, keyword, value)
            if keyword and not kw_met:
                for s, block in all_blocks:          # D5: prefer any docs example that passes the keyword (and the gold value)
                    found, met = pick_block([block], name, keyword, value)
                    if found and met:
                        example, kw_met = found, True
                        break
            if example is None:                       # section has no example: first block in the same file
                same_file = [b for s, b in all_blocks if s.path == section.path]
                example, _ = pick_block(same_file, name)
            source = {"type": "docs", "ref": section.ref, "sha256": section.file_sha256, "repo": docs_manifest["repo"],
                      "tag": docs_manifest["tag"], "commit": docs_manifest["commit"], "path": section.path, "heading": section.heading}
        else:
            summary = doc.get("summary_region", "")
            description = description_from_summary(summary)
            note = deprecation_note(summary)
            example, kw_met = _source_example(library, symbol, entry, doc, keyword, value)
            source = {"type": "docstring", "ref": symbol, "sha256": doc.get("doc_sha256")}
            if not source["sha256"]:
                # No docstring (a config key read from annotations): the inventory entry is the source.
                source = {"type": "inventory", "ref": symbol, "sha256": sha256_text(json.dumps(entry, sort_keys=True))}
        if entry["kind"] == "config_key":
            # A config docs section is a list of keys: describe the key by the line that names it.
            if section is not None:
                hit = next((ln for ln in section.body.splitlines() if pydantic_docs.mention_pattern(name).search(ln)), None)
                if hit:
                    description = hit.strip().lstrip("-* ").strip()
            if not description:
                description = f"Model configuration key `{name}`."
        parts = Parts(fqn=symbol, library=library, version=version, kind=entry["kind"], title=title,
                      signature=entry.get("signature"), description=description, deprecation_note=note)
        # Signature order, from the owner's params list (inventory entries are sorted by symbol).
        by_name = {p["name"]: p for p in params_by_owner.get(symbol, [])}
        params = [by_name[n] for n in entry.get("params", []) if n in by_name]
        keep = exclusive_params(diff, symbol) | ({keyword} if keyword else set())
        composed = fit(parts, count_tokens, params, bool(entry.get("accepts_var_kwargs")), keep)
        drafts.append({
            "symbol": symbol, "entry": entry, "params": [p["name"] for p in params], "composed": composed,
            "example": example, "keyword": keyword, "gold_value": None if value is ANY else repr(value),
            "keyword_example": kw_met if keyword else None, "source": source,
        })
    return drafts


def check_examples(library: str, side: str, drafts: list[dict], manifest: dict, cache: CheckCache,
                   timeout: float, log: Callable[[str], None]) -> set[tuple[str, str]]:
    """Fills draft["check"] with the tagged and other-environment results. Returns the cache keys used."""
    used: set[tuple[str, str]] = set()
    envs = {"tagged": env_name(library, side), "other": env_name(library, other_side(side))}
    locks = {k: manifest[e]["lock_sha256"] for k, e in envs.items()}
    fitting = {}
    for d in drafts:
        d["check"] = None
        if not d["example"]:
            d["dropped"] = "no example"
            continue
        if with_example(d["composed"], d["example"], count_tokens) is None:
            d["dropped"] = "length"
            continue
        fitting[example_sha(d["example"])] = d["example"]
    for which in ("tagged", "other"):
        wanted = fitting if which == "tagged" else {
            sha: code for sha, code in fitting.items() if cache.get(locks["tagged"], sha).status == "ok"}
        todo = [(sha, code) for sha, code in wanted.items() if cache.get(locks[which], sha) is None]
        if todo:
            log(f"  [{envs[which]}] running {len(todo)} example(s) ({len(wanted) - len(todo)} cached)")
            for sha, result in run_checks(envs[which], library, todo, timeout=timeout, log=log).items():
                cache.put(locks[which], sha, envs[which], result)
        used |= {(locks[which], sha) for sha in wanted}
    for d in drafts:
        if d.get("dropped"):
            continue
        sha = example_sha(d["example"])
        tagged: CheckResult = cache.get(locks["tagged"], sha)
        other = cache.get(locks["other"], sha) if tagged.status == "ok" else None
        d["check"] = {
            "example_sha256": sha,
            "status": tagged.status,
            "error": tagged.error,
            "soft_warnings": tagged.soft_warnings,
            "retried": tagged.retried,
            "other_env": envs["other"],
            "other_status": other.status if other else None,
            "other_error": other.error if other else None,
            "discriminative": bool(other and other.status == "error"),
        }
        if tagged.status != "ok":
            d["dropped"] = tagged.status
    return used


def finalize(library: str, version: str, d: dict, lock: str, created_at: str) -> dict:
    composed: Composed = d["composed"]
    if d["example"] and not d.get("dropped"):
        composed = with_example(composed, d["example"], count_tokens)
    parts = composed.parts
    chunk = {
        "chunk_id": f"{library}-{version}-{parts.title}",
        "library": library,
        "version": version,
        "kind": "api",
        "symbol_kind": d["entry"]["kind"],
        "symbols": [d["symbol"]] + [f"{d['symbol']}({p})" for p in d["params"]],
        "title": parts.title,
        "text": composed.text,
        "n_tokens": composed.n_tokens,
        "parts": {"fqn": parts.fqn, "signature": parts.signature, "description": parts.description,
                  "deprecation_note": parts.deprecation_note, "example": parts.example},
        "example_check": d["check"] if parts.example else None,
        "example_dropped": None if parts.example else (d.get("dropped") or "no example"),
        "example_dropped_detail": (d["check"] or {}).get("error") if not parts.example and d.get("check") else None,
        # D5: whether the example in the final chunk passes the gold keyword (None: no gold keyword here).
        "keyword_example": None if d["keyword"] is None else bool(d["keyword_example"] and parts.example),
        "keyword": d["keyword"],
        "trims": composed.trims,
        "source": d["source"],
    }
    chunk["provenance"] = {
        "library": library, "version": version, "lock_sha256": lock, "source": "varag corpus build",
        "content_sha256": sha256_text(composed.text), "created_at": created_at, "tokenizer": tokenizer_provenance(),
    }
    return chunk


def build_library(library: str, manifest: dict, log: Callable[[str], None] = print) -> dict:
    cfg = load_libraries()["libraries"][library]
    timeout = float(load_experiment().get("corpus", {}).get("example_timeout_s", 10))
    inventories = load_inventories(library)
    diff = load_diff(library)
    keywords = gold_keywords(library)
    cache = CheckCache(corpus_dir(library) / "example_checks.jsonl")
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    drafts_by_side, versions, used = {}, {}, set()
    for side in SIDES:
        env = env_name(library, side)
        versions[side] = manifest[env]["library_version"]
        entries = inventories[side]
        symbols = [e["symbol"] for e in entries if e["kind"] in CHUNK_KINDS]
        log(f"[{env}] reading {len(symbols)} docstrings")
        docs = read_docstrings(env, cfg["inventory_roots"], symbols)
        sections, docs_manifest = None, None
        if library == "pydantic":
            docs_manifest, sections = pydantic_docs.load_sections(versions[side], log)
        drafts_by_side[side] = compose_side(library, side, versions[side], entries, diff, docs, keywords[side], sections, docs_manifest)
    for side in SIDES:
        log(f"[{library} {versions[side]}] checking examples")
        used |= check_examples(library, side, drafts_by_side[side], manifest, cache, timeout, log)
    cache.save(keep=used)
    report = {"library": library, "created_at": created_at, "versions": {}}
    for side in SIDES:
        version = versions[side]
        lock = manifest[env_name(library, side)]["lock_sha256"]
        chunks = sorted((finalize(library, version, d, lock, created_at) for d in drafts_by_side[side]), key=lambda c: c["chunk_id"])
        path = corpus_path(library, version)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for c in chunks:
                fh.write(json.dumps(c, sort_keys=True) + "\n")
        report["versions"][version] = summarize(chunks)
        log(f"[{library} {version}] {len(chunks)} chunks -> {path.name}; " + json.dumps(report["versions"][version]["examples"]))
    (corpus_dir(library) / "build_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return report


def summarize(chunks: list[dict]) -> dict:
    tokens = sorted(c["n_tokens"] for c in chunks)

    def pct(p: float) -> int:
        return tokens[min(len(tokens) - 1, int(p * len(tokens)))] if tokens else 0

    with_example = [c for c in chunks if c["parts"]["example"]]
    return {
        "chunks": len(chunks),
        "n_tokens": {"min": tokens[0] if tokens else 0, "p10": pct(0.1), "median": int(statistics.median(tokens)) if tokens else 0,
                     "p90": pct(0.9), "max": tokens[-1] if tokens else 0,
                     "under_200": sum(1 for t in tokens if t < 200), "over_350": sum(1 for t in tokens if t > 350)},
        "examples": {
            "kept": len(with_example),
            "discriminative": sum(1 for c in with_example if c["example_check"]["discriminative"]),
            "with_soft_warnings": sum(1 for c in with_example if c["example_check"]["soft_warnings"]),
            "dropped": dict(Counter(c["example_dropped"] for c in chunks if c["example_dropped"])),
        },
        "trims": dict(Counter(t for c in chunks for t in c["trims"])),
        "sources": dict(Counter(c["source"]["type"] for c in chunks)),
    }


def build_corpus(libraries: list[str] | None = None, log: Callable[[str], None] = print) -> dict:
    libraries = libraries or list(load_libraries()["libraries"])
    require_verified([env_name(lib, side) for lib in libraries for side in SIDES])
    manifest = read_manifest()
    return {lib: build_library(lib, manifest, log) for lib in libraries}
