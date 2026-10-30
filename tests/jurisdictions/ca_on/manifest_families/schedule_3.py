"""The CA-ON manifest entries of Schedule 3 Part 1, flipped property (see `test_manifest.py` and
`test_manifest_schedule_3.py`).

Schedule 3 Part 1 is the form `ca/schedule_3`, a form of its own with no instances: it runs once
and reads the manifest inputs, the answer to line 17905 and the nine tick boxes of line 17906. Its
selections belong to the form (`FORM_STEPS` and `FORM_WIRING`), in the parts
`03h_schedule_3_flipped_property.yaml` and `27_schedule_3_life_event_checks.yaml`, not to the
return. The form exports the flag `ca/flipped_property`, the line 17900 box
`ca/principal_residence_designation_box` and the checked count of the life events ticked without a
"Yes" on line 17905, `ca/flipped_property_life_event_without_yes_checked` (`FORM_EXPORTS`). Nothing
on the return reads them, so the return declares no output for them
(`OUTPUTS` is empty) and selects no step of its own (`STEPS` and `WIRING` are empty). The ten
inputs are the return's inputs (`INPUTS`); the box step reads `ca/principal_residence_properties`,
a return input already.
"""

from __future__ import annotations

from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_designation_box import (
    PrincipalResidenceDesignationBoxCapability,
)
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    FLIPPED_PROPERTY,
    FLIPPED_PROPERTY_DISPOSED,
    FLIPPED_PROPERTY_DISPOSED_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_1,
    FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_2,
    FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_3,
    FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_4,
    FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_5,
    FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_6,
    FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_7,
    FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_8,
    FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_9,
    FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES,
    FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES_CHECKED,
    PRINCIPAL_RESIDENCE_DESIGNATION_BOX,
    PRINCIPAL_RESIDENCE_PROPERTIES,
)

# The ten inputs: line 17905 and boxes 1 to 9 of line 17906, each a 0 or 1 count.
INPUTS = frozenset(
    {
        "ca/flipped_property_disposed",
        "ca/flipped_property_life_event_1",
        "ca/flipped_property_life_event_2",
        "ca/flipped_property_life_event_3",
        "ca/flipped_property_life_event_4",
        "ca/flipped_property_life_event_5",
        "ca/flipped_property_life_event_6",
        "ca/flipped_property_life_event_7",
        "ca/flipped_property_life_event_8",
        "ca/flipped_property_life_event_9",
    }
)

# The form's exports: the flag, the form's own answer to whether the housing unit is a flipped
# property, line 17900, the principal residence designation box (1, 2 or 3; 0 with no property),
# and the checked count of the life event boxes ticked while line 17905 is not "Yes" (0 or 1).
FORM_EXPORTS = (
    "ca/flipped_property",
    "ca/principal_residence_designation_box",
    "ca/flipped_property_life_event_without_yes_checked",
)

# Nothing on the return reads the flag, so the return declares no output for the form.
OUTPUTS: frozenset[str] = frozenset()

# The return selects no step of its own: its Schedule 3 Part 1 lines are the form's.
STEPS: set[CapabilitySelection] = set()

FORM_STEPS = {
    # Form 5000-S3 Part 1, page 1, "Line 17905: Did you dispose of a housing unit, or a right to
    # acquire a housing unit, located in Canada (including a rental property) that was not
    # considered inventory and was owned for less than 365 consecutive days before the disposition?
    # Yes or No": the answer taken as a count, 1 for "Yes" and 0 for "No", checked to be 0 or 1
    # before the count that reads it (line 17905 is a yes or no answer, not a dollars-and-cents
    # line).
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_disposed"},
        produces={"output": "ca/flipped_property_disposed_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 1: the death of the taxpayer or a related
    # person": a tick box, 1 when ticked and 0 when not, checked to be 0 or 1 before the count that
    # reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_1"},
        produces={"output": "ca/flipped_property_life_event_1_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 2: a related person joining the taxpayer's
    # household or the taxpayer joining a related person's household (for example, birth of a child,
    # adoption, or care of an elderly parent)": a tick box, 1 when ticked and 0 when not, checked to
    # be 0 or 1 before the count that reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_2"},
        produces={"output": "ca/flipped_property_life_event_2_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 3: the breakdown of a marriage or common-law
    # partnership where the taxpayer had been living separate and apart from their spouse or
    # common-law partner for at least 90 days before the disposition": a tick box, 1 when ticked and
    # 0 when not, checked to be 0 or 1 before the count that reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_3"},
        produces={"output": "ca/flipped_property_life_event_3_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 4: a threat to the personal safety of the
    # taxpayer or a related person (for example, domestic violence)": a tick box, 1 when ticked and
    # 0 when not, checked to be 0 or 1 before the count that reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_4"},
        produces={"output": "ca/flipped_property_life_event_4_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 5: a serious disability or illness of the
    # taxpayer or a related person": a tick box, 1 when ticked and 0 when not, checked to be 0 or 1
    # before the count that reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_5"},
        produces={"output": "ca/flipped_property_life_event_5_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 6: the eligible relocation of the taxpayer or
    # their spouse or common-law partner where the taxpayer's new home (including area code): is at
    # least 40 kilometres closer to the new work (including area code): location or school
    # (generally, an eligible relocation allows the taxpayer to carry on business, be employed, or
    # attend full-time post-secondary education)": a tick box, 1 when ticked and 0 when not, checked
    # to be 0 or 1 before the count that reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_6"},
        produces={"output": "ca/flipped_property_life_event_6_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 7: the involuntary termination of employment of
    # the taxpayer or their spouse or common-law partner": a tick box, 1 when ticked and 0 when not,
    # checked to be 0 or 1 before the count that reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_7"},
        produces={"output": "ca/flipped_property_life_event_7_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 8: the insolvency of the taxpayer (for example,
    # due to an accumulation of debt)": a tick box, 1 when ticked and 0 when not, checked to be 0 or
    # 1 before the count that reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_8"},
        produces={"output": "ca/flipped_property_life_event_8_checked"},
    ),
    # Form 5000-S3 Part 1, page 2, line 17906 "Box 9: the destruction or expropriation of the
    # taxpayer's property (for example, when the property is destroyed due to natural or man-made
    # disaster)": a tick box, 1 when ticked and 0 when not, checked to be 0 or 1 before the count
    # that reads it.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/flipped_property_life_event_9"},
        produces={"output": "ca/flipped_property_life_event_9_checked"},
    ),
    # Form 5000-S3 Part 1, line 17900 "Line 17900: Box 1: I designate the property as my
    # principal residence for all of the years that I owned it or for all of the years that I owned
    # it except one year. Box 2: I designate the property as my principal residence for some but not
    # all of the years that I owned it. Box 3: I designate the properties as my principal residences
    # for some or all of the years that I owned them.": the box from the consumed properties, 0 when
    # there is no property, 3 when there is more than one, and for one property 1 when the years
    # designated (lines 3) are at least the years owned (line 7) less one, else 2. Its own form's
    # figure, not on the return (see `FORM_EXPORTS`).
    CapabilitySelection(
        name="ca/principal_residence_designation_box",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_designation_box"},
    ),
    # Form 5000-S3 Part 1 "If you ticked "no", the housing unit is not considered a flipped
    # property." (line 17905), "If any of the life events above apply to you, the housing unit is
    # not considered a flipped property." and "If none of the life events above apply to you, the
    # housing unit is considered a flipped property and the gain is taxable as business income."
    # (line 17906): a count of 0 when line 17905 is "No" or a box of line 17906 is ticked, and 1
    # when none applies, so the flag is 1 only for a housing unit that is a flipped property.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/schedule_3_flipped_property_conditions"},
        consumes={
            "counts": (
                "ca/flipped_property_disposed_checked",
                "ca/flipped_property_life_event_1_checked",
                "ca/flipped_property_life_event_2_checked",
                "ca/flipped_property_life_event_3_checked",
                "ca/flipped_property_life_event_4_checked",
                "ca/flipped_property_life_event_5_checked",
                "ca/flipped_property_life_event_6_checked",
                "ca/flipped_property_life_event_7_checked",
                "ca/flipped_property_life_event_8_checked",
                "ca/flipped_property_life_event_9_checked",
            ),
            "amounts": (),
        },
        produces={"output": "ca/flipped_property"},
    ),
    # Form 5000-S3 Part 1, page 1, line 17905: "If you ticked "yes", continue at line 17906 on the
    # next page.", and page 2, line 17906: a box ticked while line 17905 is not "Yes" is refused (an
    # input error), the guard of this form, not a rule the form prints. The count is 1 when line
    # 17905 is "No" (0) and a box of line 17906 is ticked (1), else 0, from the same ten checked
    # answers in the same order as the flag.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/schedule_3_life_event_without_yes"},
        consumes={
            "counts": (
                "ca/flipped_property_disposed_checked",
                "ca/flipped_property_life_event_1_checked",
                "ca/flipped_property_life_event_2_checked",
                "ca/flipped_property_life_event_3_checked",
                "ca/flipped_property_life_event_4_checked",
                "ca/flipped_property_life_event_5_checked",
                "ca/flipped_property_life_event_6_checked",
                "ca/flipped_property_life_event_7_checked",
                "ca/flipped_property_life_event_8_checked",
                "ca/flipped_property_life_event_9_checked",
            ),
            "amounts": (),
        },
        produces={"output": "ca/flipped_property_life_event_without_yes"},
    ),
    # The count above is refused when it is 1, the input error naming the box ticked without a
    # "Yes" on line 17905 (not capped, and not a printed line). Its checked count is the form's
    # export, read by nothing on the return.
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/schedule_3_life_event_without_yes_refused"},
        consumes={"count": "ca/flipped_property_life_event_without_yes"},
        produces={"output": "ca/flipped_property_life_event_without_yes_checked"},
    ),
}

FORM_WIRING = {
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_DISPOSED}),
        frozenset({FLIPPED_PROPERTY_DISPOSED_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_1}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_2}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_3}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_4}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_5}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_6}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_7}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_8}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_9}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                FLIPPED_PROPERTY_DISPOSED_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED,
            }
        ),
        frozenset({FLIPPED_PROPERTY}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                FLIPPED_PROPERTY_DISPOSED_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED,
                FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED,
            }
        ),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES}),
    ),
    (
        CountRefusedByConditions,
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES}),
        frozenset({FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES_CHECKED}),
    ),
    (
        PrincipalResidenceDesignationBoxCapability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_DESIGNATION_BOX}),
    ),
}

WIRING: set[object] = set()
