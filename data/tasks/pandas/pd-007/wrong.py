import pandas as pd


def parse_stamps(values):
    return pd.to_datetime([pd.Timestamp(v) for v in values])
