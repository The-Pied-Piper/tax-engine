"""CA-ON 2025 end to end: return DT, the flipped property of Schedule 3 Part 1.

Return DT is `returns/2025_return_dt.yaml`: a condominium sold within 365 days of being owned, with
no life event ticked, so it is a flipped property and the flag is 1. The other tests here vary the
answers, with the same starting inputs: line 17905 "No", and box 6 (the eligible relocation) ticked
with line 17905 "Yes". Each run gives the form's inputs to the shared starting values.
"""

from __future__ import annotations

import re

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FLIPPED_PROPERTY,
    FLIPPED_PROPERTY_DISPOSED_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_1,
    FLIPPED_PROPERTY_LIFE_EVENT_2,
    FLIPPED_PROPERTY_LIFE_EVENT_3,
    FLIPPED_PROPERTY_LIFE_EVENT_4,
    FLIPPED_PROPERTY_LIFE_EVENT_5,
    FLIPPED_PROPERTY_LIFE_EVENT_6,
    FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_7,
    FLIPPED_PROPERTY_LIFE_EVENT_8,
    FLIPPED_PROPERTY_LIFE_EVENT_9,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, service, starting

LIFE_EVENTS = (
    FLIPPED_PROPERTY_LIFE_EVENT_1,
    FLIPPED_PROPERTY_LIFE_EVENT_2,
    FLIPPED_PROPERTY_LIFE_EVENT_3,
    FLIPPED_PROPERTY_LIFE_EVENT_4,
    FLIPPED_PROPERTY_LIFE_EVENT_5,
    FLIPPED_PROPERTY_LIFE_EVENT_6,
    FLIPPED_PROPERTY_LIFE_EVENT_7,
    FLIPPED_PROPERTY_LIFE_EVENT_8,
    FLIPPED_PROPERTY_LIFE_EVENT_9,
)

# Line 17905 "No" is condition 1 and the boxes of line 17906 are conditions 2 to 10 (box k is
# condition k + 1), in the trace's wording.
NO_CONDITION_LINE = (
    'flipped_property: condition 1 "If you ticked "no", the housing unit is not considered a '
    'flipped property.": flipped_property_disposed_checked 1, does not apply'
)


def schedule_3(disposed: int, *ticked: int) -> Worksheet:
    """The worksheet of Schedule 3 Part 1 of return DT, for line 17905 (1 for "Yes") and the boxes
    of line 17906 ticked (numbered from 1); the return's other starting values are none."""
    result = service().compute(
        CA_ON,
        2025,
        *starting(
            "0",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            flipped_property_disposed=disposed,
            flipped_property_life_event_1=int(1 in ticked),
            flipped_property_life_event_2=int(2 in ticked),
            flipped_property_life_event_3=int(3 in ticked),
            flipped_property_life_event_4=int(4 in ticked),
            flipped_property_life_event_5=int(5 in ticked),
            flipped_property_life_event_6=int(6 in ticked),
            flipped_property_life_event_7=int(7 in ticked),
            flipped_property_life_event_8=int(8 in ticked),
            flipped_property_life_event_9=int(9 in ticked),
        ),
    )
    (worksheet,) = result["ca/schedule_3"]
    return worksheet


def test_a_disposition_within_365_days_with_no_life_event_is_a_flipped_property() -> None:
    worksheet = schedule_3(1)
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    assert worksheet.get(FLIPPED_PROPERTY_DISPOSED_CHECKED).value == 1
    assert worksheet.get(FLIPPED_PROPERTY).value == 1
    # The trace: the answer to line 17905, each condition (none applies), then the count of 1.
    assert (
        "flipped_property_disposed_checked: flipped_property_disposed 1, "
        "a yes or no answer of 0 or 1"
    ) in rendered
    assert NO_CONDITION_LINE in rendered
    assert "flipped_property: no condition applies, so 1" in rendered


def test_line_17905_no_with_no_box_ticked_is_not_a_flipped_property() -> None:
    assert schedule_3(0).get(FLIPPED_PROPERTY).value == 0

    rendered = EnglishTraceRenderer().render_all(schedule_3(0).trace)
    assert "flipped_property: condition 1 applies, so 0" in rendered


@pytest.mark.parametrize("ticked", [(6,), (1, 2, 3, 4, 5, 6, 7, 8, 9)])
def test_line_17905_no_with_a_box_ticked_is_refused_not_computed(ticked: tuple[int, ...]) -> None:
    # A box of line 17906 is asked only after a "Yes" on line 17905: with "No" a ticked box is an
    # input error, naming the condition, not a flag of 0.
    message = (
        "ca/flipped_property_life_event_without_yes 1 is refused: a box of line 17906 is ticked "
        'without a "Yes" on line 17905'
    )

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        schedule_3(0, *ticked)


def test_box_6_the_eligible_relocation_ticked_with_line_17905_yes_is_not_a_flipped_property() -> (
    None
):
    worksheet = schedule_3(1, 6)
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    assert worksheet.get(FLIPPED_PROPERTY).value == 0
    assert worksheet.get(FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED).value == 1
    # Box 6 is condition 7 of the form: its line is the printed condition, which applies.
    assert (
        "flipped_property_life_event_6_checked: flipped_property_life_event_6 1, "
        "a yes or no answer of 0 or 1"
    ) in rendered
    assert any(
        line.startswith('flipped_property: condition 7 "Box 6: the eligible relocation')
        and line.endswith(": flipped_property_life_event_6_checked 1, applies")
        for line in rendered
    )
    assert "flipped_property: condition 7 applies, so 0" in rendered


def test_a_tick_above_1_is_refused() -> None:
    # Line 17905 and each box of line 17906 is a yes or no answer: 2 is an input error.
    with pytest.raises(InputAboveBoundError, match="flipped_property_disposed 2"):
        service().compute(
            CA_ON, 2025, *starting("0", (), "0", "0", "0", "0", "0", flipped_property_disposed=2)
        )
    with pytest.raises(InputAboveBoundError, match="flipped_property_life_event_6 2"):
        service().compute(
            CA_ON,
            2025,
            *starting("0", (), "0", "0", "0", "0", "0", flipped_property_life_event_6=2),
        )
