"""The New Brunswick return exports the two rates and the NB428 form exports the lines it reads.

Through the registered engine (`build_tax_computation().compute`, as the line tests read the
return): the return summary holds the average and the marginal income tax rate, and the NB428 form
holds line 5 "Rate", line 83 "Line 81 minus line 82 (if negative, enter "0")", line 86 (the
low-income tax reduction) and line 97 "Line 95 minus line 96 (if negative, enter "0")". The 2025
manifest serves 2026, so the return summary and line 5 checks run for both years; lines 83, 86 and
97 are pinned for 2025. The export lists themselves are pinned in
`test_manifest_header.py` and `test_form_nb428.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
NEW_BRUNSWICK = JurisdictionCode("CA-NB")


def _sheet(year: int, salary: str, form: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(
    "name",
    [
        "ca/refund_or_balance_owing",
        "ca-nb/average_tax_rate",
        "ca-nb/marginal_tax_rate",
    ],
)
def test_the_return_summary_holds_each_of_its_three_outputs(year: int, name: str) -> None:
    sheet = _sheet(year, "70000", "ca-nb/return")

    assert isinstance(_value(sheet, name), Decimal)


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(
    ("salary", "line_5"),
    [("20000", "0.094"), ("70000", "0.14"), ("250000", "0.195")],
)
def test_the_nb428_form_exports_the_line_5_rate(year: int, salary: str, line_5: str) -> None:
    # Line 5 prints the rate of the column line 1 falls in: 9.4%, 14%, 16% or 19.5%.
    sheet = _sheet(year, salary, "ca-nb/nb428")

    assert _value(sheet, "ca-nb/nb428_bracket_rate_line_5") == D(line_5)


@pytest.mark.parametrize(
    ("salary", "line_83", "line_86", "line_97"),
    [
        ("20000", "0.00", "802.00", "0.00"),
        ("28000", "5835.00", "626.95", "565.63"),
        ("70000", "47415.00", "0.00", "5676.89"),
    ],
)
def test_the_nb428_form_exports_lines_83_86_and_97(
    salary: str, line_83: str, line_86: str, line_97: str
) -> None:
    sheet = _sheet(2025, salary, "ca-nb/nb428")

    assert _value(sheet, "ca-nb/nb428_line_83") == D(line_83)
    assert _value(sheet, "ca-nb/nb428_line_86") == D(line_86)
    assert _value(sheet, "ca-nb/nb428_new_brunswick_tax_line_97") == D(line_97)
