"""ON428 (2025) lines 1 and 3, from the salary alone, real engine.

Form text (Form ON428, CRA 5006-c-25e.txt, repo copy docs/cra-forms-2025/5006-c-25e.txt): line 3
(per column) is 0.00 / 52,886.00 / 105,775.00 / 150,000.00 / 220,000.00, with "Use column 1 if
line 1 is $52,886 or less; column 2 if more than $52,886 but not more than $105,775; column 3 if
more than $105,775 but not more than $150,000; column 4 if more than $150,000 but not more than
$220,000; column 5 if more than $220,000." Line 3 is the printed lower bound of the column that
taxable income falls in.

Line 1 is the T1 taxable income (line 26000). The T1 form exports it as `ca/taxable_income`,
which reaches this form only as the record list `ca/t1_taxable_income.taxable_income`, so line 1
is a `core/record_total` over it (output `ca-on/on428_taxable_income_line_1`). Line 2 is a copy
of line 1 and has no step. Line 3 is `core/bracket_column_lower_bound` over line 1 with the
`ca-on/brackets` schedule, output `ca-on/on428_bracket_lower_bound_line_3`. Both steps are in the
one part `on428_line_3.yaml`.

The real parts composed here: the salary, the real Schedule 8, the T1 taxable-income lines and
inputs, and `on428_line_3.yaml`. The ON428 form declaration is test-local: it exports lines 1 and
3, because the real header exports lines whose parts are not composed here.

Figures: T1 line 26000 is 19,835.00 at a $20,000 salary, 69,335.00 at $70,000 and 148,926.00 at
$150,000 (the worked figures of the ticket).
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
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "on428_line_3.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The ON428 declaration, test-local: lines 1 and 3 are composed, so it exports those.
ON428 = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
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
        ("20000", "19835.00"),
        ("70000", "69335.00"),
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
        # Line 1 is 19,835.00, not over 52,886: column 1.
        ("20000", "0.00"),
        # Line 1 is 69,335.00, over 52,886 and not over 105,775: column 2.
        ("70000", "52886.00"),
        # Line 1 is 148,926.00, over 105,775 and not over 150,000: column 3.
        ("150000", "105775.00"),
    ],
)
def test_line_3_is_the_lower_bound_of_the_column_line_1_falls_in(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = _on428(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(LINE_3)).value == D(expected)


def test_the_kinds_are_registered_and_not_negative() -> None:
    kinds = bundled_kinds()

    for identifier in (LINE_1, LINE_3):
        kind = kinds.kind(identifier)
        assert kind.identifier == identifier
        assert non_negative(kind)
