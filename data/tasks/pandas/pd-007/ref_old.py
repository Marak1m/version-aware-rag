import pandas as pd


def parse_stamps(values):
    return pd.Series(pd.to_datetime(values, infer_datetime_format=True))
