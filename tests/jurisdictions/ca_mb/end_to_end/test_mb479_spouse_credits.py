"""MB479 (2025) lines 9 to 12, the spouse or common-law partner credits, through the real engine.

Form text (Form MB479, CRA 5007-TC, 5007-tc-25e.txt): line 9 "Basic credit for spouse or common-law
partner Claim $195", line 10 "Age credit for spouse or common-law partner (if they were born in 1960
or earlier) Claim $113", line 11 "Disability credit for spouse or common-law partner Claim $113",
line 12 "Add lines 9 to 11.", then line 17 "Add lines 7, 8, and 12 to 16. Total credits". Lines 9
to 11 are the caller's optional inputs (blank when left out); line 12 and the total are computed.

The hand figures are asserted (not a CRA example): line 7 is 195.00, so lines 9 and 11 claimed give
195 + 113 = 308.00 on line 12 and 195 + 308 = 503.00 on line 17.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.jurisdictions.ca_mb.catalog as mb
from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

D = Decimal
MANITOBA = JurisdictionCode("CA-MB")


def _mb479(salary: str, **given: str) -> Worksheet:
    inputs = {
        "line_9": mb.MB479_BASIC_CREDIT_SPOUSE_LINE_9,
        "line_10": mb.MB479_AGE_CREDIT_SPOUSE_LINE_10,
        "line_11": mb.MB479_DISABILITY_CREDIT_SPOUSE_LINE_11,
    }
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(inputs[name], D(value)) for name, value in given.items()]
    (sheet,) = build_tax_computation().compute(MANITOBA, 2025, *artifacts)["ca-mb/mb479"]
    return sheet


def _value(sheet: Worksheet, kind: AmountKind) -> Decimal:
    value = sheet.get(kind).value
    assert isinstance(value, Decimal)
    return value


def test_a_salary_only_caller_has_no_spouse_credits() -> None:
    sheet = _mb479("70000")

    assert _value(sheet, mb.MB479_SPOUSE_CREDITS_LINE_12) == D("0.00")
    assert _value(sheet, mb.MB479_TOTAL_CREDITS_LINE_17) == D("195.00")


def test_line_12_adds_lines_9_to_11() -> None:
    sheet = _mb479("70000", line_9="195", line_10="113", line_11="113")

    assert _value(sheet, mb.MB479_SPOUSE_CREDITS_LINE_12) == D("421.00")
    # Line 17: 195.00 + 421.00.
    assert _value(sheet, mb.MB479_TOTAL_CREDITS_LINE_17) == D("616.00")


def test_lines_9_and_11_alone_give_308() -> None:
    sheet = _mb479("70000", line_9="195", line_11="113")

    assert _value(sheet, mb.MB479_SPOUSE_CREDITS_LINE_12) == D("308.00")
    assert _value(sheet, mb.MB479_TOTAL_CREDITS_LINE_17) == D("503.00")
