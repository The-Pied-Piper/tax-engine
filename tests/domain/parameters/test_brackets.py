"""Unit tests for BracketSchedule: the form's bracket columns over ascending thresholds.

Each bracket holds the threshold it starts `from` (`lower`) and its `rate`. The schedule computes
each bracket's `tax_at_start`, the tax at the bracket's start: the exact cumulative tax on the
brackets below, rounded with the schedule's `tax_at_start_rounding` rule (by default none, the
exact sum); the first bracket's is 0. The tax on an amount is the form's two lines for the bracket
the amount falls in: the rate on the excess over the bracket's lower, plus its tax at its start.
An amount at a threshold falls in the lower bracket ("more than ... but not more than ...").

Values are made up; real jurisdictions' brackets are tested with the pilot data.
"""

from __future__ import annotations

from dataclasses import fields
from decimal import Decimal

import pytest

from tax_calculator.domain.errors import DomainError, InvalidBracketScheduleError
from tax_calculator.domain.parameters.brackets import Bracket, BracketColumn, BracketSchedule
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)

D = Decimal

CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# 10% to 100, 20% from 100 to 300, 30% above 300; the tax at each start is exact: 10% of 100,
# plus 20% of 200.
SCHEDULE = BracketSchedule(
    (
        Bracket(D(0), D("0.10")),
        Bracket(D(100), D("0.20")),
        Bracket(D(300), D("0.30")),
    )
)

# Tax at a start with a half cent: 10.5% of 105 is 11.025; plus 20.5% of 105 (21.525) is 32.55
# exactly. Rounded half-up to the cent: 11.03 and 32.55; summing the rounded 11.03 would give 32.56.
HALF_CENT = (
    Bracket(D(0), D("0.105")),
    Bracket(D(105), D("0.205")),
    Bracket(D(210), D("0.30")),
)
EXACT = BracketSchedule(HALF_CENT)
ROUNDED = BracketSchedule(HALF_CENT, CENT)


def tax_at_starts(schedule: BracketSchedule) -> list[Decimal]:
    """Each bracket's tax at its start, read from the column of an amount just above its lower."""
    return [schedule.column_for(b.lower + D("0.01")).tax_at_start for b in schedule.brackets]


@pytest.mark.parametrize(
    ("amount", "tax"),
    [
        ("0", "0"),
        ("50", "5.0"),
        ("100", "10.0"),  # at the threshold: the lower bracket's column
        ("250", "40.0"),  # 20% of (250 - 100) + 10
        ("300", "50.0"),
        ("1000", "260.0"),  # 30% of (1000 - 300) + 50
        ("100.01", "10.002"),  # exact: no rounding of the excess times the rate
    ],
)
def test_tax_on_is_the_rate_on_the_excess_plus_the_brackets_tax_at_its_start(
    amount: str, tax: str
) -> None:
    assert SCHEDULE.tax_on(D(amount)) == D(tax)


@pytest.mark.parametrize(
    ("amount", "tax"),
    [
        ("150", "20.255"),  # 20.5% of 45 = 9.225, plus the rounded 11.03, not the exact 11.025
        ("210", "32.555"),  # at the threshold: 20.5% of 105 + 11.03, not the next column's 32.55
        ("310", "62.55"),  # 30% of 100 + 32.55
        ("105", "11.025"),  # at the first threshold: 10.5% of 105 + 0, not the rounded 11.03
    ],
)
def test_tax_on_uses_the_rounded_tax_at_the_start_not_the_exact_tax_below(
    amount: str, tax: str
) -> None:
    assert ROUNDED.tax_on(D(amount)) == D(tax)


def test_column_for_is_the_bracket_the_amount_falls_in() -> None:
    assert SCHEDULE.column_for(D(250)) == BracketColumn(
        lower=D(100), rate=D("0.20"), excess=D(150), tax_at_start=D("10.00"), tax=D("40.00")
    )


def test_column_for_an_amount_at_a_threshold_is_the_lower_brackets() -> None:
    assert SCHEDULE.column_for(D(300)) == BracketColumn(
        lower=D(100), rate=D("0.20"), excess=D(200), tax_at_start=D("10.00"), tax=D("50.00")
    )


def test_column_for_zero_is_the_first_brackets() -> None:
    assert SCHEDULE.column_for(D(0)) == BracketColumn(
        lower=D(0), rate=D("0.10"), excess=D(0), tax_at_start=D(0), tax=D(0)
    )


def test_top_bracket_is_open_ended() -> None:
    top = SCHEDULE.column_for(D(1000))

    assert (top.lower, top.excess, top.tax_at_start, top.tax) == (
        D(300),
        D(700),
        D("50.00"),
        D("260.00"),
    )


def test_tax_on_is_the_columns_tax() -> None:
    for amount in (D(0), D(50), D(250), D(1000)):
        assert SCHEDULE.tax_on(amount) == SCHEDULE.column_for(amount).tax


def test_a_column_holds_its_fields_in_order() -> None:
    assert [field.name for field in fields(BracketColumn)] == [
        "lower",
        "rate",
        "excess",
        "tax_at_start",
        "tax",
    ]


def test_a_column_holds_no_upper_bound() -> None:
    assert "upper" not in [field.name for field in fields(BracketColumn)]


def test_the_schedule_offers_one_column_per_amount_and_its_tax() -> None:
    data = {field.name for field in fields(BracketSchedule)}
    public = {name for name in vars(BracketSchedule) if not name.startswith("_")} - data

    assert public == {"column_for", "tax_on"}


def test_single_bracket_is_a_flat_rate() -> None:
    assert BracketSchedule((Bracket(D(0), D("0.25")),)).tax_on(D(80)) == D("20.00")


@pytest.mark.parametrize("amount", [D(-1), D("-0.01")])
def test_rejects_negative_amount(amount: Decimal) -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        SCHEDULE.tax_on(amount)
    with pytest.raises(ValueError, match="must not be negative"):
        SCHEDULE.column_for(amount)


def test_rejects_non_decimal_amount() -> None:
    with pytest.raises(TypeError, match="must be a Decimal"):
        SCHEDULE.tax_on(100)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="must be a Decimal"):
        SCHEDULE.column_for(100)  # type: ignore[arg-type]


# --- the tax at each bracket's start, computed by the schedule's rule ------------------


def test_a_schedule_holds_its_brackets_and_its_tax_at_start_rounding_in_order() -> None:
    assert [field.name for field in fields(BracketSchedule)] == [
        "brackets",
        "tax_at_start_rounding",
    ]


def test_a_schedule_is_built_positionally_in_field_order() -> None:
    assert BracketSchedule(HALF_CENT, CENT) == BracketSchedule(
        brackets=HALF_CENT, tax_at_start_rounding=CENT
    )


def test_by_default_a_schedule_does_not_round_the_tax_at_each_start() -> None:
    assert EXACT.tax_at_start_rounding == NO_ROUNDING
    assert EXACT == BracketSchedule(HALF_CENT, NO_ROUNDING)


def test_schedules_differing_only_in_their_rule_differ() -> None:
    assert EXACT != ROUNDED


def test_without_a_rule_each_tax_at_start_is_the_exact_tax_below() -> None:
    # 10.5% of 105 = 11.025; plus 20.5% of 105 = 32.55.
    assert tax_at_starts(EXACT) == [D(0), D("11.025"), D("32.55")]


def test_a_half_up_cent_rule_rounds_a_half_cent_up() -> None:
    assert ROUNDED.column_for(D(150)).tax_at_start == D("11.03")


def test_each_tax_at_start_rounds_the_exact_cumulative_tax_not_a_sum_of_rounded_figures() -> None:
    # 11.025 + 21.525 = 32.55 exactly; the rounded 11.03 + 21.525 would give 32.555 -> 32.56.
    assert tax_at_starts(ROUNDED) == [D(0), D("11.03"), D("32.55")]


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        pytest.param(RoundTo(D(1), RoundingMode.HALF_UP), ["0", "11", "33"], id="whole-half-up"),
        pytest.param(RoundTo(D(1), RoundingMode.DOWN), ["0", "11", "32"], id="whole-down"),
        pytest.param(RoundTo(D(1), RoundingMode.UP), ["0", "12", "33"], id="whole-up"),
        pytest.param(
            RoundTo(D("0.05"), RoundingMode.HALF_UP), ["0", "11.05", "32.55"], id="nickel"
        ),
        pytest.param(
            RoundTo(D("0.01"), RoundingMode.HALF_EVEN), ["0", "11.02", "32.55"], id="even"
        ),
    ],
)
def test_the_rule_may_be_any_increment_and_mode(rule: RoundTo, expected: list[str]) -> None:
    assert tax_at_starts(BracketSchedule(HALF_CENT, rule)) == [D(x) for x in expected]


def test_a_whole_unit_rule_gives_the_tax_on_an_amount_from_the_rounded_start() -> None:
    whole = BracketSchedule(HALF_CENT, RoundTo(D(1), RoundingMode.HALF_UP))

    # 20.5% of 45 = 9.225, plus 11 (11.025 rounded to the unit), with the product unrounded.
    assert whole.column_for(D(150)) == BracketColumn(
        lower=D(105), rate=D("0.205"), excess=D(45), tax_at_start=D(11), tax=D("20.225")
    )


def test_the_rule_rounds_only_the_tax_at_each_start_not_the_columns_tax() -> None:
    # 20.5% of 45.01 = 9.22705, plus 11.03: the column's tax keeps its fractions of a cent.
    assert ROUNDED.tax_on(D("150.01")) == D("20.25705")


def test_the_first_brackets_tax_at_start_is_zero_under_any_rule() -> None:
    up = BracketSchedule(HALF_CENT, RoundTo(D(1), RoundingMode.UP))

    assert up.column_for(D(50)).tax_at_start == 0
    assert up.tax_on(D(0)) == 0


@pytest.mark.parametrize(
    ("rule", "text"),
    [
        pytest.param(CENT, "0.00", id="cent"),
        pytest.param(RoundTo(D("0.05"), RoundingMode.HALF_UP), "0.00", id="nickel"),
        pytest.param(RoundTo(D(1), RoundingMode.HALF_UP), "0", id="whole"),
        pytest.param(NO_ROUNDING, "0", id="none"),
    ],
)
def test_the_first_brackets_tax_at_start_carries_the_rules_scale(
    rule: RoundingRule, text: str
) -> None:
    # The first start goes through the rule like the others: 0.00 under the cent, as 11.03 is.
    schedule = BracketSchedule(HALF_CENT, rule)

    assert str(schedule.column_for(D(50)).tax_at_start) == text
    assert str(schedule.column_for(D(0)).tax_at_start) == text


def test_a_rule_does_not_change_a_tax_at_start_already_on_its_increment() -> None:
    rounded = BracketSchedule(SCHEDULE.brackets, CENT)

    assert tax_at_starts(rounded) == [D(0), D("10.00"), D("50.00")]
    assert rounded.tax_on(D(250)) == SCHEDULE.tax_on(D(250))


def test_the_schedule_holds_no_rounding_rule_of_its_own() -> None:
    assert "_CONSTANT_ROUNDING" not in vars(BracketSchedule)


# --- the bracket -------------------------------------------------------------------------


def test_a_bracket_holds_its_fields_in_order() -> None:
    assert [field.name for field in fields(Bracket)] == ["lower", "rate"]


def test_a_bracket_is_built_positionally_in_field_order() -> None:
    assert Bracket(D(100), D("0.20")) == Bracket(lower=D(100), rate=D("0.20"))


def test_a_bracket_takes_no_tax_at_start() -> None:
    with pytest.raises(TypeError):
        Bracket(D(100), D("0.20"), D("10.00"))  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        Bracket(D(100), D("0.20"), tax_at_start=D("10.00"))  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("brackets", "message"),
    [
        ((), "at least one bracket"),
        ((Bracket(D(10), D("0.1")),), "first bracket must start at 0"),
        ((Bracket(D(0), D("0.1")), Bracket(D(0), D("0.2"))), "strictly ascending"),
        (
            (
                Bracket(D(0), D("0.1")),
                Bracket(D(200), D("0.2")),
                Bracket(D(100), D("0.3")),
            ),
            "strictly ascending",
        ),
    ],
)
def test_rejects_invalid_schedules(brackets: tuple[Bracket, ...], message: str) -> None:
    with pytest.raises(InvalidBracketScheduleError, match=message):
        BracketSchedule(brackets)


@pytest.mark.parametrize(
    ("lower", "rate", "message"),
    [
        (D(-1), D("0.1"), "lower must not be negative"),
        (D(0), D("-0.1"), "rate must be between 0 and 1"),
        (D(0), D("1.01"), "rate must be between 0 and 1"),
        (D("NaN"), D("0.1"), "lower must be finite"),
        (D(0), D("Infinity"), "rate must be finite"),
    ],
)
def test_rejects_invalid_brackets(lower: Decimal, rate: Decimal, message: str) -> None:
    with pytest.raises(InvalidBracketScheduleError, match=message):
        Bracket(lower, rate)


@pytest.mark.parametrize(
    ("lower", "rate", "name"),
    [
        (0, D("0.1"), "lower"),
        (D(0), 0.1, "rate"),
        (D(0), "0.1", "rate"),
    ],
)
def test_rejects_non_decimal_bracket_values(lower: object, rate: object, name: str) -> None:
    with pytest.raises(TypeError, match=f"bracket {name} must be a Decimal"):
        Bracket(lower, rate)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("rule", "got"),
    [
        ("x", "str"),
        ("none", "str"),
        (None, "NoneType"),
        (D("0.01"), "Decimal"),
        (RoundingMode.HALF_UP, "RoundingMode"),
    ],
)
def test_rejects_a_tax_at_start_rounding_that_is_not_a_rounding_rule(
    rule: object, got: str
) -> None:
    with pytest.raises(
        TypeError, match=f"^schedule tax_at_start_rounding must be a RoundingRule, got {got}$"
    ):
        BracketSchedule(HALF_CENT, rule)  # type: ignore[arg-type]


def test_invalid_schedule_is_a_domain_error() -> None:
    assert issubclass(InvalidBracketScheduleError, DomainError)
