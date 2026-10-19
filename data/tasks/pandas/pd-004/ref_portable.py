import pandas as pd


def to_epoch_ns(values):
    series = pd.Series(pd.to_datetime(values))
    since_epoch = series - pd.Timestamp("1970-01-01")
    return [int(v) for v in since_epoch // pd.Timedelta(1, "ns")]
