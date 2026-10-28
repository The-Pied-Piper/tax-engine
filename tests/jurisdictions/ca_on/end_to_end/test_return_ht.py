"""CA-ON 2025 end to end: return ht, Form T1172 Part A (the original subscriber's AIPs).

Return HT is Return Y's filer with Part A of Form T1172 on $50,000 of AIPs and $10,000 contributed
to an RRSP, as in `returns/2025_return_ht.yaml`. Part A's lines 1 to 10 are hand-checked there, and
the net federal tax and balance owing are Return Y's plus the additional tax. A figure typed in the
part that does not apply is not read ("Fill out Part A or Part B (whichever applies)"), checked here
too.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    NET_FEDERAL_TAX,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    RESP_AIPS_ADDITIONAL_TAX,
    RESP_AIPS_CONTRIBUTIONS_COUNTED,
    RESP_AIPS_LIFETIME_LIMIT,
    RESP_AIPS_LIMIT_REMAINING,
    RESP_AIPS_PART_A_TAX,
    RESP_AIPS_PART_B_TAX,
    RESP_AIPS_REDUCTION,
    RESP_AIPS_SUBJECT_TO_TAX,
    SPECIAL_TAXES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ht(**changes: Any) -> dict[str, Any]:
    """Return HT's inputs, as in `returns/2025_return_ht.yaml`: Return Y's filer on $60,000 of
    employment income, with Part A on the AIPs and RRSP contributions given, the count 1."""
    values: dict[str, Any] = {
        "resp_aips_received_part_a": "50000",
        "resp_aips_rrsp_contributions": "10000",
        "resp_aips_reduction_used_in_previous_years": "0",
        "resp_aips_received_part_b": "0",
        "resp_aips_part_a_applies": 1,
    }
    values.update(changes)
    return values


def worksheet(**changes: Any) -> Worksheet:
    """The return of `return_ht`, computed from employment income of 60,000."""
    return compute(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
        care_supporting_persons_adjusted_income="30000",
        **return_ht(**changes),
    )


def test_part_a_lines_1_to_10_are_hand_checked() -> None:
    # Line 3 is min(50000, 10000) = 10000; line 4 is 50,000.00; line 6 is 50,000.00 less 0;
    # line 7 is min(10000, 50000) = 10000; line 8 is 50000 - 10000 = 40000; line 10 is 20% of
    # 40000 = 8000.00. Part B is not chosen, so its line 13 is 0.00.
    result = worksheet()

    assert result.get(RESP_AIPS_CONTRIBUTIONS_COUNTED).value == D("10000")
    assert result.get(RESP_AIPS_LIFETIME_LIMIT).value == D("50000.00")
    assert result.get(RESP_AIPS_LIMIT_REMAINING).value == D("50000.00")
    assert result.get(RESP_AIPS_REDUCTION).value == D("10000")
    assert result.get(RESP_AIPS_SUBJECT_TO_TAX).value == D("40000")
    assert result.get(RESP_AIPS_PART_A_TAX).value == D("8000.00")
    assert result.get(RESP_AIPS_PART_B_TAX).value == D("0.00")


def test_the_additional_tax_of_part_a_is_entered_on_line_41800() -> None:
    result = worksheet()

    assert result.get(RESP_AIPS_ADDITIONAL_TAX).value == D("8000.00")
    assert result.get(SPECIAL_TAXES).value == D("8000.00")
    rendered = EnglishTraceRenderer().render_all(result.trace)
    assert (
        "resp_aips_contributions_counted: lesser of resp_aips_received_part_a 50000 "
        "and resp_aips_rrsp_contributions 10000 = 10000"
    ) in rendered
    assert (
        "resp_aips_reduction: lesser of resp_aips_contributions_counted 10000 "
        "and resp_aips_limit_remaining 50000 = 10000"
    ) in rendered
    assert (
        "resp_aips_subject_to_tax: resp_aips_received_part_a 50000 less resp_aips_reduction 10000 "
        "= 40000"
    ) in rendered
    assert (
        "resp_aips_part_a_tax: 20% of resp_aips_subject_to_tax 40000 (half-up to 0.01)"
    ) in rendered
    assert (
        "resp_aips_additional_tax: resp_aips_part_a_tax 8000, chosen as "
        "resp_aips_part_a_applies_checked "
        "is 1"
    ) in rendered


def test_the_net_federal_tax_and_the_balance_rise_by_the_additional_tax() -> None:
    # The same return with Part A not entered (the flag 0, no AIPs): the difference is the 8000.00
    # of line 41800, in the net federal tax and in the balance owing, as nothing else reads it.
    with_part_a = worksheet()
    without = worksheet(
        resp_aips_received_part_a="0",
        resp_aips_rrsp_contributions="0",
        resp_aips_part_a_applies=0,
    )

    assert with_part_a.get(NET_FEDERAL_TAX).value - without.get(NET_FEDERAL_TAX).value == D(
        "8000.00"
    )
    assert with_part_a.get(REFUND_OR_BALANCE_OWING).value - without.get(
        REFUND_OR_BALANCE_OWING
    ).value == D("8000.00")


def test_the_return_ht_balance_owing_is_2590_69() -> None:
    # Return Y's refund of 5409.31 less the 8000.00 of line 41800 is a balance owing of 2590.69, so
    # the refund (line 48400) is 0.
    result = worksheet()

    assert result.get(REFUND_OR_BALANCE_OWING).value == D("2590.69")
    assert result.get(REFUND).value == D("0")


def test_a_part_b_figure_with_part_a_applying_is_not_read() -> None:
    # Part A applies, so line 11 (10000) is not filled: line 13 is still computed (2000.00) but
    # line 41800 is line 10, 8000.00, and the balance owing is the same 2590.69 as without it.
    result = worksheet(resp_aips_received_part_b="10000")

    assert result.get(RESP_AIPS_ADDITIONAL_TAX).value == D("8000.00")
    assert result.get(SPECIAL_TAXES).value == D("8000.00")
    assert result.get(REFUND_OR_BALANCE_OWING).value == D("2590.69")


def test_part_a_figures_with_part_a_not_applying_are_not_read() -> None:
    # Part A does not apply, so lines 1, 2 and 5 are not filled: line 41800 is line 13, 20% of
    # 10000 = 2000.00, and Return Y's refund of 5409.31 less 2000.00 is a balance of -3409.31.
    result = worksheet(
        resp_aips_reduction_used_in_previous_years="5000",
        resp_aips_received_part_b="10000",
        resp_aips_part_a_applies=0,
    )

    assert result.get(RESP_AIPS_ADDITIONAL_TAX).value == D("2000.00")
    assert result.get(SPECIAL_TAXES).value == D("2000.00")
    assert result.get(REFUND_OR_BALANCE_OWING).value == D("-3409.31")


def test_a_flag_0_with_only_part_b_is_the_additional_tax() -> None:
    # Part B applies alone: line 13 is 20% of 10000, 2000.00, and it is the additional tax.
    result = worksheet(
        resp_aips_received_part_a="0",
        resp_aips_rrsp_contributions="0",
        resp_aips_received_part_b="10000",
        resp_aips_part_a_applies=0,
    )

    assert result.get(RESP_AIPS_ADDITIONAL_TAX).value == D("2000.00")
