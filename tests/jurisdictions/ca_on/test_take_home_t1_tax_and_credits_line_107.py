"""T1 General 2025 (5006-R, Ontario) line 107 and line 33099 "Medical expenses for self, spouse or
common-law partner and your dependent children under 18 years of age",
from the salary alone.

Line 107 is a copy of line 33099, which the T1 lines copied by provinces form owns as an optional
input (0 when blank) and exports as a record list, so the part is one `core/record_total` over
that list and produces `ca/medical_expenses_line_107`, a non-negative kind.

The real parts are composed beside a test-local header: the salary, the real T1 lines copied by
provinces form (the optional medical expenses input), the real Schedule 8 and T2204 parts, the real
T1 taxable-income lines and inputs,
and the part under test. The form declaration is test-local: its one export is line 107.

The salary is the only input the caller gives, except the medical expenses where a test gives them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import MEDICAL_EXPENSES
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE = "ca/medical_expenses_line_107"
# The real parts composed beside the test's header, and the part under test.
PARTS = (
    "salary.yaml",
    *form_part_names("t1_lines_copied_by_provinces"),
    *form_part_names("schedule_8"),
    *form_part_names("t2204"),
    *form_part_names("t1_taxable_income", "t1_employment_income"),
    "t1_tax_and_credits_line_107.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str, medical: str | None) -> Worksheet:
    """The tax and credits sheet for `salary`, with the medical expenses when given."""
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if medical is not None:
        artifacts.append(Artifact(MEDICAL_EXPENSES, D(medical)))
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, *artifacts
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "medical", "expected"),
    [
        ("70000", None, "0.00"),
        ("70000", "5000", "5000.00"),
    ],
)
def test_line_107_figures(
    take_home_service: TakeHomeService, salary: str, medical: str | None, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary, medical)

    value = sheet.get(bundled_kinds().kind(LINE)).value
    assert value == D(expected)
    assert value.as_tuple().exponent == -2


def test_the_line_107_step_is_in_the_trace(take_home_service: TakeHomeService) -> None:
    sheet = _sheet(take_home_service, "70000", "5000")

    assert (
        "Line 33099 of T1 Income Tax and Benefit Return (CA$5000.00) gives CA$5000.00."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_107_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE)

    assert kind.identifier == LINE
    assert non_negative(kind) is True
