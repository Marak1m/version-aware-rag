import pandas as pd


def tally(s):
    return pd.DataFrame({"value": s.unique(), "n": s.value_counts().values})
