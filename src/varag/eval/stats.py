"""Statistics for the report (handoff, "Statistics" and "What size of difference the benchmark
can show"). Pure functions over per-concept and per-instance indicators; no model, no
environment.

- 95% percentile bootstrap intervals from resamples of concepts (clusters), fixed seed.
- Wilson intervals on concept-level proportions, alongside the bootstrap.
- Paired bootstrap on per-concept mean differences between two methods; an exact McNemar test on
  instance pairs as a cross-check; Holm correction across comparisons.
- Detectable difference at 80% power from Miller's formula for paired proportions, with the
  discordant rate and the intra-concept correlation (rho), and an estimate of rho from a run.
- Risk-coverage sweep and AUROC of the absolute margin for predicting a correct commit.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

Z_975 = 1.959963984540054
Z_80 = 0.8416212335729143


@dataclass
class Interval:
    estimate: float | None
    low: float | None
    high: float | None
    n: int

    def to_dict(self) -> dict:
        return {"estimate": self.estimate, "low": self.low, "high": self.high, "n": self.n}


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def cluster_bootstrap(by_concept: dict[str, list[float]], n_resamples: int = 10000, seed: int = 1234) -> Interval:
    """Percentile interval of the instance mean, resampling concepts with replacement."""
    concepts = sorted(c for c, v in by_concept.items() if v)
    values = [x for c in concepts for x in by_concept[c]]
    if not values:
        return Interval(None, None, None, 0)
    rng = random.Random(seed)
    means = []
    for _ in range(n_resamples):
        picked = [concepts[rng.randrange(len(concepts))] for _ in concepts]
        total = sum(sum(by_concept[c]) for c in picked)
        count = sum(len(by_concept[c]) for c in picked)
        means.append(total / count)
    means.sort()
    low = means[int(0.025 * (n_resamples - 1))]
    high = means[int(0.975 * (n_resamples - 1))]
    return Interval(mean(values), low, high, len(values))


def wilson(successes: float, n: int, z: float = Z_975) -> Interval:
    """Wilson score interval for a proportion."""
    if n == 0:
        return Interval(None, None, None, 0)
    p = successes / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return Interval(p, max(0.0, centre - half), min(1.0, centre + half), n)


def concept_means(by_concept: dict[str, list[float]]) -> dict[str, float]:
    return {c: sum(v) / len(v) for c, v in by_concept.items() if v}


def paired_bootstrap(a: dict[str, list[float]], b: dict[str, list[float]], n_resamples: int = 10000, seed: int = 1234) -> Interval:
    """Interval of the mean per-concept difference a - b over the concepts both methods ran."""
    ma, mb = concept_means(a), concept_means(b)
    concepts = sorted(set(ma) & set(mb))
    if not concepts:
        return Interval(None, None, None, 0)
    diffs = [ma[c] - mb[c] for c in concepts]
    rng = random.Random(seed)
    means = sorted(sum(diffs[rng.randrange(len(diffs))] for _ in diffs) / len(diffs) for _ in range(n_resamples))
    return Interval(sum(diffs) / len(diffs), means[int(0.025 * (n_resamples - 1))], means[int(0.975 * (n_resamples - 1))], len(concepts))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from the discordant counts (a passes, b fails) and (a fails, b passes)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def holm(p_values: dict[str, float]) -> dict[str, float]:
    """Holm step-down adjusted p-values."""
    items = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted: dict[str, float] = {}
    running = 0.0
    for rank, (name, p) in enumerate(items):
        running = max(running, min(1.0, (m - rank) * p))
        adjusted[name] = running
    return adjusted


def detectable_difference(n_instances: int, per_concept: float, discordant: float, rho: float,
                          alpha: float = 0.05, power: float = 0.8) -> float:
    """The smallest difference in pass rate (as a fraction) a paired comparison can show, from
    Miller's formula: delta = (z_{alpha/2} + z_power) * sqrt(discordant / n_effective), with
    n_effective = n / (1 + (m - 1) rho) for m instances per concept."""
    z = Z_975 if alpha == 0.05 else _z_two_sided(alpha)
    zb = Z_80 if power == 0.8 else _z_one_sided(power)
    design_effect = 1 + (per_concept - 1) * rho
    n_eff = n_instances / design_effect
    return (z + zb) * math.sqrt(discordant / n_eff)


def _z_two_sided(alpha: float) -> float:
    return _probit(1 - alpha / 2)


def _z_one_sided(power: float) -> float:
    return _probit(power)


def _probit(p: float) -> float:
    """Inverse normal CDF (Acklam's approximation; enough for the table)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    if p < 0.02425:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > 1 - 0.02425:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def intraclass_correlation(by_concept: dict[str, list[float]]) -> float | None:
    """One-way ANOVA estimate of rho for a binary indicator clustered by concept."""
    groups = [v for v in by_concept.values() if len(v) >= 1]
    k = len(groups)
    n = sum(len(g) for g in groups)
    if k < 2 or n <= k:
        return None
    grand = sum(sum(g) for g in groups) / n
    ss_between = sum(len(g) * (sum(g) / len(g) - grand) ** 2 for g in groups)
    ss_within = sum((x - sum(g) / len(g)) ** 2 for g in groups for x in g)
    ms_between = ss_between / (k - 1)
    ms_within = ss_within / (n - k)
    m0 = (n - sum(len(g) ** 2 for g in groups) / n) / (k - 1)
    denominator = ms_between + (m0 - 1) * ms_within
    if denominator == 0:
        return 0.0
    return max(0.0, min(1.0, (ms_between - ms_within) / denominator))


def risk_coverage(margins: list[float], correct: list[bool]) -> list[dict]:
    """Sweep a threshold on |margin|: at each distinct value, the share of instances answered
    (|margin| >= threshold) and the error rate among them."""
    pairs = sorted(zip((abs(m) for m in margins), correct), key=lambda t: -t[0])
    out = []
    n = len(pairs)
    for i, (threshold, _) in enumerate(pairs):
        kept = [c for m, c in pairs if m >= threshold]
        out.append({"threshold": threshold, "coverage": len(kept) / n, "risk": 1 - sum(kept) / len(kept)})
    return out


def auroc(scores: list[float], labels: list[bool]) -> float | None:
    """AUROC of a score for predicting a positive label, by the rank formula with ties at half."""
    positives = [s for s, y in zip(scores, labels) if y]
    negatives = [s for s, y in zip(scores, labels) if not y]
    if not positives or not negatives:
        return None
    total = 0.0
    for p in positives:
        for q in negatives:
            total += 1.0 if p > q else (0.5 if p == q else 0.0)
    return total / (len(positives) * len(negatives))
