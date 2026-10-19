import pandas as pd


def hour_marks(start, n):
    end = pd.Timestamp(start) + pd.Timedelta(hours=n)
    return pd.date_range(start, end, freq="h")
