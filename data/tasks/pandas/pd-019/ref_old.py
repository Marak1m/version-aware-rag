import pandas as pd


def load_table(path):
    return pd.read_csv(path, delim_whitespace=True)
