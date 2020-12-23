from todayi.util.iter import is_iterable


def test_is_iterable_list():
    a = ["a", "b", "c"]
    assert is_iterable(a) is True


def test_is_iterable_str_not_allowed():
    a = "abcdefg"
    assert is_iterable(a) is False


def test_is_iterable_str():
    a = "abcdefg"
    assert is_iterable(a, allow_str=True) is True
