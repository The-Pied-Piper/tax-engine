"""Unit tests for AmountByBand: a printed chart of bands by income, the `amount_by_band` values.

A band (`AmountBand`) is one row of the chart: `over`, the lower bound the row starts above, and
either a flat `amount` (the row prints one figure) or a sloped figure, `(income minus minus) x
rate plus plus`. A row is a flat row (`amount` alone) or a sloped row (`minus`, `rate` and `plus`
all set, `amount` None); any other mix is an `InvalidAmountByBandError`. Every figure is finite
and not negative; a zero figure is kept as a plain zero, its scale kept.

A chart (`AmountByBand`) holds at least one band, the first from 0, each `over` strictly above the
one before. `band_for(income)` is the band whose lower bound is the highest `over` strictly below
the income, so an income at a boundary falls in the lower band, as in `BracketSchedule.column_for`.
A negative income is a ValueError and a non-Decimal one a TypeError. Figures are made up.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_engine.domain.errors import DomainError, InvalidAmountByBandError
from tax_engine.domain.parameters.amount_by_band import (
    AMOUNT_BY_BAND,
    AmountBand,
    AmountByBand,
)
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate

D = Decimal

TEN_PERCENT = Rate(D("0.10"))
QUARTER = Rate(D("0.25"))

# Made up: a flat zero to 100; 10% of the income over 100 to 200; a flat 12 to 300; then 15 plus
# 25% of the income over 300.
FLAT_ZERO = AmountBand(D(0), amount=D(0))
SLOPED_100 = AmountBand(D(100), minus=D(100), rate=TEN_PERCENT, plus=D(0))
FLAT_12 = AmountBand(D(200), amount=D(12))
SLOPED_300 = AmountBand(D(300), minus=D(300), rate=QUARTER, plus=D(15))
BANDS = (FLAT_ZERO, SLOPED_100, FLAT_12, SLOPED_300)


def chart(*bands: AmountBand) -> AmountByBand:
    """By default the made-up four bands above."""
    return AmountByBand(bands or BANDS)


# --- one band ---------------------------------------------------------------------------------


def test_a_flat_band_holds_its_over_and_amount() -> None:
    band = AmountBand(D("20000"), amount=D("300"))

    assert band.over == D("20000")
    assert band.amount == D("300")
    assert (band.minus, band.rate, band.plus) == (None, None, None)


def test_a_sloped_band_holds_its_over_minus_rate_and_plus() -> None:
    band = AmountBand(D("20000"), minus=D("20000"), rate=TEN_PERCENT, plus=D("300"))

    assert (band.over, band.minus, band.rate, band.plus) == (
        D("20000"),
        D("20000"),
        TEN_PERCENT,
        D("300"),
    )
    assert band.amount is None


def test_a_band_holds_its_fields_in_that_order() -> None:
    assert [field.name for field in fields(AmountBand)] == [
        "over",
        "amount",
        "minus",
        "rate",
        "plus",
    ]


def test_a_flat_band_gives_its_amount_whatever_the_income() -> None:
    assert AmountBand(D(0), amount=D("300")).amount_at(D("99999")) == D("300")
    assert AmountBand(D(0), amount=D("300")).amount_at(D("1")) == D("300")


def test_a_sloped_band_gives_the_rate_on_the_income_over_minus_plus_plus() -> None:
    band = AmountBand(D("20000"), minus=D("20000"), rate=TEN_PERCENT, plus=D("300"))

    # (22000 - 20000) x 10% + 300 = 500.
    assert band.amount_at(D("22000")) == D("500")


def test_a_sloped_band_is_not_rounded() -> None:
    band = AmountBand(D(100), minus=D(100), rate=TEN_PERCENT, plus=D(0))

    # (100.05 - 100) x 10% = 0.005, exact: no rounding to the cent.
    assert band.amount_at(D("100.05")) == D("0.005")


def test_a_sloped_band_gives_its_plus_at_its_minus() -> None:
    band = AmountBand(D(100), minus=D(100), rate=TEN_PERCENT, plus=D("7.50"))

    assert band.amount_at(D(100)) == D("7.50")


def test_a_band_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, FLAT_12).amount = D("1")


def test_equal_bands_are_equal_and_hash_alike() -> None:
    assert AmountBand(D(0), amount=D(0)) == AmountBand(D("0.00"), amount=D("0"))
    assert hash(AmountBand(D(0), amount=D(0))) == hash(AmountBand(D("0.00"), amount=D("0")))
    assert AmountBand(D(0), amount=D(0)) != AmountBand(D(0), amount=D(1))
    assert SLOPED_100 != AmountBand(D(100), minus=D(100), rate=QUARTER, plus=D(0))


@pytest.mark.parametrize(
    "band",
    [
        pytest.param(AmountBand(D(0), amount=D(0)), id="flat-zero"),
        pytest.param(AmountBand(D("20000"), amount=D("300")), id="flat"),
        pytest.param(AmountBand(D(0), minus=D(0), rate=TEN_PERCENT, plus=D(0)), id="sloped-at-0"),
        pytest.param(AmountBand(D(1), minus=D(0), rate=Rate(D(0)), plus=D(0)), id="zero-rate"),
    ],
)
def test_accepts_a_flat_row_or_a_sloped_row(band: AmountBand) -> None:
    assert band.over >= 0


@pytest.mark.parametrize(
    "make",
    [
        pytest.param(lambda: AmountBand(D(0)), id="neither-shape"),
        pytest.param(lambda: AmountBand(D(0), amount=D(1), minus=D(1)), id="amount-and-minus"),
        pytest.param(lambda: AmountBand(D(0), amount=D(1), rate=TEN_PERCENT), id="amount-and-rate"),
        pytest.param(lambda: AmountBand(D(0), amount=D(1), plus=D(1)), id="amount-and-plus"),
        pytest.param(
            lambda: AmountBand(D(0), amount=D(1), minus=D(0), rate=TEN_PERCENT, plus=D(0)),
            id="amount-with-all-three",
        ),
        pytest.param(
            lambda: AmountBand(D(0), minus=D(0), rate=TEN_PERCENT), id="sloped-without-plus"
        ),
        pytest.param(lambda: AmountBand(D(0), minus=D(0), plus=D(0)), id="sloped-without-rate"),
        pytest.param(
            lambda: AmountBand(D(0), rate=TEN_PERCENT, plus=D(0)), id="sloped-without-minus"
        ),
        pytest.param(lambda: AmountBand(D(0), rate=TEN_PERCENT), id="rate-alone"),
    ],
)
def test_rejects_a_row_that_is_neither_flat_nor_sloped(make: Any) -> None:
    with pytest.raises(InvalidAmountByBandError):
        make()


@pytest.mark.parametrize(
    ("make", "message"),
    [
        pytest.param(lambda: AmountBand(D("-1"), amount=D(0)), "must not be negative", id="over"),
        pytest.param(lambda: AmountBand(D(0), amount=D("-1")), "must not be negative", id="amount"),
        pytest.param(
            lambda: AmountBand(D("-0.01"), minus=D(0), rate=TEN_PERCENT, plus=D(0)),
            "must not be negative",
            id="over-slightly",
        ),
        pytest.param(
            lambda: AmountBand(D(0), minus=D("-1"), rate=TEN_PERCENT, plus=D(0)),
            "must not be negative",
            id="minus",
        ),
        pytest.param(
            lambda: AmountBand(D(0), minus=D(0), rate=TEN_PERCENT, plus=D("-1")),
            "must not be negative",
            id="plus",
        ),
        pytest.param(lambda: AmountBand(D("Infinity"), amount=D(0)), "must be finite", id="inf"),
        pytest.param(lambda: AmountBand(D(0), amount=D("NaN")), "must be finite", id="amount-nan"),
        pytest.param(
            lambda: AmountBand(D(0), minus=D("-Infinity"), rate=TEN_PERCENT, plus=D(0)),
            "must be finite",
            id="minus-neg-inf",
        ),
        pytest.param(
            lambda: AmountBand(D(0), minus=D(0), rate=TEN_PERCENT, plus=D("NaN")),
            "must be finite",
            id="plus-nan",
        ),
    ],
)
def test_rejects_a_figure_that_is_negative_or_not_finite(make: Any, message: str) -> None:
    with pytest.raises(InvalidAmountByBandError, match=message):
        make()


@pytest.mark.parametrize(
    "make",
    [
        pytest.param(lambda: AmountBand(cast(Any, 0), amount=D(0)), id="over-int"),
        pytest.param(lambda: AmountBand(cast(Any, "0"), amount=D(0)), id="over-str"),
        pytest.param(lambda: AmountBand(D(0), amount=cast(Any, 100)), id="amount-int"),
        pytest.param(lambda: AmountBand(D(0), amount=cast(Any, 100.5)), id="amount-float"),
        pytest.param(
            lambda: AmountBand(D(0), minus=cast(Any, "100"), rate=TEN_PERCENT, plus=D(0)),
            id="minus-str",
        ),
        pytest.param(
            lambda: AmountBand(D(0), minus=D(0), rate=cast(Any, D("0.1")), plus=D(0)),
            id="rate-not-a-rate",
        ),
        pytest.param(
            lambda: AmountBand(D(0), minus=D(0), rate=TEN_PERCENT, plus=cast(Any, 1.0)),
            id="plus-float",
        ),
    ],
)
def test_rejects_a_figure_that_is_not_of_its_type(make: Any) -> None:
    with pytest.raises(TypeError):
        make()


def test_keeps_a_zero_amount_as_a_plain_zero_with_its_scale() -> None:
    band = AmountBand(D(0), amount=D("-0.00"))

    assert band.amount is not None
    assert band.amount.is_signed() is False
    assert str(band.amount) == "0.00"


def test_keeps_its_figures_exactly_as_given() -> None:
    band = AmountBand(D("20000.00"), minus=D("20000.00"), rate=Rate(D("0.0600")), plus=D("300.0"))

    assert [str(band.over), str(band.minus), str(band.plus)] == ["20000.00", "20000.00", "300.0"]
    assert band.rate is not None
    assert str(band.rate.value) == "0.0600"


# --- the chart ----------------------------------------------------------------------------------


def test_holds_its_bands() -> None:
    assert chart().bands == BANDS


def test_holds_its_bands_as_a_tuple() -> None:
    assert isinstance(chart().bands, tuple)


def test_holds_one_field() -> None:
    assert [field.name for field in fields(AmountByBand)] == ["bands"]


def test_is_built_positionally() -> None:
    assert AmountByBand((FLAT_ZERO,)) == AmountByBand((AmountBand(D(0), amount=D(0)),))


def test_keeps_the_order_of_its_bands() -> None:
    assert chart().bands[1] is SLOPED_100
    assert chart().bands[3] is SLOPED_300


def test_equal_charts_are_equal() -> None:
    assert chart() == AmountByBand(
        (
            AmountBand(D("0.00"), amount=D("0")),
            AmountBand(D(100), minus=D(100), rate=Rate(D("0.1")), plus=D("0.0")),
            AmountBand(D(200), amount=D(12)),
            AmountBand(D(300), minus=D(300), rate=QUARTER, plus=D(15)),
        )
    )


def test_charts_differ_by_any_band() -> None:
    assert chart() != chart(FLAT_ZERO, SLOPED_100, FLAT_12, AmountBand(D(300), amount=D(15)))
    assert chart() != chart(FLAT_ZERO, SLOPED_100, FLAT_12)


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, chart()).bands = ()


def test_is_hashable() -> None:
    assert hash(chart()) == hash(chart())


def test_accepts_a_single_band_from_zero() -> None:
    assert chart(AmountBand(D(0), amount=D(5))).bands == (AmountBand(D(0), amount=D(5)),)


def test_rejects_an_empty_chart() -> None:
    with pytest.raises(InvalidAmountByBandError, match="must not be empty"):
        AmountByBand(())


@pytest.mark.parametrize(
    "bands",
    [
        pytest.param((AmountBand(D(1), amount=D(0)),), id="starts-above-zero"),
        pytest.param((AmountBand(D(5), amount=D(0)), FLAT_12), id="first-not-zero"),
    ],
)
def test_rejects_a_chart_whose_first_band_is_not_from_zero(bands: tuple[AmountBand, ...]) -> None:
    with pytest.raises(InvalidAmountByBandError, match="must start at 0"):
        AmountByBand(bands)


@pytest.mark.parametrize(
    "bands",
    [
        pytest.param((FLAT_ZERO, AmountBand(D(0), amount=D(5))), id="equal"),
        pytest.param((FLAT_ZERO, FLAT_12, SLOPED_100), id="descending-after-ascending"),
        pytest.param((FLAT_ZERO, SLOPED_100, SLOPED_100), id="repeated-boundary"),
    ],
)
def test_rejects_overs_that_are_not_strictly_increasing(bands: tuple[AmountBand, ...]) -> None:
    with pytest.raises(InvalidAmountByBandError, match="strictly increasing"):
        AmountByBand(bands)


def test_invalid_amount_by_band_is_a_domain_error() -> None:
    assert issubclass(InvalidAmountByBandError, DomainError)


# --- the band a given income falls in ------------------------------------------------------------


@pytest.mark.parametrize(
    ("income", "over"),
    [
        pytest.param("0", "0", id="zero-is-the-first-band"),
        pytest.param("0.01", "0", id="just-above-zero"),
        pytest.param("50", "0", id="inside-the-first-band"),
        pytest.param("100", "0", id="at-the-first-boundary-falls-in-the-lower-band"),
        pytest.param("100.01", "100", id="just-above-the-first-boundary"),
        pytest.param("200", "100", id="at-the-second-boundary-falls-in-the-lower-band"),
        pytest.param("200.01", "200", id="just-above-the-second-boundary"),
        pytest.param("300", "200", id="at-the-third-boundary-falls-in-the-lower-band"),
        pytest.param("300.01", "300", id="just-above-the-third-boundary"),
        pytest.param("1000000", "300", id="far-above-the-last-boundary"),
    ],
)
def test_band_for_takes_the_band_whose_over_is_the_highest_below_the_income(
    income: str, over: str
) -> None:
    band = chart().band_for(D(income))

    assert band.over == D(over)
    assert band in BANDS


def test_band_for_an_income_at_a_boundary_is_the_lower_band() -> None:
    assert chart().band_for(D("200")) is SLOPED_100
    assert chart().band_for(D("300")) is FLAT_12


def test_band_for_zero_is_the_first_band() -> None:
    assert chart().band_for(D(0)) is FLAT_ZERO


def test_band_for_on_a_single_band_chart_is_that_band() -> None:
    only = AmountBand(D(0), amount=D(5))

    assert chart(only).band_for(D("10000")) is only
    assert chart(only).band_for(D(0)) is only


def test_band_for_keeps_the_band_it_finds() -> None:
    band = chart().band_for(D("150"))

    assert band == SLOPED_100
    assert band.amount_at(D("150")) == D("5")


@pytest.mark.parametrize("income", ["-0.01", "-1", "-1000000"])
def test_band_for_a_negative_income_is_a_value_error(income: str) -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        chart().band_for(D(income))


@pytest.mark.parametrize("income", [100, "100", 100.0, None])
def test_band_for_a_non_decimal_income_is_a_type_error(income: object) -> None:
    with pytest.raises(TypeError):
        chart().band_for(cast(Any, income))


# --- the kind ------------------------------------------------------------------------------------


def test_amount_by_band_kind() -> None:
    assert AMOUNT_BY_BAND == ParameterKind("amount_by_band", AmountByBand)
    assert AMOUNT_BY_BAND.name == "amount_by_band"
    assert AMOUNT_BY_BAND.value_type is AmountByBand
