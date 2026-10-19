import pandas as pd


def days_before(start, end):
    return pd.date_range(start, end, freq="D")
