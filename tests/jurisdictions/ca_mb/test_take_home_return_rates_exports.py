"""The Manitoba return exports the two rates and the forms export the lines it reads (2025).

Through the registered engine (`build_tax_computation().compute`, as the line tests read the
return): the return summary holds the average and the marginal income tax rate, the MB428 credits
form holds the line 5 rate, the MB428 form line 65 and Worksheet MB428 lines 5, 7, 8 and 9 it
exports. The export lists themselves are pinned in `test_manifest_header.py`,
`test_form_mb428_credits.py`, `test_form_mb428.py` and `test_worksheet_mb428_form.py`.
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
MANITOBA = JurisdictionCode("CA-MB")


def _sheet(salary: str, form: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        MANITOBA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
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
        "ca-mb/average_income_tax_rate",
        "ca-mb/marginal_tax_rate",
    ],
)
def test_the_return_summary_holds_each_of_its_three_outputs(name: str) -> None:
    sheet = _sheet("70000", "ca-mb/return")

    assert isinstance(_value(sheet, name), Decimal)


@pytest.mark.parametrize(
    ("salary", "line_5"),
    [("0", "0.108"), ("200000", "0.174")],
)
def test_the_mb428_credits_form_exports_the_line_5_rate(salary: str, line_5: str) -> None:
    # Line 5 is the rate of the column line 1 is in (10.8% to 47,000, 12.75% to 100,000, 17.4%
    # above); the form fills one column, so the line is never blank.
    sheet = _sheet(salary, "ca-mb/mb428_credits")

    assert _value(sheet, "ca-mb/mb428_bracket_rate_line_5") == D(line_5)


@pytest.mark.parametrize(
    ("salary", "line_65"),
    [("10000", "0.00"), ("70000", "5747.59")],
)
def test_the_mb428_form_exports_line_65(salary: str, line_65: str) -> None:
    sheet = _sheet(salary, "ca-mb/mb428")

    assert _value(sheet, "ca-mb/mb428_tax_after_credits_line_65") == D(line_65)


@pytest.mark.parametrize(
    ("salary", "line_8", "line_9"),
    [
        ("70000", "0.00", "15780.00"),
        ("250000", "3860.26", "11919.74"),
    ],
)
def test_the_worksheet_exports_lines_5_7_8_and_9(salary: str, line_8: str, line_9: str) -> None:
    sheet = _sheet(salary, "ca-mb/worksheet_mb428")

    assert _value(sheet, "ca-mb/worksheet_mb428_basic_personal_amount_line_5") == D("200000.00")
    assert _value(sheet, "ca-mb/worksheet_mb428_basic_personal_amount_line_7") == D("15780.00")
    assert _value(sheet, "ca-mb/worksheet_mb428_line_8") == D(line_8)
    assert _value(sheet, "ca-mb/worksheet_mb428_basic_personal_amount_line_9") == D(line_9)
