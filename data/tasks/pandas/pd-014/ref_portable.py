import pandas as pd


def add_row(df, row):
    return pd.concat([df, pd.DataFrame([row])], ignore_index=True)
