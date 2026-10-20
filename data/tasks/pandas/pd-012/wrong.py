import pandas as pd


def long_form(df):
    return df.unstack()
