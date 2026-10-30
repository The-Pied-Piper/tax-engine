"""CA-ON 2025 end to end: return EK, Guide T4037's machinery example, situation C.

Return EK is `returns/2025_return_ek.yaml`: machinery bought in 2022 for $10,000, with $6,000 of UCC
at the start of 2025, sold in 2025 for $12,000. The recapture of CCA is $6,000 less the lesser of
$10,000 and $12,000, that is ($4,000), income; the capital gain is $12,000 - $10,000 = $2,000. The
guide's machinery is a business property; it is modelled on a T776 Area A row, whose column 5
proceeds of $10,000 are the filer's figure (the lesser). Situations A and B are not built.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    NET_RENTAL_INCOME,
    REAL_ESTATE_GAIN_OR_LOSS,
    RENTAL_CCA_TABLE_RECAPTURE,
    RENTAL_CLOSING_UCC,
    RENTAL_RECAPTURED_CCA,
    TAXABLE_CAPITAL_GAINS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# T776 Area A, the one row: Class 8 (a chosen class), UCC at the start 6,000.00, no additions,
# column 5 proceeds of 10,000.00 (the lesser of the capital cost and the 12,000 proceeds), no CCA
# claimed, no property left in the class.
MACHINERY_ROW = ("8", "6000.00", "0", "10000.00", "0", "0", "0", 1, "0", "0", "0", "0")

# Schedule 3 Part 3: proceeds 12,000, adjusted cost base (the capital cost) 10,000, no outlays.
SALE = ("12000", "10000", "0", 0)


def run_ek(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return EK's inputs, as in `returns/2025_return_ek.yaml`, with `overrides` over them."""
    inputs: dict[str, Any] = {
        "employment_income": "0",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "rental_statements": ({"rental_cca_classes_rows": (MACHINERY_ROW,)},),
        "real_estate_dispositions": (SALE,),
    }
    return run(**{**inputs, **overrides})


def test_the_recapture_of_cca_is_4000() -> None:
    result = run_ek()
    (t776,) = result["ca/t776"]

    # UCC 6,000.00 - lesser of capital cost 10,000 and proceeds 12,000 = 10,000.00: (4,000.00).
    assert t776.get(RENTAL_CCA_TABLE_RECAPTURE).value == D("4000.00")
    assert t776.get(RENTAL_RECAPTURED_CCA).value == D("4000.00")
    assert t776.get(NET_RENTAL_INCOME).value == D("4000.00")
    (closing,) = t776.get(RENTAL_CLOSING_UCC).value.records
    assert closing[CCA_CLASS_NUMBER] == D("8")
    assert closing[CCA_UCC_AT_END] == D("0.00")


def test_the_capital_gain_is_2000_and_the_taxable_gain_1000() -> None:
    (ret,) = run_ek()["ca-on/return"]

    assert ret.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("2000")  # 12,000 - 10,000
    assert ret.get(TAXABLE_CAPITAL_GAINS).value == D("1000.00")


def test_total_income_is_the_recapture_plus_the_taxable_gain() -> None:
    (ret,) = run_ek()["ca-on/return"]

    assert ret.get(NET_RENTAL_INCOME).value == D("4000.00")
    assert ret.get(TOTAL_INCOME).value == D("5000.00")  # 4,000.00 + 1,000.00


def test_proceeds_equal_to_the_ucc_leave_no_recapture() -> None:
    row = ("8", "6000.00", "0", "6000.00", "0", "0", "0", 1, "0", "0", "0", "0")
    (t776,) = run_ek(rental_statements=({"rental_cca_classes_rows": (row,)},))["ca/t776"]

    assert t776.get(RENTAL_RECAPTURED_CCA).value == D("0")
