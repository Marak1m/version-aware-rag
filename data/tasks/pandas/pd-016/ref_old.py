import pandas as pd


def flip(df):
    return df.swapaxes(0, 1)
