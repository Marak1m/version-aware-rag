import pandas as pd


def to_epoch_ns(values):
    return [int(ts.timestamp()) for ts in pd.to_datetime(values)]
