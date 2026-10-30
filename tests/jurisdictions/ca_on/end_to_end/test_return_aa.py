"""CA-ON 2025 end to end: return aa."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
    CWB_ELIGIBLE_SPOUSES,
    CWB_FAMILY_NET_INCOME_LINE_13,
    CWB_FAMILY_WORKING_INCOME,
    CWB_LINE_28_BY_SPOUSE,
    CWB_SECONDARY_EARNER_EXEMPTION,
    CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM,
    CWB_SECONDARY_EARNER_SPOUSES,
    CWB_SECONDARY_EARNER_YOURS,
    CWB_SPOUSE_WORKING_INCOME,
    CWB_WORKING_INCOME_LESS_SPOUSE,
    NET_INCOME,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.catalog import (
    LIFT_CREDIT,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_LIFT_CREDIT,
    ONTARIO_TAX_AFTER_REDUCTION,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, service, spouse_inputs, starting

CA_ON = JurisdictionCode("CA-ON")


def return_aa(*, eligible_spouse: int = 1, **overrides: Any) -> Worksheet:
    """Return AA's inputs (`returns/2025_return_aa.yaml`): a filer with a spouse at year end.

    `eligible_spouse` is the Schedule 6 line 38101 answer, 1 for the spouse of Return AA, and
    `overrides` replace any keyword of `starting`, for the variants below.
    """
    given: dict[str, Any] = {
        "income_tax_deducted": "2500",
        "spouse_net_income": "50000",
        "spouse_or_common_law_partner_on_december_31": 1,
        "spouse_net_income_before_adjustments": "50000",
    }
    spouse = {**spouse_inputs("50000"), "cwb_eligible_spouses": eligible_spouse}
    artifacts = starting(
        "25217.17", (), "0", "0", "4500", "0", "0", **{**spouse, **given, **overrides}
    )
    return service().compute(CA_ON, 2025, *artifacts)["ca-on/return"][0]


def test_return_aas_lift_credit_is_375_from_part_b_and_comes_off_the_ontario_tax() -> None:
    # Return AA: employment income of 25217.17 (net income 25000.00 after the first additional
    # CPP contribution of 217.17), a spouse at the end of the year with a net income of 50000.
    # Schedule ON428-A line 41 is 875 - 5% of (75000.00 - 65000.00) = 875 - 500.00 = 375.00.
    # The Ontario tax on 25000.00 is 1262.50 less the credits 5.05% x (12747 + 1075.00 + 413.56 =
    # 14235.56) = 718.90, 543.60; the tax reduction is 588.00 - 543.60 = 44.40, so line 81 is
    # 499.20 and line 86 is 499.20 - 375.00 = 124.20. With the health premium of 300 the Ontario
    # tax is 424.20; the federal tax after credits is 3625.00 - 2767.84 = 857.16, so the total
    # payable is 857.16 + 424.20 = 1281.36 and, with the chosen tax deducted of 2500 and no
    # Canada workers benefit (the eligible spouse's Schedule 6 benefit is 0, see the test below),
    # line 167 is 1281.36 - 2500.00 = -1218.64, a refund.
    worksheet = return_aa()

    assert worksheet.get(NET_INCOME).value == D("25000.00")
    assert worksheet.get(ontario.LIFT_ADJUSTED_NET_INCOME).value == D("25000.00")
    assert worksheet.get(ontario.LIFT_SPOUSE_ADJUSTED_NET_INCOME).value == D("50000")
    assert worksheet.get(ontario.LIFT_FAMILY_NET_INCOME).value == D("75000.00")
    assert worksheet.get(ontario.LIFT_CREDIT_SINGLE).value == D("875")
    assert worksheet.get(ontario.LIFT_CREDIT_WITH_SPOUSE).value == D("375.00")
    assert worksheet.get(LIFT_CREDIT).value == D("375.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("499.20")
    assert worksheet.get(ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("124.20")
    assert worksheet.get(ONTARIO_TAX).value == D("424.20")
    assert worksheet.get(TOTAL_PAYABLE).value == D("1281.36")
    assert worksheet.get(TOTAL_CREDITS).value == D("2500.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1218.64")


def test_return_aa_schedule_6_secondary_earner_exemption_is_capped_at_16386() -> None:
    # Schedule 6 with the eligible spouse (line 38101, 1). Column 1: working income 25217.17
    # (line 5), line 12 is 25000.00. Column 2: working income 50000.00 (line 5), line 12 50000.00.
    # Line 6 family working income is 25217.17 + 50000.00 = 75217.17. Line 13 is 25000.00 +
    # 50000.00 = 75000.00. Line 14: 25217.17 is less than 50000.00, so column 1's amount, the less
    # of 25217.17 and 25000.00, which is 25000.00; the maximum is $16,386, so line 14 is 16386.00.
    # Line 15 is 75000.00 - 16386.00 = 58614.00, the adjusted family net income.
    worksheet = return_aa()

    assert worksheet.get(CWB_ELIGIBLE_SPOUSES).value == 1
    assert worksheet.get(CWB_SPOUSE_WORKING_INCOME).value == D("50000.00")
    assert worksheet.get(CWB_FAMILY_WORKING_INCOME).value == D("75217.17")
    assert worksheet.get(CWB_WORKING_INCOME_LESS_SPOUSE).value == D("-24782.83")
    assert worksheet.get(CWB_SECONDARY_EARNER_YOURS).value == D("25000.00")
    assert worksheet.get(CWB_SECONDARY_EARNER_SPOUSES).value == D("50000.00")
    assert worksheet.get(CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM).value == D("25000.00")
    assert worksheet.get(CWB_SECONDARY_EARNER_EXEMPTION).value == D("16386.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_13).value == D("75000.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("58614.00")


def test_return_aa_canada_workers_benefit_is_0_for_the_married_filer() -> None:
    # Schedule 6 line 21 and line 24 take the eligible spouse figures ($2,813 and $30,639):
    # line 22 is the lesser of 27% of 72217.17 (19498.64) and 2813, so 2813.00; line 25 is
    # 58614.00 - 30639.00 = 27975.00 and line 27 is 15% of it, 4196.25; line 28 is 2813.00 -
    # 4196.25, negative, so 0. Line 45300 is 0, total credits are the tax deducted of 2500.00, and
    # the refund is 1281.36 - 2500.00 = -1218.64.
    worksheet = return_aa()

    # Line 28 by spouse: the eligible spouse's line 28 (the line with an eligible spouse), 0.
    assert worksheet.get(CWB_LINE_28_BY_SPOUSE).value == D("0.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITH_DEPENDANT).value == D("0.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("2500.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1218.64")


def test_return_aa_without_the_spouse_at_year_end_takes_the_whole_875() -> None:
    # The same return with a count of 0 (single, or the spouse died during the year): Part A's
    # line 20 is 875 - 0 = 875, so line 86 is 499.20 - 875, below zero, 0, and the Ontario tax is
    # the health premium of 300 alone. With no spouse at year end the Schedule 6 spouse answer is
    # 0 too, so the spouse's column is 0.
    worksheet = return_aa(spouse_or_common_law_partner_on_december_31=0, eligible_spouse=0)

    assert worksheet.get(LIFT_CREDIT).value == D("875")
    assert worksheet.get(ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_TAX).value == D("300")
