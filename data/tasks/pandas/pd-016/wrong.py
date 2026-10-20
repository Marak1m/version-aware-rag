import pandas as pd


def flip(df):
    return pd.DataFrame(df.values.T)
