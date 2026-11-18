"""The Saskatchewan return exports the two rates and the forms export the lines it reads (2025).

Through the registered engine (`build_tax_computation().compute`, as the line tests read the
return): the return summary holds the average and the marginal income tax rate, the SK428 credits
form holds the line 5 rate, and the SK428 form holds line 67 "Line 62 minus line 66 (if negative,
enter "0")". The export lists themselves are pinned in `test_manifest_header.py`,
`test_form_sk428_credits.py` and `test_form_sk428.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
SASKATCHEWAN = JurisdictionCode("CA-SK")


def _sheet(salary: str, form: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        SASKATCHEWAN, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


@pytest.mark.parametrize(
    "name",
    [
        "ca/refund_or_balance_owing",
        "ca-sk/average_income_tax_rate",
        "ca-sk/marginal_tax_rate",
    ],
)
def test_the_return_summary_holds_each_of_its_three_outputs(name: str) -> None:
    sheet = _sheet("70000", "ca-sk/return")

    assert isinstance(_value(sheet, name), Decimal)


@pytest.mark.parametrize(
    ("salary", "line_5"),
    [("20000", "0.105"), ("70000", "0.125"), ("200000", "0.145")],
)
def test_the_sk428_credits_form_exports_the_line_5_rate(salary: str, line_5: str) -> None:
    # Line 5 prints the rate of the column line 1 falls in: 10.5% up to 53,463, 12.5% up to
    # 152,750 and 14.5% above it.
    sheet = _sheet(salary, "ca-sk/sk428_credits")

    assert _value(sheet, "ca-sk/sk428_bracket_rate_line_5") == D(line_5)


@pytest.mark.parametrize(
    ("salary", "line_67"),
    [("20000", "0.00"), ("70000", "5092.30"), ("200000", "22207.93")],
)
def test_the_sk428_form_exports_line_67(salary: str, line_67: str) -> None:
    # Nothing is subtracted after line 67 for a salary-only filer, so line 67 equals line 82.
    sheet = _sheet(salary, "ca-sk/sk428")

    assert _value(sheet, "ca-sk/sk428_tax_after_credits_line_67") == D(line_67)
