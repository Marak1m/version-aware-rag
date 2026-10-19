import pandas as pd

from solution import load_orders

CSV = "order_id,ordered_at,qty\n1,05/01/2020,3\n2,31/12/2021,1\n"


def test_dates_are_parsed_day_first():
    with open("orders.csv", "w", encoding="utf-8") as fh:
        fh.write(CSV)
    df = load_orders("orders.csv")
    assert list(df.columns) == ["order_id", "ordered_at", "qty"]
    assert df["ordered_at"].tolist() == [pd.Timestamp(2020, 1, 5), pd.Timestamp(2021, 12, 31)]
    assert df["qty"].tolist() == [3, 1]
