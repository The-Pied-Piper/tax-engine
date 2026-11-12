"""ON428 (2025) line 7, from the salary alone, real engine.

Form text (Form ON428, CRA 5006-c-25e.txt, repo copy cra-docs/docs/cra-forms-2025/5006-c-25e.txt):
each of
the five columns prints "Line 7:" with the tax at the column's start, 0.00, 2,670.74, 7,510.09,
12,445.60 and 20,957.60 (the constants listed in the dataset file ca-on/brackets 2025). The
Transcriber's Note says: "Use the amount from column 1 if the amount on line 1 is $52,886 or less.
Use the amount from column 2 if the amount on line 1 is more than $52,886 but not more than
$105,775." (columns 3 to 5 follow the same wording). Line 7 is the printed constant of the column
that taxable income (line 1) falls in.

Line 7 is `core/bracket_column_tax_at_start` over line 1 with the `ca-on/brackets` schedule, output
`ca-on/on428_tax_at_column_start_line_7`, in the one part `on428_line_7.yaml`. Line 1 comes from the
real part `on428_line_3.yaml` (`ca-on/on428_taxable_income_line_1`).

The real parts composed here: the salary, the real Schedule 8, the T1 taxable-income lines and
inputs, `on428_line_3.yaml` (for line 1) and `on428_line_7.yaml`. The ON428 form declaration is
test-local: it exports line 7, because the real header exports lines whose parts are not composed.

Figures: T1 line 26000 is 19,835.00 at a $20,000 salary, 69,335.00 at $70,000 and 148,926.00 at
$150,000 (the worked figures). Line 1 is 52,886.00 at a salary of 53,384.85 and 52,886.01 at
53,384.86 (the engine's own line 1 for those salaries, found by search; "to be confirmed" against
a CRA worked example).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca-on/on428"
LINE_1 = "ca-on/on428_taxable_income_line_1"
LINE_3 = "ca-on/on428_bracket_lower_bound_line_3"
LINE_7 = "ca-on/on428_tax_at_column_start_line_7"
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
    "on428_line_3.yaml",
    "on428_line_7.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The ON428 declaration, test-local: lines 3 and 7 are composed (line 3 comes with the part that
# owns line 1), so it exports both.
ON428 = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_3}
        - {LINE_7}
    """)


def _on428(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, ON428, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 is 19,835.00, not over 52,886: column 1.
        ("20000", "0.00"),
        # Line 1 is 69,335.00, over 52,886 and not over 105,775: column 2.
        ("70000", "2670.74"),
        # Line 1 is 148,926.00, over 105,775 and not over 150,000: column 3.
        ("150000", "7510.09"),
    ],
)
def test_line_7_is_the_printed_tax_at_the_start_of_the_column_line_1_falls_in(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _on428(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_7)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "line_1", "expected"),
    [
        # Line 1 exactly 52,886.00: "$52,886 or less", column 1.
        ("53384.85", "52886.00", "0.00"),
        # A cent over: column 2.
        ("53384.86", "52886.01", "2670.74"),
    ],
)
def test_line_1_exactly_at_a_threshold_is_in_the_lower_column(
    take_home_service: TakeHomeService, salary: str, line_1: str, expected: str
) -> None:
    sheet = _on428(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_1)).value == D(line_1)
    assert sheet.get(bundled_kinds().kind(LINE_7)).value == D(expected)


def test_the_kind_is_registered_and_not_negative() -> None:
    kind = bundled_kinds().kind(LINE_7)

    assert kind.identifier == LINE_7
    assert non_negative(kind)
