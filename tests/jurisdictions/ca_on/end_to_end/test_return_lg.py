"""CA-ON 2025 end to end: return lg (Guide T4036 "Non-arm's length transactions", Teresa's example).

Guide T4036 (2025): "Teresa bought a refrigerator from her father, Roman, for $400 to use in her
rental operation. Roman paid $1,000 for the refrigerator and was using it in his rental
operations. Since the amount Teresa paid is less than the amount Roman paid, we consider Teresa's
cost to be $1,000. [...] In Area B, Teresa enters $1,000 in column 3, "Total cost." In Area A, she
enters $400 in column 3, "Cost of additions in the year," as the addition for the current tax
year."

The worked return `returns/2025_return_lg.yaml` (checked by `test_worked_returns.py`) pins the
figure CRA prints: Area B line 9925 of 1000. This module reads the two totals of Areas B and C,
the personal portion of column 4, and a personal portion above the total cost.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    RENTAL_BUILDING_ADDITIONS_TOTAL,
    RENTAL_CLOSING_UCC,
    RENTAL_EQUIPMENT_ADDITIONS_TOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, RentalCcaRow, rental_return

# The Guide prints no class and no rent: gross rents of 5000 and class 8 are chosen.
TERESA = {"rental_properties": ((1, "0", "5000"),)}

# Area A: class 8, no UCC at the start, the $400 Teresa paid as additions and no CCA claimed (the
# worked return also marks the additions as exempt from the half-year rule; no claim is made here,
# so the closing UCC does not depend on it).
REFRIGERATOR: RentalCcaRow = ("8", "0", "400", "0", "0", "0", "0", 0, "0", "0", "0", "0")

# Area B, the refrigerator: class 8, total cost 1000 (Roman's cost), no personal portion.
AREA_B = (("8", "1000", "0"),)


def teresa(
    equipment: tuple[tuple[str, str, str], ...] = AREA_B,
    buildings: tuple[tuple[str, str, str], ...] = (),
) -> Worksheet:
    return rental_return(
        TERESA,
        {
            "rental_cca_classes_rows": (REFRIGERATOR,),
            "rental_equipment_additions_rows": equipment,
            "rental_building_additions_rows": buildings,
        },
    )["ca/t776"][0]


def test_teresas_total_equipment_additions_are_1000_and_area_a_keeps_her_400() -> None:
    worksheet = teresa()

    assert worksheet.get(RENTAL_EQUIPMENT_ADDITIONS_TOTAL).value == D("1000")
    assert worksheet.get(RENTAL_BUILDING_ADDITIONS_TOTAL).value == D("0")
    (closing,) = worksheet.get(RENTAL_CLOSING_UCC).value.records
    assert closing[CCA_CLASS_NUMBER] == D("8")
    assert closing[CCA_UCC_AT_END] == D("400")


def test_the_personal_portion_of_column_4_is_taken_off_the_cost_of_column_3() -> None:
    # Column 5 "Rental portion (column 3 minus column 4)": 1000 less 250 is 750.
    worksheet = teresa(equipment=(("8", "1000", "250"),))

    assert worksheet.get(RENTAL_EQUIPMENT_ADDITIONS_TOTAL).value == D("750")


def test_area_c_adds_the_rental_portion_of_each_building() -> None:
    # Two buildings: 60000 and 40000 less a personal portion of 10000; 90000 in all.
    worksheet = teresa(buildings=(("1", "60000", "0"), ("1", "40000", "10000")))

    assert worksheet.get(RENTAL_BUILDING_ADDITIONS_TOTAL).value == D("90000")
    assert worksheet.get(RENTAL_EQUIPMENT_ADDITIONS_TOTAL).value == D("1000")


def test_a_personal_portion_above_the_total_cost_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="item 1: the personal portion"):
        teresa(equipment=(("8", "1000", "1000.01"),))
