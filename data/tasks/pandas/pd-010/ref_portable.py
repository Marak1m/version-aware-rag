import pandas as pd


def day_stamps_ns(start, n):
    days = pd.date_range(start, periods=n, freq="D")
    return ((days - pd.Timestamp(0)) // pd.Timedelta(1, "ns")).tolist()
