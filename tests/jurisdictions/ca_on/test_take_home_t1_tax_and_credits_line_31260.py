"""T1 General 2025 (5006-R, Ontario) Step 5 Part B line 31260 "Canada employment amount", from the
salary and the optional line 10400 input.

Line 31260 is "Line 92 and line 31260: Canada employment amount: Enter whichever is less: $1,471 or
line 1 plus line 2." (T1 General 5006-R, CRA 5006-R-25E, confirmed in
docs/cra-forms-2025/5006-r-25e.txt, line 538). Line 1 is line 10100 employment income and line 2 is
line 10400 other employment income. The General Guide 5000-G (docs/cra-forms-2025/5000-g-25e.txt,
line 2874) gives the cook example: "if you are a cook who received $35,000 in employment income in
2025 that you reported on line 10100 of your return, you can claim $1,471 (the maximum amount) on
line 31260 of your return."

The line is two steps. The first is a `core/sum` of `ca/employment_income` and
`ca/other_employment_income` into `ca/canada_employment_amount_income`, rounded to the cent. The
second is a `core/capped_amount` over the 2025 dataset `ca/canada_employment_amount` ($1,471,
half-up to the cent), which produces `ca/canada_employment_amount`. The line 10400 input is optional
and reads as 0 when the caller gives none, so a salary-only request is the salary.

The test's form declaration is test-local: it exports `ca/canada_employment_amount` as its one
export. The caller gives the salary, and in some tests an other-employment-income amount as well.
Nothing else is an input of this line, so the parts are the salary, the real line 10400 input and
the part under test.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME, OTHER_EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
INCOME_SUM = "ca/canada_employment_amount_income"
CAP = "ca/canada_employment_amount"
# The real parts composed beside the test's header: the salary, the real optional line 10400 input,
# and the part under test.
PARTS = (
    "salary.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "t1_tax_and_credits_line_31260.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 31260, the only line
# composed here.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {CAP}
    """)


def _sheet(take_home_service: TakeHomeService, *artifacts: Artifact[Any]) -> Worksheet:
    """The tax and credits sheet computed from `artifacts`: the salary, and any other input."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, *artifacts
    )
    (sheet,) = worksheets[FORM]
    return sheet


def _salary(salary: str) -> Artifact[Any]:
    return Artifact(EMPLOYMENT_INCOME, D(salary))


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # The General Guide's cook: 35,000 of employment income claims the whole $1,471.
        ("35000", "1471"),
        ("70000", "1471.00"),
        # Below the cap the income itself is the lesser: 1,000.00.
        ("1000", "1000.00"),
        # At the cap the income and the cap are equal, and above it the cap is the lesser.
        ("1471", "1471.00"),
        ("1472", "1471.00"),
    ],
)
def test_line_31260_is_the_lesser_of_1471_and_the_income(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, _salary(salary))

    assert sheet.get(bundled_kinds().kind(CAP)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("70000", "70000.00"),
        # A salary-only request leaves the optional line 10400 blank, which counts as 0, so the
        # sum is the salary alone.
        ("1000", "1000.00"),
    ],
)
def test_line_31260_income_is_the_salary_when_line_10400_is_blank(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, _salary(salary))

    assert sheet.get(bundled_kinds().kind(INCOME_SUM)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "other", "income", "expected"),
    [
        # Line 1 plus line 2 is 1,300.00, below the cap, so the cap line is the sum itself.
        ("1000", "300", "1300.00", "1300.00"),
        # Line 1 plus line 2 is 1,700.00, above the cap, so the cap line is 1,471.00.
        ("1400", "300", "1700.00", "1471.00"),
    ],
)
def test_other_employment_income_adds_to_the_salary_before_the_cap(
    take_home_service: TakeHomeService, salary: str, other: str, income: str, expected: str
) -> None:
    sheet = _sheet(
        take_home_service,
        _salary(salary),
        Artifact(OTHER_EMPLOYMENT_INCOME, D(other)),
    )

    assert sheet.get(bundled_kinds().kind(INCOME_SUM)).value == D(income)
    assert sheet.get(bundled_kinds().kind(CAP)).value == D(expected)


@pytest.mark.parametrize("kind_identifier", [INCOME_SUM, CAP])
def test_the_line_31260_kinds_are_registered_and_non_negative(kind_identifier: str) -> None:
    # Non-negative: both are amounts of dollars the form takes as a line 1 plus line 2 total or
    # its lesser, never a negative figure.
    kind = bundled_kinds().kind(kind_identifier)

    assert kind.identifier == kind_identifier
    assert non_negative(kind) is True


def test_line_31260_names_the_income_and_the_cap_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, _salary("70000"))
    kinds = bundled_kinds()

    assert (
        f"{kinds.kind(CAP).label}: lesser of {kinds.kind(INCOME_SUM).label} 70000.00 and 1471 "
        "(half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)
