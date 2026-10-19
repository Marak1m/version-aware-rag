import pandas as pd


def load_orders(path):
    return pd.read_csv(path, parse_dates=["ordered_at"])
