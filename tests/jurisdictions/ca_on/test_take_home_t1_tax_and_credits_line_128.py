"""T1 General 2025 (5006-R, Ontario) line 128 "Line 126 plus line 127 =", from the salary alone.

Line 128 is "Line 126 plus line 127 =" (T1 General 5006-R, CRA 5006-R-25E, confirmed in
docs/cra-forms-2025/5006-r-25e.txt). Line 126 is line 42900 (`ca/federal_tax_after_credits`). Line
127 (the federal surtax) is absent for an Ontario resident, so it is left out and not wired. Line
128 is therefore one `core/sum` over line 42900 only, rounded half-up to the cent with the shared
`ca/cent_rounding` dataset, and produces `ca/federal_tax_with_surtax`, a signed kind (not
non-negative).

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106, 33500,
33800, 35000, 76, 40400, 125 and 42900 and the part under test. The form declaration of line 128 is
test-local: its one export is line 128.

The salary is the only input the caller gives. Ontario resident, single filer, salary the only
income, tax withheld 0, basic credits only, as the take-home calculator states them.
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
LINE_42900 = "ca/federal_tax_after_credits"
LINE_128 = "ca/federal_tax_with_surtax"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 84, 31260, 96, 98, 101, 106,
# 33500, 33800, 35000, 40400, 125 and 42900, and the part under test.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 128, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_128}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 42900 and 128 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 42900 alone, line 127 being absent.
        ("70000", "7585.64"),
        # $20,000: line 42900 alone.
        ("20000", "158.09"),
        # $200,000: line 42900 alone.
        ("200000", "39467.74"),
        # $10,000: line 42900 is 0, so the line is 0.
        ("10000", "0.00"),
    ],
)
def test_line_128_is_line_42900(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_128 = sheet.get(kinds.kind(LINE_128)).value
    assert line_128 == D(expected)
    assert line_128 == sheet.get(kinds.kind(LINE_42900)).value
    assert line_128.as_tuple().exponent == -2


def test_line_128_names_line_42900_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    kinds = bundled_kinds()
    output = kinds.kind(LINE_128)
    line_42900 = kinds.kind(LINE_42900)

    assert (
        f"{output.label}: {line_42900.label} 7585.64 = 7585.64 (half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)


def test_the_line_128_kind_is_registered_and_signed() -> None:
    kind = bundled_kinds().kind(LINE_128)

    assert kind.identifier == LINE_128
    assert non_negative(kind) is False
