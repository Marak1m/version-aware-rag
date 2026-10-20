import pandas as pd


def load_table(path):
    return pd.read_csv(path, sep=r"\s+")
