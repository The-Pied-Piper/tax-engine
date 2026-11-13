"""ON428 (2025) line 5, the bracket column rate, computed from the real part file through the real
engine.

Form text (Form ON428, CRA 5006-c-25e.txt): each of
the five columns prints its rate on "Line 5": "Line 5: Rate 5.05%", "Line 5: Rate 9.15%",
"Line 5: Rate 11.16%", "Line 5: Rate 12.16%" and "Line 5: Rate 13.16%". Line 5 is the printed rate
of the column that taxable income falls in, and a taxable income exactly at a column's upper bound
falls in that lower column ("more than ... but not more than").

Line 1 is the taxable income (line 26000), taken as given: it is declared as a required input of
the test header and given directly as an Artifact, so this test does not compose the T1 lines.
Line 5 is one `core/bracket_column_rate` over line 1 with the `ca-on/brackets` schedule, output
`ca-on/on428_bracket_column_rate_line_5`, in the one part `on428_line_5.yaml`. The output is a rate
held in a Decimal artifact, not rounded. The form declaration is test-local: it exports line 5.

Figures: the taxable income at a $20,000 salary is 19,835.00, at $70,000 is 69,335.00 and at
$150,000 is 148,926.00 (the worked figures), so line 5 is 5.05%, 9.15% and 11.16%.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
CODE = JurisdictionCode("CA-ON")
FORM_NAME = "ca-on/on428"
LINE_1 = "ca-on/on428_taxable_income_line_1"
LINE_5 = "ca-on/on428_bracket_column_rate_line_5"
PART = "on428_line_5.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_1}
    required: true
outputs:
  - {LINE_1}
capabilities: []
"""

FORM = f"""\
form:
  name: {FORM_NAME}
  required: true
  exports:
    - {LINE_5}
capabilities: []
"""


def _line_5(take_home_service: TakeHomeService, taxable_income: str) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_1), D(taxable_income))]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)[FORM_NAME][0]
    value = worksheet.get(kinds.kind(LINE_5)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # The worked figure for a $20,000 salary: 19,835.00 is in column 1, rate 5.05%.
        ("19835.00", "0.0505"),
        # The worked figure for a $70,000 salary: 69,335.00 is in column 2, rate 9.15%.
        ("69335.00", "0.0915"),
        # The worked figure for a $150,000 salary: 148,926.00 is in column 3, rate 11.16%.
        ("148926.00", "0.1116"),
    ],
)
def test_line_5_is_the_rate_of_the_column_line_1_falls_in(
    take_home_service: TakeHomeService, taxable_income: str, expected: str
) -> None:
    assert _line_5(take_home_service, taxable_income) == D(expected)


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # 0 is the lower bound of column 1, so it takes column 1's rate.
        ("0.00", "0.0505"),
        # Each threshold falls in the lower column, so it takes that column's rate.
        ("52886.00", "0.0505"),
        ("105775.00", "0.0915"),
        ("150000.00", "0.1116"),
        ("220000.00", "0.1216"),
    ],
)
def test_line_5_at_a_threshold_is_the_rate_of_the_lower_column(
    take_home_service: TakeHomeService, taxable_income: str, expected: str
) -> None:
    assert _line_5(take_home_service, taxable_income) == D(expected)


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # One cent above 52,886 is over the threshold, so it is in column 2.
        ("52886.01", "0.0915"),
        # One cent above 105,775 is in column 3.
        ("105775.01", "0.1116"),
        # One cent above 150,000 is in column 4.
        ("150000.01", "0.1216"),
        # One cent above 220,000 is in column 5.
        ("220000.01", "0.1316"),
    ],
)
def test_line_5_one_cent_above_a_threshold_is_the_rate_of_the_next_column(
    take_home_service: TakeHomeService, taxable_income: str, expected: str
) -> None:
    assert _line_5(take_home_service, taxable_income) == D(expected)


def test_the_kind_is_registered_and_not_negative() -> None:
    kind = bundled_kinds().kind(LINE_5)

    assert kind.identifier == LINE_5
    assert non_negative(kind)
