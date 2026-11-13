"""T1 General 2025 (5006-R, Ontario) line 138 / line 41600 "Credits against federal tax", from the
salary alone.

Line 41600 is "Add lines 135 to 137" (T1 General 5006-R, CRA 5006-R-25E, to be confirmed against the
file); the parts are line 41000 (political contribution
credit), line 41200 (investment tax credit) and line 41400 (labour-sponsored funds credit). The
take-home filer has none of the three (basic credits only), so by ruling R2 the sum has no parts and
gives 0. It is built, as a `core/sum` over an empty list of parts, because line 41700 subtracts it
and both operands must exist (R2b, R3). It reads nothing and takes no dataset beyond the shared cent
rounding.

The only part composed beside the test's header is the salary, which gives the output header its
input. The form header of line 41600 is test-local: it declares `ca/credits_against_federal_tax` as
its one export.

Ontario resident, single filer, salary the only income, tax withheld 0, basic credits only, as the
take-home calculator states them. The figure is 0.00 at any salary.
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
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE_41600 = "ca/credits_against_federal_tax"
# The salary gives the output header its input; line 41600 reads nothing.
PARTS = ("salary.yaml", "t1_tax_and_credits_line_41600.yaml")
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 41600, the only line
# composed here.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_41600}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_41600_is_zero_at_any_salary(take_home_service: TakeHomeService, salary: str) -> None:
    line_41600 = _sheet(take_home_service, salary).get(bundled_kinds().kind(LINE_41600)).value

    assert line_41600 == D("0.00")
    # The cent zero of the rounding dataset, not a bare 0.
    assert line_41600.as_tuple().exponent == -2
    assert not line_41600.is_signed()


def test_the_trace_shows_a_sum_with_no_parts(take_home_service: TakeHomeService) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert "Nothing to add, so 0.00." in EnglishTraceRenderer().render_all(sheet.trace)


def test_the_line_41600_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_41600)

    assert kind.identifier == LINE_41600
    assert non_negative(kind) is True
