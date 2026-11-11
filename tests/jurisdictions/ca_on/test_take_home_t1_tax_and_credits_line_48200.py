"""T1 General 2025 (5006-R, Ontario) line 48200 "Total credits", from the salary alone.

5006-R-25E (docs/cra-forms-2025/5006-r-25e.txt): "Line 166 and line 48200: Add lines 150 to 165.
Total credits". The take-home filer has two of those credits. T1 line 45000 is the EI overpayment:
T2204 line 15, "Enter whichever is less: amount from line 9 or line 14. If this amount is more than
$1, enter it on line 45000 of your return." T1 line 45300 is the Canada workers benefit: Schedule 6
line 28, "If you are not completing Step 3, enter this amount on line 45300 of your return."

Each of the two is another form's export, and the engine lets one form read another form's exports
only as a record list, so each is a `core/record_total` step of the T1 tax and credits form:
`ca/t2204.ei_overpayment` into the new non-negative kind `ca/ei_overpayment_line_45000`, and
`ca/schedule_6.cwb_benefit_line_28` into the new non-negative kind `ca/cwb_line_45300`. Line 48200
is a `core/sum` of the two, rounded to the cent by `ca/cent_rounding`, and produces the existing
signed kind `ca/total_credits`.

The test composes the real salary, Schedule 8, T1 taxable income, T2204 and Schedule 6 parts and
the real part under test. The header and the form's export of line 48200 are test-local. The
salary is the only input. Ontario resident, single filer, salary the only income, tax withheld 0,
basic credits only.

The T2204 line 15 edge: line 15 counts only when more than $1. Run through the real parts, line 15
is 1.01 at a salary of 2,032.32 (counted) and 1.00 at 2,032.33 (not more than $1, counts as 0);
so the edge is between those two salaries. The EI overpayment exists only below
a salary of about 2,033 and the CWB only above about 3,000 (0.00 at 3,000, 135.00 at 3,500), so no
salary has both non-zero.
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
LINE_45000 = "ca/ei_overpayment_line_45000"
LINE_45300 = "ca/cwb_line_45300"
LINE_48200 = "ca/total_credits"
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
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
    *(part.name for part in sorted(TAKE_HOME.rglob("t2204*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_6*.yaml"))),
    "t1_tax_and_credits_line_48200.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 48200, the only line
# composed here.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_48200}
    """)


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


def _figures(take_home_service: TakeHomeService, salary: str) -> tuple[Decimal, Decimal, Decimal]:
    """Line 45000, line 45300 and line 48200 for a salary."""
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()
    return (
        sheet.get(kinds.kind(LINE_45000)).value,
        sheet.get(kinds.kind(LINE_45300)).value,
        sheet.get(kinds.kind(LINE_48200)).value,
    )


@pytest.mark.parametrize(
    ("salary", "ei_overpayment", "cwb", "total"),
    [
        # EI premiums are at the cap and the CWB is fully reduced: nothing to add.
        ("70000", "0.00", "0.00", "0.00"),
        # No overpayment; Schedule 6 line 28 is 1,633.00.
        ("20000", "0.00", "1633.00", "1633.00"),
        # No overpayment; Schedule 6 line 28 is 1,201.00.
        ("30000", "0.00", "1201.00", "1201.00"),
        # T2204 line 15 is 22.96 (more than $1) and counts; the CWB is 0.00 at this salary.
        ("2010", "22.96", "0.00", "22.96"),
        # The most line 15 reaches with the salary at the 2,000 threshold: 32.80, all counted.
        ("2000", "32.80", "0.00", "32.80"),
        # Line 15 is 1.32 here, more than $1, so it counts.
        ("2032", "1.32", "0.00", "1.32"),
        # Last cent where line 15 is more than $1: 1.01 counts.
        ("2032.32", "1.01", "0.00", "1.01"),
        # First cent where line 15 is not more than $1 (it is exactly 1.00): it counts as 0.
        ("2032.33", "0.00", "0.00", "0.00"),
        ("2033", "0.00", "0.00", "0.00"),
        # Above the EI overpayment range and below the CWB range (CWB starts above 3,000).
        ("3000", "0.00", "0.00", "0.00"),
        # CWB only: Schedule 6 line 28 is 135.00 and 270.00 on the way up.
        ("3500", "0.00", "135.00", "135.00"),
        ("4000", "0.00", "270.00", "270.00"),
    ],
)
def test_line_48200_is_the_ei_overpayment_plus_the_cwb(
    take_home_service: TakeHomeService,
    salary: str,
    ei_overpayment: str,
    cwb: str,
    total: str,
) -> None:
    line_45000, line_45300, line_48200 = _figures(take_home_service, salary)

    assert line_45000 == D(ei_overpayment)
    assert line_45300 == D(cwb)
    assert line_48200 == D(total)
    assert line_48200.as_tuple().exponent == -2


def test_line_48200_at_70000_is_the_cwb_alone(take_home_service: TakeHomeService) -> None:
    # At $70,000 line 48200 is the CWB alone, which is 0.
    line_45000, line_45300, line_48200 = _figures(take_home_service, "70000")

    assert line_48200 == line_45300 == D("0.00")
    assert line_45000 == D("0.00")


def test_the_line_45000_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_45000)

    assert kind.identifier == LINE_45000
    assert non_negative(kind) is True


def test_the_line_45300_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_45300)

    assert kind.identifier == LINE_45300
    assert non_negative(kind) is True


def test_the_total_credits_kind_stays_registered_and_signed() -> None:
    kind = bundled_kinds().kind(LINE_48200)

    assert kind.identifier == LINE_48200
    assert non_negative(kind) is False


def test_line_48200_names_lines_45000_and_45300_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "Line 45000 (0.00) plus line 45300 (0.00) gives 0.00 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)
