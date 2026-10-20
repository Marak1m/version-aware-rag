import pandas as pd


def load_clean(path):
    return pd.read_csv(path, error_bad_lines=False)
