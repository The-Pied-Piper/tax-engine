"""Form BC479 (2026, British Columbia credits, single filer) from the salary alone: the real
British Columbia manifest composed end to end for tax year 2026.

The British Columbia 2026 datasets are PROVISIONAL: each carries a `# Provisional:` header, the
2026 forms (Form BC428, CRA 5010-c; Form BC479, CRA 5010-tc) are not yet published, and the
figures come from T4127 (July 2026) or are carried forward or derived from 2025. The sales tax
credit figures of Form BC479 (the basic credit of 75.00, the threshold of 15,000.00 and the rate of
2%) are not in T4127 and are carried forward unchanged from 2025, as are the other families the
form does not take from T4127. The net income of line 1 follows from the T4127 CPP figures. The
pinned figures are therefore not confirmed CRA figures: they follow the provisional datasets, and
must be re-checked when CRA publishes the 2026 forms.

The British Columbia manifest is 2025-only but the engine runs 2026 on it, reading each dataset
family's 2026 file. `build_tax_computation` (the registered engine, which lists British Columbia)
runs with the gross salary (`ca/employment_income`) the only input and every optional input left
blank. It asserts the British Columbia credits of BC479 line 45 at salaries of $17,000, $20,000,
$30,000, $40,000, $70,000 and $200,000, and the lines of the sales tax credit on the way (1, 9 and
15).

Form text (Form BC479, CRA 5010-tc, 2025 text; the 2026 form is not yet published): "Line 45: Line
36 plus line 44 Enter this amount on line 47900 of your return. British Columbia credits = ^".

Every figure here was computed by hand, independently of the engine, with plain decimal
arithmetic from the 2026 British Columbia and CPP datasets, and the engine then agreed to the cent.
The line 45 figures are 37.70 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00. The basic credit of line 9 is
75.00; the sales tax credit (line 13) is that less 2% of the net income over the 15,000.00
threshold of line 7, not below 0, and line 15 is the page 1 total. The net income of line 1 is the
salary less the Schedule 8 enhanced CPP contributions: 16,865.00 / 19,835.00 / 29,735.00 /
39,635.00 / 69,335.00 / 198,873.00. At $17,000 the credit is 75.00 - 37.30 = 37.70; from a net
income of 18,750.00 it is nil. The renter's credit of line 44 is left blank and read as 0. The
line 45 credit reaches the return's T1 line 167 (see `test_bc428_2026.py`).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
BC479 = "ca-bc/bc479"
LINE_1 = "ca-bc/bc479_net_income_line_1"
LINE_9 = "ca-bc/bc479_basic_sales_tax_credit_line_9"
LINE_15 = "ca-bc/bc479_page_1_total_line_15"
LINE_45 = "ca-bc/bc479_british_columbia_credits_line_45"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _bc479(salary: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        BRITISH_COLUMBIA, 2026, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (bc479,) = worksheets[BC479]
    return bc479


@pytest.mark.parametrize(
    ("salary", "british_columbia_credits"),
    [
        ("17000", "37.70"),
        ("20000", "0.00"),
        ("30000", "0.00"),
        ("40000", "0.00"),
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
        ("40000", "39635.00", "75.00", "0.00"),
        ("70000", "69335.00", "75.00", "0.00"),
        ("200000", "198873.00", "75.00", "0.00"),
    ],
)
def test_the_lines_leading_to_line_45(salary: str, line_1: str, line_9: str, line_15: str) -> None:
    bc479 = _bc479(salary)

    assert _figure(bc479, LINE_1) == D(line_1)
    assert _figure(bc479, LINE_9) == D(line_9)
    assert _figure(bc479, LINE_15) == D(line_15)
