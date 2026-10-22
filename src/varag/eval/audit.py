"""``varag audit sample``: export outputs with the detector's verdict for hand labelling (handoff,
"Detector audit"): precision and recall of the blend detector on natural model output.

The population is every targeted answer with code, one repeat per (instance, method): the lowest
repeat index. Several runs can be pooled (the final sweep pools the three models' test runs).
``stratify`` draws half the sample from answers the detector flags (``blend_static`` or a guard
flag) and half from the rest, because blending is rare and a uniform draw of 50 holds almost no
positives. Each record carries its stratum and weight (stratum population over stratum sample),
so recall is estimated with the weights and precision read directly from the flagged stratum.
Within a stratum the draw rotates over (model, method) so every method appears.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from varag.eval.metrics import first_repeat, load_run, trace_of


def _guard(trace: dict | None, target: str | None) -> dict:
    answers = ((trace or {}).get("method_trace") or {}).get("answers") or []
    return next((a.get("guard") for a in answers if a.get("side") in (target, None)), (answers[0].get("guard") if answers else None)) or {}


def _draw(pool: list[dict], k: int, rng: random.Random) -> list[dict]:
    by_cell: dict[tuple[str, str], list[dict]] = {}
    for r in pool:
        by_cell.setdefault((r["model"], r["method"]), []).append(r)
    picked: list[dict] = []
    while len(picked) < min(k, len(pool)):
        for cell in sorted(by_cell):
            if by_cell[cell] and len(picked) < k:
                picked.append(by_cell[cell].pop(rng.randrange(len(by_cell[cell]))))
    return picked


def audit_sample(run_dirs: Path | list[Path], n: int = 50, seed: int = 1234, out_dir: Path | None = None,
                 stratify: bool = False) -> Path:
    run_dirs = [run_dirs] if isinstance(run_dirs, Path) else list(run_dirs)
    population: list[dict] = []
    run_ids = []
    for run_dir in run_dirs:
        run_json, rows, traces = load_run(run_dir)
        run_ids.append(run_json.get("run_id"))
        for r in first_repeat([r for r in rows if r.get("target") and r.get("code")]):
            guard = _guard(trace_of(traces, r["method"], r), r["target"])
            population.append({**r, "model": r.get("model") or run_json.get("model"), "run_id": run_json.get("run_id"), "_guard": guard,
                               "_flagged": bool(r.get("blend_static")) or bool(guard.get("flagged"))})
    rng = random.Random(seed)
    if stratify:
        strata = {"detector_flagged": [r for r in population if r["_flagged"]], "detector_clean": [r for r in population if not r["_flagged"]]}
        first = min(n // 2, len(strata["detector_flagged"]))
        sizes = {"detector_flagged": first, "detector_clean": n - first}
    else:
        strata = {"all": population}
        sizes = {"all": n}
    out = []
    for name, pool in strata.items():
        picked = _draw(list(pool), sizes[name], rng)
        weight = len(pool) / len(picked) if picked else None
        for r in picked:
            guard = r["_guard"]
            out.append({
                "run_id": r["run_id"], "model": r["model"], "instance_id": r["instance_id"], "method": r["method"], "repeat": r.get("repeat", 0),
                "library": r["library"], "target": r["target"], "code": r["code"],
                "stratum": name, "stratum_population": len(pool), "stratum_sample": len(picked), "weight": weight,
                "detector": {"flagged": r["_flagged"], "blend_static": r.get("blend_static"), "blend_exec": r.get("blend_exec"),
                             "guard_flagged": guard.get("flagged"), "guard_violations": guard.get("violations", [])},
                "execution": {side: {"status": e.get("status"), "last_line": e.get("last_line")} for side, e in (r.get("exec") or {}).items() if isinstance(e, dict)},
                "outcome": r["outcome"],
                "label": {"mixes_versions": None, "notes": ""},
            })
    target_dir = out_dir or run_dirs[0]
    target_dir.mkdir(parents=True, exist_ok=True)
    jsonl = target_dir / "audit_sample.jsonl"
    jsonl.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n", encoding="utf-8", newline="\n")
    strata_line = "; ".join(f"{name}: {sum(1 for x in out if x['stratum'] == name)} of {len(pool)}" for name, pool in strata.items())
    md = [f"# Audit sample: {len(out)} outputs from {', '.join(str(i) for i in run_ids)}", "",
          "For each output, record whether the code mixes APIs of the two versions (`mixes_versions`: yes/no) in audit_sample.jsonl. "
          "The detector's verdict is shown so precision and recall can be computed afterwards"
          + (": precision from the flagged stratum, recall with each record's `weight` (stratum population over stratum sample)." if stratify else "."), "",
          f"Population: targeted answers with code, repeat 0, {len(population)} in all. Strata: {strata_line}.", ""]
    for i, x in enumerate(out, 1):
        md += [f"## {i}. {x['model']} / {x['method']} on {x['instance_id']}", "",
               f"Stratum {x['stratum']}; detector: blend_static={x['detector']['blend_static']}, guard_flagged={x['detector']['guard_flagged']}"
               + (f" ({', '.join(v['symbol'] for v in x['detector']['guard_violations'])})" if x["detector"]["guard_violations"] else "")
               + f"; outcome={x['outcome']}", "",
               "```python", x["code"].rstrip(), "```", ""]
    (target_dir / "audit_sample.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    return jsonl


def _label(record: dict) -> bool | None:
    value = (record.get("label") or {}).get("mixes_versions")
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.strip().lower() in ("yes", "y", "true", "1"):
        return True
    if isinstance(value, str) and value.strip().lower() in ("no", "n", "false", "0"):
        return False
    return None


def score_labels(path: Path) -> dict:
    """The detector's precision and recall from the hand labels in audit_sample.jsonl
    (``label.mixes_versions``: yes/no). Stratified sample: precision is read on the flagged stratum;
    recall weights each labelled record by its stratum's population over the stratum's labelled
    count, so the clean stratum's misses count for the whole clean population. Unlabelled records
    are left out; the result says how many were labelled."""
    from varag.eval.stats import wilson

    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    strata: dict[str, dict] = {}
    for r in records:
        s = strata.setdefault(r.get("stratum", "all"), {"population": r.get("stratum_population") or len(records), "sample": 0, "labelled": 0,
                                                         "mixes": 0, "flagged_mixes": 0, "flagged_labelled": 0})
        s["sample"] += 1
        y = _label(r)
        if y is None:
            continue
        s["labelled"] += 1
        s["mixes"] += y
        if (r.get("detector") or {}).get("flagged"):
            s["flagged_labelled"] += 1
            s["flagged_mixes"] += y
    labelled = sum(s["labelled"] for s in strata.values())
    out: dict = {"records": len(records), "labelled": labelled, "complete": labelled == len(records), "strata": strata,
                 "precision": None, "precision_wilson": None, "recall": None}
    if not labelled:
        return out
    flagged_n = sum(s["flagged_labelled"] for s in strata.values())
    flagged_yes = sum(s["flagged_mixes"] for s in strata.values())
    if flagged_n:
        w = wilson(flagged_yes, flagged_n)
        out.update(precision=flagged_yes / flagged_n, precision_wilson=[w.low, w.high], precision_n=flagged_n)
    # Estimated positives in the population: each stratum's labelled positive share times its size.
    caught = missed = 0.0
    for s in strata.values():
        if not s["labelled"]:
            continue
        weight = s["population"] / s["labelled"]
        caught += weight * s["flagged_mixes"]
        missed += weight * (s["mixes"] - s["flagged_mixes"])
    if caught + missed:
        out["recall"] = caught / (caught + missed)
        out["estimated_positives"] = round(caught + missed, 1)
    return out


# --- the detector audit as scored on 2026-10-21 (user instruction, Part A step 3) -------------------

VARIANTS = {
    "main": {},
    "borderline counted as yes": {"borderline_yes": True},
    "semantic counted as no": {"semantic_no": True},
    "unparseable excluded": {"unparseable_excluded": True},
}


def _variant_label(record: dict, variant: dict) -> bool | None:
    label = record.get("label") or {}
    y = _label(record)
    if y is None or (variant.get("unparseable_excluded") and label.get("unparseable")):
        return None
    if variant.get("borderline_yes") and label.get("borderline"):
        y = True
    if variant.get("semantic_no") and label.get("basis") == "semantic":
        y = False
    return y


def detector_audit(records: list[dict], variant: dict | None = None, n_boot: int = 10000, seed: int = 1234) -> dict:
    """The static blend detector (``blend_static`` on the shown code) against the labels.

    Precision is read on the detector's own flagged rows, leaving out ``post_repair`` rows (the code
    shown is the guard's repair; the execution oracle covers the guard), with a Wilson interval.
    Recall weights each labelled record by its stratum's population over the stratum's labelled
    count; its interval is a stratified bootstrap (labelled records resampled within each stratum).
    A guard-only row of the flagged stratum that mixes versions counts as a miss of the static
    detector, as a clean-stratum one does."""
    from varag.eval.stats import wilson

    variant = variant or {}
    rows = []
    for r in records:
        y = _variant_label(r, variant)
        if y is not None:
            rows.append((r.get("stratum", "all"), int(r.get("stratum_population") or len(records)), bool((r.get("detector") or {}).get("blend_static")),
                         y, (r.get("label") or {}).get("basis")))
    prec = [y for _, _, flagged, y, basis in rows if flagged and basis != "post_repair"]
    w = wilson(sum(prec), len(prec)) if prec else None

    def recall_of(sample: list[tuple]) -> tuple[float | None, float]:
        by: dict[str, list[tuple]] = {}
        for row in sample:
            by.setdefault(row[0], []).append(row)
        caught = positives = mixing = population = 0.0
        for members in by.values():
            weight = members[0][1] / len(members)
            caught += weight * sum(1 for m in members if m[3] and m[2])
            positives += weight * sum(1 for m in members if m[3])
            population += members[0][1]
        return (caught / positives if positives else None), (positives / population if population else 0.0)

    recall, prevalence = recall_of(rows)
    import random

    rng = random.Random(seed)
    strata: dict[str, list[tuple]] = {}
    for row in rows:
        strata.setdefault(row[0], []).append(row)
    boots, undefined = [], 0
    for _ in range(n_boot):
        sample = [rng.choice(members) for members in strata.values() for _ in members]
        value, _ = recall_of(sample)
        if value is None:
            undefined += 1
        else:
            boots.append(value)
    boots.sort()
    interval = [boots[int(0.025 * (len(boots) - 1))], boots[int(0.975 * (len(boots) - 1))]] if boots else [None, None]
    return {"labelled": len(rows), "precision": (sum(prec) / len(prec)) if prec else None, "precision_n": len(prec), "precision_yes": sum(prec),
            "precision_wilson": [w.low, w.high] if w else [None, None], "recall": recall, "recall_bootstrap": interval,
            "recall_undefined_share": undefined / n_boot, "prevalence": prevalence,
            "positives_by_stratum": {s: sum(1 for m in members if m[3]) for s, members in strata.items()},
            "labelled_by_stratum": {s: len(members) for s, members in strata.items()}}


def audit_variants(path: Path) -> dict:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {name: detector_audit(records, variant) for name, variant in VARIANTS.items()}
