import pandas as pd


def fill_forward(df):
    return df.fillna(method="ffill")
