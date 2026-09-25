import pytest
from parrot_utils import (
    check_parrot_trouble_early_morning,
    check_parrot_trouble_late_night,
    check_parrot_safe_midday,
    check_parrot_quiet_early_morning,
    check_parrot_trouble_boundary_start,
    check_parrot_trouble_boundary_end,
)


def test_parrot_is_talking_and_hour_is_6_returns_true():
    """AC-1: Given the parrot is talking and the hour is 6, When the trouble check is evaluated, Then it returns true"""
    result = check_parrot_trouble_early_morning(is_talking=True, hour=6)
    assert result is True


def test_parrot_is_talking_and_hour_is_21_returns_true():
    """AC-2: Given the parrot is talking and the hour is 21, When the trouble check is evaluated, Then it returns true"""
    result = check_parrot_trouble_late_night(is_talking=True, hour=21)
    assert result is True


def test_parrot_is_talking_and_hour_is_12_returns_false():
    """AC-3: Given the parrot is talking and the hour is 12, When the trouble check is evaluated, Then it returns false"""
    result = check_parrot_safe_midday(is_talking=True, hour=12)
    assert result is False


def test_parrot_is_not_talking_and_hour_is_5_returns_false():
    """AC-4: Given the parrot is not talking and the hour is 5, When the trouble check is evaluated, Then it returns false"""
    result = check_parrot_quiet_early_morning(is_talking=False, hour=5)
    assert result is False


def test_parrot_is_talking_and_hour_is_exactly_7_returns_false():
    """AC-5: Given the parrot is talking and the hour is exactly 7, When the trouble check is evaluated, Then it returns false"""
    result = check_parrot_trouble_boundary_start(is_talking=True, hour=7)
    assert result is False


def test_parrot_is_talking_and_hour_is_exactly_20_returns_false():
    """AC-6: Given the parrot is talking and the hour is exactly 20, When the trouble check is evaluated, Then it returns false"""
    result = check_parrot_trouble_boundary_end(is_talking=True, hour=20)
    assert result is False