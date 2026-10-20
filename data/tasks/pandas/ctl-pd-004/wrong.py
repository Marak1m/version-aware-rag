import pandas as pd


def one_tag_per_row(tags):
    return pd.Series([tag for row in tags for tag in row])
