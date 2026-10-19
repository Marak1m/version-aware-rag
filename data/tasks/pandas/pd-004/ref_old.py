import pandas as pd


def to_epoch_ns(values):
    series = pd.Series(pd.to_datetime(values))
    return [int(v) for v in series.astype("int64")]
