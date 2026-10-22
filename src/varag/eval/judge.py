"""The blend-audit judge (Part A step 4, 2026-10-21): an LLM judge for "does this answer mix the two
versions", used to bound the static blend detector's recall, which the 25-item clean stratum of
the hand-label audit cannot.

- Judge model: ``judge`` in configs/models.yaml, a strong OpenRouter model that is not one of the
  three under test (and not of the family that wrote the calibration labels).
- Input: the concept's two references (``ref_old.py``, and ``ref_new.py`` or, for a one_directional
  concept, ``ref_portable.py``, said to run on both), the pinned versions and the answer code. Never
  the detector's verdict, the guard's, the rule files or the tests.
- Output: JSON with ``mixes_versions`` (yes/no), ``basis`` (exclusive | semantic | deprecated |
  none) and a one-line ``reason``.
- Rubric: written from the user's basis taxonomy and the benchmark's own definitions (config keys
  count wherever they are written: a ``class Config`` body, ``ConfigDict(...)`` or a
  ``model_config`` dict, as the M5 extractor reads them), not tuned on the calibration labels.
- Calibration: the 50 labelled audit outputs; agreement and Cohen's kappa; the full run goes ahead
  only at 45 of 50 or more.
- Full run: every flagged answer of the audit population (202; for a guard-flagged answer the
  stored pre-guard draft as well) and a stratified random 600 of the clean answers (by model x
  method, proportional, seed 1234).
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from varag.llm.client import ChatRequest, OpenRouterBackend

JUDGE_SYSTEM = "You review Python code against two pinned versions of one library. Reply with a single JSON object and nothing else."

RUBRIC = """Does the answer mix the two versions? Say "yes" when the code uses at least one API that belongs only to OLD together with at least one API that belongs only to NEW. An API here is an import path, module, function, class, decorator, method, attribute, keyword argument, accepted argument value, or configuration key.
- OLD-only: removed in NEW or renamed in NEW; kept in NEW only as a deprecated alias that warns; or used with a meaning only OLD gives it.
- NEW-only: added in NEW (absent from OLD); or used with a meaning only NEW gives it.
- Configuration keys count wherever they are written (for pydantic: a `class Config` body, `ConfigDict(...)` or a `model_config` dict); judge the keys, not which of these containers holds them.
- Say "no" when the code uses one version's APIs plus APIs common to both, or only common APIs, even if the code is wrong in other ways or would fail. A name that exists in neither version is not evidence for either side.
- Judge what the code uses, not its comments. If the code does not parse, judge the APIs it uses anyway.
basis: "exclusive" (the mix rests on APIs that exist in one version only), "semantic" (a shared API used with a meaning valid in one version only), "deprecated" (an OLD API that NEW keeps only as a warning alias, beside a NEW-only API), or "none" (the answer is "no").
Reply with JSON only: {"mixes_versions": "yes" or "no", "basis": "exclusive" | "semantic" | "deprecated" | "none", "reason": "one line naming the APIs"}"""

RUBRIC_SHA = hashlib.sha256((JUDGE_SYSTEM + RUBRIC).encode()).hexdigest()


class JudgeBackend(OpenRouterBackend):
    """OpenRouter for the judge: a reasoning model takes no temperature, top_p or repetition
    penalty; the request sends the reasoning effort, the seed and JSON output, and still pins one
    provider with parameters required."""

    @property
    def cache_revision(self) -> str:
        return f"{self.model}@{self.provider}#judge"

    def body(self, request: ChatRequest) -> dict:
        p = request.params
        return {"model": self.model, "messages": request.messages, "max_tokens": p["max_tokens"], "seed": p["seed"],
                "reasoning": {"effort": p["reasoning_effort"]}, "response_format": {"type": "json_object"},
                "provider": {"order": [self.provider], "allow_fallbacks": False, "require_parameters": True}, "usage": {"include": True}}


def judge_params(spec: dict) -> dict:
    return {"max_tokens": int(spec.get("max_tokens", 1200)), "seed": 1234, "reasoning_effort": spec.get("reasoning_effort", "low"), "rubric_sha256": RUBRIC_SHA}


def references(concept) -> tuple[str, str, bool]:
    d = Path(concept.directory)
    old = (d / "ref_old.py").read_text(encoding="utf-8")
    if (d / "ref_new.py").exists():
        return old, (d / "ref_new.py").read_text(encoding="utf-8"), False
    return old, (d / "ref_portable.py").read_text(encoding="utf-8"), True


def judge_messages(concept, versions: dict[str, str], code: str) -> list[dict]:
    old_ref, new_ref, portable = references(concept)
    lib = concept.library
    content = (f"Library: {lib}. OLD = {lib} {versions['old']}. NEW = {lib} {versions['new']}.\n\n"
               f"Reference solution written for OLD ({lib} {versions['old']}):\n```python\n{old_ref.rstrip()}\n```\n\n"
               f"Reference solution written for NEW ({lib} {versions['new']})" + (" (it also runs on OLD)" if portable else "")
               + f":\n```python\n{new_ref.rstrip()}\n```\n\nAnswer to judge:\n```python\n{code.rstrip()}\n```\n\n{RUBRIC}\n")
    return [{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": content}]


def parse_verdict(text: str) -> dict:
    match = re.search(r"\{.*\}", text or "", re.S)
    try:
        data = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        data = {}
    raw = str(data.get("mixes_versions", "")).strip().lower()
    verdict = True if raw in ("yes", "true") else (False if raw in ("no", "false") else None)
    return {"mixes_versions": verdict, "basis": data.get("basis"), "reason": data.get("reason"), "parse_error": verdict is None}


_cache_lock = threading.Lock()


def judge_one(backend, concept, versions: dict[str, str], code: str, params: dict, item_id: str) -> dict:
    request = ChatRequest(judge_messages(concept, versions, code), params, {"instance_id": item_id})
    response = backend.complete(request)
    return {**parse_verdict(response.text), "raw": response.text, "cached": response.cached, "usage": response.usage}


def judge_backend(budget):
    from varag.config import load_models
    from varag.llm.client import make_backend

    spec = load_models()["backends"]["judge"]
    backend = make_backend("judge", budget=budget)
    backend.session = f"judge@{spec['model']}"
    return backend, spec


def judge_items(items: list[dict], budget_usd: float | None = None, workers: int = 8, log=print, backend=None) -> list[dict]:
    """Judge items ({id, concept, versions, code}) in parallel threads; a BudgetExceeded stops the
    remaining items, which come back without a verdict."""
    from varag.llm.client import Budget, BudgetExceeded

    if backend is None:
        backend, spec = judge_backend(Budget(budget_usd))
    else:
        from varag.config import load_models

        spec = load_models()["backends"]["judge"]
    params = judge_params(spec)
    out: list[dict | None] = [None] * len(items)
    done = Counter()

    def work(i: int) -> None:
        item = items[i]
        try:
            out[i] = {**{k: v for k, v in item.items() if k not in ("concept",)}, **judge_one(backend, item["concept"], item["versions"], item["code"], params, item["id"])}
        except BudgetExceeded as exc:
            out[i] = {**{k: v for k, v in item.items() if k not in ("concept",)}, "mixes_versions": None, "error": f"budget: {exc}"}
        except Exception as exc:  # noqa: BLE001
            out[i] = {**{k: v for k, v in item.items() if k not in ("concept",)}, "mixes_versions": None, "error": f"{type(exc).__name__}: {exc}"[:300]}
        with _cache_lock:
            done["n"] += 1
            if done["n"] % 50 == 0:
                log(f"  judged {done['n']}/{len(items)}; spent ${backend.cost_total:.4f}")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(work, range(len(items))))
    log(f"  judged {len(items)}; spent ${backend.cost_total:.4f} ({backend.calls} paid calls, {backend.cache_hits} cache hits)")
    return [x for x in out if x is not None]


# --- the population ------------------------------------------------------------------------------


def population(record: dict) -> list[dict]:
    """The audit population: every targeted answer with code in the three models' test runs, knows
    arm, repeat 0, with the static detector's and the guard's verdicts and the stored draft."""
    from varag.eval.metrics import first_repeat, load_run, trace_of
    from varag.eval.run import runs_dir

    out = []
    for model, entry in record["models"].items():
        run_id = entry["runs"]["test-knows"]
        _, rows, traces = load_run(runs_dir() / run_id)
        for r in first_repeat([r for r in rows if r.get("target") and r.get("code")]):
            t = trace_of(traces, r["method"], r)
            answers = ((t or {}).get("method_trace") or {}).get("answers") or []
            guard = next((a.get("guard") for a in answers if a.get("side") in (r["target"], None)), (answers[0].get("guard") if answers else None)) or {}
            draft = guard.get("pre_guard_code") if guard.get("flagged") else None
            out.append({"id": f"{model}/{r['method']}/{r['instance_id']}/r{r.get('repeat', 0)}", "model": model, "run_id": run_id, "method": r["method"],
                        "instance_id": r["instance_id"], "concept_id": r["concept_id"], "library": r["library"], "repeat": r.get("repeat", 0),
                        "code": r["code"], "draft": draft if draft and draft != r["code"] else None, "blend_static": bool(r.get("blend_static")),
                        "guard_flagged": bool(guard.get("flagged")), "guard_outcome": guard.get("outcome"),
                        "flagged": bool(r.get("blend_static")) or bool(guard.get("flagged"))})
    return out


def stratified_sample(clean: list[dict], n: int, seed: int = 1234) -> tuple[list[dict], dict[tuple[str, str], dict]]:
    """Proportional allocation over (model, method) cells by largest remainder, then a seeded draw
    within each cell. Returns the sample and each cell's population and sample size."""
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for x in clean:
        cells[(x["model"], x["method"])].append(x)
    total = len(clean)
    quotas = {k: n * len(v) / total for k, v in cells.items()}
    alloc = {k: int(q) for k, q in quotas.items()}
    for k in sorted(cells, key=lambda k: -(quotas[k] - int(quotas[k])))[: n - sum(alloc.values())]:
        alloc[k] += 1
    rng = random.Random(seed)
    sample = []
    for k in sorted(cells):
        members = sorted(cells[k], key=lambda x: x["id"])
        sample += rng.sample(members, alloc[k])
    return sample, {k: {"population": len(v), "sample": alloc[k]} for k, v in cells.items()}


def cohen_kappa(a: list[bool], b: list[bool]) -> float | None:
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else None


# --- the run and its analysis --------------------------------------------------------------------

CLEAN_SAMPLE = 600
MIN_AGREE = 45


def _item(x: dict, code: str, concepts: dict, versions: dict, kind: str) -> dict:
    c = concepts[x["concept_id"]]
    return {"id": f"{x['id']}#{kind}", "kind": kind, "model": x["model"], "method": x["method"], "instance_id": x["instance_id"],
            "concept": c, "versions": versions[c.library], "code": code, "blend_static": x.get("blend_static"),
            "guard_flagged": x.get("guard_flagged"), "flagged": x.get("flagged")}


def _label_yes(record: dict) -> bool | None:
    from varag.eval.audit import _label

    return _label(record)


def calibrate(audit_path: Path, backend, concepts: dict, versions: dict, log=print) -> tuple[dict, list[dict]]:
    records = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    items = []
    for n, r in enumerate(records, 1):
        c = concepts[r["instance_id"].split("/")[0]]
        items.append({"id": f"audit#{n}", "kind": "calibration", "n": n, "model": r["model"], "method": r["method"], "instance_id": r["instance_id"],
                      "concept": c, "versions": versions[c.library], "code": r["code"], "label": _label_yes(r), "label_basis": (r.get("label") or {}).get("basis")})
    out = judge_items(items, backend=backend, log=log)
    pairs = [(o["label"], o["mixes_versions"]) for o in out if o["label"] is not None and o["mixes_versions"] is not None]
    agree = sum(a == b for a, b in pairs)
    stats = {"n": len(pairs), "of": len(records), "agree": agree, "kappa": cohen_kappa([a for a, _ in pairs], [b for _, b in pairs]),
             "passed": agree >= MIN_AGREE and len(pairs) == len(records), "no_verdict": [o["id"] for o in out if o["mixes_versions"] is None],
             "disagreements": [{"n": o["n"], "id": f"{o['model']}/{o['method']} {o['instance_id']}", "label": "yes" if o["label"] else "no",
                                "label_basis": o["label_basis"], "judge": "yes" if o["mixes_versions"] else "no", "judge_basis": o.get("basis"),
                                "reason": o.get("reason")} for o in out if o["label"] is not None and o["mixes_versions"] is not None and o["label"] != o["mixes_versions"]]}
    return stats, out


def analyse(pop: list[dict], flagged_out: list[dict], clean_out: list[dict], cells: dict, n_boot: int = 10000, seed: int = 1234) -> dict:
    """Prevalence of mixing in the final answers and the static detector's precision and recall,
    judge as the oracle. The flagged answers are a census; the clean ones a stratified sample by
    (model, method) weighted by cell population over cell sample. Main statistics on parseable
    answers. Variants: the judge's "semantic" or "deprecated" basis counted as no."""
    from varag.eval.stats import wilson
    from varag.pipeline.generate import parses

    variants = {"main": set(), "semantic counted as no": {"semantic"}, "deprecated counted as no": {"deprecated"}}
    final_flagged = [o for o in flagged_out if o["kind"] == "final" and o["mixes_versions"] is not None and parses(o["code"])]
    drafts = [o for o in flagged_out if o["kind"] == "draft" and o["mixes_versions"] is not None]
    clean = [o for o in clean_out if o["mixes_versions"] is not None and parses(o["code"])]
    parseable_pop = {k: 0 for k in cells}
    for x in pop:
        if not x["flagged"] and parses(x["code"]):
            parseable_pop[(x["model"], x["method"])] += 1
    by_cell: dict[tuple, list[dict]] = defaultdict(list)
    for o in clean:
        by_cell[(o["model"], o["method"])].append(o)
    n_parseable = len(final_flagged) + sum(parseable_pop.values())
    out: dict = {"flagged": sum(1 for o in flagged_out if o["kind"] == "final"), "drafts": len(drafts), "clean_sample": len(clean_out),
                 "clean_population": sum(c["population"] for c in cells.values()), "unparseable_judged": sum(1 for o in flagged_out + clean_out if not parses(o["code"])),
                 "parseable_population": n_parseable, "variants": {}}
    rng = random.Random(seed)
    for name, as_no in variants.items():
        yes = lambda o, as_no=as_no: bool(o["mixes_versions"]) and (o.get("basis") not in as_no)  # noqa: E731
        static = [o for o in final_flagged if o.get("blend_static")]
        s_yes = sum(yes(o) for o in static)
        f_yes = sum(yes(o) for o in final_flagged)

        def clean_yes(groups: dict) -> float:
            return sum(parseable_pop[k] / len(v) * sum(yes(o) for o in v) for k, v in groups.items() if v)

        est = clean_yes(by_cell)
        prevalence = (f_yes + est) / n_parseable if n_parseable else None
        recall = s_yes / (f_yes + est) if (f_yes + est) else None
        prevs, recalls = [], []
        for _ in range(n_boot):
            sample = {k: [rng.choice(v) for _ in v] for k, v in by_cell.items() if v}
            e = clean_yes(sample)
            prevs.append((f_yes + e) / n_parseable)
            if f_yes + e:
                recalls.append(s_yes / (f_yes + e))
        prevs.sort()
        recalls.sort()
        w = wilson(s_yes, len(static)) if static else None
        out["variants"][name] = {"prevalence": prevalence, "prevalence_ci": [prevs[int(0.025 * (n_boot - 1))], prevs[int(0.975 * (n_boot - 1))]],
                                 "precision": s_yes / len(static) if static else None, "precision_yes": s_yes, "precision_n": len(static),
                                 "precision_wilson": [w.low, w.high] if w else [None, None], "recall": recall,
                                 "recall_ci": [recalls[int(0.025 * (len(recalls) - 1))], recalls[int(0.975 * (len(recalls) - 1))]] if recalls else [None, None],
                                 "flagged_yes": f_yes, "clean_yes_sampled": sum(yes(o) for o in clean), "clean_yes_estimated": est}
    out["guard_drafts"] = len(drafts)
    out["guard_drafts_yes"] = sum(bool(o["mixes_versions"]) for o in drafts)
    out["clean_positives"] = sum(bool(o["mixes_versions"]) for o in clean_out)
    out["basis_counts"] = {"flagged_final": dict(Counter(o.get("basis") for o in final_flagged if o["mixes_versions"])),
                           "clean": dict(Counter(o.get("basis") for o in clean if o["mixes_versions"]))}
    return out


def run_judge(record: dict, out_dir: Path, max_usd: float, log=print) -> dict:
    from varag.bench.schema import load_concepts
    from varag.eval.run import library_versions
    from varag.llm.client import Budget

    jdir = out_dir / "judge"
    jdir.mkdir(parents=True, exist_ok=True)
    concepts = {c.id: c for c in load_concepts()}
    versions = library_versions()
    budget = Budget(max_usd)
    backend, spec = judge_backend(budget)
    result: dict = {"model": spec["model"], "provider": spec["provider"], "reasoning_effort": spec.get("reasoning_effort"), "rubric_sha256": RUBRIC_SHA,
                    "max_usd": max_usd}
    log(f"calibration: judging the 50 labelled audit outputs with {spec['model']} on {spec['provider']}")
    stats, cal = calibrate(out_dir / "audit_sample.jsonl", backend, concepts, versions, log=log)
    _write_jsonl(jdir / "calibration.jsonl", cal)
    result["calibration"] = stats
    calls = max(1, backend.calls)
    per_call = backend.cost_total / calls
    log(f"calibration: {stats['agree']}/{stats['n']} agree, kappa {stats['kappa']}; ${backend.cost_total:.4f} for {backend.calls} paid calls (${per_call:.5f} each)")
    if not stats["passed"]:
        result["cost_usd"] = round(backend.cost_total, 6)
        _write_json(jdir / "analysis.json", result)
        log(f"STOP: calibration below {MIN_AGREE} of 50; the full run does not go ahead")
        return result
    pop = population(record)
    flagged = [x for x in pop if x["flagged"]]
    clean = [x for x in pop if not x["flagged"]]
    sample, cells = stratified_sample(clean, CLEAN_SAMPLE)
    items = [_item(x, x["code"], concepts, versions, "final") for x in flagged]
    items += [_item(x, x["draft"], concepts, versions, "draft") for x in flagged if x.get("draft")]
    clean_items = [_item(x, x["code"], concepts, versions, "clean") for x in sample]
    estimate = per_call * (len(items) + len(clean_items))
    log(f"full run: {len(items)} flagged items ({sum(1 for i in items if i['kind'] == 'draft')} drafts) and {len(clean_items)} clean; "
        f"estimate ${estimate:.2f}, ${budget.remaining():.2f} left of the ${max_usd:.2f} cap")
    if estimate > (budget.remaining() or 0):
        result["error"] = f"estimate ${estimate:.2f} exceeds the ${budget.remaining():.2f} left"
        result["cost_usd"] = round(backend.cost_total, 6)
        _write_json(jdir / "analysis.json", result)
        log(f"STOP: {result['error']}")
        return result
    flagged_out = judge_items(items, backend=backend, log=log)
    clean_out = judge_items(clean_items, backend=backend, log=log)
    _write_jsonl(jdir / "flagged.jsonl", flagged_out)
    _write_jsonl(jdir / "clean_sample.jsonl", clean_out)
    result["cells"] = {f"{k[0]}/{k[1]}": v for k, v in cells.items()}
    result["full"] = analyse(pop, flagged_out, clean_out, cells)
    result["missing_verdicts"] = [o["id"] for o in flagged_out + clean_out if o["mixes_versions"] is None]
    result["cost_usd"] = round(backend.cost_total, 6)
    positives = [o for o in clean_out if o["mixes_versions"]][:30]
    md = [f"# Clean-stratum judge positives ({len(positives)} of {sum(1 for o in clean_out if o['mixes_versions'])}, judge {spec['model']})", "",
          "Answers the static detector and the guard did not flag, which the judge says mix versions. For review.", ""]
    for i, o in enumerate(positives, 1):
        md += [f"## {i}. {o['model']} / {o['method']} on {o['instance_id']}", "", f"Judge: {o.get('basis')}: {o.get('reason')}", "",
               "```python", o["code"].rstrip(), "```", ""]
    (jdir / "clean_positives.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    _write_json(jdir / "analysis.json", result)
    return result


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps({k: v for k, v in r.items() if k not in ("concept", "versions")}, ensure_ascii=False, default=str) + "\n"
                            for r in rows), encoding="utf-8", newline="\n")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
