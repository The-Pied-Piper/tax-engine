"""The Alberta return exports the two rates and the forms export the lines it reads, both years.

Through the public service API (`build_tax_computation().compute`, as the Alberta line tests read
the return): the return summary holds the average and the marginal income tax rate, the AB428
credits form holds the line 5 and line 12 rates it exports, and the AB428 tax form holds line 68.
The 2025 manifest serves 2026 (a dataset with only one year is fatal for the other), so every check
runs for both years. The export lists themselves are pinned in `test_manifest_header.py`,
`test_ab428_credits_form.py` and `test_form_ab428.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
ALBERTA = JurisdictionCode("CA-AB")


def _sheet(year: int, salary: str, form: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        ALBERTA, year, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[form]
    return sheet


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(
    "name",
    [
        "ca/refund_or_balance_owing",
        "ca-ab/average_income_tax_rate",
        "ca-ab/marginal_tax_rate",
    ],
)
def test_the_return_summary_holds_each_of_its_three_outputs(year: int, name: str) -> None:
    sheet = _sheet(year, "70000", "ca-ab/return")

    assert isinstance(sheet.get(bundled_kinds().kind(name)).value, Decimal)


@pytest.mark.parametrize(
    ("year", "salary", "line_5", "line_12"),
    [
        (2025, "70000", "0.10", None),
        (2025, "200000", None, "0.13"),
        (2026, "70000", "0.10", None),
        (2026, "200000", None, "0.13"),
    ],
)
def test_the_ab428_credits_form_exports_the_line_5_and_line_12_rates(
    year: int, salary: str, line_5: str | None, line_12: str | None
) -> None:
    # Line 5 is the rate of table 1 (taxable income up to 181,481) and line 12 of table 2 (above
    # it); the one that does not apply is blank, which the sheet may hold as nothing or as 0.
    sheet = _sheet(year, salary, "ca-ab/ab428_credits")
    kinds = bundled_kinds()

    for name, expected in (
        ("ca-ab/ab428_bracket_rate_line_5", line_5),
        ("ca-ab/ab428_bracket_rate_line_12", line_12),
    ):
        if expected is not None:
            assert sheet.get(kinds.kind(name)).value == D(expected)


@pytest.mark.parametrize(
    ("year", "salary", "line_68"),
    [
        (2025, "20000", "0.00"),
        (2025, "70000", "3598.12"),
        (2026, "20000", "0.00"),
        (2026, "70000", "3534.79"),
    ],
)
def test_the_ab428_form_exports_line_68(year: int, salary: str, line_68: str) -> None:
    sheet = _sheet(year, salary, "ca-ab/ab428")

    assert sheet.get(bundled_kinds().kind("ca-ab/ab428_tax_line_68")).value == D(line_68)
