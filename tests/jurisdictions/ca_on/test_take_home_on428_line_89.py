"""ON428 (2025) line 89, the Ontario health premium, from the salary alone, real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 89: Ontario health premium (complete the chart
below)". Chart line 1: "Enter your taxable income from line 26000 of your return", then the chart's
rows, each a flat amount or a sloped (income minus a threshold) x rate plus an amount. The chart
is read row by row by `core/amount_by_band` over the `ca-on/health_premium_rows` dataset.

Line 1 is a `core/record_total` over the real T1 export `ca/t1_taxable_income.taxable_income`
(T1 line 26000), the same way ON428-A line 6 reads net income: the form exports taxable income and
another form reads it only as a record list. Line 89 reads line 1 as its base. The output is
`ca-on/on428_ontario_health_premium_line_89`; line 1 is `ca-on/on428_taxable_income_line_89`.

The T1 side is the real `ca/t1_taxable_income` form and its parts, read from the salary through
the real Schedule 8 and T1 lines, as in the ON428-A line 13 test. The salary is the only input the
caller gives. This test declares lines 1 and 89 as the exports of its form, since the form's
header does not, and loads the take-home folder's `on428/on428_line_89.yaml` beside it.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca-on/on428"
LINE_1 = "ca-on/on428_taxable_income_line_89"
LINE_89 = "ca-on/on428_ontario_health_premium_line_89"
# The real parts composed beside the test's header: the salary, the real Schedule 8, the real T1
# taxable-income lines and inputs, and the ON428 line 89 part.
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
    "on428_line_89.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The ON428 declaration, test-local: its exports are lines 1 and 89, the two lines of this part.
ON428 = f"""\
form:
  name: {FORM}
  required: true
  exports:
    - {LINE_1}
    - {LINE_89}
"""


def _on428(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, ON428, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # The $20,000 salary: T1 line 26000 is 19,835.00.
        ("20000", "19835.00"),
        # The $70,000 salary: T1 line 26000 is 69,335.00.
        ("70000", "69335.00"),
        # The $150,000 salary: T1 line 26000 is 148,926.00.
        ("150000", "148926.00"),
    ],
)
def test_line_1_is_the_t1_taxable_income(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _on428(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_1)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # The $20,000 salary: taxable income 19,835.00 is "$20,000 or less", so $0.
        ("20000", "0.00"),
        # The $70,000 salary: taxable income 69,335.00 is "more than $48,600 but not more than
        # $72,000", so $600.
        ("70000", "600.00"),
        # The $150,000 salary: taxable income 148,926.00 is "more than $72,600 but not more than
        # $200,000", so $750.
        ("150000", "750.00"),
    ],
)
def test_line_89_is_the_ontario_health_premium_on_line_1(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _on428(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_89)).value == D(expected)


def test_the_catalog_declares_lines_1_and_89_as_non_negative_amounts() -> None:
    kinds = bundled_kinds()

    for identifier in (LINE_1, LINE_89):
        assert identifier in kinds.identifiers()
        kind = kinds.kind(identifier)
        assert isinstance(kind, AmountKind)
        assert kind.identifier == identifier
        assert kind.non_negative is True
