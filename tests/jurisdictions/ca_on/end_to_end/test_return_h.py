"""CA-ON 2025 end to end: return h."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ADDITIONAL_DEDUCTIONS,
    CANADA_WORKERS_BENEFIT,
    CPP_ENHANCED_CONTRIBUTIONS,
    DEDUCTIONS_FROM_NET_INCOME,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    INCOME_SUPPORT_BENEFITS,
    INTEREST_AND_OTHER_INVESTMENT_INCOME,
    INVESTMENT_INCOME_BEFORE_PRIOR_YEARS,
    NET_INCOME,
    NON_REFUNDABLE_TAX_CREDITS,
    OTHER_PAYMENTS_DEDUCTION,
    OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED,
    PENSION_CHART_LINE_5,
    PENSION_CHART_LINE_6,
    PENSION_FOREIGN_INCOME,
    PENSION_INCOME_CREDIT,
    PENSION_RRIF_TRANSFERRED,
    PENSION_US_IRA_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
    WORKING_INCOME,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    LIFT_CREDIT,
    LIFT_REDUCTION,
    ONTARIO_BASIC_TAX,
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    ReturnAndSchedule8,
    compute_with_schedule_8,
    service,
    starting,
)


def test_return_hs_pension_and_benefit_income_is_all_of_its_total_income() -> None:
    # Return H, a retiree: OAS 8000 (line 11300), CPP benefits 9000 (11400), other pensions
    # 20000 (11500), RRSP income 5000 (12900) and workers' compensation 2000 (14400, so line
    # 14700); interest from the Federal Worksheet: T5 slips 1200 (line 2) plus bank interest with
    # no slip 300 (line 7) is 1500 (line 9), less 100 reported in previous years (line 10): 1400
    # (line 12100). Total income 8000 + 9000 + 20000 + 1400 + 5000 + 2000 = 45400, with no
    # employment income, so no CPP contributions, EI premiums, Canada employment amount, LIFT
    # credit or Canada workers benefit. With no amount entered on line 14600, line 25000 is line
    # 14700, 2000, so taxable income is 45400 - 2000 = 43400.
    worksheet = compute_with_schedule_8(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        old_age_security="8000",
        cpp_or_qpp_benefits="9000",
        other_pensions_and_superannuation="20000",
        t5_investment_income="1200",
        investment_income_without_a_slip="300",
        investment_income_reported_in_previous_years="100",
        rrsp_income="5000",
        workers_compensation_benefits="2000",
        income_tax_deducted="3000",
    )

    assert worksheet.get(INVESTMENT_INCOME_BEFORE_PRIOR_YEARS).value == D("1500")
    assert worksheet.get(INTEREST_AND_OTHER_INVESTMENT_INCOME).value == D("1400")
    assert worksheet.get(INCOME_SUPPORT_BENEFITS).value == D("2000")
    assert worksheet.get(TOTAL_INCOME).value == D("45400")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS).value == D("0")
    assert worksheet.get(NET_INCOME).value == D("45400")
    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION).value == D("2000")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("2000")
    assert worksheet.get(TAXABLE_INCOME).value == D("43400.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("6293.00")
    # 14.5% of 18129.00, the basic personal amount 16129.00 plus the pension income amount 2000.00
    # (line 31400: 20000 of other pensions on line 11500, capped at 2000): 2628.705, up to 2628.71.
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("2628.71")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3664.29")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("2191.70")
    # 5.05% of 14509.00, the basic personal amount 12747.00 plus the pension income amount 1762.00
    # (line 58360: the lesser of 2000.00 on line 31400 and 1762): 732.7045, down to 732.70.
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("732.70")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("1459.00")
    assert worksheet.get(LIFT_REDUCTION).value == D("645.00")
    assert worksheet.get(LIFT_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("450")
    assert worksheet.get(ONTARIO_TAX).value == D("1909.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5573.29")
    assert worksheet.get(WORKING_INCOME).value == D("0")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2573.29")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "total_income: employment_income 0 + other_employment_income 0 + old_age_security 8000 "
        "+ cpp_or_qpp_benefits 9000 + other_pensions_and_superannuation 20000 "
        "+ t2205_on_line_11500 0 + elected_split_pension_amount 0 + universal_child_care_benefit 0 "
        "+ ei_and_other_benefits 0 + taxable_dividends 0 "
        "+ interest_and_other_investment_income 1400 "
        "+ net_partnership_income 0 + rdsp_income 0 + net_rental_income 0 "
        "+ taxable_capital_gains 0 "
        "+ taxable_support_payments 0 + rrsp_income 5000 + t2205_on_line_12900 0 "
        "+ fhsa_income 0 + other_fhsa_income 0 + other_income 0 + t2205_on_line_13000 0 "
        "+ taxable_scholarships 0 + net_self_employment_income 0 "
        "+ income_support_benefits 2000 = 45400"
    ) in rendered


def other_payments_return_h(**overrides: Any) -> ReturnAndSchedule8:
    """Return H's inputs, as in `tests/jurisdictions/ca_on/returns/2025_return_h.yaml`, with the
    2000 on line 14700 entered as net federal supplements (line 14600), so the Federal Worksheet's
    chart applies, and other pensions raised to 100000 so that its line 9 is more than $93,454;
    the chart's amount for line 25000 is 2000.

    Both counts are derived from those lines. The net federal supplements are the whole of line
    14700 here (2000).
    """
    inputs: dict[str, Any] = {
        "old_age_security": "8000",
        "cpp_or_qpp_benefits": "9000",
        "other_pensions_and_superannuation": "100000",
        "t5_investment_income": "1200",
        "investment_income_without_a_slip": "300",
        "investment_income_reported_in_previous_years": "100",
        "rrsp_income": "5000",
        "net_federal_supplements": "2000",
        "other_payments_deduction_above_limit": "2000",
    }
    return compute_with_schedule_8("0", (), "0", "0", "0", "0", "0", **{**inputs, **overrides})


def test_a_chart_amount_of_zero_is_accepted_and_is_line_25000() -> None:
    # The line 25000 chart's line 9 is over $93,454 and line 14600 was entered, so the chart's
    # amount is chosen over line 14700. The chart's 0 is at most line 14700 (2000), so the checked
    # amount is 0 and line 25000 is 0: taxable income is the net income after the social benefits
    # repayment (125400 - 4808.55 = 120591.45) less 0.
    worksheet = other_payments_return_h(other_payments_deduction_above_limit="0")

    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED).value == D("0")
    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION).value == D("0")
    assert worksheet.get(TAXABLE_INCOME).value == D("120591.45")


def test_a_chart_amount_equal_to_line_14700_is_accepted_as_it_is() -> None:
    # "Otherwise, enter the amount from line 14700 of your return on line 25000 of your return"
    # (Federal Worksheet line 25000): the chart's amount 2000 equals line 14700 (2000), so it is
    # accepted as it is. Line 25000 is 2000, taxable income is 120591.45 - 2000 = 118591.45.
    worksheet = other_payments_return_h()

    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED).value == D("2000")
    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION).value == D("2000")
    assert worksheet.get(TAXABLE_INCOME).value == D("118591.45")


@pytest.mark.parametrize("amount", ["2000.01", "30000"])
def test_a_chart_amount_above_line_14700_is_refused_not_capped(amount: str) -> None:
    # The deduction is a part of line 14700: Form 5000-G line 25000 says "you may not be entitled
    # to claim the full amount from line 14700 of your return", so an amount above line 14700 (2000)
    # is an input error naming the input and line 14700, not capped to it.
    message = (
        f"ca/other_payments_deduction_above_limit {amount} is above ca/income_support_benefits 2000"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        other_payments_return_h(other_payments_deduction_above_limit=amount)


# The input error of `core/at_most` on line 5 against line 1: "ca/pension_chart_line_5 <amount> is
# above ca/pension_chart_line_1 <bound>".
ABOVE_LINE_11500 = r"ca/pension_chart_line_5 \S+ is above ca/pension_chart_line_1 \S+"


def return_h(
    *, foreign: str = "0", us_ira: str = "0", rrif: str = "0", additional_deductions: str = "0"
) -> Worksheet:
    """Return H's inputs as in `returns/2025_return_h.yaml` (a retiree with other pensions 20000 on
    line 11500), with the three amounts of line 5 given: foreign pension income, U.S. IRA income
    and RRIF or PRPP amounts transferred. The foreign pension income is deducted on line 25600,
    which `additional_deductions` gives (0 when none is claimed)."""
    base = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        old_age_security="8000",
        cpp_or_qpp_benefits="9000",
        other_pensions_and_superannuation="20000",
        t5_investment_income="1200",
        investment_income_without_a_slip="300",
        investment_income_reported_in_previous_years="100",
        rrsp_income="5000",
        workers_compensation_benefits="2000",
        income_tax_deducted="3000",
        born_in_1960_or_earlier=1,
    )
    given = (
        Artifact(PENSION_FOREIGN_INCOME, D(foreign)),
        Artifact(PENSION_US_IRA_INCOME, D(us_ira)),
        Artifact(PENSION_RRIF_TRANSFERRED, D(rrif)),
        Artifact(ADDITIONAL_DEDUCTIONS, D(additional_deductions)),
    )
    kinds = {artifact.kind for artifact in given}
    rest = [artifact for artifact in base if artifact.kind not in kinds]
    return service().compute(CA_ON, 2025, *rest, *given)["ca-on/return"][0]


def test_a_foreign_pension_of_30000_above_line_11500_of_20000_is_refused() -> None:
    # Federal Worksheet, line 2 "Foreign pension income included in the amount on line 11500":
    # 30,000 is more than the whole of line 11500 (20,000), so line 5 is refused as an input error
    # rather than line 6 going negative and the pension amount being lost.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_11500):
        return_h(foreign="30000", additional_deductions="30000")


@pytest.mark.parametrize(
    "amounts",
    [
        {"foreign": "30000", "additional_deductions": "30000"},
        {"us_ira": "30000"},
        {"rrif": "30000"},
    ],
    ids=["foreign_pension", "us_ira", "rrif_or_prpp"],
)
def test_each_of_the_three_amounts_alone_above_line_11500_is_refused(
    amounts: dict[str, str],
) -> None:
    # Line 3 "Income from a U.S. individual retirement account (IRA) included in the amount on line
    # 11500", line 4 "Amounts from a RRIF or PRPP included in the amount on line 11500": each is
    # refused alone when it is above line 1.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_11500):
        return_h(**amounts)


def test_the_us_ira_of_15000_and_the_rrif_of_10000_together_above_line_11500_are_refused() -> None:
    # Lines 3 and 4 together are 25,000 of the 20,000 on line 11500: line 5 is refused, not taken as
    # not below zero to nothing.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_11500):
        return_h(us_ira="15000", rrif="10000")


def test_line_5_one_cent_above_line_11500_is_refused_not_capped() -> None:
    # The bound is inclusive: 20,000.01 on line 5 against 20,000 on line 1 is refused as an input
    # error, not capped to 20,000.00.
    with pytest.raises(
        InputAboveBoundError,
        match=re.escape("ca/pension_chart_line_5 20000.01 is above ca/pension_chart_line_1"),
    ):
        return_h(foreign="20000.01", additional_deductions="20000.01")


def test_line_5_equal_to_line_11500_is_accepted_and_line_6_is_0() -> None:
    # Line 5 of 20,000 is equal to line 1, so line 6 "Line 1 minus line 5" is 0 and the pension
    # amount on line 31400 is 0.
    worksheet = return_h(foreign="20000", additional_deductions="20000")

    assert worksheet.get(PENSION_CHART_LINE_5).value == D("20000.00")
    assert worksheet.get(PENSION_CHART_LINE_6).value == D("0")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("0")


# Form T1 line 25600 "Additional deductions" (the foreign pension income is deducted there, Federal
# Worksheet line 2): "ca/pension_foreign_income <amount> is above
# ca/additional_deductions_total <bound>".
ABOVE_LINE_25600 = r"ca/pension_foreign_income \S+ is above ca/additional_deductions_total \S+"


def test_a_foreign_pension_of_20000_with_nothing_deducted_on_line_25600_is_refused() -> None:
    # Federal Worksheet, line 2 "Foreign pension income included in the amount on line 11500 of your
    # return and deducted on line 25600 of your return": 20,000 is not deducted on line 25600 (0),
    # so it is refused as an input error, not taken into line 5 and the pension amount.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_25600):
        return_h(foreign="20000")


def test_a_foreign_pension_of_20000_deducted_on_line_25600_of_20000_is_accepted() -> None:
    # With 20,000 on line 25600 the foreign pension is deducted there: taxable income is 43,400.00
    # less the 20,000.00 deduction, 23,400.00. Federal and Ontario tax are then 0.00 and the refund
    # (a negative balance owing) is the 3,000.00 withheld less the 204.00 Ontario Health Premium,
    # 2,796.00.
    worksheet = return_h(foreign="20000", additional_deductions="20000")

    assert worksheet.get(TAXABLE_INCOME).value == D("23400.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2796.00")


def test_line_5_of_zero_is_accepted_and_line_6_is_the_whole_line_11500() -> None:
    # No foreign pension, U.S. IRA or RRIF amounts: line 5 is 0, line 6 is 20,000.00, and line 8 is
    # 20,000.00, so line 31400 is the worksheet's 2,000.00.
    worksheet = return_h()

    assert worksheet.get(PENSION_CHART_LINE_5).value == D("0")
    assert worksheet.get(PENSION_CHART_LINE_6).value == D("20000.00")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("2000.00")
