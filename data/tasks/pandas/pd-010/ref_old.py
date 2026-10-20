import pandas as pd


def day_stamps_ns(start, n):
    return pd.date_range(start, periods=n, freq="D").astype("int64").tolist()
