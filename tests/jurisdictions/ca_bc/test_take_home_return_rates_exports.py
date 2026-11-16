"""The British Columbia return exports the two rates and the forms export the lines it reads, both
years.

Through the engine over the British Columbia package list (`british_columbia_service().compute`, as
the line tests read the return; British Columbia is not yet in `registrations.JURISDICTIONS`): the
return summary holds the average and the marginal income tax rate, and the BC428 form holds the
line 5 and line 12 rates, the line 78 reduction clawback, the line 79 tax reduction and line 80 it
exports. The 2025 manifest serves 2026 (a dataset with only one year is fatal for the other), so
every check runs for both years. The export lists themselves are pinned in `test_manifest_header.py`
and `test_form_bc428.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_bc.support import british_columbia_kinds, british_columbia_service

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")


def _sheet(year: int, salary: str, form: str) -> Worksheet:
    worksheets = british_columbia_service().compute(
        BRITISH_COLUMBIA, year, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Worksheet, name: str) -> Decimal:
    kind = british_columbia_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(
    "name",
    [
        "ca/refund_or_balance_owing",
        "ca-bc/average_income_tax_rate",
        "ca-bc/marginal_tax_rate",
    ],
)
def test_the_return_summary_holds_each_of_its_three_outputs(year: int, name: str) -> None:
    sheet = _sheet(year, "70000", "ca-bc/return")

    assert isinstance(_value(sheet, name), Decimal)


@pytest.mark.parametrize(
    ("year", "salary", "line_5", "line_12"),
    [
        (2025, "70000", "0.077", None),
        (2025, "200000", None, "0.168"),
        (2026, "70000", "0.077", None),
        (2026, "200000", None, "0.168"),
    ],
)
def test_the_bc428_form_exports_the_line_5_and_line_12_rates(
    year: int, salary: str, line_5: str | None, line_12: str | None
) -> None:
    # Line 5 is the rate of table 1 (taxable income up to 137,407) and line 12 of table 2 (above
    # it); the one that does not apply is blank, which the sheet may hold as nothing or as 0.
    sheet = _sheet(year, salary, "ca-bc/bc428")

    for name, expected in (
        ("ca-bc/bc428_bracket_rate_line_5", line_5),
        ("ca-bc/bc428_bracket_rate_line_12", line_12),
    ):
        if expected is not None:
            assert _value(sheet, name) == D(expected)


@pytest.mark.parametrize(
    ("year", "salary", "line_78", "line_79", "line_80"),
    [
        (2025, "20000", "0.00", "562.00", "0.00"),
        (2025, "30000", "167.85", "394.15", "364.81"),
        (2025, "70000", "1577.61", "0.00", "3162.39"),
    ],
)
def test_the_bc428_form_exports_lines_78_79_and_80(
    year: int, salary: str, line_78: str, line_79: str, line_80: str
) -> None:
    sheet = _sheet(year, salary, "ca-bc/bc428")

    assert _value(sheet, "ca-bc/bc428_reduction_clawback_line_78") == D(line_78)
    assert _value(sheet, "ca-bc/bc428_british_columbia_tax_reduction_line_79") == D(line_79)
    assert _value(sheet, "ca-bc/bc428_tax_after_reduction_line_80") == D(line_80)
