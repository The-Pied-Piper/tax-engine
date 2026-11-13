"""T1 General 2025 (5006-R, Ontario) line 132 "Line 130 plus line 131", from the salary alone.

Line 132 is "Line 130 plus line 131" (T1 General 5006-R, CRA 5006-R-25E, confirmed). Line 130 is
`ca/federal_tax_less_foreign_tax_credit`. Line
131 (the recapture of investment tax credit, Form T2038(IND)) is absent for a take-home filer, so
it is left out and not wired. Line 132 is therefore one `core/sum` over line 130 only, rounded
half-up to the cent with the shared `ca/cent_rounding` dataset, and produces
`ca/federal_tax_with_itc_recapture`, a signed kind (not non-negative).

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106, 33500,
33800, 35000, 76, 40400, 125, 42900, 128 and 130 and the part under test with its inputs. The form
declaration of line 132 is test-local: its one export is line 132.

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
LINE_128 = "ca/federal_tax_with_surtax"
LINE_130 = "ca/federal_tax_less_foreign_tax_credit"
LINE_132 = "ca/federal_tax_with_itc_recapture"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 31260, 84, 96, 98, 101, 106,
# 33500, 33800, 35000, 125, 40400, 42900 and 128, the line 130 inputs, line 130, and the part under
# test.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 132, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_132}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 130 and 132 on it."""
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 130 alone, line 131 being absent.
        ("70000", "7585.64"),
        # $20,000: line 130 alone.
        ("20000", "158.09"),
        # $200,000: line 130 alone.
        ("200000", "39467.74"),
        # $10,000: line 130 is 0, so the line is 0.
        ("10000", "0.00"),
    ],
)
def test_line_132_is_line_130(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_132 = sheet.get(kinds.kind(LINE_132)).value
    assert line_132 == D(expected)
    assert line_132 == sheet.get(kinds.kind(LINE_130)).value
    assert line_132.as_tuple().exponent == -2


def test_line_132_names_line_130_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "Line 130 (CA$7585.64) gives CA$7585.64 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_132_kind_is_registered_and_signed() -> None:
    kind = bundled_kinds().kind(LINE_132)

    assert kind.identifier == LINE_132
    assert non_negative(kind) is False
