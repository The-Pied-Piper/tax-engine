"""Form BC428 (2025, British Columbia tax, single filer) from the salary alone: the real British
Columbia manifest composed end to end.

Every BC428 line part has its own test with its neighbours typed in. This module runs the whole
chain: the registered engine (`build_tax_computation`) over the real British Columbia 2025 manifest,
with the gross salary (`ca/employment_income`) the only input and every
optional input left blank. It asserts the British Columbia tax of BC428 line 91 at salaries of
$17,000, $20,000, $30,000, $70,000 and $200,000, the intermediate lines of the form on the way
(1, 74 and 79), and the return's T1 line 167 ("ca/refund_or_balance_owing").

Form text (Form BC428, CRA 5010-c): "Line 91: Line 89 minus line 90 (if negative, enter "0")
Enter this amount on line 42800 of your return. British Columbia tax =".

The line 91 figures are hand-computed from the printed form: 0.00 / 0.00 / 364.81 / 3,162.39 /
19,230.76. At $30,000 the taxable income is 29,735.00 and the tax after credits (line 72) is
758.96; the printed reduction (562.00 less 3.56% of the net income over 25,020.00) is 562.00 -
167.85 = 394.15, leaving 364.81. At $17,000 and $20,000 the reduction of 562.00 takes the tax after
credits (151.09 and 291.37) to 0.00. From a net income of 40,807.00 the reduction is 0.00.

The lines 1, 74 and 79 figures follow from the salary: the taxable income (line 1) and the net
income (line 74) are the salary less the Schedule 8 enhanced contributions, and line 79 is the
reduction above. The T1
line 167 figures are the engine's own, not computed by hand: they pin the current output of the
whole chain, including the sales tax credit of BC479 line 45 (T1 line 47900, pinned in
`test_bc479.py`). Line 167 is the refund (negative) or balance owing (positive) of the return.
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
BC428 = "ca-bc/bc428"
RETURN = "ca-bc/return"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_74 = "ca-bc/bc428_net_income_line_74"
LINE_79 = "ca-bc/bc428_british_columbia_tax_reduction_line_79"
LINE_91 = "ca-bc/bc428_british_columbia_tax_line_91"
LINE_167 = "ca/refund_or_balance_owing"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        BRITISH_COLUMBIA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


@pytest.mark.parametrize(
    ("salary", "british_columbia_tax"),
    [
        ("17000", "0.00"),
        ("20000", "0.00"),
        ("30000", "364.81"),
        ("70000", "3162.39"),
        ("200000", "19230.76"),
    ],
)
def test_line_91_is_the_british_columbia_tax(salary: str, british_columbia_tax: str) -> None:
    (bc428,) = _worksheets(salary)[BC428]

    assert _figure(bc428, LINE_91) == D(british_columbia_tax)


@pytest.mark.parametrize(
    ("salary", "line_1", "line_74", "line_79"),
    [
        ("17000", "16865.00", "16865.00", "562.00"),
        ("20000", "19835.00", "19835.00", "562.00"),
        ("30000", "29735.00", "29735.00", "394.15"),
        ("70000", "69335.00", "69335.00", "0.00"),
        ("200000", "198926.00", "198926.00", "0.00"),
    ],
)
def test_the_lines_leading_to_line_91(salary: str, line_1: str, line_74: str, line_79: str) -> None:
    (bc428,) = _worksheets(salary)[BC428]

    assert _figure(bc428, LINE_1) == D(line_1)
    assert _figure(bc428, LINE_74) == D(line_74)
    assert _figure(bc428, LINE_79) == D(line_79)


@pytest.mark.parametrize(
    ("salary", "refund_or_balance_owing"),
    [
        # Line 48200: 1,633.00 (Canada workers benefit) plus 37.70 (BC479 line 45), against no tax.
        ("17000", "-1670.70"),
        ("20000", "-1474.91"),
        ("30000", "661.85"),
        ("70000", "10748.03"),
        ("200000", "58698.50"),
    ],
)
def test_t1_line_167_is_the_refund_or_balance_owing(
    salary: str, refund_or_balance_owing: str
) -> None:
    (summary,) = _worksheets(salary)[RETURN]

    assert _figure(summary, LINE_167) == D(refund_or_balance_owing)
