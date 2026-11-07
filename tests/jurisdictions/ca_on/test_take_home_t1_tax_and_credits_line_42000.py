"""T1 General 2025 (5006-R, Ontario) line 142 / line 42000 "Net federal tax", from the
salary alone.

Line 42000 is "Line 142 and line 42000: Add lines 139 to 141. Net federal tax" (T1 General
5006-R, CRA 5006-R-25E, confirmed in docs/cra-forms-2025/5006-r-25e.txt). Line 139 is
`ca/federal_tax_less_credits` (line 41700, same form). Lines 140 (41500) and 141 (41800) are absent
for the take-home filer and are left out, so line 42000 is one `core/sum` over line 139 only,
rounded half-up to the cent with the shared `ca/cent_rounding` dataset, and produces
`ca/net_federal_tax`, a non-negative kind. It equals line 41700 at any salary.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106, 33500,
33800, 35000, 76, 40400, 125, 42900, 128, 130 and 132, lines 40600, 41600 and 41700 with the input
of line 40600, and the part under test. The form declaration of line 42000 is test-local: its one
export is line 42000.

The salary is the only required input. Ontario resident, single filer, salary the only income, tax
withheld 0, basic credits only, as the take-home calculator states them.
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
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE_139 = "ca/federal_tax_less_credits"
LINE_142 = "ca/net_federal_tax"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 84, 31260, 96, 98, 101, 106,
# 33500, 33800, 35000, 40400, 125, 42900, 128, 130 and 132, lines 40600 and 41600 with the input of
# line 40600, line 41700 and the part under test.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t2204*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "t1_tax_and_credits_line_30000.yaml",
    "t1_tax_and_credits_line_76.yaml",
    "t1_tax_and_credits_line_31260.yaml",
    "t1_tax_and_credits_line_84.yaml",
    "t1_tax_and_credits_line_96.yaml",
    "t1_tax_and_credits_line_98.yaml",
    "t1_tax_and_credits_line_101.yaml",
    "t1_tax_and_credits_line_106.yaml",
    "t1_tax_and_credits_line_33500.yaml",
    "t1_tax_and_credits_line_33800.yaml",
    "t1_tax_and_credits_line_35000.yaml",
    "t1_tax_and_credits_line_125.yaml",
    "t1_tax_and_credits_line_40400.yaml",
    "t1_tax_and_credits_line_42900.yaml",
    "t1_tax_and_credits_line_128.yaml",
    "t1_tax_and_credits_line_40500_inputs.yaml",
    "t1_tax_and_credits_line_130.yaml",
    "t1_tax_and_credits_line_132.yaml",
    "t1_tax_and_credits_line_40600_inputs.yaml",
    "t1_tax_and_credits_line_40600.yaml",
    "t1_tax_and_credits_line_41600.yaml",
    "t1_tax_and_credits_line_41700.yaml",
    "t1_tax_and_credits_line_42000.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 42000, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_142}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 139 and 142 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 139 is 7,585.64.
        ("70000", "7585.64"),
        # $20,000: line 139 is 158.09.
        ("20000", "158.09"),
        # $200,000: line 139 is 39,467.74.
        ("200000", "39467.74"),
        # $10,000: line 139 is 0, so the line is 0.
        ("10000", "0.00"),
    ],
)
def test_line_42000_is_line_139_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_142 = sheet.get(kinds.kind(LINE_142)).value
    assert line_142 == D(expected)
    assert line_142 == sheet.get(kinds.kind(LINE_139)).value
    assert line_142.as_tuple().exponent == -2


def test_line_42000_names_line_139_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    kinds = bundled_kinds()
    output = kinds.kind(LINE_142)
    line_139 = kinds.kind(LINE_139)

    assert (
        f"{output.label}: {line_139.label} 7585.64 = 7585.64 (half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)


def test_the_42000_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_142)

    assert kind.identifier == LINE_142
    assert non_negative(kind) is True
