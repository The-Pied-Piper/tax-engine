"""A yes or no flag above 1 is refused on the whole return, and 1 is accepted as the checked count.

Each of the 28 flags that `ca/yes_or_no_count` checks (`30_yes_or_no_flag_checks.yaml`,
including Schedule 8 Parts 4 and 5 completed, and `05t_t929_yes_or_no_flag_check.yaml` for the
FHSA flag) is set to 2 on an otherwise valid return, which is refused with
`InputAboveBoundError`, and set to 1 it is accepted as the checked count of 1. A count of 2 is an
input error, not a "no" that quietly changes the return.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AGED_18_OR_OLDER_AT_END_OF_2025,
    AGED_18_OR_OLDER_AT_END_OF_2025_CHECKED,
    AGED_19_OR_OLDER_AT_END_OF_2025,
    AGED_19_OR_OLDER_AT_END_OF_2025_CHECKED,
    BORN_IN_1960_OR_EARLIER,
    BORN_IN_1960_OR_EARLIER_CHECKED,
    CONFINED_TO_PRISON_FOR_90_DAYS,
    CONFINED_TO_PRISON_FOR_90_DAYS_CHECKED,
    CPP_PART_4_COMPLETED,
    CPP_PART_4_COMPLETED_YES_OR_NO_CHECKED,
    CPP_PART_5_COMPLETED,
    CPP_PART_5_COMPLETED_YES_OR_NO_CHECKED,
    DEPENDANT_CAREGIVER_AGED_18_OR_OLDER,
    DEPENDANT_CAREGIVER_AGED_18_OR_OLDER_CHECKED,
    DEPENDANT_CAREGIVER_ELIGIBLE,
    DEPENDANT_CAREGIVER_ELIGIBLE_CHECKED,
    EI_SPECIAL_BENEFITS_AGREEMENT,
    EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED,
    ELIGIBLE_FOR_DISABILITY_AMOUNT,
    ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED,
    EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY,
    EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY_CHECKED,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED,
    FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS,
    FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS_CHECKED,
    PENSION_ANNUITY_CONDITIONS_MET,
    PENSION_ANNUITY_CONDITIONS_MET_CHECKED,
    RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025,
    RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025_CHECKED,
    RESIDENT_IN_CANADA_THROUGHOUT_2025,
    RESIDENT_IN_CANADA_THROUGHOUT_2025_CHECKED,
    RESP_AIPS_PART_A_APPLIES,
    RESP_AIPS_PART_A_APPLIES_CHECKED,
    SEARCH_AND_RESCUE_CONDITIONS_MET,
    SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED,
    SPOUSE_CAREGIVER_ELIGIBLE,
    SPOUSE_CAREGIVER_ELIGIBLE_CHECKED,
    SPOUSE_NOT_SEPARATED_90_DAYS,
    SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED,
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31,
    SPOUSES_CLAIMED,
    SPOUSES_CLAIMED_CHECKED,
    T657_CHART_2016_USES_D_INSTEAD,
    T657_CHART_2016_USES_D_INSTEAD_CHECKED,
    T657_CHART_2017_USES_D_INSTEAD,
    T657_CHART_2017_USES_D_INSTEAD_CHECKED,
    T657_CHART_2018_USES_D_INSTEAD,
    T657_CHART_2018_USES_D_INSTEAD_CHECKED,
    T657_CHART_2019_USES_D_INSTEAD,
    T657_CHART_2019_USES_D_INSTEAD_CHECKED,
    T657_CHART_2020_USES_D_INSTEAD,
    T657_CHART_2020_USES_D_INSTEAD_CHECKED,
    T657_CHART_2021_USES_D_INSTEAD,
    T657_CHART_2021_USES_D_INSTEAD_CHECKED,
    T657_CHART_2022_USES_D_INSTEAD,
    T657_CHART_2022_USES_D_INSTEAD_CHECKED,
    T657_CHART_2023_USES_D_INSTEAD,
    T657_CHART_2023_USES_D_INSTEAD_CHECKED,
    UNDER_18_ON_DECEMBER_31,
    UNDER_18_ON_DECEMBER_31_CHECKED,
    VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET,
    VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    CLAIMS_SENIORS_CARE_CREDIT,
    CLAIMS_SENIORS_CARE_CREDIT_CHECKED,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, service, starting

# The other inputs the return needs for the flag at 1 to be consistent: an under-18 filer is not
# also 18 or older, the Canada caregiver amount for a spouse needs the spouse amount claimed (line
# 30300), and the one for a dependant needs an eligible dependant (line 30400).
COMPANIONS: dict[str, dict[str, Any]] = {
    "under_18_on_december_31": {"aged_18_or_older_at_end_of_2025": 0},
    "spouse_caregiver_eligible": {"spouses_claimed": 1},
    "dependant_caregiver_eligible": {"eligible_dependants": 1},
    # Part 4 is for filers with no employment income (Schedule 8 Part 4 heading): a Part 4 at 1 is
    # refused on a return with T4 pensionable earnings, so the filer here has none on a T4.
    # The contributions on the T4 are nil with the earnings (they are bounded by the earnings).
    "cpp_part_4_completed": {
        "t4_cpp_pensionable_earnings_outside_quebec": "0",
        "cpp_t4_base_and_first_additional_contributions": "0",
        "cpp_t4_second_additional_contributions": "0",
    },
}

# The flag's short name, its input kind and its checked kind, one row per flag checked.
YES_OR_NO_FLAGS: tuple[tuple[str, ArtifactKind[int], ArtifactKind[int]], ...] = (
    ("claims_seniors_care_credit", CLAIMS_SENIORS_CARE_CREDIT, CLAIMS_SENIORS_CARE_CREDIT_CHECKED),
    (
        "aged_18_or_older_at_end_of_2025",
        AGED_18_OR_OLDER_AT_END_OF_2025,
        AGED_18_OR_OLDER_AT_END_OF_2025_CHECKED,
    ),
    (
        "resident_in_canada_throughout_2025",
        RESIDENT_IN_CANADA_THROUGHOUT_2025,
        RESIDENT_IN_CANADA_THROUGHOUT_2025_CHECKED,
    ),
    (
        "aged_19_or_older_at_end_of_2025",
        AGED_19_OR_OLDER_AT_END_OF_2025,
        AGED_19_OR_OLDER_AT_END_OF_2025_CHECKED,
    ),
    (
        "resided_with_spouse_or_child_at_end_of_2025",
        RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025,
        RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025_CHECKED,
    ),
    (
        "full_time_student_for_more_than_13_weeks",
        FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS,
        FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS_CHECKED,
    ),
    (
        "confined_to_prison_for_90_days",
        CONFINED_TO_PRISON_FOR_90_DAYS,
        CONFINED_TO_PRISON_FOR_90_DAYS_CHECKED,
    ),
    (
        "exempt_as_foreign_officer_or_family",
        EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY,
        EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY_CHECKED,
    ),
    ("born_in_1960_or_earlier", BORN_IN_1960_OR_EARLIER, BORN_IN_1960_OR_EARLIER_CHECKED),
    ("under_18_on_december_31", UNDER_18_ON_DECEMBER_31, UNDER_18_ON_DECEMBER_31_CHECKED),
    (
        "eligible_for_disability_amount",
        ELIGIBLE_FOR_DISABILITY_AMOUNT,
        ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED,
    ),
    ("spouses_claimed", SPOUSES_CLAIMED, SPOUSES_CLAIMED_CHECKED),
    ("spouse_caregiver_eligible", SPOUSE_CAREGIVER_ELIGIBLE, SPOUSE_CAREGIVER_ELIGIBLE_CHECKED),
    (
        "dependant_caregiver_eligible",
        DEPENDANT_CAREGIVER_ELIGIBLE,
        DEPENDANT_CAREGIVER_ELIGIBLE_CHECKED,
    ),
    (
        "dependant_caregiver_aged_18_or_older",
        DEPENDANT_CAREGIVER_AGED_18_OR_OLDER,
        DEPENDANT_CAREGIVER_AGED_18_OR_OLDER_CHECKED,
    ),
    (
        "spouse_not_separated_90_days",
        SPOUSE_NOT_SEPARATED_90_DAYS,
        SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED,
    ),
    (
        "ei_special_benefits_agreement",
        EI_SPECIAL_BENEFITS_AGREEMENT,
        EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED,
    ),
    (
        "pension_annuity_conditions_met",
        PENSION_ANNUITY_CONDITIONS_MET,
        PENSION_ANNUITY_CONDITIONS_MET_CHECKED,
    ),
    ("resp_aips_part_a_applies", RESP_AIPS_PART_A_APPLIES, RESP_AIPS_PART_A_APPLIES_CHECKED),
    (
        "search_and_rescue_conditions_met",
        SEARCH_AND_RESCUE_CONDITIONS_MET,
        SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED,
    ),
    (
        "volunteer_firefighters_conditions_met",
        VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET,
        VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED,
    ),
    (
        "t657_chart_2016_uses_d_instead",
        T657_CHART_2016_USES_D_INSTEAD,
        T657_CHART_2016_USES_D_INSTEAD_CHECKED,
    ),
    (
        "t657_chart_2017_uses_d_instead",
        T657_CHART_2017_USES_D_INSTEAD,
        T657_CHART_2017_USES_D_INSTEAD_CHECKED,
    ),
    (
        "t657_chart_2018_uses_d_instead",
        T657_CHART_2018_USES_D_INSTEAD,
        T657_CHART_2018_USES_D_INSTEAD_CHECKED,
    ),
    (
        "t657_chart_2019_uses_d_instead",
        T657_CHART_2019_USES_D_INSTEAD,
        T657_CHART_2019_USES_D_INSTEAD_CHECKED,
    ),
    (
        "t657_chart_2020_uses_d_instead",
        T657_CHART_2020_USES_D_INSTEAD,
        T657_CHART_2020_USES_D_INSTEAD_CHECKED,
    ),
    (
        "t657_chart_2021_uses_d_instead",
        T657_CHART_2021_USES_D_INSTEAD,
        T657_CHART_2021_USES_D_INSTEAD_CHECKED,
    ),
    (
        "t657_chart_2022_uses_d_instead",
        T657_CHART_2022_USES_D_INSTEAD,
        T657_CHART_2022_USES_D_INSTEAD_CHECKED,
    ),
    (
        "t657_chart_2023_uses_d_instead",
        T657_CHART_2023_USES_D_INSTEAD,
        T657_CHART_2023_USES_D_INSTEAD_CHECKED,
    ),
    (
        "fhsa_maximum_participation_period_ended",
        FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED,
        FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED,
    ),
    (
        "cpp_part_4_completed",
        CPP_PART_4_COMPLETED,
        CPP_PART_4_COMPLETED_YES_OR_NO_CHECKED,
    ),
    (
        "cpp_part_5_completed",
        CPP_PART_5_COMPLETED,
        CPP_PART_5_COMPLETED_YES_OR_NO_CHECKED,
    ),
)


def return_with(kind: ArtifactKind[int], value: int, **inputs: Any) -> Worksheet:
    """Return AO's inputs, as in `returns/2025_return_ao.yaml`, with the flag `kind` at `value`.

    The filer is the higher-income spouse of return AO (see `test_return_ao.py`); `inputs` are the
    other inputs the flag needs, by their short names, over those. The flag itself is set as an
    input artifact, so the four flags `starting` does not name are given too.
    """
    base = starting(
        "22139.77",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        dependent_children=2,
        spouse_or_common_law_partner_on_december_31=1,
        spouse_net_income="15000",
        **inputs,
    )
    rest = [artifact for artifact in base if artifact.kind != kind]
    return service().compute(CA_ON, 2025, *rest, Artifact(kind, value))["ca-on/return"][0]


@pytest.mark.parametrize(
    ("flag", "kind", "checked"),
    YES_OR_NO_FLAGS,
    ids=lambda row: row if isinstance(row, str) else "",
)
def test_a_yes_or_no_answer_of_2_is_refused_and_not_read_as_no(
    flag: str, kind: ArtifactKind[int], checked: ArtifactKind[int]
) -> None:
    with pytest.raises(InputAboveBoundError, match=f"{flag} 2 is above a yes or no answer of 1"):
        return_with(kind, 2, **COMPANIONS.get(flag, {}))


@pytest.mark.parametrize(
    ("flag", "kind", "checked"),
    YES_OR_NO_FLAGS,
    ids=lambda row: row if isinstance(row, str) else "",
)
def test_a_yes_or_no_answer_of_1_is_accepted_as_the_checked_count_of_1(
    flag: str, kind: ArtifactKind[int], checked: ArtifactKind[int]
) -> None:
    worksheet = return_with(kind, 1, **COMPANIONS.get(flag, {}))

    assert worksheet.get(checked).value == 1


def test_the_shared_spouse_answer_of_2_is_refused_once_by_the_form_that_holds_it() -> None:
    # The fact is entered once, checked 0 or 1 inside the form `ca/spouse_on_december_31`,
    # so one answer of 2 is refused for ON428 and Schedule ON428-A alike.
    with pytest.raises(
        InputAboveBoundError,
        match="spouse_or_common_law_partner_on_december_31 2 is above a yes or no answer of 1",
    ):
        return_with(SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31, 2)
