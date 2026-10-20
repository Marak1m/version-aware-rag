import pandas as pd


def load_clean(path):
    return pd.read_csv(path, on_bad_lines="skip")
