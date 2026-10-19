import pandas as pd


def load_orders(path):
    df = pd.read_csv(path)
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], format="%d/%m/%Y")
    return df
