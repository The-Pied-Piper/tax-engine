"""Form BC479 line 44 (the renter's tax credit) with the months of line 37, end to end: the
registered engine composed over the real British Columbia manifest, for tax years 2025 and 2026.

Form text (British Columbia Tax Information for 2025, CRA 5010-PC, section "British Columbia
renter's tax credit"): "You rented and occupied a rental unit for at least six months in the
calendar year in British Columbia". Form BC479 (CRA 5010-TC) line 44: "If you qualify, and your
adjusted family net income, on line 6 of page 1, is less than $64,764, enter $400 on line 60576. If
the adjusted family net income is between $64,764 and $84,764, complete lines 38 to 43 below and
enter the result on line 44."

Rent paid for 5 months gives 0.00; 6 months gives the credit. The salary of $17,000 is below the
$64,764 threshold (400.00); at $70,000 the net income of line 6 is 69,335.00, so line 41 is 4,571.00
and line 43 is 91.42, giving 308.58. The 2026 figures follow the provisional 2026 datasets, carried
from 2025. The figures were computed by hand from the printed lines, not an official example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC479_RENTERS_MONTHS_LINE_37
from tax_engine.registrations import artifact_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
LINE_44 = "ca-bc/bc479_renters_credit_line_44"


def _line_44(year: int, salary: str, months: int) -> Decimal:
    worksheets = build_tax_computation().compute(
        BRITISH_COLUMBIA,
        year,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(BC479_RENTERS_MONTHS_LINE_37, months),
    )
    (bc479,) = worksheets["ca-bc/bc479"]
    kind = artifact_kinds().kind(LINE_44)
    assert isinstance(kind, AmountKind)
    return bc479.get(kind).value


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(("salary", "credit"), [("17000", "400.00"), ("70000", "308.58")])
def test_line_44_is_zero_for_five_months_and_the_credit_for_six(
    year: int, salary: str, credit: str
) -> None:
    five = _line_44(year, salary, 5)
    six = _line_44(year, salary, 6)

    assert str(five) == "0.00"
    assert six == D(credit)
    assert str(six) == credit
