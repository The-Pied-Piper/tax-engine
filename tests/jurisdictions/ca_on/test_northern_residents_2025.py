"""The 2025 Northern Residents Deductions datasets, checked against CRA's Form T2222.

Form T2222 2025 (`t2222-25e.txt`), Step 2: line 1 "Enter the number of days you lived in a
prescribed northern zone in 2025. multiplied by $11.00 =" and line 2 "Enter the number of days you
qualify for the additional residency amount in 2025. multiplied by $11.00 =" (Zone A); line 6
"Enter the number of days you lived in an intermediate zone in 2025. multiplied by $5.50 =" and
line 7 "Enter the number of days you qualify for the additional residency amount in 2025. multiplied
by $5.50 =" (Zone B); line 12 "Enter your net income from line 23600 of your return. multiplied by
20%  =". Step 3: Chart A "Row C: Enter the total of all amounts in row B. This total cannot be
more than $1,200." and line 15 "Enter the total from box B. Line 67560 multiplied by 50% =". So the
$11.00 and $5.50 are per-unit amounts (the `amount` kind), the 20% and the 50% rates (the `rate`
kind) applied to line 12's net income and to the total of box B, and the $1,200 a plain bound (the
`amount` kind). Every line is a dollars-and-cents box, so each is rounded half-up to the cent, the
owner's decision, as the form states no rounding rule.

Each dataset is tested with the one capability that reads it, on made-up kinds; the lines together
are in test_end_to_end_2025.py.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.chart_a_row_c_total import ChartARowCTotal
from tax_engine.jurisdictions.ca.catalog import (
    STANDARD_AMOUNT_ALLOCATED_1,
    STANDARD_AMOUNT_ALLOCATED_2,
    STANDARD_AMOUNT_ALLOCATED_3,
    TRAVEL_INDIVIDUAL,
    TRAVEL_INDIVIDUALS,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
ZONE_A_DAILY = "ca/northern_zone_a_daily_amount"
ZONE_B_DAILY = "ca/northern_zone_b_daily_amount"
RESIDENCY_RATE = "ca/northern_residency_rate"
TRAVEL_RATE = "ca/northern_travel_zone_b_rate"
STANDARD_AMOUNT = "ca/northern_travel_standard_amount"
T2222_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2222/t2222-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: a count of days, the amount for them, a net income, a
# deduction, and the total of Chart A.
DAYS = ArtifactKind("ex/days", int)
FOR_DAYS = ArtifactKind("ex/amount_for_days", Decimal)
INCOME = ArtifactKind("ex/income", Decimal)
LIMIT = ArtifactKind("ex/limit", Decimal)
ALLOCATED = ArtifactKind("ex/allocated", Decimal)


def test_2025_zone_a_daily_amount_is_11_00() -> None:
    data = SOURCE.get(ZONE_A_DAILY, 2025, AMOUNT)

    assert data.values == Amount(D("11.00"))
    # Lines 1 and 2, dollars-and-cents boxes: half-up to the cent.
    assert data.rounding == CENT


def test_2025_zone_b_daily_amount_is_5_50() -> None:
    data = SOURCE.get(ZONE_B_DAILY, 2025, AMOUNT)

    assert data.values == Amount(D("5.50"))
    # Lines 6 and 7, dollars-and-cents boxes: half-up to the cent.
    assert data.rounding == CENT


def test_2025_residency_rate_is_20_percent() -> None:
    data = SOURCE.get(RESIDENCY_RATE, 2025, RATE)

    assert data.values == Rate(D("0.20"))
    # Line 12, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_travel_rate_for_zone_b_is_50_percent() -> None:
    data = SOURCE.get(TRAVEL_RATE, 2025, RATE)

    assert data.values == Rate(D("0.50"))
    # Line 15, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_standard_amount_is_1200() -> None:
    data = SOURCE.get(STANDARD_AMOUNT, 2025, AMOUNT)

    assert data.values == Amount(D("1200.00"))
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("family", "kind"),
    [
        (ZONE_A_DAILY, AMOUNT),
        (ZONE_B_DAILY, AMOUNT),
        (RESIDENCY_RATE, RATE),
        (TRAVEL_RATE, RATE),
        (STANDARD_AMOUNT, AMOUNT),
    ],
)
def test_2025_datasets_cite_only_the_t2222_text(family: str, kind: object) -> None:
    assert SOURCE.get(family, 2025, kind).sources == (T2222_TEXT,)  # type: ignore[call-overload,arg-type,unused-ignore]


@pytest.mark.parametrize(
    ("days", "amount"),
    [
        (0, "0.00"),
        (1, "11.00"),
        # Question 1: "$352 ($11 multiplied by 32 days - November 30, 2025, to December 31,
        # 2025)".
        (32, "352.00"),
        # Example 1: 292 days (March 15 to December 31, 2025) at $11 each.
        (292, "3212.00"),
        (365, "4015.00"),
    ],
)
def test_zone_a_is_11_00_for_each_day(days: int, amount: str) -> None:
    capability = PerUnitAmount(SOURCE.get(ZONE_A_DAILY, 2025, AMOUNT), DAYS, FOR_DAYS)

    result = capability.compute((Artifact(DAYS, days),))

    assert result.outputs == (Artifact(FOR_DAYS, D(amount)),)


@pytest.mark.parametrize(
    ("days", "amount"),
    [
        (0, "0.00"),
        (1, "5.50"),
        (3, "16.50"),
        # Example 2: 292 days at $5.50 each.
        (292, "1606.00"),
        (365, "2007.50"),
    ],
)
def test_zone_b_is_5_50_for_each_day(days: int, amount: str) -> None:
    capability = PerUnitAmount(SOURCE.get(ZONE_B_DAILY, 2025, AMOUNT), DAYS, FOR_DAYS)

    result = capability.compute((Artifact(DAYS, days),))

    assert result.outputs == (Artifact(FOR_DAYS, D(amount)),)


@pytest.mark.parametrize(
    ("net_income", "limit"),
    [
        ("0", "0.00"),
        ("50000", "10000.00"),
        ("49535.00", "9907.00"),
        # 49999.99 x 20% = 9999.998, rounded half-up to the cent.
        ("49999.99", "10000.00"),
        # 33.33 x 20% = 6.666, up to 6.67; 0.02 x 20% = 0.004, down to 0.00.
        ("33.33", "6.67"),
        ("0.02", "0.00"),
        # 0.025 x 20% = 0.005, a tie, up to 0.01.
        ("0.025", "0.01"),
    ],
)
def test_the_residency_deduction_is_limited_to_20_percent_of_net_income(
    net_income: str, limit: str
) -> None:
    capability = ApplyRate(SOURCE.get(RESIDENCY_RATE, 2025, RATE), INCOME, LIMIT)

    result = capability.compute((Artifact(INCOME, D(net_income)),))

    assert result.outputs == (Artifact(LIMIT, D(limit)),)


@pytest.mark.parametrize(
    ("box_b", "deduction"),
    [
        ("0", "0.00"),
        ("1200", "600.00"),
        # 1234.57 x 50% = 617.285, a tie, rounded half-up to 617.29.
        ("1234.57", "617.29"),
        ("0.01", "0.01"),
    ],
)
def test_a_zone_b_trip_amount_counts_at_50_percent(box_b: str, deduction: str) -> None:
    capability = ApplyRate(SOURCE.get(TRAVEL_RATE, 2025, RATE), INCOME, LIMIT)

    result = capability.compute((Artifact(INCOME, D(box_b)),))

    assert result.outputs == (Artifact(LIMIT, D(deduction)),)


def test_the_standard_amount_bounds_each_individuals_row_c() -> None:
    capability = ChartARowCTotal(
        SOURCE.get(STANDARD_AMOUNT, 2025, AMOUNT), TRAVEL_INDIVIDUALS, ALLOCATED
    )
    row: dict[ArtifactKind[Any], object] = {
        TRAVEL_INDIVIDUAL: 1,
        STANDARD_AMOUNT_ALLOCATED_1: D("1200"),
        STANDARD_AMOUNT_ALLOCATED_2: D("0"),
        STANDARD_AMOUNT_ALLOCATED_3: D("0"),
    }

    result = capability.compute(
        (Artifact(TRAVEL_INDIVIDUALS, RecordList(TRAVEL_INDIVIDUALS.fields, [row])),)
    )

    assert result.outputs == (Artifact(ALLOCATED, D("1200")),)
