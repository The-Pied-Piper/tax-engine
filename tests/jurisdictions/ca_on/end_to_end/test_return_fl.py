"""CA-ON 2025 end to end: return fl, the Ontario tax reduction for dependants and the LIFT credit.

Return FL is `returns/2025_return_fl.yaml`: a filer with a spouse on December 31 whose net income
is equal to the filer's, two dependants with an impairment and no dependent child, a UCCB and
RDSP income on both spouses' returns, so that the lines no other worked return sets are non-zero:
the tax reduction for dependants (ON428 line 76), the tie of net income with the spouse, and the
LIFT credit with UCCB and RDSP income taken off the adjusted net incomes. Five of the six
conditions that enter "0" on line 80 are each set on their own in a test of their own.
The figures are chosen (no CRA example exists) and worked out by hand from the form text, as the
description of the return shows. The tests check the hand figure of each line; the engine's
refund figures and the lines the return does not reach are checked in the YAML only.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, spouse_inputs, starting


def return_fl(*overrides: Artifact[Any]) -> Worksheet:
    """The worksheet of return FL: the inputs of `returns/2025_return_fl.yaml`.

    Each artifact in `overrides` replaces the input of the same kind that `starting(...)` gives,
    so a test can change one condition and keep every other input of the return.
    """
    base = starting(
        "31500",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t4_cpp_pensionable_earnings_outside_quebec="31500",
        cpp_t4_base_and_first_additional_contributions="1666.00",
        cpp_t4_second_additional_contributions="0",
        t2204_insurable_earnings="31500",
        t2204_premiums_deducted="516.60",
        cpp_months=12,
        qpp_months=12,
        universal_child_care_benefit="1200",
        rdsp_income="500",
        income_tax_deducted="3000",
        resident_in_canada_throughout_2025=1,
        aged_18_or_older_at_end_of_2025=1,
        dependants=2,
        spouse_or_common_law_partner_on_december_31=1,
        claims_tax_reduction_amounts_at_equal_net_income=1,
        spouse_net_income="32920",
        spouse_net_income_before_adjustments="32920",
        spouse_universal_child_care_benefit="800",
        spouse_rdsp_income="300",
        unapplied_net_capital_losses_2000="0",
        **spouse_inputs("32920"),
    )
    given = {artifact.kind for artifact in overrides}
    rest = [artifact for artifact in base if artifact.kind not in given]
    return service().compute(CA_ON, 2025, *rest, *overrides)["ca-on/return"][0]


def test_net_and_taxable_income_are_32920_after_the_cpp_first_additional_deduction() -> None:
    # Total income: 31,500 (employment income) + 1,200 (universal child care benefit) + 500 (RDSP
    # income) = 33,200. The CPP first additional contributions are 1% x 28,000 = 280.00, deducted
    # on line 22215, so net and taxable income are 33,200 - 280 = 32,920. Net income before
    # adjustments is the same.
    worksheet = return_fl()

    assert worksheet.get(TOTAL_INCOME).value == D("33200.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32920.00")
    assert worksheet.get(NET_INCOME).value == D("32920.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("32920.00")


def test_ontario_basic_tax_is_1662_46_at_5_05_percent_of_32920() -> None:
    # ON428 line 1: 5.05% x 32,920 = 1,662.46 (rounded half up to the cent).
    worksheet = return_fl()

    assert worksheet.get(ontario.ONTARIO_BASIC_TAX).value == D("1662.46")


def test_the_credit_amounts_of_14649_60_give_739_80_and_tax_after_credits_of_922_66() -> None:
    # Credit amounts: the basic personal amount 12,747.00 + the CPP base contributions 1,386.00 +
    # the EI premiums 516.60 = 14,649.60. At 5.05%: 14,649.60 x 5.05% = 739.8048, so 739.80.
    # Tax after credits: 1,662.46 - 739.80 = 922.66.
    worksheet = return_fl()

    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("14649.60")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("739.80")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_CREDITS).value == D("922.66")


def test_the_tax_before_reduction_is_922_66_with_no_dividend_credit_or_minimum_tax() -> None:
    # No dividend tax credit (no slip and no dividend), and no additional tax for minimum tax
    # purposes: line 71 is 922.66 and line 73 (line 71 + line 72) is 922.66.
    worksheet = return_fl()

    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("922.66")
    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_REDUCTION).value == D("922.66")


def test_two_dependants_with_an_impairment_give_reduction_amounts_of_1382() -> None:
    # Line 74 basic reduction 294.00. Line 75 (dependent children) 0 x 544 = 0.00. Line 76 (the
    # dependants) 2 x 544 = 1,088.00: the filer claims lines 75 and 76 at the equal net income,
    # since the claim is the caller's choice (one claim, so each amount counts once). Line 77 =
    # 294.00 + 0.00 + 1,088.00 = 1,382.00.
    worksheet = return_fl()

    assert worksheet.get(ontario.TAX_REDUCTION_BASIC).value == D("294.00")
    assert worksheet.get(ontario.TAX_REDUCTION_FOR_CHILDREN_BEFORE_SPOUSE_RULE).value == D("0.00")
    assert worksheet.get(ontario.TAX_REDUCTION_FOR_CHILDREN).value == D("0.00")
    assert worksheet.get(ontario.TAX_REDUCTION_FOR_DEPENDANTS_BEFORE_SPOUSE_RULE).value == D(
        "1088.00"
    )
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS_CLAIMABLE).value == 1
    assert worksheet.get(ontario.TAX_REDUCTION_FOR_DEPENDANTS).value == D("1088.00")
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS).value == D("1382.00")


def test_the_reduction_of_1841_34_is_taken_and_the_tax_after_reduction_is_0() -> None:
    # Line 78 = 1,382.00 x 2 = 2,764.00. Line 79 = 922.66. Line 80 = 2,764.00 - 922.66 = 1,841.34,
    # and none of the six conditions applies, so line 80 is 1,841.34. Line 81 = 922.66 - 1,841.34
    # is negative, so it is entered as 0.
    worksheet = return_fl()

    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION_BEFORE_CONDITIONS).value == D("1841.34")
    assert worksheet.get(ontario.TAX_REDUCTION_CLAIMABLE).value == 1
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == D("1841.34")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_REDUCTION).value == D("0")


@pytest.mark.parametrize(
    "condition",
    [
        ontario.NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR,
        ontario.NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END,
        ontario.BANKRUPT_IN_YEAR,
        ontario.RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY,
        ontario.NOT_CLAIMING_ONTARIO_TAX_REDUCTION,
    ],
    ids=[
        "not_resident_of_canada_at_start_of_year",
        "not_resident_of_ontario_at_year_end",
        "bankrupt_in_year",
        "return_filed_by_trustee_in_bankruptcy",
        "not_claiming_ontario_tax_reduction",
    ],
)
def test_each_condition_alone_enters_0_on_line_80(
    condition: ArtifactKind[int],
) -> None:
    # Each of the five conditions set to 1, the others 0: line 80 is entered as 0 (the reduction
    # before the conditions, 2,764.00 - 922.66 = 1,841.34, is unchanged).
    worksheet = return_fl(Artifact(condition, 1))

    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION_BEFORE_CONDITIONS).value == D("1841.34")
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == D("0.00")


def test_without_the_claim_at_a_tie_only_the_basic_reduction_of_294_remains() -> None:
    # The net incomes are equal (32,920 each). With the claim at equal net income set to 0 the
    # filer does not claim lines 75 and 76: the claimable count is 0, the dependants amount is
    # 0 x 1,088.00 = 0.00, and line 77 is the basic reduction alone, 294.00.
    worksheet = return_fl(Artifact(ontario.CLAIMS_TAX_REDUCTION_AMOUNTS_AT_EQUAL_NET_INCOME, 0))

    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS_CLAIMABLE).value == 0
    assert worksheet.get(ontario.TAX_REDUCTION_FOR_DEPENDANTS).value == D("0.00")
    assert worksheet.get(ontario.TAX_REDUCTION_AMOUNTS).value == D("294.00")


def test_the_lift_credit_is_capped_at_875_with_employment_income_of_31500() -> None:
    # Line 3: employment income 31,500.00. Line 5: 5.05% x 31,500 = 1,590.75, more than the
    # maximum of 875, so the credit is 875.00 (line 14 and line 29).
    worksheet = return_fl()

    assert worksheet.get(ontario.LIFT_EMPLOYMENT_INCOME).value == D("31500.00")
    assert worksheet.get(ontario.LIFT_CREDIT_BEFORE_MAXIMUM).value == D("1590.75")
    assert worksheet.get(ontario.LIFT_MAXIMUM_CREDIT).value == D("875.00")


def test_adjusted_net_incomes_of_31220_and_31820_after_the_uccb_and_rdsp_income() -> None:
    # Filer: line 9 is 32,920.00; line 10 (UCCB) 1,200.00 and line 11 (RDSP income) 500.00, line
    # 12 = 1,700.00; line 13 = 32,920 - 1,700 = 31,220.00. Spouse: line 24 is 32,920.00; line 25
    # (UCCB) 800.00 and line 26 (RDSP income) 300.00, line 27 = 1,100.00; line 28 = 32,920 -
    # 1,100 = 31,820.00. Both are below the 32,500 threshold of Part A and Part B.
    worksheet = return_fl()

    assert worksheet.get(ontario.LIFT_NET_INCOME_AND_REPAYMENTS).value == D("32920.00")
    assert worksheet.get(ontario.LIFT_UCCB_AND_RDSP_INCOME).value == D("1700.00")
    assert worksheet.get(ontario.LIFT_ADJUSTED_NET_INCOME).value == D("31220.00")
    assert worksheet.get(ontario.LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS).value == D("32920.00")
    assert worksheet.get(ontario.LIFT_SPOUSE_UCCB_AND_RDSP_INCOME).value == D("1100.00")
    assert worksheet.get(ontario.LIFT_SPOUSE_ADJUSTED_NET_INCOME).value == D("31820.00")


def test_uccb_and_rdsp_income_is_taken_off_both_incomes_for_the_family_income() -> None:
    # Line 35: 31,220 + 31,820 = 63,040.00, below the 65,000 of line 36, so line 37 is 0. Without
    # the UCCB and RDSP income taken off on lines 12 and 27 the family income would be
    # 32,920 + 32,920 = 65,840, 840 over 65,000, and the credit 875 - 5% x 840 = 833.00. The
    # subtraction is what keeps the family income under the threshold.
    worksheet = return_fl()

    assert worksheet.get(ontario.LIFT_UCCB_AND_RDSP_INCOME).value == D("1700.00")
    assert worksheet.get(ontario.LIFT_SPOUSE_UCCB_AND_RDSP_INCOME).value == D("1100.00")
    assert worksheet.get(ontario.LIFT_FAMILY_NET_INCOME).value == D("63040.00")


def test_the_family_income_below_65000_gives_the_full_lift_credit_of_875() -> None:
    # Line 41: line 29 (875.00) - line 40 (0.00) = 875.00. The credit with a spouse is 875.00,
    # and that is the LIFT credit (ON428 line 85 and the return's LIFT line).
    worksheet = return_fl()

    assert worksheet.get(ontario.LIFT_CREDIT_SINGLE).value == D("875.00")
    assert worksheet.get(ontario.LIFT_CREDIT_WITH_SPOUSE).value == D("875.00")
    assert worksheet.get(ontario.LIFT_CREDIT).value == D("875.00")


def test_the_lift_credit_of_875_leaves_no_tax_so_the_tax_after_lift_is_0() -> None:
    # ON428 line 86 = 0 - 875.00 is negative, so it is entered as 0.
    worksheet = return_fl()

    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("0")
