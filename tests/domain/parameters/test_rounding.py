"""Unit tests for rounding rules (design.md §3, Rounding).

Rounding is a parameter: a capability decides *where* it rounds and the rule
decides *how*. The default is no rounding, and only exact amounts are accepted: a `Decimal` or an
exact `fractions.Fraction` (a quotient a capability has not yet turned into a `Decimal`).
`RoundingRule.apply` is also the one place allowed to be inexact under the engine's trapped
`decimal` context: it rounds without raising `decimal.Inexact`, and leaves the caller's
context as it found it.
"""

from __future__ import annotations

import copy
import decimal
from dataclasses import FrozenInstanceError
from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest

from tax_engine.domain.errors import DomainError, InvalidRoundingRuleError
from tax_engine.domain.parameters import rounding as rounding_module
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)

D = Decimal
CENT = D("0.01")


def rule(mode: RoundingMode, increment: str = "0.01") -> RoundTo:
    return RoundTo(increment=D(increment), mode=mode)


# --- no rounding ---------------------------------------------------------------


@pytest.mark.parametrize("amount", ["0", "1.005", "-1.005", "123456.789012345", "-0.0000001"])
def test_no_rounding_returns_amount_unchanged(amount: str) -> None:
    result = NO_ROUNDING.apply(D(amount))

    assert result == D(amount)
    assert result.as_tuple() == D(amount).as_tuple()  # same digits and scale


def test_both_rule_kinds_are_rounding_rules() -> None:
    assert isinstance(NO_ROUNDING, RoundingRule)
    assert isinstance(rule(RoundingMode.HALF_UP), RoundingRule)


def test_no_rounding_is_only_exposed_as_the_constant() -> None:
    assert not hasattr(rounding_module, "NoRounding")


@pytest.mark.parametrize("copier", [copy.copy, copy.deepcopy])
def test_copies_of_no_rounding_still_equal_the_constant(copier: object) -> None:
    # Copying or serialising creates a new instance; value equality keeps it the same rule.
    duplicate = copier(NO_ROUNDING)  # type: ignore[operator]

    assert duplicate == NO_ROUNDING
    assert hash(duplicate) == hash(NO_ROUNDING)


@pytest.mark.parametrize("rounding", [NO_ROUNDING, RoundTo(CENT, RoundingMode.HALF_UP)])
@pytest.mark.parametrize("attribute", ["increment", "extra"])
def test_rules_are_immutable(rounding: RoundingRule, attribute: str) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(rounding, attribute, 1)


# --- modes ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mode", "amount", "expected"),
    [
        # half-up: ties away from zero
        (RoundingMode.HALF_UP, "1.005", "1.01"),
        (RoundingMode.HALF_UP, "1.004", "1.00"),
        (RoundingMode.HALF_UP, "-1.005", "-1.01"),
        (RoundingMode.HALF_UP, "2.675", "2.68"),  # 2.67 with binary floats
        # half-even: ties to the even neighbour
        (RoundingMode.HALF_EVEN, "1.005", "1.00"),
        (RoundingMode.HALF_EVEN, "1.015", "1.02"),
        (RoundingMode.HALF_EVEN, "1.0151", "1.02"),
        (RoundingMode.HALF_EVEN, "-1.005", "-1.00"),
        # down: toward zero (drops the remainder)
        (RoundingMode.DOWN, "1.019", "1.01"),
        (RoundingMode.DOWN, "-1.019", "-1.01"),
        # up: away from zero
        (RoundingMode.UP, "1.001", "1.01"),
        (RoundingMode.UP, "-1.001", "-1.01"),
        # floor: toward negative infinity
        (RoundingMode.FLOOR, "1.019", "1.01"),
        (RoundingMode.FLOOR, "-1.011", "-1.02"),
        # ceiling: toward positive infinity
        (RoundingMode.CEILING, "1.001", "1.01"),
        (RoundingMode.CEILING, "-1.019", "-1.01"),
    ],
)
def test_rounds_to_a_cent_by_mode(mode: RoundingMode, amount: str, expected: str) -> None:
    assert rule(mode).apply(D(amount)) == D(expected)


@pytest.mark.parametrize("mode", list(RoundingMode))
def test_amount_already_on_the_increment_is_unchanged(mode: RoundingMode) -> None:
    assert rule(mode).apply(D("-42.17")) == D("-42.17")


# --- mode resolution ------------------------------------------------------------

F = Fraction


@pytest.mark.parametrize(
    ("mode", "value", "expected"),
    [
        (RoundingMode.HALF_UP, F(5, 2), 3),
        (RoundingMode.HALF_UP, F(-5, 2), -3),
        (RoundingMode.HALF_UP, F(12, 5), 2),
        (RoundingMode.HALF_UP, F(13, 5), 3),
        (RoundingMode.HALF_EVEN, F(5, 2), 2),
        (RoundingMode.HALF_EVEN, F(7, 2), 4),
        (RoundingMode.HALF_EVEN, F(-5, 2), -2),
        (RoundingMode.HALF_EVEN, F(-7, 2), -4),
        (RoundingMode.HALF_EVEN, F(13, 5), 3),
        (RoundingMode.DOWN, F(29, 10), 2),
        (RoundingMode.DOWN, F(-29, 10), -2),
        (RoundingMode.UP, F(21, 10), 3),
        (RoundingMode.UP, F(-21, 10), -3),
        (RoundingMode.FLOOR, F(29, 10), 2),
        (RoundingMode.FLOOR, F(-21, 10), -3),
        (RoundingMode.CEILING, F(21, 10), 3),
        (RoundingMode.CEILING, F(-29, 10), -2),
    ],
)
def test_mode_resolves_a_fraction_to_an_integer(
    mode: RoundingMode, value: Fraction, expected: int
) -> None:
    assert mode.to_integer(value) == expected


@pytest.mark.parametrize("mode", list(RoundingMode))
@pytest.mark.parametrize("value", [F(0), F(4), F(-4)])
def test_mode_leaves_integers_unchanged(mode: RoundingMode, value: Fraction) -> None:
    assert mode.to_integer(value) == value


# --- increments ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("increment", "mode", "amount", "expected"),
    [
        ("1", RoundingMode.HALF_UP, "2.5", "3"),
        ("1", RoundingMode.HALF_UP, "2.49", "2"),
        ("1", RoundingMode.DOWN, "2.99", "2"),
        ("0.05", RoundingMode.HALF_UP, "1.024", "1.00"),
        ("0.05", RoundingMode.HALF_UP, "1.025", "1.05"),
        ("0.05", RoundingMode.HALF_UP, "1.074", "1.05"),
        ("0.05", RoundingMode.HALF_UP, "1.075", "1.10"),
        # A non-decimal ratio: 0.045 / 0.03 is exactly 1.5, a tie.
        ("0.03", RoundingMode.HALF_UP, "0.045", "0.06"),
        ("0.03", RoundingMode.HALF_EVEN, "0.045", "0.06"),
        ("0.03", RoundingMode.DOWN, "0.045", "0.03"),
    ],
)
def test_rounds_to_any_positive_increment(
    increment: str, mode: RoundingMode, amount: str, expected: str
) -> None:
    assert rule(mode, increment).apply(D(amount)) == D(expected)


def test_result_carries_the_increments_scale() -> None:
    result = rule(RoundingMode.HALF_UP).apply(D("7"))

    assert str(result) == "7.00"


# --- rejected inputs -----------------------------------------------------------


@pytest.mark.parametrize("increment", ["0", "-0.01", "NaN", "Infinity"])
def test_rejects_non_positive_or_non_finite_increment(increment: str) -> None:
    with pytest.raises(InvalidRoundingRuleError, match="increment"):
        RoundTo(increment=D(increment), mode=RoundingMode.HALF_UP)


def test_invalid_rule_is_a_domain_error() -> None:
    assert issubclass(InvalidRoundingRuleError, DomainError)


@pytest.mark.parametrize("increment", [0.01, 1, "0.01"])
def test_rejects_increment_that_is_not_a_decimal(increment: object) -> None:
    with pytest.raises(TypeError, match="increment must be a Decimal"):
        RoundTo(increment=increment, mode=RoundingMode.HALF_UP)  # type: ignore[arg-type]


def test_rejects_mode_that_is_not_a_rounding_mode() -> None:
    with pytest.raises(TypeError, match="mode must be a RoundingMode"):
        RoundTo(increment=CENT, mode="half_up")  # type: ignore[arg-type]


@pytest.mark.parametrize("rounding", [NO_ROUNDING, RoundTo(CENT, RoundingMode.HALF_UP)])
@pytest.mark.parametrize("amount", [1.005, 1, "1.005"])
def test_rejects_amount_that_is_not_a_decimal(rounding: RoundingRule, amount: object) -> None:
    with pytest.raises(TypeError, match="amount must be a Decimal"):
        rounding.apply(amount)  # type: ignore[arg-type]


@pytest.mark.parametrize("rounding", [NO_ROUNDING, RoundTo(CENT, RoundingMode.HALF_UP)])
@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-Infinity"])
def test_rejects_non_finite_amount(rounding: RoundingRule, amount: str) -> None:
    with pytest.raises(ValueError, match="amount must be finite"):
        rounding.apply(D(amount))


# --- value semantics and description --------------------------------------------


def test_rules_are_equal_by_value_and_hashable() -> None:
    assert rule(RoundingMode.HALF_UP) == rule(RoundingMode.HALF_UP)
    assert rule(RoundingMode.HALF_UP) != rule(RoundingMode.HALF_EVEN)
    assert len({rule(RoundingMode.HALF_UP), rule(RoundingMode.HALF_UP), NO_ROUNDING}) == 2


@pytest.mark.parametrize(
    ("rounding", "text"),
    [
        (NO_ROUNDING, "no rounding"),
        (RoundTo(CENT, RoundingMode.HALF_UP), "half-up to 0.01"),
        (RoundTo(D("1"), RoundingMode.FLOOR), "floor to 1"),
        (RoundTo(D("0.05"), RoundingMode.HALF_EVEN), "half-even to 0.05"),
    ],
)
def test_str_is_a_readable_repr(rounding: RoundingRule, text: str) -> None:
    assert str(rounding) == text


def test_mode_values_are_stable_identifiers() -> None:
    assert [m.value for m in RoundingMode] == [
        "half_up",
        "half_even",
        "down",
        "up",
        "floor",
        "ceiling",
    ]


# --- exact fractions -------------------------------------------------------------
#
# A capability that divides hands the rule the exact quotient as a `fractions.Fraction`, so the
# rule rounds once and nothing before it is inexact. `NO_ROUNDING` can only return a quotient that
# has a finite decimal expansion; any other raises `decimal.Inexact`, never a rounded Decimal.


@pytest.mark.parametrize(
    ("amount", "text"),
    [
        (Fraction(1, 4), "0.25"),
        (Fraction(40000), "40000"),
        (Fraction(0), "0"),
        (Fraction(-3, 8), "-0.375"),
        (Fraction(20001, 30), "666.7"),
        (Fraction(7, 2), "3.5"),
    ],
)
def test_no_rounding_returns_a_terminating_fraction_as_the_decimal_with_fewest_digits(
    amount: Fraction, text: str
) -> None:
    result = NO_ROUNDING.apply(amount)

    assert type(result) is Decimal
    assert result == D(text)
    assert str(result) == text


def test_no_rounding_keeps_every_digit_of_a_terminating_fraction_beyond_the_context() -> None:
    # 1 / 2**100 = 5**100 / 10**100 has 70 significant digits, far past the 28 of the context.
    result = NO_ROUNDING.apply(Fraction(1, 2**100))

    # Built from its digits, so the expected value is not itself rounded by the context.
    assert result == D((0, tuple(int(digit) for digit in str(5**100)), -100))


@pytest.mark.parametrize(
    "amount", [Fraction(2, 3), Fraction(1, 7), Fraction(-1, 3), Fraction(100000, 3)]
)
def test_no_rounding_raises_inexact_for_a_fraction_with_no_finite_expansion(
    amount: Fraction,
) -> None:
    with pytest.raises(decimal.Inexact):
        NO_ROUNDING.apply(amount)


def test_no_rounding_does_not_round_a_non_terminating_fraction_to_the_contexts_precision() -> None:
    # What the engine did before: 50000 × 2 / 3 silently became 33333.33333333333333333333333.
    with pytest.raises(decimal.Inexact):
        NO_ROUNDING.apply(Fraction(100000, 3))


@pytest.mark.parametrize(
    ("mode", "amount", "expected"),
    [
        (RoundingMode.HALF_UP, Fraction(100000, 3), "33333.33"),
        (RoundingMode.HALF_UP, Fraction(5, 7), "0.71"),
        (RoundingMode.HALF_UP, Fraction(1005, 1000), "1.01"),  # an exact tie goes away from zero
        (RoundingMode.HALF_EVEN, Fraction(1005, 1000), "1.00"),  # an exact tie goes to even
        (RoundingMode.HALF_UP, Fraction(-1005, 1000), "-1.01"),
        (RoundingMode.DOWN, Fraction(2, 3), "0.66"),
        (RoundingMode.UP, Fraction(1, 3), "0.34"),
        (RoundingMode.FLOOR, Fraction(-1, 3), "-0.34"),
        (RoundingMode.CEILING, Fraction(1, 3), "0.34"),
        (RoundingMode.HALF_UP, Fraction(7), "7.00"),
    ],
)
def test_round_to_rounds_an_exact_fraction_once(
    mode: RoundingMode, amount: Fraction, expected: str
) -> None:
    result = rule(mode).apply(amount)

    assert type(result) is Decimal
    assert result == D(expected)
    assert str(result) == expected


def test_round_to_a_fraction_gives_the_same_as_the_decimal_it_equals() -> None:
    for text in ("1.005", "1.015", "1.025", "-2.675", "0.004", "123456.785"):
        assert rule(RoundingMode.HALF_UP).apply(Fraction(D(text))) == rule(
            RoundingMode.HALF_UP
        ).apply(D(text))


def test_round_to_sees_the_exact_value_of_a_fraction_not_a_digit_limited_one() -> None:
    # A hair above and a hair below the half-cent tie, far past 28 digits: only the exact
    # fraction tells them apart.
    tie = Fraction(5, 1000)

    assert rule(RoundingMode.HALF_UP).apply(tie + Fraction(1, 10**40)) == D("0.01")
    assert rule(RoundingMode.HALF_UP).apply(tie - Fraction(1, 10**40)) == D("0.00")


@pytest.mark.parametrize("rounding", [NO_ROUNDING, RoundTo(CENT, RoundingMode.HALF_UP)])
@pytest.mark.parametrize("amount", [1.005, 1, "1.005", None])
def test_still_rejects_amounts_that_are_neither_a_decimal_nor_a_fraction(
    rounding: RoundingRule, amount: Any
) -> None:
    with pytest.raises(TypeError, match="amount must be a Decimal"):
        rounding.apply(amount)


# --- under the trapped context ---------------------------------------------------
#
# The engine runs capabilities under a context that traps `decimal.Inexact`. Rounding is the one
# place allowed to be inexact, so it must round there, and must leave the context as it found it.


def trapped() -> decimal.Context:
    context = decimal.Context()
    context.traps[decimal.Inexact] = True
    return context


@pytest.mark.parametrize(
    ("mode", "amount", "expected"),
    [
        (RoundingMode.HALF_UP, "1.005", "1.01"),
        (RoundingMode.HALF_UP, "2.675", "2.68"),
        (RoundingMode.HALF_EVEN, "2.675", "2.68"),
        (RoundingMode.HALF_UP, "0.1234567890123456789012345678901234", "0.12"),
        (RoundingMode.DOWN, "99.999", "99.99"),
        (RoundingMode.UP, "0.0000000000000000000000000000001", "0.01"),
    ],
)
def test_round_to_rounds_a_decimal_under_a_context_that_traps_inexact(
    mode: RoundingMode, amount: str, expected: str
) -> None:
    with decimal.localcontext(trapped()):
        result = rule(mode).apply(D(amount))

    assert result == D(expected)
    assert str(result) == expected


def test_round_to_rounds_a_fraction_under_a_context_that_traps_inexact() -> None:
    with decimal.localcontext(trapped()):
        result = rule(RoundingMode.HALF_UP).apply(Fraction(100000, 3))

    assert result == D("33333.33")


def test_round_to_keeps_every_digit_of_a_result_longer_than_the_context() -> None:
    # 32 integer digits rounded to a whole number: the 28-digit context must not round them again.
    amount = D("12345678901234567890123456789012.4")

    with decimal.localcontext(trapped()):
        result = RoundTo(D("1"), RoundingMode.HALF_UP).apply(amount)

    assert result == D("12345678901234567890123456789012")


def test_round_to_keeps_every_digit_of_a_cent_result_longer_than_the_context() -> None:
    amount = D("1234567890123456789012345678.904")

    with decimal.localcontext(trapped()):
        result = rule(RoundingMode.HALF_UP).apply(amount)

    assert result == D("1234567890123456789012345678.90")
    assert str(result) == "1234567890123456789012345678.90"


@pytest.mark.parametrize("amount", ["0.1234567890123456789012345678901234", "1234.5"])
def test_no_rounding_returns_a_decimal_as_is_under_a_context_that_traps_inexact(
    amount: str,
) -> None:
    with decimal.localcontext(trapped()):
        result = NO_ROUNDING.apply(D(amount))

    assert result == D(amount)
    assert str(result) == amount


@pytest.mark.parametrize("amount", [D("1.005"), Fraction(100000, 3)])
def test_round_to_leaves_the_callers_inexact_trap_on(amount: Decimal | Fraction) -> None:
    with decimal.localcontext(trapped()) as context:
        rule(RoundingMode.HALF_UP).apply(amount)

        assert context.traps[decimal.Inexact]
        assert decimal.getcontext().traps[decimal.Inexact]
        with pytest.raises(decimal.Inexact):
            D(1) / D(3)  # the caller's context still traps what rounding was allowed to do


@pytest.mark.parametrize("amount", [D("1.005"), Fraction(100000, 3)])
def test_round_to_leaves_the_callers_precision_and_flags_alone(amount: Decimal | Fraction) -> None:
    with decimal.localcontext(trapped()) as context:
        context.prec = 40
        rule(RoundingMode.HALF_UP).apply(amount)

        assert context.prec == 40
        assert not context.flags[decimal.Inexact]
        assert not context.flags[decimal.Rounded]


def test_round_to_leaves_the_default_context_untrapped() -> None:
    rule(RoundingMode.HALF_UP).apply(D("1.005"))

    assert not decimal.getcontext().traps[decimal.Inexact]
