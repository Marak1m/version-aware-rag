from solution import make_ticker


def test_symbol_is_uppercased_by_the_model():
    assert make_ticker("aapl").symbol == "AAPL"
    assert make_ticker("Brk.b").symbol == "BRK.B"
    assert make_ticker("MSFT").symbol == "MSFT"
