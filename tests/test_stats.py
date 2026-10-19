"""The statistics behind the report."""

import pytest

from varag.eval.stats import (auroc, cluster_bootstrap, detectable_difference, holm, intraclass_correlation, mcnemar_exact,
                              paired_bootstrap, risk_coverage, wilson)


def test_detectable_effect_reproduces_the_handoff_table():
    # 60 concepts, 240 instances, 80% power, two-sided 5%.
    assert round(100 * detectable_difference(240, 4, 0.2, 0.25), 1) == 10.7
    assert round(100 * detectable_difference(240, 4, 0.2, 0.5), 1) == 12.8
    assert round(100 * detectable_difference(240, 4, 0.3, 0.5), 1) == 15.7
    # Other alpha and power go through the probit approximation.
    assert abs(detectable_difference(240, 4, 0.2, 0.25, alpha=0.05, power=0.8) - detectable_difference(240, 4, 0.2, 0.25, alpha=0.050001, power=0.8)) < 1e-4


def test_wilson_and_bootstrap_intervals():
    w = wilson(8, 10)
    assert w.estimate == 0.8 and 0.49 < w.low < 0.5 and 0.94 < w.high < 0.95
    assert wilson(0, 0).estimate is None
    grouped = {f"c{i}": [1.0, 1.0, 0.0, 1.0] if i % 2 else [1.0, 0.0, 0.0, 0.0] for i in range(10)}
    ci = cluster_bootstrap(grouped, n_resamples=2000, seed=1)
    assert ci.estimate == 0.5 and ci.low < 0.5 < ci.high and ci.n == 40
    again = cluster_bootstrap(grouped, n_resamples=2000, seed=1)
    assert (ci.low, ci.high) == (again.low, again.high)          # fixed seed


def test_paired_bootstrap_mcnemar_and_holm():
    a = {f"c{i}": [1.0, 1.0] for i in range(8)}
    b = {f"c{i}": [1.0 if i < 4 else 0.0, 0.0] for i in range(8)}
    diff = paired_bootstrap(a, b, n_resamples=2000, seed=2)
    assert diff.estimate == 0.75 and diff.low > 0
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(10, 0) == pytest.approx(2 / 1024)
    assert mcnemar_exact(5, 5) == 1.0
    adjusted = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adjusted == {"a": 0.03, "c": 0.06, "b": 0.06}


def test_icc_risk_coverage_and_auroc():
    assert intraclass_correlation({"c1": [1.0, 1.0, 1.0], "c2": [0.0, 0.0, 0.0], "c3": [1.0, 1.0, 1.0], "c4": [0.0, 0.0, 0.0]}) == 1.0
    assert intraclass_correlation({"c1": [1.0, 0.0], "c2": [0.0, 1.0]}) == 0.0
    assert intraclass_correlation({"c1": [1.0]}) is None
    curve = risk_coverage([3.0, 2.0, 1.0, 0.5], [True, True, False, True])
    assert curve[0] == {"threshold": 3.0, "coverage": 0.25, "risk": 0.0}
    assert curve[-1]["coverage"] == 1.0 and curve[-1]["risk"] == 0.25
    assert auroc([3.0, 2.0, 1.0, 0.5], [True, True, False, True]) == pytest.approx(2 / 3)
    assert auroc([1.0, 1.0], [True, False]) == 0.5
    assert auroc([1.0], [True]) is None
