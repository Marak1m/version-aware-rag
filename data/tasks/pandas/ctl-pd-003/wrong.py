import pandas as pd


def age_bands(ages, edges, labels):
    return list(pd.cut(ages, bins=edges, labels=labels, right=False))
