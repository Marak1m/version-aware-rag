import pandas as pd


def fiscal_year_ends(start, n):
    return pd.date_range(start, periods=n, freq=pd.offsets.YearEnd())
