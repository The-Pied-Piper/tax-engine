"""ON428 (2025) line 4 from the salary alone, real engine.

Form text (Form ON428, CRA 5006-c-25e.txt, repo copy cra-docs/docs/cra-forms-2025/5006-c-25e.txt):
each
Part A column prints "Line 4: Line 2 minus line 3 (cannot be negative) =". Line 2 is a copy of
line 1 (the T1 taxable income, line 26000), and line 3 is the printed lower bound of the column
that line 1 falls in. Line 4 is therefore line 1 less line 3, floored at zero.

Line 1 is `ca-on/on428_taxable_income_line_1` (a `core/record_total` over the T1 taxable-income
records) and line 3 is `ca-on/on428_bracket_lower_bound_line_3` (`core/bracket_column_lower_bound`
over line 1). Line 2 is a copy of line 1 and has no step. Line 4 is `core/subtract_not_below_zero`
with `amount` = line 1 and `less` = line 3, output
`ca-on/on428_taxable_income_over_lower_bound_line_4`. The step lives in the one part
`on428_line_4.yaml`.

The real parts composed here: the salary, the real Schedule 8, the T1 taxable-income lines and
inputs, `on428_line_3.yaml` and `on428_line_4.yaml`. The ON428 form declaration is test-local: it
exports lines 1, 3 and 4, because the real header exports lines whose parts are not composed here.

Figures (worked, hand computed): line 1 is 19,835.00 at a $20,000 salary, 69,335.00 at $70,000 and
148,926.00 at $150,000; line 3 is 0.00, 52,886.00 and 105,775.00; so line 4 is 19,835.00,
16,449.00 and 43,151.00.
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
LINE_4 = "ca-on/on428_taxable_income_over_lower_bound_line_4"
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
    "on428_line_4.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The ON428 declaration, test-local: lines 1, 3 and 4 are composed, so it exports those.
ON428 = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
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
        # Line 1 is 19,835.00 and line 3 is 0.00 (column 1): line 4 is line 1 itself.
        ("20000", "19835.00"),
        # Line 1 is 69,335.00 and line 3 is 52,886.00 (column 2).
        ("70000", "16449.00"),
        # Line 1 is 148,926.00 and line 3 is 105,775.00 (column 3).
        ("150000", "43151.00"),
    ],
)
def test_line_4_is_line_2_minus_line_3_for_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _on428(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_4)).value == D(expected)


def test_the_kind_is_registered_and_not_negative() -> None:
    kinds = bundled_kinds()

    kind = kinds.kind(LINE_4)
    assert kind.identifier == LINE_4
    assert non_negative(kind)
