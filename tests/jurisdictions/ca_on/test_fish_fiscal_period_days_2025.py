"""The 2025 proration of the CCA of a short fiscal period on Form T2121, checked against the guide.

Guide T4002 2025 (confirmed from the PDF, docs/cra-forms-2025/t4002-25e.pdf; the guide covers
Forms T2125, T2042 and T2121), "You were asking?": "Q. How do I calculate my CCA claim if I start a
business and my first fiscal period is from June 1, 2025, to December 31, 2025? A. Since your
fiscal period is less than 365 days, you have to prorate your CCA claim. Calculate your CCA using
the rules discussed in this chapter. However, base your CCA claim on the number of days in your
fiscal period compared to 365 days. In this case, your fiscal period is 214 days. Suppose you
calculate your CCA to be $3,500. The amount of CCA you can claim is $2,052 ($3,500 × 214 ÷ 365)."
The 365 is the `full_year_days` of the `ca/cca_class_rates` dataset, which the T2125, the T2042 and
the T2121 share; the days of the fiscal period are the caller's input of each form, 0 for none
entered (a full year).

The capabilities are tested with the dataset the form reads, on made-up kinds; the form's lines,
for its own kinds, are tested here by running one T2121 statement; the lines of a whole return are
in `returns/2025_return_ce.yaml` (T2125) and `returns/2025_return_cf.yaml` (T2042).

Worked values, by hand: Class 8 (20%), column 3 35,000.00 and nothing else: column 7 and column 13
35,000.00, column 18 17,500.00 (the half-year rule), column 19 17,500.00, maximum 3,500.00. 214
days: 3,500.00 x 214 / 365 = 749,000 / 365 = 2,052.0547..., 2,052.05; column 22 is 35,000.00 -
2,052.05 = 32,947.95. 100 days: 350,000 / 365 = 958.9041..., 958.90. 365 days or none: 3,500.00.

The same days prorate the immediate expensing limit (Guide T4002, "Immediate expensing incentive":
"The limit is also prorated for tax years shorter than 365 days"): with no EPOP the limit is the
$1.5 million, which for 100 days is 1,500,000 x 100 / 365 = 150,000,000 / 365 = 410,958.9041...,
410,958.90, and for 214 days 1,500,000 x 214 / 365 = 321,000,000 / 365 = 879,452.0547...,
879,452.05.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.parameters.class_rates import CLASS_RATES
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities.cca_claim_prorated import CcaClaimProrated
from tax_calculator.jurisdictions.ca.capabilities.closing_ucc_prorated import ClosingUccProrated
from tax_calculator.jurisdictions.ca.capabilities.fiscal_period_days import FiscalPeriodDays
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FISH_CCA_CLAIM,
    FISH_CCA_TABLE_CLAIM,
    FISH_CLOSING_UCC,
    FISH_FISCAL_PERIOD_DAYS,
    FISH_FISCAL_PERIOD_DAYS_ENTERED,
    FISH_IMMEDIATE_EXPENSING_LIMIT,
    FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
)
from tax_calculator.jurisdictions.ca.trace import FiscalPeriodDaysLine
from tests.jurisdictions.ca.capabilities.cca_table import CLASSES, CLOSING_UCC, classes, row
from tests.jurisdictions.ca_on.end_to_end.support import run

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
RATES = SOURCE.get("ca/cca_class_rates", 2025, CLASS_RATES)

# Made up for this test and not registered: the days entered, the days of the fiscal period, the
# claim and the closing UCC.
ENTERED = ArtifactKind("ex/fish_fiscal_period_days_entered", int)
DAYS = ArtifactKind("ex/fish_fiscal_period_days", int)
CLAIM = ArtifactKind("ex/fish_cca_claim", Decimal)

FISH = {"fish_products": "49150", "vehicle_sales_tax_rate": "13"}


def fish_class_8(
    claim: str,
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9): Class 8 with additions of 35000."""
    return ("8", "0", "35000", "0", "0", "0", claim, 0, "0", "0", "0")


def statement_fish(claim: str, days: int, **changes: Any) -> Worksheet:
    statement: dict[str, Any] = {
        "fish": FISH,
        "fish_cca_classes_rows": (fish_class_8(claim),),
        "fish_fiscal_period_days_entered": days,
        **changes,
    }
    return run("0", (), "0", "0", "0", "0", "0", fish_statements=(statement,))["ca/t2121"][0]


def test_2025_full_year_is_365_days() -> None:
    assert RATES.values.full_year_days == 365


@pytest.mark.parametrize(("entered", "result"), [(214, 214), (0, 365), (365, 365), (1, 1)])
def test_the_days_of_the_fiscal_period_are_those_entered_or_a_full_year(
    entered: int, result: int
) -> None:
    capability = FiscalPeriodDays(RATES, ENTERED, DAYS)

    outputs = capability.compute((Artifact(ENTERED, entered),))

    assert outputs.outputs == (Artifact(DAYS, result),)
    assert outputs.trace == (FiscalPeriodDaysLine(DAYS, entered, result, 365),)


def test_more_than_366_days_are_refused() -> None:
    capability = FiscalPeriodDays(RATES, ENTERED, DAYS)

    with pytest.raises(InputAboveBoundError) as raised:
        capability.compute((Artifact(ENTERED, 367),))

    assert str(raised.value) == "ex/fish_fiscal_period_days_entered 367 is above the maximum 366"


@pytest.mark.parametrize(
    ("days", "claim", "closing"),
    [
        (214, "2052.05", "32947.95"),
        (100, "958.90", "34041.10"),
        (365, "3500.00", "31500.00"),
    ],
)
def test_the_prorated_claim_and_closing_ucc_of_the_dataset_for_class_8(
    days: int, claim: str, closing: str
) -> None:
    given = (
        classes(row("8", "0", "35000", claimed=claim)),
        Artifact(DAYS, days),
    )

    (claimed,) = CcaClaimProrated(RATES, CLASSES, DAYS, CLAIM).compute(given).outputs
    (closed,) = ClosingUccProrated(RATES, CLASSES, DAYS, CLOSING_UCC).compute(given).outputs

    assert claimed.value == D(claim)
    assert [record[CCA_UCC_AT_END] for record in closed.value.records] == [D(closing)]


def test_a_t2121_of_214_days_prorates_its_claim_and_closing_ucc() -> None:
    # Column 19 17,500.00 x 20% = 3,500.00; x 214 / 365 = 2,052.05; column 22 is 35,000.00 -
    # 2,052.05 = 32,947.95.
    statement = statement_fish("2052.05", 214)
    rendered = "\n".join(EnglishTraceRenderer().render_all(statement.trace))

    assert statement.get(FISH_FISCAL_PERIOD_DAYS).value == 214
    assert statement.get(FISH_CCA_TABLE_CLAIM).value == D("2052.05")
    assert statement.get(FISH_CCA_CLAIM).value == D("2052.05")
    records = statement.get(FISH_CLOSING_UCC).value.records
    assert [(r[CCA_CLASS_NUMBER], r[CCA_UCC_AT_END]) for r in records] == [(D("8"), D("32947.95"))]
    assert "fish_fiscal_period_days: entered 214, fiscal period 214 days" in rendered
    assert "prorated 214/365 = 2052.05, claim 2052.05" in rendered
    assert "less claim 2052.05 (prorated 214/365) = 32947.95" in rendered


def test_a_t2121_with_no_days_entered_is_a_full_year() -> None:
    statement = statement_fish("3500.00", 0)
    rendered = "\n".join(EnglishTraceRenderer().render_all(statement.trace))

    assert statement.get(FISH_FISCAL_PERIOD_DAYS).value == 365
    assert statement.get(FISH_CCA_TABLE_CLAIM).value == D("3500.00")
    assert "fish_fiscal_period_days: entered 0, a full year of 365 days" in rendered
    assert ", prorated " not in rendered
    assert "(prorated " not in rendered


def test_a_t2121_claim_above_the_prorated_maximum_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        statement_fish("2052.06", 214)

    assert str(raised.value) == (
        "ca/t2121, instance 1: item 1: ca/cca_claimed 2052.06 is above the maximum 2052.05"
    )


def test_a_t2121_with_more_than_366_days_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        statement_fish("0", 367)

    assert str(raised.value) == (
        "ca/t2121, instance 1: ca/fish_fiscal_period_days_entered 367 is above the maximum 366"
    )


def test_the_t2121_days_entered_is_the_forms_own_kind() -> None:
    assert FISH_FISCAL_PERIOD_DAYS_ENTERED.identifier == "ca/fish_fiscal_period_days_entered"
    assert FISH_FISCAL_PERIOD_DAYS.identifier == "ca/fish_fiscal_period_days"


# Income Tax Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation year
# that is less than 51 weeks" (357 days in 2025) the limit is prorated by the days over 365; 356
# days of 1500000 is 1500000 x 356 / 365 = 1463013.70, and 357 and 364 days are not prorated.
@pytest.mark.parametrize(
    ("days", "limit"),
    [
        (100, "410958.90"),
        (214, "879452.05"),
        (356, "1463013.70"),
        (357, "1500000.00"),
        (364, "1500000.00"),
        (365, "1500000.00"),
        (0, "1500000.00"),
    ],
)
def test_a_t2121_prorates_its_immediate_expensing_limit_by_the_days(days: int, limit: str) -> None:
    statement = statement_fish("0", days)

    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION).value == D("1500000")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT).value == D(limit)
