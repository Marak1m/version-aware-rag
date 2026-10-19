import pandas as pd


def day_stamps_ns(start, n):
    return [int(ts.timestamp() * 1000) for ts in pd.date_range(start, periods=n, freq="D")]
