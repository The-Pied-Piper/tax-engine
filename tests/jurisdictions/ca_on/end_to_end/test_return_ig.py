"""CA-ON 2025 end to end: return ig, the spouse on December 31 entered once.

Return IG is `returns/2025_return_ig.yaml`: return FL's filer and figures (a spouse or
common-law partner on December 31, a tie of net income with the spouse, two dependants, a UCCB and
RDSP income on both returns), with the one answer to "had a spouse or common-law partner on
December 31, 2025" entered once. Form ON428 reads it before lines 75 and 76 and Schedule
ON428-A reads it to choose Part A or Part B; both read the export of the form
`ca/spouse_on_december_31` as the total `ca/spouse_or_common_law_partner_on_december_31_total`, so
the two cannot disagree. The return has no second input for the fact.

The tests flip the one input and show that both the LIFT choice and the tax reduction spouse rule
follow it. The figures are Return FL's, and for the flips a spouse net income of 44,880 (chosen),
worked out by hand below.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    NET_INCOME,
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_CHECKED,
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, spouse_inputs, starting

TOTAL = "spouse_or_common_law_partner_on_december_31_total"
CHECKED = "spouse_or_common_law_partner_on_december_31_checked"
RULE = (
    'condition 1 "If you had a spouse or common-law partner on December 31, 2025, only the '
    'individual with the higher net income can claim the amounts on lines 75 and 76."'
)


def inputs(**overrides: Any) -> tuple[Artifact[Any], ...]:
    """The inputs of return IG (return FL's, with the one spouse input), `overrides` over them."""
    given: dict[str, Any] = {
        "t4_cpp_pensionable_earnings_outside_quebec": "31500",
        "cpp_t4_base_and_first_additional_contributions": "1666.00",
        "cpp_t4_second_additional_contributions": "0",
        "t2204_insurable_earnings": "31500",
        "t2204_premiums_deducted": "516.60",
        "cpp_months": 12,
        "qpp_months": 12,
        "universal_child_care_benefit": "1200",
        "rdsp_income": "500",
        "income_tax_deducted": "3000",
        "resident_in_canada_throughout_2025": 1,
        "aged_18_or_older_at_end_of_2025": 1,
        "dependants": 2,
        "spouse_or_common_law_partner_on_december_31": 1,
        "claims_tax_reduction_amounts_at_equal_net_income": 1,
        "spouse_net_income": "32920",
        "spouse_net_income_before_adjustments": "32920",
        "spouse_universal_child_care_benefit": "800",
        "spouse_rdsp_income": "300",
        "unapplied_net_capital_losses_2000": "0",
    }
    return starting(
        "31500",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        **{**spouse_inputs("32920", overrides), **given, **overrides},
    )


def results(**overrides: Any) -> Mapping[str, Sequence[Worksheet]]:
    return service().compute(CA_ON, 2025, *inputs(**overrides))


def return_ig(**overrides: Any) -> Worksheet:
    return results(**overrides)["ca-on/return"][0]


def render(worksheet: Worksheet) -> str:
    return "\n".join(EnglishTraceRenderer().render_all(worksheet.trace))


def test_the_one_input_is_the_only_spouse_on_december_31_artifact_the_return_starts_from() -> None:
    kinds = {artifact.kind.identifier for artifact in inputs()}

    assert "ca/spouse_or_common_law_partner_on_december_31" in kinds
    assert "ca-on/lift_spouse_at_year_end" not in kinds


def test_the_form_checks_the_one_answer_and_the_return_reads_its_total() -> None:
    # The form `ca/spouse_on_december_31` runs once on the input and exports the checked count of
    # 1; the return takes the first value of that export (one record), 1.
    found = results()

    (spouse,) = found["ca/spouse_on_december_31"]
    assert spouse.get(SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_CHECKED).value == 1
    assert (
        found["ca-on/return"][0].get(SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL).value == 1
    )


def test_the_total_is_traced_as_the_first_of_one_item_of_the_checked_count() -> None:
    rendered = render(return_ig())

    assert f"{TOTAL}: item 1 {CHECKED} 1 of 1 items" in rendered


def test_at_the_tie_with_the_spouse_the_figures_are_return_fls() -> None:
    # Return FL's lines: the claim at the tie gives line 76 1,088.00 and line 77 1,382.00, the
    # LIFT credit with a spouse is 875.00 and the reduction (1,841.34) takes the tax to 0.
    worksheet = return_ig()

    assert worksheet.get(NET_INCOME).value == D("32920.00")
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS_CLAIMABLE).value == 1
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS).value == D("1382.00")
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == D("1841.34")
    assert worksheet.get(ontario.LIFT_FAMILY_NET_INCOME).value == D("63040.00")
    assert worksheet.get(ontario.LIFT_CREDIT_WITH_SPOUSE).value == D("875.00")
    assert worksheet.get(ontario.LIFT_CREDIT).value == D("875.00")


# A spouse net income of 44,880 (chosen), with UCCB 800 and RDSP income 300 as in return FL.
# With a spouse (the one input at 1):
#   Tax reduction: the spouse's net income 44,880 is above the filer's 32,920, so the filer may
#   not claim lines 75 and 76 (the count is 0): line 76 = 0.00, line 77 = 294.00 (the basic
#   reduction), line 78 = 294.00 x 2 = 588.00, line 79 = 922.66 and line 80 = 588.00 - 922.66 is
#   negative, entered as 0, so line 81 = 922.66.
#   LIFT: Part B. Line 28 = 44,880 - 1,100 = 43,780.00; line 35 = 31,220.00 + 43,780.00 =
#   75,000.00, 10,000 over the 65,000 of line 36; line 37 = 10,000 and line 40 = 5% x 10,000 =
#   500.00; line 41 = 875.00 - 500.00 = 375.00, the LIFT credit; line 86 = 922.66 - 375.00 =
#   547.66.
# With no spouse (the same input at 0):
#   Tax reduction: no spouse, so the filer claims lines 75 and 76: the count is 1, line 76 =
#   1,088.00, line 77 = 1,382.00, line 80 = 2,764.00 - 922.66 = 1,841.34, line 81 = 0.
#   LIFT: Part A. Line 13 = 31,220.00 is below 32,500, so line 20 = 875.00 - 0.00 = 875.00, the
#   LIFT credit; line 86 = 0 - 875.00 is negative, entered as 0.
SPOUSE_INCOME = {"spouse_net_income": "44880", "spouse_net_income_before_adjustments": "44880"}


def test_with_a_spouse_of_higher_net_income_the_one_input_at_1_follows_part_b_and_the_rule() -> (
    None
):
    worksheet = return_ig(**SPOUSE_INCOME)

    assert worksheet.get(SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL).value == 1
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS_CLAIMABLE).value == 0
    assert worksheet.get(ontario.TAX_REDUCTION_FOR_DEPENDANTS).value == D("0")
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS).value == D("294.00")
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_REDUCTION).value == D("922.66")
    assert worksheet.get(ontario.LIFT_SPOUSE_ADJUSTED_NET_INCOME).value == D("43780.00")
    assert worksheet.get(ontario.LIFT_FAMILY_NET_INCOME).value == D("75000.00")
    assert worksheet.get(ontario.LIFT_FAMILY_REDUCTION).value == D("500.00")
    assert worksheet.get(ontario.LIFT_CREDIT_WITH_SPOUSE).value == D("375.00")
    assert worksheet.get(ontario.LIFT_CREDIT).value == D("375.00")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("547.66")


def test_flipping_the_one_input_to_0_changes_both_the_lift_choice_and_the_tax_reduction_rule() -> (
    None
):
    worksheet = return_ig(spouse_or_common_law_partner_on_december_31=0, **SPOUSE_INCOME)

    assert worksheet.get(SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL).value == 0
    # The tax reduction: no spouse, so the amounts of lines 75 and 76 are claimed.
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS_CLAIMABLE).value == 1
    assert worksheet.get(ontario.TAX_REDUCTION_FOR_DEPENDANTS).value == D("1088.00")
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS).value == D("1382.00")
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == D("1841.34")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_REDUCTION).value == D("0")
    # The LIFT: Part A, the credit as if single, whatever the spouse figures given.
    assert worksheet.get(ontario.LIFT_CREDIT_SINGLE).value == D("875.00")
    assert worksheet.get(ontario.LIFT_CREDIT_WITH_SPOUSE).value == D("375.00")
    assert worksheet.get(ontario.LIFT_CREDIT).value == D("875.00")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("0")


def test_the_trace_names_the_one_total_in_the_lift_choice_with_a_spouse() -> None:
    rendered = render(return_ig(**SPOUSE_INCOME))

    assert f"lift_credit: lift_credit_with_spouse 375, chosen as {TOTAL} is 1" in rendered


def test_the_trace_names_the_one_total_in_the_lift_choice_without_a_spouse() -> None:
    rendered = render(return_ig(spouse_or_common_law_partner_on_december_31=0, **SPOUSE_INCOME))

    assert f"lift_credit: lift_credit_single 875, chosen as {TOTAL} is 0" in rendered


def test_the_trace_names_the_one_total_in_the_spouse_rule_of_the_tax_reduction() -> None:
    with_spouse = render(return_ig(**SPOUSE_INCOME))
    without = render(return_ig(spouse_or_common_law_partner_on_december_31=0, **SPOUSE_INCOME))

    assert f"tax_reduction_amounts_claimable: {RULE}: {TOTAL} 1, net_income 32920" in with_spouse
    assert f"tax_reduction_amounts_claimable: {RULE}: {TOTAL} 0, net_income 32920" in without


def test_an_answer_of_2_is_refused_once_for_both_forms() -> None:
    with pytest.raises(InputAboveBoundError, match="is above a yes or no answer of 1"):
        return_ig(spouse_or_common_law_partner_on_december_31=2)
