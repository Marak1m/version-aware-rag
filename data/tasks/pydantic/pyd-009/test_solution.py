from solution import make_contact


def test_email_is_lowered_by_the_model():
    assert make_contact("Ada.Lovelace@Example.COM").email == "ada.lovelace@example.com"
    assert make_contact("bob@example.com").email == "bob@example.com"
