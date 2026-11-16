"""Form BC479 (2025, British Columbia credits, single filer) from the salary alone: the real
British Columbia manifest composed end to end.

Every BC479 line part has its own test with its neighbours typed in. This module runs the whole
chain: the engine over the real British Columbia 2025 manifest (`british_columbia_service`, the
British Columbia package list standing in for `registrations.JURISDICTIONS`, which does not list
British Columbia yet), with the gross salary (`ca/employment_income`) the only input and every
optional input left blank. It asserts the British Columbia credits of BC479 line 45 at salaries of
$17,000, $20,000, $30,000, $70,000 and $200,000, and the lines of the sales tax credit on the way
(1, 9 and 15).

Form text (Form BC479, CRA 5010-tc): "Line 45: Line 36 plus line 44 Enter this amount on line 47900
of your return. British Columbia credits = ^".

The line 45 figures are hand-computed from the printed form: 37.70 / 0.00 / 0.00 / 0.00 / 0.00. The
basic credit of line 9 is 75.00; the sales tax credit (line 13) is that less 2% of the net income
over the 15,000.00 threshold of line 7, not below 0, and line 15 is the page 1 total. At $17,000 the
net income of line 1 is 16,865.00, so the credit is 75.00 - 37.30 = 37.70; from a net income of
18,750.00 it is nil. The renter's credit of line 44 is left blank and read as 0.

The line 45 figure reaches T1 line 167 through T1 line 47900: at $17,000 the return's line 167 (see
`test_bc428.py`) includes this 37.70 credit.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_bc.support import british_columbia_kinds, british_columbia_service

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
BC479 = "ca-bc/bc479"
LINE_1 = "ca-bc/bc479_net_income_line_1"
LINE_9 = "ca-bc/bc479_basic_sales_tax_credit_line_9"
LINE_15 = "ca-bc/bc479_page_1_total_line_15"
LINE_45 = "ca-bc/bc479_british_columbia_credits_line_45"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = british_columbia_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _bc479(salary: str) -> Worksheet:
    worksheets = british_columbia_service().compute(
        BRITISH_COLUMBIA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (bc479,) = worksheets[BC479]
    return bc479


@pytest.mark.parametrize(
    ("salary", "british_columbia_credits"),
    [
        ("17000", "37.70"),
        ("20000", "0.00"),
        ("30000", "0.00"),
        ("70000", "0.00"),
        ("200000", "0.00"),
    ],
)
def test_line_45_is_the_british_columbia_credits(
    salary: str, british_columbia_credits: str
) -> None:
    assert _figure(_bc479(salary), LINE_45) == D(british_columbia_credits)


@pytest.mark.parametrize(
    ("salary", "line_1", "line_9", "line_15"),
    [
        ("17000", "16865.00", "75.00", "37.70"),
        ("20000", "19835.00", "75.00", "0.00"),
        ("30000", "29735.00", "75.00", "0.00"),
        ("70000", "69335.00", "75.00", "0.00"),
        ("200000", "198926.00", "75.00", "0.00"),
    ],
)
def test_the_lines_leading_to_line_45(salary: str, line_1: str, line_9: str, line_15: str) -> None:
    bc479 = _bc479(salary)

    assert _figure(bc479, LINE_1) == D(line_1)
    assert _figure(bc479, LINE_9) == D(line_9)
    assert _figure(bc479, LINE_15) == D(line_15)
