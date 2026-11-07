"""T1 General 2025 (5006-R, Ontario) line 126 (42900) "Basic federal tax", from the salary alone.

Line 126 is "Line 121 minus line 125 (if negative, enter "0")" (T1 General 5006-R, CRA 5006-R-25E,
confirmed in docs/cra-forms-2025/5006-r-25e.txt). Line 121 is line 40400
(`ca/federal_tax_with_split_income`) and line 125 is `ca/credits_against_basic_federal_tax`. Line
42900 is one `core/subtract_not_below_zero`, rounded half-up to the cent with the shared
`ca/cent_rounding` dataset, and produces `ca/federal_tax_after_credits`, a non-negative kind.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106, 33500,
33800, 35000, 76, 40400 and 125 and the part under test. The form declaration of line 42900 is
test-local: its one export is line 42900.

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
LINE_40400 = "ca/federal_tax_with_split_income"
LINE_125 = "ca/credits_against_basic_federal_tax"
LINE_42900 = "ca/federal_tax_after_credits"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 84, 31260, 96, 98, 101, 106,
# 33500, 33800, 35000, 40400 and 125, and the part under test.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 42900, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_42900}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 40400, 125 and 42900 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "line_40400", "line_125", "expected"),
    [
        # $70,000: 10,771.18 less 3,185.54.
        ("70000", "10771.18", "3185.54", "7585.64"),
        # $20,000: 2,876.08 less 2,717.99.
        ("20000", "2876.08", "2717.99", "158.09"),
        # $200,000: 42,598.33 less 3,130.59.
        ("200000", "42598.33", "3130.59", "39467.74"),
        # $10,000: the credits exceed the tax, so the line is 0.
        ("10000", None, None, "0.00"),
    ],
)
def test_line_42900_is_line_40400_less_line_125(
    take_home_service: TakeHomeService,
    salary: str,
    line_40400: str | None,
    line_125: str | None,
    expected: str,
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_42900 = sheet.get(kinds.kind(LINE_42900)).value
    assert line_42900 == D(expected)
    assert line_42900.as_tuple().exponent == -2
    if line_40400 is not None and line_125 is not None:
        assert sheet.get(kinds.kind(LINE_40400)).value == D(line_40400)
        assert sheet.get(kinds.kind(LINE_125)).value == D(line_125)


def test_line_42900_is_never_below_zero(take_home_service: TakeHomeService) -> None:
    sheet = _sheet(take_home_service, "10000")
    kinds = bundled_kinds()

    assert sheet.get(kinds.kind(LINE_125)).value > sheet.get(kinds.kind(LINE_40400)).value
    assert sheet.get(kinds.kind(LINE_42900)).value == D("0.00")


def test_line_42900_names_its_two_lines_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")
    kinds = bundled_kinds()
    output = kinds.kind(LINE_42900)
    line_40400 = kinds.kind(LINE_40400)
    line_125 = kinds.kind(LINE_125)

    assert (
        f"{output.label}: {line_40400.label} 10771.18 less {line_125.label} 3185.54, "
        "not below 0 = 7585.64 (half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)


def test_the_line_42900_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_42900)

    assert kind.identifier == LINE_42900
    assert non_negative(kind) is True
