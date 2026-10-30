"""CA-ON 2025 end to end: return bc."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARM_CCA_CLAIM,
    FARM_CCA_CLAIM_LESS_PERSONAL_PART,
    FARM_EPOP_ASSOCIATED_CHECKED,
    FARM_EXPENSES_SUBTOTAL,
    FARM_GROSS_INCOME,
    FARM_GROSS_INCOME_BEFORE_EXPENSES,
    FARM_HOME_ALLOWABLE_CLAIM,
    FARM_HOME_CARRY_FORWARD,
    FARM_HOME_EXPENSES,
    FARM_HOME_EXPENSES_AVAILABLE,
    FARM_HOME_EXPENSES_BUSINESS_PART,
    FARM_HOME_EXPENSES_SUBTOTAL,
    FARM_HOME_INCOME_LIMIT,
    FARM_MOTOR_VEHICLE_EXPENSES,
    FARM_NET_INCOME_AFTER_ADJUSTMENTS,
    FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    FARM_OTHER_INCOME_WITH_RECAPTURE,
    FARM_PARTNER_CHECKED,
    FARM_PARTNER_OTHER_AMOUNTS,
    FARM_PARTNER_OTHER_AMOUNTS_TOTAL,
    FARM_PARTNERSHIP_TOTAL,
    FARM_RECAPTURED_CCA,
    FARM_SHARE_OF_NET_INCOME,
    FARM_TERMINAL_LOSS,
    FARM_TOTAL_EXPENSES,
    FARMING_INCOME,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca.trace import BusinessVehicleLine
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return BC's T2042: income lines of 80000 (wheat 50000 on line 9371, cattle 30000 on line 9471)
# and expenses of 50000 (fertilizers and lime 20000 on line 9662, seeds and plants 30000 on line
# 9664), with no capital cost allowance, inventory adjustment or partner.
FARM = {
    "wheat": "50000",
    "cattle": "30000",
    "fertilizers_and_lime": "20000",
    "seeds_and_plants": "30000",
    # Charts A to C for one leased passenger vehicle that is used for no farming: business
    # kilometres 0 (amount 1), so line 9819 (amount 16 of Chart A) is 0, the same as before the
    # charts; every Chart B and C line is still computed as printed.
    "vehicle_sales_tax_rate": "13",
}

# One vehicle of the statement, a record of `ca/business_vehicles`: the amounts of Charts A to C.
VEHICLE = {
    "business_kilometres": "0",
    "total_kilometres": "10000",
    "fuel_and_oil": "1000",
    "insurance": "600",
    "maintenance_and_repairs": "200",
    "other_expenses_10": "653",
    "interest_payable": "400",
    "interest_days": "183",
    "lease_charges": "2550",
    "lease_days": "183",
    "list_price": "60000",
}


def run_bc() -> dict[str, tuple[Worksheet, ...]]:
    """Return BC's inputs, as in `returns/2025_return_bc.yaml`: a sole proprietor whose only
    activity is a farming business, one T2042 statement for it: income of 80000 (line 9659 and T1
    line 14099), expenses of 50000 (4B), so line 9899 is 30000, which is line 9946 and T1 line
    14100.
    """
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({"farm": FARM, "farm_vehicles_rows": (VEHICLE,)},),
    )


def return_bc() -> Worksheet:
    """The return form's worksheet of `run_bc`: T1 lines 14100, 27 and below."""
    return run_bc()["ca-on/return"][0]


def statement_bc() -> Worksheet:
    """The worksheet of Return BC's one T2042 statement: its lines, as the form computes them."""
    return run_bc()["ca/t2042"][0]


def test_return_bcs_gross_farm_income_is_80000_on_line_9659_and_t1_line_14099() -> None:
    # Part 3: the income lines add to 50000 + 30000 = 80000, with no recapture (no Area A rows)
    # and line 9600 "Other income (specify)" 0, so line 9659, "Total of the income lines", is 80000,
    # which is T1 line 14099 and amount 4A.
    worksheet = statement_bc()

    assert worksheet.get(FARM_RECAPTURED_CCA).value == D("0")
    assert worksheet.get(FARM_OTHER_INCOME_WITH_RECAPTURE).value == D("0")
    assert worksheet.get(FARM_GROSS_INCOME).value == D("80000")
    assert worksheet.get(FARM_GROSS_INCOME_BEFORE_EXPENSES).value == D("80000")


def test_return_bcs_expenses_are_50000_and_net_income_before_inventory_adjustments_30000() -> None:
    # Part 4: amount 4B is the expense lines (20000 + 30000), 9937 and 9938 0 and line 9790 0, so
    # 4B is 50000; line 9898 is 4B plus line 9936, 50000 + 0; line 9899 is 80000 - 50000 = 30000.
    # With no inventory adjustments, amount 4C is 30000.
    worksheet = statement_bc()

    assert worksheet.get(FARM_EXPENSES_SUBTOTAL).value == D("50000")
    assert worksheet.get(FARM_TOTAL_EXPENSES).value == D("50000")
    assert worksheet.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000")
    assert worksheet.get(FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS).value == D("30000")


def test_return_bcs_has_no_cca_terminal_loss_or_recapture() -> None:
    # No Area A rows: the CCA claim (line 9936), the terminal loss (line 9790) and the recapture
    # (line 9600) are all 0, so none of them changes the figures above.
    worksheet = statement_bc()

    assert worksheet.get(FARM_CCA_CLAIM_LESS_PERSONAL_PART).value == D("0")
    assert worksheet.get(FARM_CCA_CLAIM).value == D("0")
    assert worksheet.get(FARM_TERMINAL_LOSS).value == D("0")
    assert worksheet.get(FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("0")


def test_return_bcs_sole_proprietor_has_no_partnership_amounts() -> None:
    # No partner (count 0): amount 5A is amount 4C, 30000, whatever the T5013 amount; amounts 9951,
    # 9974 and 6A to 6E are 0, so amount 5B is 30000, line 9943 is 0 and amount 5C is 30000.
    worksheet = statement_bc()

    assert worksheet.get(FARM_SHARE_OF_NET_INCOME).value == D("30000")
    assert worksheet.get(FARM_PARTNER_OTHER_AMOUNTS_TOTAL).value == D("0")
    assert worksheet.get(FARM_PARTNER_OTHER_AMOUNTS).value == D("0")
    assert worksheet.get(FARM_PARTNERSHIP_TOTAL).value == D("30000")
    assert worksheet.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("30000")


def test_return_bcs_business_use_of_home_is_nil() -> None:
    # Part 7: every amount 7A to 7L is 0, so amounts 7H, 7J, 7M and line 9945 are 0; amount 7N is
    # amount 5C, 30000, and amount 7O is 0 - 30000 floored, so 0, and amount 7P is 0.
    worksheet = statement_bc()

    assert worksheet.get(FARM_HOME_EXPENSES_SUBTOTAL).value == D("0")
    assert worksheet.get(FARM_HOME_EXPENSES_BUSINESS_PART).value == D("0")
    assert worksheet.get(FARM_HOME_EXPENSES_AVAILABLE).value == D("0")
    assert worksheet.get(FARM_HOME_INCOME_LIMIT).value == D("30000")
    assert worksheet.get(FARM_HOME_CARRY_FORWARD).value == D("0")
    assert worksheet.get(FARM_HOME_ALLOWABLE_CLAIM).value == D("0")
    assert worksheet.get(FARM_HOME_EXPENSES).value == D("0")


def test_return_bcs_net_farming_income_is_30000_on_line_9946_and_t1_line_14100() -> None:
    # Line 9946 is amount 5C minus line 9945: 30000 - 0 = 30000, T1 line 25 and line 14100; the net
    # self-employment income (line 27) is 0 + 0 + 0 + 30000 + 0.
    result = run_bc()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2042"][0].get(FARMING_INCOME).value == D("30000")
    assert worksheet.get(FARMING_INCOME).value == D("30000")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000")


def test_return_bcs_line_27_is_in_total_income_and_flows_down() -> None:
    # Line 27 (30000) is in total income (line 15000) and there is no other income, so total
    # income, net income and taxable income are 30000, and the tax is Return BB's on the same
    # figure: federal basic tax 4350.00, Ontario basic tax 1515.00 and a total payable of 3182.57.
    worksheet = return_bc()

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_return_bcs_trace_names_each_line_of_the_farm_statement() -> None:
    # The lines of the one T2042 statement, then those of the return form.
    result = run_bc()
    trace = (*result["ca/t2042"][0].trace, *result["ca-on/return"][0].trace)
    rendered = EnglishTraceRenderer().render_all(trace)

    for rendered_line in (
        "farm_gross_income_before_expenses: farm_gross_income 80000 = 80000",
        "farm_total_expenses: farm_expenses_subtotal 50000 + farm_cca_claim 0 = 50000",
        "farm_net_income_before_adjustments: farm_gross_income_before_expenses 80000 "
        "less farm_total_expenses 50000 = 30000",
        "farm_net_income_after_inventory_adjustments: farm_net_income_before_adjustments 30000 "
        "+ farm_optional_inventory_adjustment_current_year 0 "
        "+ farm_mandatory_inventory_adjustment_current_year 0 = 30000",
        "farm_share_of_net_income: farm_net_income_after_inventory_adjustments 30000, "
        "chosen as farm_partner_checked is 0",
        "farm_partnership_total: farm_share_of_net_income 30000 "
        "+ farm_fuel_charge_credit 0 + farm_partner_gst_hst_rebate 0 = 30000",
        "farm_net_income_after_adjustments: farm_partnership_total 30000 "
        "less farm_partner_other_amounts 0 = 30000",
        "farm_home_expenses_available: farm_home_expenses_business_part 0 "
        "+ farm_home_cca 0 + farm_home_carried_forward 0 = 0",
        "farm_home_income_limit: farm_net_income_after_adjustments 30000, not below 0 = 30000",
        "farm_home_carry_forward: farm_home_expenses_available 0 "
        "less farm_home_income_limit 30000, not below 0 = 0",
        "farm_home_allowable_claim: lesser of farm_home_expenses_available 0 "
        "and farm_home_income_limit 30000 = 0",
        "farm_home_expenses: farm_home_allowable_claim 0 = 0",
        "farming_income: farm_net_income_after_adjustments 30000 less farm_home_expenses 0 = 30000",
        "net_self_employment_income: business_income 0 + professional_income 0 "
        "+ commission_income 0 + farming_income 30000 + fishing_income 0 = 30000",
    ):
        assert rendered_line in rendered, rendered_line


def test_return_bcs_motor_vehicle_line_9819_is_0_from_charts_a_to_c() -> None:
    # Chart B: 350 ÷ 30 × 183 days = 2135.00, and the lesser of that and the 400 payable is 400.
    # Chart C: 44706 plus 13% is 50517.78, 1100 plus 13% is 1243.00 and 38000 plus 13% is 42940.00;
    # 60000 is the greater of 60000 and 50517.78, 85% of it is 51000.00, 1243.00 x 183 ÷ 30 is
    # 7582.30 and 42940.00 x 2550 ÷ 51000.00 is 2147.00, so the leasing cost is 2147.00. Chart A:
    # 1000 + 400 + 600 + 200 + 2147 + 653 = 5000, and 0 kilometres for farming give a business use
    # part of 0 x 5000 ÷ 10000 = 0, so line 9819 is 0 and the farm expenses are still 50000.
    worksheet = statement_bc()

    (vehicle,) = [each for each in worksheet.trace if isinstance(each, BusinessVehicleLine)]
    assert vehicle.line_12 == D("5000.00")
    assert vehicle.line_13 == D("0.00")
    assert vehicle.line_19 == D("400.00")
    assert vehicle.line_28 == D("2147.00")
    assert vehicle.line_16 == D("0.00")
    assert worksheet.get(FARM_MOTOR_VEHICLE_EXPENSES).value == D("0.00")
    assert worksheet.get(FARM_EXPENSES_SUBTOTAL).value == D("50000")


# Amount 7I, the personal-use part of the business-use-of-home expenses, is a part of amount 7H, the
# subtotal of amounts 7A to 7G: above it, it is refused as an input error, not capped.


def run_bc_home(**amounts: str) -> dict[str, tuple[Worksheet, ...]]:
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({"farm": {**FARM, **amounts}, "farm_vehicles_rows": (VEHICLE,)},),
    )


def test_a_home_part_above_the_subtotal_is_not_refused() -> None:
    # No printed bound applies: amount 7J is -400 as printed and, with no income limit above it,
    # the allowable claim (amount 7P, the lesser of 7M and 7N) is -400 too.
    statement = run_bc_home(home_heat="100", home_personal_use_part="500")["ca/t2042"][0]

    assert statement.get(FARM_HOME_EXPENSES_BUSINESS_PART).value == D("-400")
    assert statement.get(FARM_HOME_ALLOWABLE_CLAIM).value == D("-400")


def test_a_home_part_with_no_home_expenses_is_not_refused() -> None:
    # No printed bound applies: amount 7J is -99999 as printed and, with no income limit above it,
    # the allowable claim (amount 7P, the lesser of 7M and 7N) is -99999 too.
    statement = run_bc_home(home_personal_use_part="99999")["ca/t2042"][0]

    assert statement.get(FARM_HOME_EXPENSES_BUSINESS_PART).value == D("-99999")
    assert statement.get(FARM_HOME_ALLOWABLE_CLAIM).value == D("-99999")


def test_a_home_personal_use_part_equal_to_the_subtotal_is_accepted() -> None:
    statement = run_bc_home(home_heat="500", home_personal_use_part="500")["ca/t2042"][0]

    assert statement.get(FARM_HOME_EXPENSES_BUSINESS_PART).value == D("0")


def test_home_cca_with_no_cca_claim_is_not_refused_and_arithmetic_stands() -> None:
    # Amount 7K of 3000 is no longer refused against the CCA claim of 0: the claim is 0 less 3000
    # = -3000 as printed, so farm expenses are 50000 less 3000 = 47000.
    result = run_bc_home(home_cca="3000")
    statement = result["ca/t2042"][0]

    assert statement.get(FARM_CCA_CLAIM).value == D("-3000")
    assert statement.get(FARM_TOTAL_EXPENSES).value == D("47000")


# The partner answer of amount 5A is a yes or no answer: 2 or more is refused, not read as yes.


def run_farm_partner(answer: int) -> dict[str, tuple[Worksheet, ...]]:
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=(
            {
                "farm": {**FARM, "partner_share": "5000" if answer else "0"},
                "farm_partner": answer,
                "farm_vehicles_rows": (VEHICLE,),
            },
        ),
    )


@pytest.mark.parametrize("answer", [2, 400])
def test_a_partner_answer_above_1_is_refused(answer: int) -> None:
    with pytest.raises(
        InputAboveBoundError, match=f"farm_partner {answer} is above a yes or no answer of 1"
    ):
        run_farm_partner(answer)


@pytest.mark.parametrize(("answer", "share"), [(1, "5000"), (0, None)])
def test_a_partner_answer_of_1_or_0_is_produced_as_it_is(answer: int, share: str | None) -> None:
    statement = run_farm_partner(answer)["ca/t2042"][0]

    assert statement.get(FARM_PARTNER_CHECKED).value == answer
    if share is not None:
        assert statement.get(FARM_SHARE_OF_NET_INCOME).value == D(share)


def test_the_trace_checks_the_partner_answer_as_a_yes_or_no_count() -> None:
    rendered = EnglishTraceRenderer().render_all(run_farm_partner(1)["ca/t2042"][0].trace)

    assert f"{FARM_PARTNER_CHECKED.label}: farm_partner 1, a yes or no answer of 0 or 1" in rendered


# The form asks no partner question and prints no rule against a partner figure with the answer no:
# 5A takes the "or" of amount 4C and the T5013 share by the 0 or 1 answer, and lines 9974 and 9943
# enter 5B and 5C with no condition, so every figure typed is used.


def test_a_partner_answer_0_uses_amount_4c_and_every_partner_figure_typed() -> None:
    # Partner no, 4C 70000 - 50000 = 20000, T5013 share typed 10000, line 9974 300, 6A 1000:
    # 5A = 20000 (the T5013 share is the other side of the "or"), 5B = 20000 + 0 + 300 = 20300
    # and 5C = 20300 - 1000 = 19300.
    farm = {
        **FARM,
        "wheat": "40000",
        "partner_share": "10000",
        "partner_gst_hst_rebate": "300",
        "partner_other_amount_a": "1000",
    }
    statement = run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({"farm": farm, "farm_partner": 0, "farm_vehicles_rows": (VEHICLE,)},),
    )["ca/t2042"][0]

    assert statement.get(FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS).value == D("20000")
    assert statement.get(FARM_SHARE_OF_NET_INCOME).value == D("20000")
    assert statement.get(FARM_PARTNERSHIP_TOTAL).value == D("20300")
    assert statement.get(FARM_PARTNER_OTHER_AMOUNTS_TOTAL).value == D("1000")
    assert statement.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("19300")


# Area G is only filled in "If you answered yes", and its figures count only in the cases the form
# names: a figure entered with the answer that switches it off is not read.


def run_farm_area_g(**changes: Any) -> dict[str, tuple[Worksheet, ...]]:
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({"farm": FARM, "farm_vehicles_rows": (VEHICLE,), **changes},),
    )


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {
            "farm_epop_associated": 1,
            "farm_epop_percentage": "40",
            "farm_epop_percentage_total": "40",
        },
        {"farm_minister_allocation_given": 1, "farm_minister_allocation": "0"},
    ],
)
def test_area_g_figures_with_their_answer_yes_or_blank_are_accepted(
    changes: dict[str, Any],
) -> None:
    statement = run_farm_area_g(**changes)["ca/t2042"][0]

    assert statement.get(FARM_EPOP_ASSOCIATED_CHECKED).value == changes.get(
        "farm_epop_associated", 0
    )
