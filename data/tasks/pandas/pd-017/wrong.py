import pandas as pd


def load_clean(path):
    return pd.read_csv(path, skip_blank_lines=True)
