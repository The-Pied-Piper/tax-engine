"""Unit tests for the FiscalPeriodDays capability (`ca/fiscal_period_days`), the days of the fiscal
period that a prorated CCA claim and closing UCC are based on.

Guide T4002 2025, "You were asking?": "Q. How do I calculate my CCA claim if I start a business and
my first fiscal period is from June 1, 2025, to December 31, 2025? A. Since your fiscal period is
less than 365 days, you have to prorate your CCA claim. Calculate your CCA using the rules
discussed in this chapter. However, base your CCA claim on the number of days in your fiscal
period compared to 365 days. In this case, your fiscal period is 214 days. Suppose you calculate
your CCA to be $3,500. The amount of CCA you can claim is $2,052 ($3,500 × 214 ÷ 365)."

Its slots: one parameter slot `class_rates` (a `class_rates` dataset, whose `full_year_days` is the
365), one consumed int slot `entered` (the days the caller enters; 0 is none entered) and one
produced int slot `output`. The output is the days entered when they are above 0, else the
dataset's `full_year_days` (a fiscal period that is not entered is a full year, so the claim is not
prorated). Days entered above `full_year_days` are refused (`InputAboveBoundError`, naming the kind
and the value: "<kind> 366 is above the maximum 365", as the CCA table words it). It records one
`FiscalPeriodDaysLine`. (A negative number of days cannot be entered: the catalog's kind is
non-negative.)

Worked values: 214 entered is 214 (June 1 to December 31, 2025 is 30 + 31 + 31 + 30 + 31 + 30 +
31 = 214 days, the guide's); 0 entered is 365; 365 entered is 365; 1 entered is 1; 366 and 400
entered are refused; a dataset of 366 days with 0 entered is 366, and 366 entered is allowed.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_calculator.domain.parameters.class_rates import CLASS_RATES, ClassRates
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.jurisdictions.ca.capabilities.fiscal_period_days import FiscalPeriodDays
from tax_calculator.jurisdictions.ca.trace import FiscalPeriodDaysLine
from tests.jurisdictions.ca.capabilities.cca_table import class_rates

ENTERED = ArtifactKind("ex/fiscal_period_days_entered", int)
DAYS = ArtifactKind("ex/fiscal_period_days", int)


def capability(full_year_days: int = 365) -> FiscalPeriodDays:
    return FiscalPeriodDays(class_rates(full_year_days=full_year_days), ENTERED, DAYS)


def days(entered: int, full_year_days: int = 365) -> Any:
    (output,) = capability(full_year_days).compute((Artifact(ENTERED, entered),)).outputs
    return output.value


def test_is_registered_as_ca_fiscal_period_days() -> None:
    assert CapabilityRegistry.shared().get("ca/fiscal_period_days") is FiscalPeriodDays


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "fiscal_period_days" in ca_capabilities.__all__
    assert ca_capabilities.fiscal_period_days.FiscalPeriodDays is FiscalPeriodDays


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({ENTERED})
    assert capability().produces == frozenset({DAYS})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(FiscalPeriodDays)
    assert "produces" not in vars(FiscalPeriodDays)


def test_declares_its_slots() -> None:
    assert FiscalPeriodDays.PARAMETERS == {"class_rates": CLASS_RATES}
    assert FiscalPeriodDays.CONSUMES == {"entered": int}
    assert FiscalPeriodDays.PRODUCES == {"output": int}


def test_its_slots_are_read_only() -> None:
    for each in (
        FiscalPeriodDays.PARAMETERS,
        FiscalPeriodDays.CONSUMES,
        FiscalPeriodDays.PRODUCES,
    ):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = int


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(FiscalPeriodDays.PARAMETERS, Mapping[str, ParameterKind[ClassRates]])
    assert_type(FiscalPeriodDays.CONSUMES, Mapping[str, type])
    assert_type(FiscalPeriodDays.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = FiscalPeriodDays(class_rates=class_rates(), entered=ENTERED, output=DAYS)

    (output,) = wired.compute((Artifact(ENTERED, 214),)).outputs
    assert output == Artifact(DAYS, 214)


def test_rejects_a_money_kind_for_the_days_entered() -> None:
    money_kind = cast(Any, ArtifactKind("ex/money", Decimal))

    with pytest.raises(InvalidCapabilityError, match="FiscalPeriodDays.*'entered'"):
        FiscalPeriodDays(class_rates(), money_kind, DAYS)


def test_the_days_entered_are_the_days_of_the_fiscal_period() -> None:
    # June 1 to December 31, 2025: 214 days, the guide's.
    assert days(214) == 214


def test_no_days_entered_is_a_full_year_of_the_dataset() -> None:
    assert days(0) == 365


def test_a_full_year_of_days_entered_is_a_full_year() -> None:
    assert days(365) == 365


def test_one_day_entered_is_one_day() -> None:
    assert days(1) == 1


def test_the_output_is_an_int_of_the_produced_kind() -> None:
    (output,) = capability().compute((Artifact(ENTERED, 214),)).outputs

    assert output.kind == DAYS
    assert type(output.value) is int


def test_a_dataset_of_366_days_gives_366_for_no_days_entered() -> None:
    assert days(0, full_year_days=366) == 366


def test_a_dataset_of_366_days_allows_366_days_entered() -> None:
    assert days(366, full_year_days=366) == 366


def test_a_dataset_of_366_days_refuses_367_days_entered() -> None:
    with pytest.raises(InputAboveBoundError, match=r"^ex/fiscal_period_days_entered 367 is above"):
        days(367, full_year_days=366)


def test_366_days_entered_are_a_period_of_12_months() -> None:
    # Guide T4002: "A fiscal period cannot be longer than 12 months"; 1 Feb 2024 to 31 Jan 2025.
    assert days(366) == 366


def test_367_days_entered_are_refused_naming_the_kind_and_the_maximum() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        days(367)

    assert str(raised.value) == "ex/fiscal_period_days_entered 367 is above the maximum 366"


def test_400_days_entered_are_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        days(400)

    assert str(raised.value) == "ex/fiscal_period_days_entered 400 is above the maximum 366"


def test_a_missing_input_is_refused() -> None:
    with pytest.raises(MissingArtifactError, match="fiscal_period_days_entered"):
        capability().compute(())


@pytest.mark.parametrize(
    ("entered", "result"),
    [
        (214, 214),
        (0, 365),
        (365, 365),
        (1, 1),
    ],
)
def test_records_one_fiscal_period_days_line(entered: int, result: int) -> None:
    trace = capability().compute((Artifact(ENTERED, entered),)).trace

    assert trace == (FiscalPeriodDaysLine(DAYS, entered, result, 365),)


def test_the_line_carries_the_full_year_of_the_dataset() -> None:
    trace = capability(366).compute((Artifact(ENTERED, 0),)).trace

    assert trace == (FiscalPeriodDaysLine(DAYS, 0, 366, 366),)
