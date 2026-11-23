"""MB428 (2025) lines 54 to 56, the donations and gifts block, through the real engine.

Form text (Form MB428, CRA 5007-c-25e.txt): line 54 "Amount from line 13 of your federal Schedule 9
multiplied by 10.8% =", line 55 "Amount from line 14 of your federal Schedule 9 multiplied by 17.4%
=" and line 56 "Line 54 plus line 55 =". Schedule 9 line 12 is the caller's optional input
(lines 13 and 14 are computed from it); lines 54 to 56 are computed.

The hand figures are asserted (not a CRA example). Line 53 at a $70,000 salary is 2,176.12, and line
57 is line 53 plus line 56.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.jurisdictions.ca_mb.catalog as mb
from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import DONATIONS_AND_GIFTS_LINE_12
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

D = Decimal
MANITOBA = JurisdictionCode("CA-MB")


def _credits(salary: str, **given: str) -> Worksheet:
    inputs = {
        "line_12": DONATIONS_AND_GIFTS_LINE_12,
    }
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(inputs[name], D(value)) for name, value in given.items()]
    (sheet,) = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, 2025, tuple(artifacts))
    )["ca-mb/mb428_credits"]
    return sheet


def _value(sheet: Worksheet, kind: AmountKind) -> Decimal:
    value = sheet.get(kind).value
    assert isinstance(value, Decimal)
    return value


def test_a_salary_only_caller_has_no_donations_claim() -> None:
    sheet = _credits("70000")

    assert _value(sheet, mb.MB428_DONATIONS_CREDIT_AT_RATE_LINE_54) == D("0.00")
    assert _value(sheet, mb.MB428_DONATIONS_CREDIT_AT_RATE_LINE_55) == D("0.00")
    assert _value(sheet, mb.MB428_DONATIONS_CREDIT_LINE_56) == D("0.00")
    assert _value(sheet, mb.MB428_NON_REFUNDABLE_CREDITS_LINE_57) == D("2176.12")


def test_each_schedule_9_amount_is_at_its_own_rate() -> None:
    sheet = _credits("70000", line_12="1200")

    assert _value(sheet, mb.MB428_DONATIONS_CREDIT_AT_RATE_LINE_54) == D("21.60")
    assert _value(sheet, mb.MB428_DONATIONS_CREDIT_AT_RATE_LINE_55) == D("174.00")
    assert _value(sheet, mb.MB428_DONATIONS_CREDIT_LINE_56) == D("195.60")
    # Line 57 is line 53 (2,176.12) plus line 56.
    assert _value(sheet, mb.MB428_NON_REFUNDABLE_CREDITS_LINE_57) == D("2371.72")


def test_a_half_cent_rounds_up() -> None:
    sheet = _credits("70000", line_12="0.05")

    assert _value(sheet, mb.MB428_DONATIONS_CREDIT_AT_RATE_LINE_54) == D("0.01")
