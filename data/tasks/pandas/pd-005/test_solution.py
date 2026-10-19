import numpy as np
import pandas as pd

from solution import fill_forward


def test_forward_fill_leaves_leading_gaps():
    df = pd.DataFrame({"a": [np.nan, 1.0, np.nan, 3.0], "b": ["x", None, None, "y"]})
    out = fill_forward(df)
    assert out["a"].tolist()[1:] == [1.0, 1.0, 3.0] and np.isnan(out["a"].tolist()[0])
    assert out["b"].tolist() == ["x", "x", "x", "y"]
    assert df["a"].isna().sum() == 2        # the input is not modified
