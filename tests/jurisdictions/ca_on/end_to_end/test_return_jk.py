"""CA-ON 2025 end to end: return jk, the advanced Canada workers benefit and who may claim the
Canada workers benefit.

Return JK is `returns/2025_return_jk.yaml`: a single Ontario resident with employment income of
10000 and 2000 of advance payments (box 10 of the RC210 slip). Schedule 6 Step 4 line 49, T1 line
41500, is the lesser of the benefit claimed (line 43) and the payments received (line 48), and
Schedule 6's conditions switch the benefit off for a filer who cannot claim it. The benefit of
Return JK is 1633.00 (27% of 7000 is 1890, at most 1633, with no reduction).
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ACWB_BASIC_PAID,
    ACWB_PAID,
    ADVANCED_CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_LINE_28,
    CWB_CLAIMED,
    CWB_ELIGIBLE,
    NET_FEDERAL_TAX,
    SPLIT_INCOME_LINE_10,
    SPLIT_INCOME_LINE_29,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_jk(**overrides: Any) -> Worksheet:
    """Return JK's inputs over the keyword overrides given: employment income of 10000 and 2000 of
    box 10, a single filer who meets every condition of Schedule 6."""
    inputs: dict[str, Any] = {"acwb_paid_to_you": "2000"}
    inputs.update(overrides)
    return compute("10000", (), "0", "0", "0", "0", "0", **inputs)


def test_the_advance_payments_over_the_benefit_charge_back_only_the_benefit() -> None:
    # Line 43 is 1633.00, line 48 is 2000, so line 49 is 1633.00, not the 2000 received.
    worksheet = return_jk()

    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1633")
    assert worksheet.get(CWB_CLAIMED).value == D("1633")
    assert worksheet.get(ACWB_PAID).value == D("2000")
    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D("1633")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("1633.00")


@pytest.mark.parametrize(
    ("box_10", "spouse", "supplement", "charged"),
    [
        ("1633", "0", "0", "1633"),
        ("1000", "0", "0", "1000"),
        ("0", "0", "0", "0"),
        # The spouse's slip adds to line 46, and the disability supplement to line 48.
        ("1000", "400", "0", "1400"),
        ("1000", "400", "100", "1500"),
        ("1000", "1000", "500", "1633"),
    ],
)
def test_line_49_is_the_lesser_of_the_benefit_and_all_the_payments(
    box_10: str, spouse: str, supplement: str, charged: str
) -> None:
    worksheet = return_jk(
        acwb_paid_to_you=box_10,
        acwb_paid_to_spouse=spouse,
        acwb_disability_supplement_paid=supplement,
    )

    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D(charged)
    assert worksheet.get(NET_FEDERAL_TAX).value == D(charged)


def test_the_payments_are_added_on_lines_46_and_48_before_the_lesser_of() -> None:
    worksheet = return_jk(
        acwb_paid_to_you="1000", acwb_paid_to_spouse="400", acwb_disability_supplement_paid="100"
    )

    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "acwb_lines_44_and_45: acwb_paid_to_you 1000 + acwb_paid_to_spouse 400 = 1400" in rendered
    )
    assert (
        "acwb_paid: acwb_basic_paid 1400 + acwb_disability_supplement_paid 100 = 1500" in rendered
    )
    assert (
        "advanced_canada_workers_benefit: lesser of cwb_claimed 1633 and acwb_paid 1500 = 1500"
    ) in rendered
    assert worksheet.get(ACWB_BASIC_PAID).value == D("1400")


def test_the_advance_payments_join_lines_10_and_29_of_form_t1206() -> None:
    # Line 10 adds line 41500 to the tax on split income (0), and line 29 adds it to line 41700.
    worksheet = return_jk()

    assert worksheet.get(SPLIT_INCOME_LINE_10).value == D("1633")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("1633")


def test_no_benefit_means_no_advance_payments_are_charged_back() -> None:
    # Employment income of 40000 gives no benefit (the reduction is more than 1633), so line 43 is
    # 0 and line 49 is 0 whatever box 10 shows.
    worksheet = compute("40000", (), "0", "0", "0", "0", "0", acwb_paid_to_you="1500")

    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D("0")


@pytest.mark.parametrize(
    "overrides",
    [
        {"resident_in_canada_throughout_2025": 0},
        {"aged_19_or_older_at_end_of_2025": 0},
        {"full_time_student_for_more_than_13_weeks": 1},
        {"confined_to_prison_for_90_days": 1},
        {"exempt_as_foreign_officer_or_family": 1},
    ],
)
def test_a_filer_who_cannot_claim_the_benefit_gets_none_and_is_not_charged_back(
    overrides: dict[str, Any],
) -> None:
    # The return is accepted: the filer is not eligible, so line 28 does not reach line 45300 and
    # line 43 is 0, so no advance payment is charged back either.
    worksheet = return_jk(**overrides)

    assert worksheet.get(CANADA_WORKERS_BENEFIT_LINE_28).value == D("1633")
    assert worksheet.get(CWB_ELIGIBLE).value == 0
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D("0")


def test_every_condition_met_leaves_the_benefit_as_it_was() -> None:
    worksheet = return_jk()

    assert worksheet.get(CWB_ELIGIBLE).value == 1


@pytest.mark.parametrize(
    "overrides",
    [
        # Under 19 but living with a spouse or common-law partner, or a child.
        {"aged_19_or_older_at_end_of_2025": 0, "resided_with_spouse_or_child_at_end_of_2025": 1},
        {"aged_19_or_older_at_end_of_2025": 0, "cwb_eligible_dependants": 1},
        # A full-time student of more than 13 weeks with an eligible dependant may claim.
        {"full_time_student_for_more_than_13_weeks": 1, "cwb_eligible_dependants": 1},
    ],
)
def test_the_exceptions_in_schedule_6_keep_the_benefit(overrides: dict[str, Any]) -> None:
    worksheet = return_jk(**overrides)

    assert worksheet.get(CWB_ELIGIBLE).value == 1
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value > 0


def test_a_student_with_no_dependant_is_told_why_in_the_trace() -> None:
    worksheet = return_jk(full_time_student_for_more_than_13_weeks=1)

    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "cwb_eligible: condition 3 applies, so 0" in rendered


@pytest.mark.parametrize(
    "flag",
    [
        "aged_19_or_older_at_end_of_2025",
        "resided_with_spouse_or_child_at_end_of_2025",
        "full_time_student_for_more_than_13_weeks",
        "confined_to_prison_for_90_days",
        "exempt_as_foreign_officer_or_family",
    ],
)
def test_a_yes_or_no_answer_of_2_is_refused(flag: str) -> None:
    with pytest.raises(InputAboveBoundError, match=f"{flag} 2 is above a yes or no answer of 1"):
        return_jk(**{flag: 2})
