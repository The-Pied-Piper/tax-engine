"""CA-ON 2025 end to end: return FT, the nine life events of Schedule 3 line 17906.

Return FT is `returns/2025_return_ft.yaml`: Return DT's condominium with line 17905 "Yes" and all
nine boxes of line 17906 ticked, so the flag is 0 and every checked tick box is 1. The tests here
tick each box alone, which no worked return does.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
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


def schedule_3(disposed: int, *ticked: int) -> Worksheet:
    """The worksheet of Schedule 3 Part 1 for line 17905 (1 for "Yes") and the boxes of line 17906
    ticked (numbered from 1); the return's other starting values are none."""
    boxes: dict[str, Any] = {
        f"flipped_property_life_event_{k}": int(k in ticked) for k in range(1, 10)
    }
    result = service().compute(
        CA_ON,
        2025,
        *starting("0", (), "0", "0", "0", "0", "0", flipped_property_disposed=disposed, **boxes),
    )
    (worksheet,) = result["ca/schedule_3"]
    return worksheet


@pytest.mark.parametrize("box", range(1, 10))
def test_each_box_ticked_alone_with_line_17905_yes_is_not_a_flipped_property(box: int) -> None:
    # Box k is condition k + 1 of the form: ticked alone, only its checked answer is 1 and only
    # its condition applies, so the count is 0.
    worksheet = schedule_3(1, box)
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    assert worksheet.get(FLIPPED_PROPERTY).value == 0
    assert [worksheet.get(kind).value for kind in CHECKED] == [int(k == box) for k in range(1, 10)]
    assert f"flipped_property: condition {box + 1} applies, so 0" in rendered


def test_all_nine_boxes_ticked_are_each_checked_and_the_flag_is_0() -> None:
    worksheet = schedule_3(1, *range(1, 10))
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    assert worksheet.get(FLIPPED_PROPERTY).value == 0
    assert [worksheet.get(kind).value for kind in CHECKED] == [1] * 9
    assert "flipped_property: conditions 2, 3, 4, 5, 6, 7, 8, 9, 10 apply, so 0" in rendered
