import math

import numpy as np
import pandas as pd

from solution import fill_forward


def test_forward_fill_leaves_leading_gaps():
    df = pd.DataFrame({"a": [np.nan, 1.0, np.nan, 3.0], "b": ["x", None, None, "y"]})
    out = fill_forward(df)
    a = out["a"].tolist()
    assert math.isnan(a[0]) and a[1:] == [1.0, 1.0, 3.0]
    assert out["b"].tolist() == ["x", "x", "x", "y"]
    assert df["a"].isna().tolist() == [True, False, True, False]        # the input is not modified
