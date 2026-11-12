"""T1 General 2025 (5006-R, Ontario) line 148 / line 43500 "Total payable", from the salary alone.

5006-R-25E (cra-docs/docs/cra-forms-2025/5006-r-25e.txt): "Line 148 and line 43500: Add lines 143 to
147.
Total payable". The take-home filer has two of those lines: line 143 "Amount from line 42000"
(`ca/net_federal_tax`, read directly from the line 42000 part) and line 147 "Provincial or
territorial tax (complete and attach your provincial or territorial Form 428, even if the result
is "0")", which is ON428 line 90 (`ca-on/on428_ontario_tax_line_90`). Lines 144 (42100), 145
(42120) and 146 (42200) are absent for the take-home filer (no self-employment, no line 23500) and
are left out.

Line 147 is a copy of ON428 line 90 and gets no step of its own in the T1 form beyond the pure
read: the ON428 form's line 90 is another form's export, so the engine reads it only as a record
list, through `core/record_total` into the new non-negative kind `ca/provincial_tax_line_42800`
(line 42800). Line 148 is a `core/sum` of the net federal tax and that kind, rounded to the cent by
`ca/cent_rounding`, and produces the existing non-negative kind `ca/total_payable`.

The test composes the real salary, Schedule 8, T1 taxable income, T2204 and ON428 parts, the real
line 42000 chain and the part under test. The header and the form's export of line 43500 are
test-local. The salary is the only input. Ontario resident, single filer, salary the only income,
tax withheld 0, basic credits only.
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
ON428_FORM = "ca-on/on428"
LINE_142 = "ca/net_federal_tax"
LINE_42800 = "ca/provincial_tax_line_42800"
LINE_43500 = "ca/total_payable"
ON428_LINE_90 = "ca-on/on428_ontario_tax_line_90"
# The real parts composed beside the test's header: the salary, the real Schedule 8 and T2204
# parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 84, 31260, 96, 98, 101, 106,
# 33500, 33800, 35000, 40400, 125, 42900, 128, 130 and 132, lines 40600 and 41600 with the input of
# line 40600, line 41700, line 42000, the real ON428 parts (the form, its lines and its inputs,
# ON428-A included), and the part under test.
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
    *(part.name for part in sorted(TAKE_HOME.rglob("on428*.yaml"))),
    "t1_tax_and_credits_line_43500.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 43500, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_43500}
    """)


def _worksheets(
    take_home_service: TakeHomeService, salary: str
) -> dict[str, tuple[Worksheet, ...]]:
    """The worksheets of one run: the T1 tax and credits form and the ON428 form beside it."""
    return take_home_service(HEADER, T1_TAX_AND_CREDITS, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 142, 42800 and 43500 on it."""
    (sheet,) = _worksheets(take_home_service, salary)[FORM]
    return sheet


def _on428_line_90(worksheets: dict[str, tuple[Worksheet, ...]]) -> Decimal:
    """ON428 line 90 of one run, read from the ON428 sheet the run computes beside the T1 form."""
    value = worksheets[ON428_FORM][0].get(bundled_kinds().kind(ON428_LINE_90)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("salary", "line_142", "line_42800", "line_43500"),
    [
        # $70,000: line 142 is 7,585.64 and ON428 line 90 is 3,911.45 (the ticket's oracle, Return
        # DD), so line 43500 is 11,497.09.
        ("70000", "7585.64", "3911.45", "11497.09"),
        # $20,000: line 142 is 158.09 and ON428 line 90 is 0.00, so line 43500 is 158.09.
        ("20000", "158.09", "0.00", "158.09"),
        # $10,000: line 142 is 0 and ON428 line 90 is 0, so line 43500 is 0.
        ("10000", "0.00", "0.00", "0.00"),
        # $150,000: ON428 line 90 is 14,852.14 (as pinned by the ON428 line 90 test). Line 142 is
        # 25,772.14, taken from a run of the real parts, so line 43500 is 40,624.28.
        ("150000", "25772.14", "14852.14", "40624.28"),
        # $200,000: line 142 is 39,467.74 (as pinned by the line 42000 test). ON428 line 90 is
        # 24,320.20, taken from a run of the real parts, so line 43500 is 63,787.94.
        ("200000", "39467.74", "24320.20", "63787.94"),
    ],
)
def test_line_43500_is_line_42000_plus_on428_line_90(
    take_home_service: TakeHomeService,
    salary: str,
    line_142: str,
    line_42800: str,
    line_43500: str,
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    total = sheet.get(kinds.kind(LINE_43500)).value
    assert total == D(line_43500)
    assert total.as_tuple().exponent == -2
    assert sheet.get(kinds.kind(LINE_142)).value == D(line_142)
    assert sheet.get(kinds.kind(LINE_42800)).value == D(line_42800)


@pytest.mark.parametrize(
    "salary", ["10000", "15000", "20000", "35000", "70000", "100000", "150000"]
)
def test_line_43500_equals_line_42000_plus_on428_line_90_read_from_the_sheets(
    take_home_service: TakeHomeService, salary: str
) -> None:
    worksheets = _worksheets(take_home_service, salary)
    (sheet,) = worksheets[FORM]
    kinds = bundled_kinds()
    line_142 = sheet.get(kinds.kind(LINE_142)).value
    line_42800 = sheet.get(kinds.kind(LINE_42800)).value

    assert line_42800 == _on428_line_90(worksheets)
    assert sheet.get(kinds.kind(LINE_43500)).value == line_142 + line_42800


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # $10,000: ON428 line 90 is 0, so line 42800 is 0.
        ("10000", "0.00"),
        # $20,000: ON428 line 90 is 0.00.
        ("20000", "0.00"),
        # $70,000: ON428 line 90 is 3,911.45.
        ("70000", "3911.45"),
        # $150,000: ON428 line 90 is 14,852.14.
        ("150000", "14852.14"),
        # $200,000: ON428 line 90 is 24,320.20, from a run of the real parts.
        ("200000", "24320.20"),
    ],
)
def test_line_42800_is_the_on428_line_90(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    line_42800 = sheet.get(bundled_kinds().kind(LINE_42800)).value

    assert line_42800 == D(expected)
    assert line_42800.as_tuple().exponent == -2


def test_line_43500_names_line_142_and_line_42800_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "Line 42000 (CA$7585.64) plus line 42800 (CA$3911.45) gives CA$11497.09 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_provincial_tax_line_42800_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_42800)

    assert kind.identifier == LINE_42800
    assert non_negative(kind) is True


def test_the_total_payable_kind_stays_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_43500)

    assert kind.identifier == LINE_43500
    assert non_negative(kind) is True
