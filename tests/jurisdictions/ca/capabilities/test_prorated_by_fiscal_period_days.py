"""Unit tests for the ProratedByFiscalPeriodDays capability (`ca/prorated_by_fiscal_period_days`),
an amount prorated by the days of the fiscal period, made-up kinds.

Income Tax Regulations, subsection 1104(3.5), paragraph (b): "where an eligible person or
partnership has a taxation year that is less than 51 weeks, its immediate expensing limit for the
year is that proportion of its immediate expensing limit for the year determined without reference
to this paragraph that the number of days in the year is of 365". The Regulations decide over
Guides T4002 and T4036, "Immediate expensing incentive": "The limit is also prorated for tax years
shorter than 365 days", which prorates a year of 357 to 364 days too.

Its slots: two parameter slots, `rounding` (a `rounding_only` dataset) and `class_rates` (a
`class_rates` dataset, read only for its `full_year_days`, the 365); three consumed slots, the
`Decimal` `amount`, the int `fiscal_period_days` and the `Decimal` `short_year_days`, the figure a
year must be shorter than to be prorated (357 in 2025, 51 weeks of 7 days, read from its artifact);
and one produced `Decimal` slot `output`.

A fiscal period of fewer days than `short_year_days` gives `rounding.apply(amount x
fiscal_period_days / full_year_days)`, formed as one exact fraction and rounded once by the
dataset's rule. Any other period gives the amount itself, unchanged and unrounded. Days below 1 are
refused (`InputBelowBoundError`, "<kind> 0 is below the minimum 1") and days above `full_year_days`
are refused (`InputAboveBoundError`, "<kind> 366 is above the maximum 365"), as the CCA table words
them. It records one `ProratedByDaysLine` (in `tax_engine.jurisdictions.ca.trace`, next to
`FiscalPeriodDaysLine`) in either case, with the output, the amount's kind and value, the days' kind
and value, the dataset's `full_year_days`, the short-year figure's kind and value and the result,
in that order.

Worked values, each worked out as an exact fraction and rounded half-up to the cent:
1500000 x 153 / 365 = 229500000 / 365 = 628767.1232..., so 628767.12 (365 x 628767 = 229499955,
remainder 45, and 45 / 365 = 0.1232...); 600000 x 153 / 365 = 91800000 / 365 = 251506.8493..., so
251506.85; 1500000 x 214 / 365 = 321000000 / 365 = 879452.0547..., so 879452.05; 1500000 x 1 / 365 =
4109.5890..., so 4109.59; 1500000 x 153 / 366 = 229500000 / 366 = 627049.1803..., so 627049.18;
1500000 x 356 / 365 = 534000000 / 365 = 1463013.6986..., so 1463013.70; 5000 x 153 / 365 =
765000 / 365 = 2095.8904..., so 2095.89. Rounding once matters: rounding 1500000 / 365 to 4109.59
first and multiplying by 153 would give 628766.27.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from decimal import Decimal
from types import MappingProxyType
from typing import assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.parameters.class_rates import CLASS_RATES
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.jurisdictions.ca.capabilities.prorated_by_fiscal_period_days import (
    ProratedByFiscalPeriodDays,
)
from tax_engine.jurisdictions.ca.trace import ProratedByDaysLine
from tests.jurisdictions.ca.capabilities.cca_table import class_rates

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
DOLLAR = RoundTo(D("1"), RoundingMode.HALF_UP)

LIMIT = ArtifactKind("ex/limit", Decimal)
DAYS = ArtifactKind("ex/fiscal_period_days", int)
SHORT_YEAR = ArtifactKind("ex/short_year_days", Decimal)
PRORATED = ArtifactKind("ex/limit_prorated", Decimal)


def rounding(rule: RoundingRule = CENT) -> ParameterDataset[RoundingOnly]:
    """By default half-up to the cent."""
    return ParameterDataset(
        "ex/limit_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rule: RoundingRule = CENT, full_year_days: int = 365) -> ProratedByFiscalPeriodDays:
    return ProratedByFiscalPeriodDays(
        rounding(rule),
        class_rates(full_year_days=full_year_days),
        LIMIT,
        DAYS,
        SHORT_YEAR,
        PRORATED,
    )


def inputs(
    amount: str, days: int, short_year: str = "357"
) -> tuple[Artifact[Decimal] | Artifact[int], ...]:
    return (Artifact(LIMIT, D(amount)), Artifact(DAYS, days), Artifact(SHORT_YEAR, D(short_year)))


def prorated(
    amount: str,
    days: int,
    rule: RoundingRule = CENT,
    full_year_days: int = 365,
    short_year: str = "357",
) -> Decimal:
    (output,) = capability(rule, full_year_days).compute(inputs(amount, days, short_year)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def test_is_registered_as_ca_prorated_by_fiscal_period_days() -> None:
    registered = CapabilityRegistry.shared().get("ca/prorated_by_fiscal_period_days")

    assert registered is ProratedByFiscalPeriodDays


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "prorated_by_fiscal_period_days" in ca_capabilities.__all__
    assert (
        ca_capabilities.prorated_by_fiscal_period_days.ProratedByFiscalPeriodDays
        is ProratedByFiscalPeriodDays
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({LIMIT, DAYS, SHORT_YEAR})
    assert capability().produces == frozenset({PRORATED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ProratedByFiscalPeriodDays)
    assert "produces" not in vars(ProratedByFiscalPeriodDays)


def test_declares_its_slots() -> None:
    assert ProratedByFiscalPeriodDays.PARAMETERS == {
        "rounding": ROUNDING_ONLY,
        "class_rates": CLASS_RATES,
    }
    assert ProratedByFiscalPeriodDays.CONSUMES == {
        "amount": Decimal,
        "fiscal_period_days": int,
        "short_year_days": Decimal,
    }
    assert ProratedByFiscalPeriodDays.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for each in (
        ProratedByFiscalPeriodDays.PARAMETERS,
        ProratedByFiscalPeriodDays.CONSUMES,
        ProratedByFiscalPeriodDays.PRODUCES,
    ):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast("MutableMapping[str, object]", each)["extra"] = int


def test_its_consumed_and_produced_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ProratedByFiscalPeriodDays.CONSUMES, Mapping[str, type])
    assert_type(ProratedByFiscalPeriodDays.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ProratedByFiscalPeriodDays(
        rounding=rounding(),
        class_rates=class_rates(),
        amount=LIMIT,
        fiscal_period_days=DAYS,
        short_year_days=SHORT_YEAR,
        output=PRORATED,
    )

    (output,) = wired.compute(inputs("1500000", 153)).outputs
    assert output == Artifact(PRORATED, D("628767.12"))


def test_rejects_an_int_kind_for_the_amount() -> None:
    int_kind = cast("Money", ArtifactKind("ex/count", int))

    with pytest.raises(InvalidCapabilityError, match="ProratedByFiscalPeriodDays.*'amount'"):
        ProratedByFiscalPeriodDays(rounding(), class_rates(), int_kind, DAYS, SHORT_YEAR, PRORATED)


def test_rejects_a_money_kind_for_the_days() -> None:
    money_kind = cast("ArtifactKind[int]", ArtifactKind("ex/money", Decimal))

    with pytest.raises(
        InvalidCapabilityError, match="ProratedByFiscalPeriodDays.*'fiscal_period_days'"
    ):
        ProratedByFiscalPeriodDays(
            rounding(), class_rates(), LIMIT, money_kind, SHORT_YEAR, PRORATED
        )


def test_rejects_an_int_kind_for_the_short_year_days() -> None:
    int_kind = cast("Money", ArtifactKind("ex/short_count", int))

    with pytest.raises(
        InvalidCapabilityError, match="ProratedByFiscalPeriodDays.*'short_year_days'"
    ):
        ProratedByFiscalPeriodDays(rounding(), class_rates(), LIMIT, DAYS, int_kind, PRORATED)


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ProratedByFiscalPeriodDays") as raised:
        ProratedByFiscalPeriodDays(rounding(), class_rates(), LIMIT, DAYS, SHORT_YEAR, LIMIT)

    assert "'amount'" in str(raised.value)
    assert "'output'" in str(raised.value)


@pytest.mark.parametrize(
    ("amount", "days", "expected"),
    [
        # A 153-day fiscal period of the $1.5 million.
        ("1500000", 153, "628767.12"),
        # The same period of a 40% share of the $1.5 million.
        ("600000", 153, "251506.85"),
        # June 1 to December 31, 2025 is 214 days.
        ("1500000", 214, "879452.05"),
        # The longest year that is prorated: 356 days of the $1.5 million.
        ("1500000", 356, "1463013.70"),
        # A year of 51 weeks, 357 days, is not prorated.
        ("1500000", 357, "1500000.00"),
        # A full year is not prorated.
        ("1500000", 365, "1500000.00"),
        ("600000", 365, "600000.00"),
        ("1500000", 1, "4109.59"),
        ("0", 153, "0.00"),
        # An amount of 0 stays 0 for the days of a full year.
        ("0", 365, "0.00"),
        # 1.825 x 1 / 365 = 0.005, a tie, rounds up to 0.01.
        ("1.825", 1, "0.01"),
    ],
)
def test_prorates_a_year_under_51_weeks_by_its_days_and_rounds_once(
    amount: str, days: int, expected: str
) -> None:
    assert prorated(amount, days) == D(expected)


@pytest.mark.parametrize("days", [357, 358, 363, 364])
def test_a_year_of_51_weeks_or_more_passes_the_amount_through(days: int) -> None:
    assert prorated("1500000", days) == D("1500000")


def test_rounds_once_not_the_daily_amount_first() -> None:
    # 1500000 / 365 = 4109.59 to the cent, and 4109.59 x 153 = 628766.27, which is not the answer.
    assert prorated("1500000", 153) == D("628767.12")
    assert prorated("1500000", 153) != D("628766.27")


def test_the_dataset_decides_the_rounding() -> None:
    assert prorated("1500000", 153, DOLLAR) == D("628767")


def test_under_no_rounding_a_product_that_is_exact_stays_exact() -> None:
    # 36500 x 73 / 365 = 7300, exact, with no rounding rule to apply.
    assert prorated("36500", 73, NO_ROUNDING) == D("7300")


def test_a_year_that_is_not_prorated_is_not_rounded() -> None:
    # The amount passes through as it is: the rounding rule applies only to a prorated amount.
    assert prorated("1000.005", 357) == D("1000.005")
    assert prorated("1000.005", 365, DOLLAR) == D("1000.005")


def test_a_dataset_of_366_days_prorates_by_366() -> None:
    assert prorated("1500000", 153, full_year_days=366) == D("627049.18")
    assert prorated("1500000", 366, full_year_days=366) == D("1500000.00")


def test_the_short_year_figure_is_the_consumed_artifact_not_a_constant() -> None:
    # A figure of 300 days moves the boundary: 299 days prorate, 300 days do not.
    assert prorated("1500000", 299, short_year="300") == D("1228767.12")
    assert prorated("1500000", 300, short_year="300") == D("1500000")


def test_the_output_is_a_decimal_of_the_produced_kind() -> None:
    (output,) = capability().compute(inputs("1500000", 153)).outputs

    assert output.kind == PRORATED
    assert type(output.value) is Decimal


def test_zero_days_are_refused_naming_the_kind_and_the_minimum() -> None:
    with pytest.raises(InputBelowBoundError) as raised:
        prorated("1500000", 0)

    assert str(raised.value) == "ex/fiscal_period_days 0 is below the minimum 1"


def test_negative_days_are_refused() -> None:
    with pytest.raises(InputBelowBoundError) as raised:
        prorated("1500000", -1)

    assert str(raised.value) == "ex/fiscal_period_days -1 is below the minimum 1"


def test_366_days_are_a_period_of_12_months_and_not_prorated() -> None:
    assert prorated("1500000", 366) == D("1500000.00")


def test_367_days_are_refused_naming_the_kind_and_the_maximum() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        prorated("1500000", 367)

    assert str(raised.value) == "ex/fiscal_period_days 367 is above the maximum 366"


def test_a_dataset_of_366_days_refuses_367_days() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        prorated("1500000", 367, full_year_days=366)

    assert str(raised.value) == "ex/fiscal_period_days 367 is above the maximum 366"


@pytest.mark.parametrize("days", [1, 365])
def test_the_days_at_the_bounds_are_allowed(days: int) -> None:
    assert prorated("365", days) == D(days)


@pytest.mark.parametrize("missing", [0, 1, 2])
def test_a_missing_consumed_artifact_is_a_missing_artifact(missing: int) -> None:
    given = tuple(a for i, a in enumerate(inputs("1500000", 153)) if i != missing)

    with pytest.raises(MissingArtifactError):
        capability().compute(given)


def test_traces_one_prorated_by_days_line() -> None:
    result = capability().compute(inputs("1500000", 153))

    assert result.trace == (
        ProratedByDaysLine(
            PRORATED, LIMIT, D("1500000"), DAYS, 153, 365, SHORT_YEAR, D("357"), D("628767.12")
        ),
    )


def test_traces_one_prorated_by_days_line_for_a_year_that_is_not_prorated() -> None:
    # The line is recorded whether or not the year is prorated, so the trace shows the figure.
    result = capability().compute(inputs("1500000", 364))

    assert result.trace == (
        ProratedByDaysLine(
            PRORATED, LIMIT, D("1500000"), DAYS, 364, 365, SHORT_YEAR, D("357"), D("1500000")
        ),
    )


def test_the_line_carries_the_full_year_of_the_dataset() -> None:
    result = capability(full_year_days=366).compute(inputs("1500000", 153))

    assert result.trace == (
        ProratedByDaysLine(
            PRORATED, LIMIT, D("1500000"), DAYS, 153, 366, SHORT_YEAR, D("357"), D("627049.18")
        ),
    )
