"""Unit tests for the FiscalPeriodDaysFromDates capability (`ca/fiscal_period_days_from_dates`), the
days of the fiscal period that a prorated CCA claim is based on, taken from the period's dates.

Form T2125 page 1 "Fiscal period From / to, Date (YYYYMMDD)": the caller enters the start and the
end of the fiscal period as whole numbers like 20250601, and 0 for either when none is entered.
Guide T4002 2025, "You were asking?": "Q. How do I calculate my CCA claim if I start a business and
my first fiscal period is from June 1, 2025, to December 31, 2025? A. Since your fiscal period is
less than 365 days, you have to prorate your CCA claim. Calculate your CCA using the rules discussed
in this chapter. However, base your CCA claim on the number of days in your fiscal period compared
to 365 days. In this case, your fiscal period is 214 days." Guide T4002, "A fiscal period cannot be
longer than 12 months."

Its slots: one parameter slot `class_rates` (a `class_rates` dataset, whose `full_year_days` is the
365), two consumed int slots `from_date` and `to_date` (YYYYMMDD, or 0 for none) and one produced
int slot `output`. The output is the inclusive number of days from the start to the end. Both 0 is
no dates entered, a full year: the dataset's `full_year_days`, so the claim is not prorated. Exactly
one 0, a value that is not a real YYYYMMDD date, or an end before the start is refused. An end after
the day before the same date a year later is refused too (`InputAboveBoundError`): a fiscal period
is at most 12 months, so 1 March 2025 to 1 March 2026 (366 days, no 29 February) is refused, and a
period starting on 29 February ends on 28 February of the next year. It records one
`FiscalPeriodDaysFromDatesLine`, which carries the two dates.

Worked values: 20250601 to 20251231 is 214 (30 + 31 + 31 + 30 + 31 + 30 + 31, the guide's); 0 and 0
is 365 (366 of a 366-day dataset); 20250101 to 20251231 is 365; 20250101 to 20250101 is 1; 20250101
to 20251222 is 356; 20240201 to 20250131 is 366; 20240229 to 20250228 is 366; 20250301 to 20260228
is 365; 20250301 to 20260301, 20240229 to 20250301, 20240201 to 20250201 and 20250101 to 20260102
are refused.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InputBelowBoundError,
    InputOutOfRangeError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.parameters.class_rates import CLASS_RATES, ClassRates
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.jurisdictions.ca.capabilities.fiscal_period_days_from_dates import (
    FiscalPeriodDaysFromDates,
)
from tax_engine.jurisdictions.ca.trace import FiscalPeriodDaysFromDatesLine
from tests.jurisdictions.ca.capabilities.cca_table import class_rates

FROM = ArtifactKind("ex/fiscal_period_from", int)
TO = ArtifactKind("ex/fiscal_period_to", int)
DAYS = ArtifactKind("ex/fiscal_period_days", int)


def capability(full_year_days: int = 365) -> FiscalPeriodDaysFromDates:
    return FiscalPeriodDaysFromDates(class_rates(full_year_days=full_year_days), FROM, TO, DAYS)


def days(start: int, end: int, full_year_days: int = 365) -> Any:
    (output,) = (
        capability(full_year_days).compute((Artifact(FROM, start), Artifact(TO, end))).outputs
    )
    return output.value


def test_is_registered_as_ca_fiscal_period_days_from_dates() -> None:
    registered = CapabilityRegistry.shared().get("ca/fiscal_period_days_from_dates")

    assert registered is FiscalPeriodDaysFromDates


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "fiscal_period_days_from_dates" in ca_capabilities.__all__
    assert (
        ca_capabilities.fiscal_period_days_from_dates.FiscalPeriodDaysFromDates
        is FiscalPeriodDaysFromDates
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({FROM, TO})
    assert capability().produces == frozenset({DAYS})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(FiscalPeriodDaysFromDates)
    assert "produces" not in vars(FiscalPeriodDaysFromDates)


def test_declares_its_slots() -> None:
    assert FiscalPeriodDaysFromDates.PARAMETERS == {"class_rates": CLASS_RATES}
    assert FiscalPeriodDaysFromDates.CONSUMES == {"from_date": int, "to_date": int}
    assert FiscalPeriodDaysFromDates.PRODUCES == {"output": int}


def test_its_slots_are_read_only() -> None:
    for each in (
        FiscalPeriodDaysFromDates.PARAMETERS,
        FiscalPeriodDaysFromDates.CONSUMES,
        FiscalPeriodDaysFromDates.PRODUCES,
    ):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = int


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(FiscalPeriodDaysFromDates.PARAMETERS, Mapping[str, ParameterKind[ClassRates]])
    assert_type(FiscalPeriodDaysFromDates.CONSUMES, Mapping[str, type])
    assert_type(FiscalPeriodDaysFromDates.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = FiscalPeriodDaysFromDates(
        class_rates=class_rates(), from_date=FROM, to_date=TO, output=DAYS
    )

    (output,) = wired.compute((Artifact(FROM, 20250601), Artifact(TO, 20251231))).outputs
    assert output == Artifact(DAYS, 214)


@pytest.mark.parametrize(("slot", "wired_at"), [("from_date", 1), ("to_date", 2)])
def test_rejects_a_money_kind_for_either_date(slot: str, wired_at: int) -> None:
    money_kind = cast(Any, ArtifactKind("ex/money", Decimal))
    args: list[Any] = [class_rates(), FROM, TO, DAYS]
    args[wired_at] = money_kind

    with pytest.raises(InvalidCapabilityError, match=f"FiscalPeriodDaysFromDates.*'{slot}'"):
        FiscalPeriodDaysFromDates(*args)


@pytest.mark.parametrize(
    ("start", "end", "result"),
    [
        (20250601, 20251231, 214),
        (20250101, 20251231, 365),
        (20250101, 20250101, 1),
        (20250101, 20251222, 356),
        (20240201, 20250131, 366),
        (20240229, 20250228, 366),
        (20250301, 20260228, 365),
    ],
)
def test_the_days_from_the_dates_are_the_inclusive_count(start: int, end: int, result: int) -> None:
    assert days(start, end) == result


def test_the_guides_fiscal_period_is_214_days() -> None:
    # Guide T4002: June 1, 2025, to December 31, 2025 is 214 days.
    assert days(20250601, 20251231) == 214


def test_no_dates_entered_is_a_full_year_of_the_dataset() -> None:
    assert days(0, 0) == 365


def test_no_dates_entered_is_a_full_year_of_a_366_day_dataset() -> None:
    assert days(0, 0, full_year_days=366) == 366


def test_the_output_is_an_int_of_the_produced_kind() -> None:
    (output,) = capability().compute((Artifact(FROM, 20250601), Artifact(TO, 20251231))).outputs

    assert output.kind == DAYS
    assert type(output.value) is int


def test_a_period_of_12_months_with_29_february_in_it_is_accepted() -> None:
    # 1 February 2024 to 31 January 2025 contains 29 February 2024: 366 days, 12 months.
    assert days(20240201, 20250131) == 366


def test_a_period_starting_on_29_february_ends_on_28_february_of_the_next_year() -> None:
    # The anniversary of 29 February 2024 is 1 March 2025 (no 29 February in 2025), so the period
    # ends on the day before it, 28 February 2025: 366 days.
    assert days(20240229, 20250228) == 366


def test_a_period_of_12_months_without_29_february_ends_on_the_day_before_its_anniversary() -> None:
    # 1 March 2025 to 28 February 2026 is 365 days, the day before 1 March 2026.
    assert days(20250301, 20260228) == 365


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (20250301, 20260301),
        (20240229, 20250301),
        (20240201, 20250201),
        (20250101, 20260102),
    ],
)
def test_an_end_after_the_day_before_the_same_date_a_year_later_is_refused(
    start: int, end: int
) -> None:
    # A fiscal period cannot be longer than 12 months: 1 March 2025 to 1 March 2026 is 366 days
    # with no 29 February, one day longer than 12 months.
    with pytest.raises(InputAboveBoundError, match=rf"^ex/fiscal_period_to {end} is "):
        days(start, end)


@pytest.mark.parametrize(
    ("start", "end", "identifier", "value"),
    [
        (20250230, 20251231, "ex/fiscal_period_from", 20250230),
        (20251301, 20251231, "ex/fiscal_period_from", 20251301),
        (123, 20251231, "ex/fiscal_period_from", 123),
        (20250601, 20250230, "ex/fiscal_period_to", 20250230),
    ],
)
def test_a_value_that_is_not_a_real_date_is_refused(
    start: int, end: int, identifier: str, value: int
) -> None:
    with pytest.raises(InputOutOfRangeError, match=rf"^{identifier} {value} is "):
        days(start, end)


@pytest.mark.parametrize(
    ("start", "end", "identifier"),
    [
        (20250601, 0, "ex/fiscal_period_to"),
        (0, 20251231, "ex/fiscal_period_from"),
    ],
)
def test_exactly_one_date_of_0_is_refused(start: int, end: int, identifier: str) -> None:
    with pytest.raises(InputOutOfRangeError, match=identifier):
        days(start, end)


def test_an_end_before_the_start_is_refused() -> None:
    with pytest.raises(InputBelowBoundError, match=r"^ex/fiscal_period_to 20250601 is "):
        days(20251231, 20250601)


def test_a_one_day_period_is_not_refused() -> None:
    assert days(20250101, 20250101) == 1


def test_a_missing_start_is_refused() -> None:
    with pytest.raises(MissingArtifactError, match="fiscal_period_from"):
        capability().compute((Artifact(TO, 20251231),))


def test_a_missing_end_is_refused() -> None:
    with pytest.raises(MissingArtifactError, match="fiscal_period_to"):
        capability().compute((Artifact(FROM, 20250601),))


def test_a_missing_input_is_refused() -> None:
    with pytest.raises(MissingArtifactError, match="fiscal_period_from"):
        capability().compute(())


@pytest.mark.parametrize(
    ("start", "end", "result", "full_year"),
    [
        (20250601, 20251231, 214, 365),
        (20250101, 20251231, 365, 365),
        (20240201, 20250131, 366, 365),
        (0, 0, 365, 365),
        (0, 0, 366, 366),
    ],
)
def test_records_one_fiscal_period_days_from_dates_line(
    start: int, end: int, result: int, full_year: int
) -> None:
    trace = capability(full_year).compute((Artifact(FROM, start), Artifact(TO, end))).trace

    assert trace == (FiscalPeriodDaysFromDatesLine(DAYS, start, end, result, full_year),)
