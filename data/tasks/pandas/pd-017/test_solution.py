from solution import load_clean

CSV = "sku,qty\nA1,3\nB2,4,extra\nC3,5\n"


def test_malformed_lines_are_dropped():
    with open("stock.csv", "w", encoding="utf-8") as fh:
        fh.write(CSV)
    df = load_clean("stock.csv")
    assert list(df.columns) == ["sku", "qty"]
    assert df["sku"].tolist() == ["A1", "C3"]
    assert df["qty"].tolist() == [3, 5]
