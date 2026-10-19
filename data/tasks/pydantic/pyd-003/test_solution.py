from solution import make_tag


def test_whitespace_is_stripped_by_the_model():
    assert make_tag("  urgent ").label == "urgent"
    assert make_tag("plain").label == "plain"
