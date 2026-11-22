"""MB479 (2025) lines 14 to 16, the disability and dependant credits, through the real engine.

Form text (Form MB479, CRA 5007-TC, 5007-tc-25e.txt): line 14 "Number of disability claims ...
multiplied by $113 =", line 15 "Number of disabled dependants ... multiplied by $62 =" and line 16
"Number of dependent children ... multiplied by $26 =", then line 17 "Add lines 7, 8, and 12 to 16.
Total credits". The three numbers are the caller's optional inputs (0 when left out); the products
and the total are computed.

The hand figures are asserted (not a CRA example): line 7 is 195.00, so one claim, one disabled
dependant and one child give 195 + 113 + 62 + 26 = 396.00 on line 17.
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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

D = Decimal
MANITOBA = JurisdictionCode("CA-MB")


def _mb479(salary: str, **given: str) -> Worksheet:
    inputs = {
        "line_14": mb.MB479_DISABILITY_CLAIMS_NUMBER_LINE_14,
        "line_15": mb.MB479_DISABLED_DEPENDANTS_NUMBER_LINE_15,
        "line_16": mb.MB479_DEPENDENT_CHILDREN_NUMBER_LINE_16,
    }
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(inputs[name], D(value)) for name, value in given.items()]
    (sheet,) = build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, 2025, tuple(artifacts))
    )["ca-mb/mb479"]
    return sheet


def _value(sheet: Worksheet, kind: AmountKind) -> Decimal:
    value = sheet.get(kind).value
    assert isinstance(value, Decimal)
    return value


def test_a_salary_only_caller_has_no_credits_on_lines_14_to_16() -> None:
    sheet = _mb479("70000")

    assert _value(sheet, mb.MB479_DISABILITY_CREDIT_LINE_14) == D("0.00")
    assert _value(sheet, mb.MB479_DISABLED_DEPENDANTS_CREDIT_LINE_15) == D("0.00")
    assert _value(sheet, mb.MB479_DEPENDENT_CHILDREN_CREDIT_LINE_16) == D("0.00")
    assert _value(sheet, mb.MB479_TOTAL_CREDITS_LINE_17) == D("195.00")


def test_each_number_is_multiplied_by_its_printed_amount() -> None:
    sheet = _mb479("70000", line_14="2", line_15="3", line_16="4")

    assert _value(sheet, mb.MB479_DISABILITY_CREDIT_LINE_14) == D("226.00")
    assert _value(sheet, mb.MB479_DISABLED_DEPENDANTS_CREDIT_LINE_15) == D("186.00")
    assert _value(sheet, mb.MB479_DEPENDENT_CHILDREN_CREDIT_LINE_16) == D("104.00")
    # Line 17: 195.00 + 226.00 + 186.00 + 104.00.
    assert _value(sheet, mb.MB479_TOTAL_CREDITS_LINE_17) == D("711.00")


def test_one_of_each_gives_396() -> None:
    sheet = _mb479("70000", line_14="1", line_15="1", line_16="1")

    assert _value(sheet, mb.MB479_TOTAL_CREDITS_LINE_17) == D("396.00")
