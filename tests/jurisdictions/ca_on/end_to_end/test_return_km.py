"""CA-ON 2025 end to end: return km (Guide T4036 "Capital cost allowance (CCA)", Abeer's example).

Guide T4036 (2025): "Last year, Abeer bought a rental building for $60,000. On her income tax
return for last year, she claimed CCA of $1,200 on the building. This year, Abeer bases her CCA
claim on her remaining balance of $58,800 ($60,000 – $1,200)."

The worked return `returns/2025_return_km.yaml` (checked by `test_worked_returns.py`) pins the
balance CRA prints: the UCC at the end of the year (Area A column 24) of 58800. This module reads
the claim and the closing UCC, and the claim one cent above the most the class allows.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    RENTAL_CCA_CLAIM,
    RENTAL_CLOSING_UCC,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, RentalCcaRow, rental_return

# Area A: class 1, no UCC at the start, the building's cost of 60000 as additions, CCA claimed
# 1200.00. The Guide prints no class and no rent: class 1 and gross rents of 5000 are chosen,
# and so is a building that is neither an AIIP nor a RIIP (entries 0): the half-year rule applies.
ABEER = {"rental_properties": ((1, "0", "5000"),)}


def abeer_row(claimed: str) -> RentalCcaRow:
    """Abeer's class 1 row with the CCA `claimed`."""
    return ("1", "0", "60000", "0", "0", "0", claimed, 0, "0", "0", "0", "0")


def test_abeers_balance_after_claiming_1200_on_a_60000_building_is_58800() -> None:
    result = rental_return(ABEER, {"rental_cca_classes_rows": (abeer_row("1200"),)})
    worksheet = result["ca/t776"][0]

    assert worksheet.get(RENTAL_CCA_CLAIM).value == D("1200")
    (closing,) = worksheet.get(RENTAL_CLOSING_UCC).value.records
    assert closing[CCA_CLASS_NUMBER] == D("1")
    assert closing[CCA_UCC_AT_END] == D("58800")


def test_a_claim_above_the_half_year_maximum_of_1200_is_refused() -> None:
    # Class 1 is 4% and the half-year rule halves the 60000 added: 4% x 30000 = 1200.
    with pytest.raises(InputAboveBoundError, match="above the maximum 1200.00"):
        rental_return(ABEER, {"rental_cca_classes_rows": (abeer_row("1200.01"),)})
