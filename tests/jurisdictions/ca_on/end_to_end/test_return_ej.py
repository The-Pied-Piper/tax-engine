"""CA-ON 2025 end to end: return EJ, Guide T4037's duplex (Example 1), sold in 2025.

Return EJ is `returns/2025_return_ej.yaml`: the rented 40% of a duplex has a recapture of CCA of
$2,772 (T776), a gain of $15,800 on its building and land (Schedule 3 Part 3, taxable $7,900) and
the 60% lived in is designated for all 38 years owned (box 1), with no gain left. The T776 column 5
proceeds of $37,500 are the filer's figure, the lesser of the selling price less outlays ($52,640)
and the purchase price ($37,500), as in the guide.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    NET_RENTAL_INCOME,
    PRINCIPAL_RESIDENCE_DESIGNATION_BOX,
    PRINCIPAL_RESIDENCE_GAIN,
    REAL_ESTATE_GAIN_OR_LOSS,
    REAL_ESTATE_PROCEEDS,
    RENTAL_CCA_TABLE_RECAPTURE,
    RENTAL_CLOSING_UCC,
    RENTAL_RECAPTURED_CCA,
    TAXABLE_CAPITAL_GAINS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# T776 Area A, the one row (see `rental_cca_classes` in support.py): Class 1 (a chosen class), the
# UCC of the rented part of the building at the start of 2025 ($34,728, the guide's figure), no
# additions, column 5 proceeds of 37,500.00 (the lesser, the filer's figure), no CCA claimed and no
# property left in the class.
BUILDING_ROW = ("1", "34728.00", "0", "37500.00", "0", "0", "0", 1, "0", "0", "0", "0")

# Schedule 3 Part 3, the guide's two rows (proceeds, adjusted cost base, outlays): the rented
# building (56,000, 37,500, 3,360: a gain of 15,140) and the rented land (14,000, 12,500, 840: 660).
BUILDING_DISPOSITION = ("56000", "37500", "3360", 0)
LAND_DISPOSITION = ("14000", "12500", "840", 0)

# Form T2091(IND) for the 60% lived in: 38 years owned after 1981 (1988 to 2025), all designated;
# proceeds 105,000.00, outlays 6,300.00 and adjusted cost base 75,000.00 (60% of the totals), no
# "plus one" and no Part 2.
RESIDENCE = (38, 0, 38, 0, "105000.00", "6300.00", "75000.00", 0)


def run_ej(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return EJ's inputs, as in `returns/2025_return_ej.yaml`, with `overrides` over them."""
    inputs: dict[str, Any] = {
        "employment_income": "0",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "rental_statements": (
            {
                "rental_cca_classes_rows": (BUILDING_ROW,),
                "rental_land_dispositions": "14000.00",
            },
        ),
        "real_estate_dispositions": (BUILDING_DISPOSITION, LAND_DISPOSITION),
        "principal_residence_properties_rows": (RESIDENCE,),
    }
    return run(**{**inputs, **overrides})


def test_the_recapture_of_cca_is_2772() -> None:
    result = run_ej()
    (t776,) = result["ca/t776"]
    (ret,) = result["ca-on/return"]

    # UCC 34,728.00 - lesser of (56,000 - 3,360 = 52,640) and 37,500 = 37,500.00: (2,772.00).
    assert t776.get(RENTAL_CCA_TABLE_RECAPTURE).value == D("2772.00")
    assert t776.get(RENTAL_RECAPTURED_CCA).value == D("2772.00")
    assert t776.get(NET_RENTAL_INCOME).value == D("2772.00")
    assert ret.get(NET_RENTAL_INCOME).value == D("2772.00")
    (closing,) = t776.get(RENTAL_CLOSING_UCC).value.records
    assert closing[CCA_CLASS_NUMBER] == D("1")
    assert closing[CCA_UCC_AT_END] == D("0.00")


def test_schedule_3_part_3_gain_is_15800_and_the_taxable_gain_is_7900() -> None:
    (ret,) = run_ej()["ca-on/return"]

    assert ret.get(REAL_ESTATE_PROCEEDS).value == D("70000")
    assert ret.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("15800")  # 15,140 + 660
    assert ret.get(CAPITAL_GAIN).value == D("15800")
    assert ret.get(TAXABLE_CAPITAL_GAINS).value == D("7900.00")


def test_total_income_is_the_recapture_plus_the_taxable_gain() -> None:
    (ret,) = run_ej()["ca-on/return"]

    assert ret.get(TOTAL_INCOME).value == D("10672.00")  # 2,772.00 + 7,900.00


def test_the_building_alone_gains_15140_and_the_land_alone_660() -> None:
    (building,) = run_ej(real_estate_dispositions=(BUILDING_DISPOSITION,))["ca-on/return"]
    (land,) = run_ej(real_estate_dispositions=(LAND_DISPOSITION,))["ca-on/return"]

    assert building.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("15140")
    assert land.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("660")


def test_the_part_lived_in_is_box_1_with_no_gain_left() -> None:
    result = run_ej()
    (schedule_3,) = result["ca/schedule_3"]
    (ret,) = result["ca-on/return"]

    assert schedule_3.get(PRINCIPAL_RESIDENCE_DESIGNATION_BOX).value == 1
    # T2091 line 18 is 105,000 - (75,000 + 6,300) = 23,700; 38 of 38 years (plus one) exempt all.
    assert ret.get(PRINCIPAL_RESIDENCE_GAIN).value == D("0")


def test_the_part_lived_in_adds_nothing_to_income() -> None:
    (with_residence,) = run_ej()["ca-on/return"]
    (without,) = run_ej(principal_residence_properties_rows=())["ca-on/return"]

    assert with_residence.get(TOTAL_INCOME).value == without.get(TOTAL_INCOME).value
