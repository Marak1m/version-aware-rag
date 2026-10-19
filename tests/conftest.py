from pathlib import Path

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


# --- a synthetic one_directional concept (numpy percentile `interpolation` -> `method`), written to
# a temp directory by tests; it is not part of data/tasks.

CONCEPT_YAML = """\
id: {id}
library: numpy
split: dev
query: >
  Write `lower_median(values)` returning the lower median of a list of numbers as a float,
  computed with numpy's percentile function using the 'lower' rule.
entry_point: lower_median
exclusivity: one_directional
change_type: param_rename
portable_alternative: plain
gold:
  old: ["numpy.percentile(interpolation)"]
  new: ["numpy.percentile(method)"]
clues:
  new:
    - {{type: code, file: clues/new_code.txt, overlap: off_target}}
control_eligible: true
"""
REF_OLD = "import numpy as np\n\n\ndef lower_median(values):\n    return float(np.percentile(values, 50, interpolation='lower'))\n"
REF_PORTABLE = "import numpy as np\n\n\ndef lower_median(values):\n    return float(np.percentile(values, 50, method='lower'))\n"
TEST = ("from solution import lower_median\n\n\ndef test_lower_median():\n"
        "    assert lower_median([1, 2, 3, 4]) == 2.0\n    assert lower_median([5, 1, 3]) == 3.0\n")
WRONG = "import numpy as np\n\n\ndef lower_median(values):\n    return float(np.median(values))\n"
CODE_CLUE = "import numpy as np\n\nx = np.trapezoid([1, 2, 3])\ny = np.cumulative_sum([1, 2, 3])\nprint(x, y)\n"


def write_concept(root: Path, concept_id: str = "np-od-900", ref_new: bool = False, portable: str = "plain") -> Path:
    directory = root / concept_id
    (directory / "clues").mkdir(parents=True)
    (directory / "concept.yaml").write_text(CONCEPT_YAML.format(id=concept_id).replace("plain", portable), encoding="utf-8")
    (directory / "ref_old.py").write_text(REF_OLD, encoding="utf-8")
    (directory / "ref_portable.py").write_text(REF_PORTABLE, encoding="utf-8")
    if ref_new:
        (directory / "ref_new.py").write_text(REF_PORTABLE, encoding="utf-8")
    (directory / "test_solution.py").write_text(TEST, encoding="utf-8")
    (directory / "wrong.py").write_text(WRONG, encoding="utf-8")
    (directory / "clues" / "new_code.txt").write_text(CODE_CLUE, encoding="utf-8")
    return directory


@pytest.fixture
def make_one_directional(tmp_path):
    def make(**kwargs):
        return write_concept(tmp_path, **kwargs)
    return make
