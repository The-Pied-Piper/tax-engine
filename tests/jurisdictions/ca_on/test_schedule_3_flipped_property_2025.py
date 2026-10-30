"""The 2025 conditions dataset of Schedule 3 Part 1, flipped property, checked against the form.

Schedule 3 (2025), Part 1, page 1, line 17905: "If you ticked "no", the housing unit is not
considered a flipped property." Page 2, line 17906: "If any of the life events above apply to you,
the housing unit is not considered a flipped property." and "If none of the life events above apply
to you, the housing unit is considered a flipped property and the gain is taxable as business
income."

A housing unit is a flipped property when line 17905 is "Yes" and no life event of line 17906 is
ticked, so the flag is 1 then and 0 otherwise. The conditions are copied in the form's order: line
17905 answered "No" (the count of position 1 equals 0), then each of the nine boxes of line 17906
ticked (the count of positions 2 to 10 equals 1). Any one of them applies, so the count when any
applies is 0 and the count when none applies is 1. Each count is a checked answer (0 or 1). The
flag is a count, not a dollars-and-cents line, so nothing is rounded.

A box of line 17906 ticked while line 17905 is not "Yes" is refused. The count of those (the
conditions `ca/schedule_3_life_event_without_yes`) is 1 when line 17905 is "No" and a box is ticked,
and the refused conditions (`ca/schedule_3_life_event_without_yes_refused`) refuse a count of 1. The
behaviour of the two counts together is tested with made-up kinds, as the flag is.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
S3_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s3/5000-s3-25e.txt"

CONDITIONS_FAMILY = "ca/schedule_3_flipped_property_conditions"
WITHOUT_YES_FAMILY = "ca/schedule_3_life_event_without_yes"
REFUSED_FAMILY = "ca/schedule_3_life_event_without_yes_refused"

# The wording of the two datasets: the condition of the count (line 17905 "No" and a box ticked),
# and the refusal of a count of 1 (a box ticked without a "Yes" on line 17905). The form prints no
# such rule; the refusal is the guard of this check.
WITHOUT_YES_TEXT = 'line 17905 is "No" and a box of line 17906 is ticked'
REFUSED_TEXT = 'a box of line 17906 is ticked without a "Yes" on line 17905'

NO_TEXT = 'If you ticked "no", the housing unit is not considered a flipped property.'

# Line 17906, the nine boxes, each condition's text word for word from the form.
BOX_TEXTS = (
    "Box 1: the death of the taxpayer or a related person",
    "Box 2: a related person joining the taxpayer's household or the taxpayer joining a related "
    "person's household (for example, birth of a child, adoption, or care of an elderly parent)",
    "Box 3: the breakdown of a marriage or common-law partnership where the taxpayer had been "
    "living separate and apart from their spouse or common-law partner for at least 90 days before "
    "the disposition",
    "Box 4: a threat to the personal safety of the taxpayer or a related person (for example, "
    "domestic violence)",
    "Box 5: a serious disability or illness of the taxpayer or a related person",
    "Box 6: the eligible relocation of the taxpayer or their spouse or common-law partner where "
    "the taxpayer's new home (including area code): is at least 40 kilometres closer to the new "
    "work (including area code): location or school (generally, an eligible relocation allows the "
    "taxpayer to carry on business, be employed, or attend full-time post-secondary education)",
    "Box 7: the involuntary termination of employment of the taxpayer or their spouse or "
    "common-law partner",
    "Box 8: the insolvency of the taxpayer (for example, due to an accumulation of debt)",
    "Box 9: the destruction or expropriation of the taxpayer's property (for example, when the "
    "property is destroyed due to natural or man-made disaster)",
)

# Made up for this test and not registered: the ten checked answers and the flag.
DISPOSED_CHECKED = ArtifactKind("ex/schedule_3_disposed_checked", int)
LIFE_EVENT_CHECKED = tuple(
    ArtifactKind(f"ex/schedule_3_life_event_{position}_checked", int) for position in range(1, 10)
)
FLAG = ArtifactKind("ex/schedule_3_flipped_property", int)


def _ticked(position: int, text: str) -> Condition:
    """The condition that the count at `position` is 1, a box ticked."""
    return Condition(
        text, (ConditionPart((ConditionTest("count", position, "equal_to", D("1"), None),)),)
    )


def test_2025_the_flipped_property_conditions_are_the_ten_printed_conditions_in_form_order() -> (
    None
):
    data = SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        0,
        (
            Condition(
                NO_TEXT,
                (ConditionPart((ConditionTest("count", 1, "equal_to", D("0"), None),)),),
            ),
            *(_ticked(position, text) for position, text in enumerate(BOX_TEXTS, start=2)),
        ),
    )


def test_2025_a_flipped_property_is_0_when_any_condition_applies_and_1_when_none_does() -> None:
    data = SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS)

    assert data.values.count_when_any_applies == 0
    assert data.values.count_when_none_applies == 1


def test_2025_the_conditions_read_the_ten_checked_answers_and_no_amount() -> None:
    data = SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS)

    assert data.values.count_positions_read == frozenset(range(1, 11))
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_flag_is_a_count_so_nothing_is_rounded() -> None:
    data = SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING


def test_2025_the_conditions_cite_the_form_they_are_printed_on() -> None:
    data = SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS)

    assert S3_TXT in data.sources


def _boxes(*ticked: int) -> tuple[int, ...]:
    """The nine tick boxes of line 17906, 1 for each box ticked, boxes numbered from 1."""
    return tuple(1 if box in ticked else 0 for box in range(1, 10))


@pytest.mark.parametrize(
    ("disposed", "boxes", "flag"),
    [
        # Line 17905 "No": not a flipped property, whatever the boxes say.
        (0, _boxes(), 0),
        (0, _boxes(1, 2, 3, 4, 5, 6, 7, 8, 9), 0),
        (0, _boxes(6), 0),
        # Line 17905 "Yes" and no life event ticked: a flipped property.
        (1, _boxes(), 1),
        # Line 17905 "Yes" and a life event ticked (box 6, the eligible relocation): not one.
        (1, _boxes(6), 0),
        (1, _boxes(1, 9), 0),
    ],
)
def test_the_flag_follows_line_17905_and_the_life_event_boxes(
    disposed: int, boxes: tuple[int, ...], flag: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS),
        (DISPOSED_CHECKED, *LIFE_EVENT_CHECKED),
        (),
        FLAG,
    )
    inputs = tuple(
        Artifact(kind, value)
        for kind, value in zip(
            (DISPOSED_CHECKED, *LIFE_EVENT_CHECKED), (disposed, *boxes), strict=True
        )
    )

    result = capability.compute(inputs).outputs

    assert result == (Artifact(FLAG, flag),)


@pytest.mark.parametrize("box", range(1, 10))
def test_each_life_event_box_alone_with_line_17905_yes_gives_0(box: int) -> None:
    capability = CountByConditions(
        SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS),
        (DISPOSED_CHECKED, *LIFE_EVENT_CHECKED),
        (),
        FLAG,
    )
    inputs = tuple(
        Artifact(kind, value)
        for kind, value in zip(
            (DISPOSED_CHECKED, *LIFE_EVENT_CHECKED), (1, *_boxes(box)), strict=True
        )
    )

    result = capability.compute(inputs).outputs

    assert result == (Artifact(FLAG, 0),)


# --- a box ticked while line 17905 is not "Yes" -------------------------------------------------

# Made up for this test and not registered: the count of the life events ticked without a "Yes"
# and its checked count.
WITHOUT_YES = ArtifactKind("ex/schedule_3_ticked_without_yes", int)
WITHOUT_YES_CHECKED = ArtifactKind("ex/schedule_3_ticked_without_yes_checked", int)


def _answers(disposed: int, boxes: tuple[int, ...]) -> tuple[Artifact[Any], ...]:
    """The ten checked answers, in the order of the conditions: line 17905, then boxes 1 to 9."""
    kinds = (DISPOSED_CHECKED, *LIFE_EVENT_CHECKED)
    return tuple(
        Artifact(kind, value) for kind, value in zip(kinds, (disposed, *boxes), strict=True)
    )


def without_yes_checked(disposed: int, boxes: tuple[int, ...]) -> int:
    """The checked count of the boxes ticked without a "Yes": the count from the ten answers, then
    the refusal of a count of 1 (which raises)."""
    counted = CountByConditions(
        SOURCE.get(WITHOUT_YES_FAMILY, 2025, CONDITIONS),
        (DISPOSED_CHECKED, *LIFE_EVENT_CHECKED),
        (),
        WITHOUT_YES,
    )
    refused = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), WITHOUT_YES, WITHOUT_YES_CHECKED
    )
    (count,) = counted.compute(_answers(disposed, boxes)).outputs
    (checked,) = refused.compute((count,)).outputs
    return int(checked.value)


def flag_of(disposed: int, boxes: tuple[int, ...]) -> int:
    """The flipped property flag for the ten answers, as the flag test above computes it."""
    capability = CountByConditions(
        SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS),
        (DISPOSED_CHECKED, *LIFE_EVENT_CHECKED),
        (),
        FLAG,
    )
    (flag,) = capability.compute(_answers(disposed, boxes)).outputs
    return int(flag.value)


@pytest.mark.parametrize("box", range(1, 10))
def test_a_box_ticked_with_line_17905_no_is_refused_naming_the_box_without_yes_text(
    box: int,
) -> None:
    message = f"{WITHOUT_YES.identifier} 1 is refused: {REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        without_yes_checked(0, _boxes(box))


def test_all_nine_boxes_ticked_with_line_17905_no_is_refused() -> None:
    message = f"{WITHOUT_YES.identifier} 1 is refused: {REFUSED_TEXT}"

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        without_yes_checked(0, _boxes(1, 2, 3, 4, 5, 6, 7, 8, 9))


@pytest.mark.parametrize(
    ("disposed", "boxes", "flag"),
    [
        # Line 17905 "No" and no box ticked: not a flipped property, and nothing is refused.
        (0, _boxes(), 0),
        # Line 17905 "Yes" and a box ticked (box 6): not a flipped property, and nothing refused.
        (1, _boxes(6), 0),
        # Line 17905 "Yes" and no box ticked: a flipped property, and nothing is refused.
        (1, _boxes(), 1),
    ],
)
def test_the_check_passes_and_the_flag_is_kept_unless_a_box_is_ticked_with_no(
    disposed: int, boxes: tuple[int, ...], flag: int
) -> None:
    assert without_yes_checked(disposed, boxes) == 0
    assert flag_of(disposed, boxes) == flag


def test_a_box_of_2_is_still_refused_by_the_yes_or_no_count_before_the_check() -> None:
    # The answer of a box is checked to be 0 or 1 by `ca/yes_or_no_count` before the count reads
    # it, so a 2 is refused there, as an input above its bound, and never reaches the check.
    raw = ArtifactKind("ex/schedule_3_box_raw", int)
    checked = ArtifactKind("ex/schedule_3_box_raw_checked", int)

    with pytest.raises(InputAboveBoundError, match=re.escape("ex/schedule_3_box_raw 2")):
        YesOrNoCount(raw, checked).compute((Artifact(raw, 2),))


# --- the datasets of the two counts -------------------------------------------------------------


def test_2025_a_life_event_without_yes_is_one_condition_of_a_no_and_a_ticked_box() -> None:
    data = SOURCE.get(WITHOUT_YES_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                WITHOUT_YES_TEXT,
                (
                    ConditionPart((ConditionTest("count", 1, "equal_to", D("0"), None),)),
                    ConditionPart(
                        tuple(
                            ConditionTest("count", position, "equal_to", D("1"), None)
                            for position in range(2, 11)
                        )
                    ),
                ),
            ),
        ),
    )


def test_2025_a_life_event_without_yes_is_1_when_its_condition_applies_and_0_otherwise() -> None:
    values = SOURCE.get(WITHOUT_YES_FAMILY, 2025, CONDITIONS).values

    assert values.count_when_any_applies == 1
    assert values.count_when_none_applies == 0
    assert values.count_positions_read == frozenset(range(1, 11))
    assert values.amount_positions_read == frozenset()


def test_2025_the_life_event_without_yes_count_is_not_rounded_and_cites_the_form() -> None:
    data = SOURCE.get(WITHOUT_YES_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert S3_TXT in data.sources


def test_2025_the_refusal_refuses_a_count_of_1_at_position_1_and_nothing_else() -> None:
    data = SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                REFUSED_TEXT,
                (ConditionPart((ConditionTest("count", 1, "equal_to", D("1"), None),)),),
            ),
        ),
    )
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    assert data.rounding == NO_ROUNDING
    assert S3_TXT in data.sources
