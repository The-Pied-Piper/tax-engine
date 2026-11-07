"""T1 General 2025 (5006-R, Ontario) line 134 (line 40600) "Federal tax", from the salary alone.

Line 134 is "Line 132 minus line 133 (if negative, enter "0") Federal tax =" (T1 General 5006-R, CRA
5006-R-25E, confirmed in docs/cra-forms-2025/5006-r-25e.txt). Line 132 is
`ca/federal_tax_with_itc_recapture`; line 133 is `ca/federal_logging_tax_credit` ("Line 133: Federal
logging tax credit"). The line prints "(if negative, enter "0")", so it is one
`core/subtract_not_below_zero`, rounded half-up to the cent with the shared `ca/cent_rounding`
dataset, and produces `ca/federal_tax`, a non-negative kind.

Line 133 is an optional input with blank fallback 0, declared by the part's own inputs file: a
salary-only caller has no logging tax credit, so a request that leaves it out gets line 132
unchanged (floored at 0). A caller who gives a credit has it subtracted, and the result is floored
at 0.

The real parts are composed beside a test-local header: the salary, the real Schedule 8 and T2204
parts, the real T1 taxable-income lines and inputs, lines 30000, 84, 31260, 96, 98, 101, 106, 33500,
33800, 35000, 76, 40400, 125, 42900, 128, 130 and 132 and the part under test with its inputs. The
form declaration of line 134 is test-local: its one export is line 134.

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
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE_132 = "ca/federal_tax_with_itc_recapture"
LINE_133 = "ca/federal_logging_tax_credit"
LINE_134 = "ca/federal_tax"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 84, 31260, 96, 98, 101, 106,
# 33500, 33800, 35000, 40400, 125, 42900, 128, 130 and 132, and the part under test with its inputs.
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
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 134, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_134}
    """)


def _sheet(
    take_home_service: TakeHomeService, salary: str, logging: str | None = None
) -> Worksheet:
    """The tax and credits sheet, with lines 132 and 134 on it; the logging credit is left out if
    None."""
    kinds = bundled_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if logging is not None:
        given.append(Artifact(kinds.kind(LINE_133), D(logging)))
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, *given
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $70,000: line 132 alone, line 133 being blank.
        ("70000", "7585.64"),
        # $20,000: line 132 alone.
        ("20000", "158.09"),
        # $200,000: line 132 alone.
        ("200000", "39467.74"),
        # $10,000: line 132 is 0, so the line is 0.
        ("10000", "0.00"),
    ],
)
def test_line_134_is_line_132_when_line_133_is_blank(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    line_134 = sheet.get(kinds.kind(LINE_134)).value
    assert line_134 == D(expected)
    assert line_134 == sheet.get(kinds.kind(LINE_132)).value
    assert line_134.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("salary", "logging", "expected"),
    [
        # $70,000: 7,585.64 less 100.00.
        ("70000", "100", "7485.64"),
        # $20,000: 158.09 less 10,000.00 is negative, so the line is floored at 0.
        ("20000", "10000", "0.00"),
        # Exactly equal: the difference is zero.
        ("20000", "158.09", "0.00"),
    ],
)
def test_line_134_subtracts_the_given_line_133_not_below_zero(
    take_home_service: TakeHomeService, salary: str, logging: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary, logging)

    line_134 = sheet.get(bundled_kinds().kind(LINE_134)).value
    assert line_134 == D(expected)
    assert line_134.as_tuple().exponent == -2


def test_line_134_names_line_132_line_133_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000", "100.00")
    kinds = bundled_kinds()
    output = kinds.kind(LINE_134)
    line_132 = kinds.kind(LINE_132)
    line_133 = kinds.kind(LINE_133)

    assert (
        f"{output.label}: {line_132.label} 7585.64 less {line_133.label} 100.00, "
        "not below 0 = 7485.64 (half-up to 0.01)"
    ) in EnglishTraceRenderer().render_all(sheet.trace)


def test_line_134_is_never_below_zero(take_home_service: TakeHomeService) -> None:
    sheet = _sheet(take_home_service, "20000", "10000")
    kinds = bundled_kinds()

    assert sheet.get(kinds.kind(LINE_132)).value == D("158.09")
    assert sheet.get(kinds.kind(LINE_134)).value == D("0.00")
