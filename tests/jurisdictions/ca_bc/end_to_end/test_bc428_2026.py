"""Form BC428 (2026, British Columbia tax, single filer) from the salary alone: the real British
Columbia manifest composed end to end for tax year 2026.

The British Columbia 2026 datasets are PROVISIONAL: each carries a `# Provisional:` header, the
2026 forms (Form BC428, CRA 5010-c; Form BC479, CRA 5010-tc) are not yet published, and the
figures come from T4127 (July 2026) or are carried forward or derived from 2025. The lowest rate
of 5.60% (up from 5.06%) and the basic reduction of 690 (up from 562) are the July 2026 T4127's.
British Columbia indexes at 2.2%, and the brackets, the basic personal amount and the reduction
base amount are T4127's. The `tax_at_start` of each bracket is derived at the 5.60% lowest rate,
rounded half-up to the cent. The other families (the 3.56% reduction rate, the minimum tax rate,
the cent rounding and the sales tax credit figures) are carried forward unchanged from 2025. The
pinned figures are therefore not confirmed CRA figures: they follow the provisional datasets, and
must be re-checked when CRA publishes the 2026 forms.

The British Columbia manifest is 2025-only but the engine runs 2026 on it, reading each dataset
family's 2026 file. `british_columbia_service` (the British Columbia package list standing in for
`registrations.JURISDICTIONS`, which does not list British Columbia yet) runs with the gross
salary (`ca/employment_income`) the only input and every optional input left blank. It asserts the
British Columbia tax of BC428 line 91 at salaries of $17,000, $20,000, $30,000, $40,000, $70,000
and $200,000, the intermediate lines of the form on the way (1, 74 and 79), and the return's T1
line 167 ("ca/refund_or_balance_owing").

Form text (Form BC428, CRA 5010-c, 2025 text; the 2026 form is not yet published): "Line 91: Line
89 minus line 90 (if negative, enter "0") Enter this amount on line 42800 of your return. British
Columbia tax =".

Every figure here was computed by hand, independently of the engine, with plain decimal
arithmetic from the 2026 British Columbia, federal, CPP and EI datasets, and the engine then
agreed to the cent. The taxable income (line 1) and the net income (line 74) are the salary less
the Schedule 8 enhanced CPP contributions (1% of the earnings over 3,500.00 up to 74,600.00, and
4% of those from 74,600.00 to 85,000.00): 16,865.00 / 19,835.00 / 29,735.00 / 39,635.00 /
69,335.00 / 198,873.00. Line 79 is the basic reduction of 690.00 less 3.56% of the net income over
25,570.00, not below 0: 690.00 / 690.00 / 541.73 / 189.29 / 0.00 / 0.00. It reaches 0 from a net
income of 44,952.00. At $17,000 and $20,000 the reduction takes the tax after credits (151.40 and
306.67) to 0.00. At $30,000 the tax after credits of 824.22 less the reduction of 541.73 leaves
282.49, and at $40,000 the tax after credits of 1,341.77 less 189.29 leaves 1,152.48. The line 91
figures are 0.00 / 0.00 / 282.49 / 1,152.48 / 3,293.84 / 19,079.61. For comparison, the 2025 line
91 figures are 0.00 / 0.00 / 364.81 / 3,162.39 / 19,230.76.

T1 line 167 is the refund (negative) or balance owing (positive) of the return: the federal tax
after the personal amount, CPP, EI and employment credits, plus the British Columbia tax, less
the Canada workers benefit (Schedule 6) and the British Columbia credits of BC479 line 45.
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
BC428 = "ca-bc/bc428"
RETURN = "ca-bc/return"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_74 = "ca-bc/bc428_net_income_line_74"
LINE_79 = "ca-bc/bc428_british_columbia_tax_reduction_line_79"
LINE_91 = "ca-bc/bc428_british_columbia_tax_line_91"
LINE_167 = "ca/refund_or_balance_owing"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = british_columbia_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return british_columbia_service().compute(
        BRITISH_COLUMBIA, 2026, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


@pytest.mark.parametrize(
    ("salary", "british_columbia_tax"),
    [
        ("17000", "0.00"),
        ("20000", "0.00"),
        ("30000", "282.49"),
        ("40000", "1152.48"),
        ("70000", "3293.84"),
        ("200000", "19079.61"),
    ],
)
def test_line_91_is_the_british_columbia_tax(salary: str, british_columbia_tax: str) -> None:
    (bc428,) = _worksheets(salary)[BC428]

    assert _figure(bc428, LINE_91) == D(british_columbia_tax)


@pytest.mark.parametrize(
    ("salary", "line_1", "line_74", "line_79"),
    [
        ("17000", "16865.00", "16865.00", "690.00"),
        ("20000", "19835.00", "19835.00", "690.00"),
        ("30000", "29735.00", "29735.00", "541.73"),
        ("40000", "39635.00", "39635.00", "189.29"),
        ("70000", "69335.00", "69335.00", "0.00"),
        ("200000", "198873.00", "198873.00", "0.00"),
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
        # Line 48200: 1,665.00 (Canada workers benefit) plus 37.70 (BC479 line 45), against no tax.
        ("17000", "-1702.70"),
        ("20000", "-1561.51"),
        ("30000", "366.31"),
        ("40000", "3843.73"),
        ("70000", "10572.03"),
        ("200000", "57956.15"),
    ],
)
def test_t1_line_167_is_the_refund_or_balance_owing(
    salary: str, refund_or_balance_owing: str
) -> None:
    (summary,) = _worksheets(salary)[RETURN]

    assert _figure(summary, LINE_167) == D(refund_or_balance_owing)
