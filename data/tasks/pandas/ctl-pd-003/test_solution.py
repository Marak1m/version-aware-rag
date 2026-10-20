from solution import age_bands


def test_upper_edge_is_inside_the_band():
    out = age_bands([5, 18, 19, 65, 70], [0, 18, 65, 120], ["child", "adult", "senior"])
    assert out == ["child", "child", "adult", "adult", "senior"]


def test_two_bands():
    assert age_bands([1, 2, 3], [0, 2, 4], ["low", "high"]) == ["low", "low", "high"]
