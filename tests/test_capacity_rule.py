from app.rules import has_available_seat


def test_seats_below_capacity():

    assert has_available_seat(29, 30) is True


def test_seats_equal():

    assert has_available_seat(30, 30) is False


def test_seats_above_capacity():

    assert has_available_seat(31, 30) is False
