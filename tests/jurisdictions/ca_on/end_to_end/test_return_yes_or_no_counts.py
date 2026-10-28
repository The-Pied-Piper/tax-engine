"""CA-ON 2025 end to end: a count of 2 on a yes or no answer is refused, not read as a claim.

The base return has employment income of 30000 and other income of 20000 and nothing else
claimed, so its total payable is 6761.60 with every count at 0. Each test changes one count.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_FEDERAL_SURTAX,
    AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED,
    CWB_ELIGIBLE_DEPENDANTS_CHECKED,
    ELIGIBLE_DEPENDANTS_CHECKED,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

NO_CLAIM_TOTAL_PAYABLE = D("6761.60")


def return_with_other_income(**overrides: Any) -> Worksheet:
    """The base return: employment income 30000 and other income 20000, over the overrides."""
    return compute("30000", (), "0", "0", "0", "0", "0", other_income="20000", **overrides)


# --- ca/eligible_dependants (T1 line 30400, Schedule 5) ---------------------------


def test_a_second_eligible_dependant_claim_is_refused_and_not_read_as_a_first() -> None:
    # Schedule 5 (docs/cra-forms-2025/5000-s5-25e.txt): "Each household is allowed only one claim
    # for this amount". A count of 2 is an input error, not a second $16,129 claim.
    with pytest.raises(
        InputAboveBoundError, match="ca/eligible_dependants 2 is above a yes or no answer of 1"
    ):
        return_with_other_income(eligible_dependants=2)


def test_one_eligible_dependant_claim_gives_a_total_payable_of_3876_33() -> None:
    worksheet = return_with_other_income(eligible_dependants=1)

    assert worksheet.get(ELIGIBLE_DEPENDANTS_CHECKED).value == 1
    assert worksheet.get(TOTAL_PAYABLE).value == D("3876.33")


def test_no_eligible_dependant_claim_gives_the_no_claim_total_payable() -> None:
    worksheet = return_with_other_income(eligible_dependants=0)

    assert worksheet.get(ELIGIBLE_DEPENDANTS_CHECKED).value == 0
    assert worksheet.get(TOTAL_PAYABLE).value == NO_CLAIM_TOTAL_PAYABLE


def test_the_trace_checks_the_eligible_dependant_answer_as_a_yes_or_no_count() -> None:
    rendered = EnglishTraceRenderer().render_all(
        return_with_other_income(eligible_dependants=1).trace
    )

    line = "eligible_dependants_checked: eligible_dependants 1, a yes or no answer of 0 or 1"
    assert line in rendered


# --- ca/amt_non_resident_or_deemed_resident (Form T691 Part 3 line 4) -------------


def test_a_non_resident_answer_of_2_is_refused_and_not_doubled() -> None:
    # Form T691 Part 3 line 4 "If not, and you are a non-resident or deemed resident, enter the
    # amount from line 2.": a count of 2 is refused rather than doubling the surtax to 4222.12.
    with pytest.raises(
        InputAboveBoundError,
        match="ca/amt_non_resident_or_deemed_resident 2 is above a yes or no answer of 1",
    ):
        return_with_other_income(amt_non_resident_or_deemed_resident=2)


def test_a_non_resident_answer_of_1_gives_the_federal_surtax_of_2111_06() -> None:
    worksheet = return_with_other_income(amt_non_resident_or_deemed_resident=1)

    assert worksheet.get(AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED).value == 1
    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("2111.06")


def test_a_non_resident_answer_of_0_gives_no_federal_surtax() -> None:
    worksheet = return_with_other_income(amt_non_resident_or_deemed_resident=0)

    assert worksheet.get(AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED).value == 0
    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("0")


# --- ca/cwb_eligible_dependants (Schedule 6 line 38100) --------------------------


def test_a_cwb_dependant_answer_of_2_is_refused_and_not_read_as_yes() -> None:
    # Schedule 6 line 38100 (the eligible dependant question): the form text is to be confirmed, as
    # Schedule 6 is not in docs/cra-forms-2025, so no quote is cited. A count of 2 is refused, as
    # it is not a yes or no answer, though it changes no dollar amount.
    with pytest.raises(
        InputAboveBoundError,
        match="ca/cwb_eligible_dependants 2 is above a yes or no answer of 1",
    ):
        return_with_other_income(cwb_eligible_dependants=2)


@pytest.mark.parametrize("answer", [0, 1])
def test_a_cwb_dependant_answer_of_0_or_1_is_produced_as_it_is_and_changes_no_total(
    answer: int,
) -> None:
    worksheet = return_with_other_income(cwb_eligible_dependants=answer)

    assert worksheet.get(CWB_ELIGIBLE_DEPENDANTS_CHECKED).value == answer
    assert worksheet.get(TOTAL_PAYABLE).value == NO_CLAIM_TOTAL_PAYABLE
