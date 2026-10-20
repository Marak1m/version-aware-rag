from solution import load_table

TEXT = "station  temp\twind\nA1       12.5\t3\nB22  -1.0     14\n"


def test_columns_split_on_runs_of_blanks():
    with open("readings.txt", "w", encoding="utf-8") as fh:
        fh.write(TEXT)
    df = load_table("readings.txt")
    assert list(df.columns) == ["station", "temp", "wind"]
    assert df["station"].tolist() == ["A1", "B22"]
    assert df["temp"].tolist() == [12.5, -1.0]
    assert df["wind"].tolist() == [3, 14]
