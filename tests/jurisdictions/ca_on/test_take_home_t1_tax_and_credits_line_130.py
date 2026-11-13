"""T1 General 2025 (5006-R, Ontario) line 130 "Line 128 minus line 129 =", from the salary alone.

Line 130 is "Line 128 minus line 129" (T1 General 5006-R, CRA 5006-R-25E, confirmed). Line 128 is
`ca/federal_tax_with_surtax`; line 129 is line
40500, the federal foreign tax credit (`ca/federal_foreign_tax_credit`, Form T2209). The line
prints no "(if negative, enter 0)", so it is one `core/subtract` with no floor, rounded half-up to
the cent with the shared `ca/cent_rounding` dataset, and produces
`ca/federal_tax_less_foreign_tax_credit`, a signed kind (not non-negative).

Line 129 is an optional input with blank fallback 0, declared by the part's own inputs file: a
salary-only caller has no foreign tax credit, so a request that leaves it out gets line 128
unchanged. A caller who gives a credit has it subtracted, and the result may go negative.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106, 33500,
33800, 35000, 76, 40400, 125, 42900 and 128 and the part under test with its inputs. The form
declaration of line 130 is test-local: its one export is line 130.

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
LINE_42900 = "ca/federal_tax_after_credits"
LINE_128 = "ca/federal_tax_with_surtax"
LINE_129 = "ca/federal_foreign_tax_credit"
LINE_130 = "ca/federal_tax_less_foreign_tax_credit"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 31260, 84, 96, 98, 101, 106,
# 33500, 33800, 35000, 125, 40400, 42900 and 128, and the part under test with its inputs.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 130, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_130}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str, credit: str | None = None) -> Worksheet:
    """The tax and credits sheet, with lines 128 and 130 on it; the credit is left out if None."""
    kinds = bundled_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if credit is not None:
        given.append(Artifact(kinds.kind(LINE_129), D(credit)))
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, *given
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 128 alone, line 129 being blank.
        ("70000", "7585.64"),
        # $20,000: line 128 alone.
        ("20000", "158.09"),
        # $200,000: line 128 alone.
        ("200000", "39467.74"),
        # $10,000: line 128 is 0, so the line is 0.
        ("10000", "0.00"),
    ],
)
def test_line_130_is_line_128_when_line_129_is_blank(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_130 = sheet.get(kinds.kind(LINE_130)).value
    assert line_130 == D(expected)
    assert line_130 == sheet.get(kinds.kind(LINE_128)).value
    assert line_130.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("salary", "credit", "expected"),
    [
        # $70,000: 7,585.64 less 1,000.00.
        ("70000", "1000", "6585.64"),
        # $20,000: 158.09 less 200.00 is negative and is not floored (signed).
        ("20000", "200", "-41.91"),
        # Exactly equal: the difference is zero.
        ("20000", "158.09", "0.00"),
    ],
)
def test_line_130_subtracts_the_given_line_129(
    take_home_service: TakeHomeService, salary: str, credit: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary, credit)

    line_130 = sheet.get(bundled_kinds().kind(LINE_130)).value
    assert line_130 == D(expected)
    assert line_130.as_tuple().exponent == -2


def test_line_130_names_line_128_line_129_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000", "1000.00")
    assert (
        "Line 128 (CA$7585.64) less line 40500 (CA$1000.00) gives CA$6585.64 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_130_kind_is_registered_and_signed() -> None:
    kind = bundled_kinds().kind(LINE_130)

    assert kind.identifier == LINE_130
    assert non_negative(kind) is False
