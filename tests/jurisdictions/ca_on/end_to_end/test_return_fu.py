"""CA-ON 2025 end to end: return FU, Schedule 3 line 17905 answered "No".

Return FU is `returns/2025_return_fu.yaml`: Return DT's condominium owned 365 days or more, so
line 17905 is "No", the boxes of line 17906 are blank, the flag is 0 and every checked answer is 0.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FLIPPED_PROPERTY,
    FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, service, starting

CHECKED = (
    FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED,
)


def schedule_3(disposed: int) -> Worksheet:
    """The worksheet of Schedule 3 Part 1 for line 17905 (1 for "Yes") with every box blank."""
    result = service().compute(
        CA_ON, 2025, *starting("0", (), "0", "0", "0", "0", "0", flipped_property_disposed=disposed)
    )
    (worksheet,) = result["ca/schedule_3"]
    return worksheet


def test_line_17905_no_with_the_boxes_blank_checks_each_box_as_0() -> None:
    worksheet = schedule_3(0)

    assert worksheet.get(FLIPPED_PROPERTY).value == 0
    assert [worksheet.get(kind).value for kind in CHECKED] == [0] * 9
