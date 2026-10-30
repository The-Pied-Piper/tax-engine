"""CA-ON 2025 end to end: return gs (returns/2025_return_gs.yaml).

Return GS has one Form T2042 (farming) statement of a sole proprietor that fills in every income
and expense line of Parts 3 and 4 that no earlier return sets, the current year's inventory
adjustments (lines 9941 and 9942) and line 9951 of Part 5. Every figure is worked by hand from the
form's lines in the comments below, not taken from the engine.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARM_CCA_CLAIM,
    FARM_EXPENSES_SUBTOTAL,
    FARM_GROSS_INCOME,
    FARM_GROSS_INCOME_BEFORE_EXPENSES,
    FARM_NET_INCOME_AFTER_ADJUSTMENTS,
    FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARM_OTHER_INCOME_WITH_RECAPTURE,
    FARM_PARTNERSHIP_TOTAL,
    FARM_TOTAL_EXPENSES,
    FARMING_INCOME,
    NET_FARMING_INCOME,
    NET_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Part 3, the lines of the form in order (the line number in the comment). Grains and oilseeds:
# wheat 9371, oats 9372, barley 9373, mixed grains 9374, corn 9375, canola 9376, flaxseed 9377,
# soybeans 9378 and 9370. Other crops: fruit 9421, potatoes 9422, vegetables 9423, tobacco 9424,
# other crops 9420, greenhouse and nursery 9425 and forage crops or seeds 9426. Livestock: cattle
# 9471, swine 9472, poultry 9473, sheep and lambs 9474 and 9470; milk and cream 9476, eggs 9477,
# other commodities 9520. Program payments: dairy subsidies 9541, crop insurance 9542, other 9540.
# Rebates 9570, custom work 9601, insurance proceeds 9604, patronage dividends 9605, other 9600.
INCOME = {
    "wheat": "24950",
    "oats": "1100",
    "barley": "1200",
    "mixed_grains": "1300",
    "corn": "1400",
    "canola": "1500",
    "flaxseed": "1600",
    "soybeans": "1700",
    "grains_and_oilseeds": "1800",
    "fruit": "2100",
    "potatoes": "2200",
    "vegetables": "2300",
    "tobacco": "2400",
    "greenhouse_and_nursery": "2500",
    "forage_crops_or_seeds": "2600",
    "other_crops": "2000",
    "cattle": "3100",
    "swine": "3200",
    "poultry": "3300",
    "sheep_and_lambs": "3400",
    "livestock_and_animal_products_revenue": "3000",
    "milk_and_cream": "4100",
    "eggs": "4200",
    "other_commodities": "4300",
    "dairy_subsidies": "5100",
    "crop_insurance": "5200",
    "other_program_payments": "5000",
    "rebates": "6100",
    "custom_work": "6200",
    "insurance_proceeds": "6300",
    "patronage_dividends": "6400",
    "other_income": "700",
}
# Part 4, the expense lines in order: 9661, 9662, 9663, 9664, 9711, 9712, 9713 (17,800), then 9760,
# 9764, 9795, 9796, 9797, 9798, 9799, 9802, 9803, 9804 (16,500), then 9805, 9808, 9809, 9810, 9811,
# 9814, 9820 (17,500). Lines 9819 (no vehicle), 9937, 9938 and 9790 are 0.
EXPENSES = {
    "containers_and_twine": "100",
    "fertilizers_and_lime": "6000",
    "pesticides": "700",
    "seeds_and_plants": "8000",
    "feed_supplements_straw_and_bedding": "900",
    "livestock_purchased": "1000",
    "veterinary_fees": "1100",
    "machinery_repairs_licences_and_insurance": "1200",
    "gasoline_diesel_and_oil": "1300",
    "building_repairs_and_maintenance": "1400",
    "clearing_levelling_and_draining": "1500",
    "crop_insurance_premiums": "1600",
    "custom_work_expenses": "1700",
    "electricity": "1800",
    "heating_and_curing_fuel": "1900",
    "insurance_program_overpayment_recapture": "2000",
    "insurance": "2100",
    "interest_and_bank_charges": "2200",
    "office_expenses": "2300",
    "professional_fees": "2400",
    "property_taxes": "2500",
    "rent": "2600",
    "salaries_wages_and_benefits": "2700",
    "small_tools": "2800",
}
# Lines 9941 (optional) and 9942 (mandatory) of the current year, and line 9951 of Part 5, entered
# as the inputs they are today (line 9951 may not be above the Form T2043 credit, entered too).
ADJUSTMENTS = {
    "optional_inventory_adjustment_current_year": "1500",
    "mandatory_inventory_adjustment_current_year": "2500",
    "fuel_charge_credit": "800",
}


def run_gs() -> dict[str, tuple[Worksheet, ...]]:
    """Return GS's inputs, as in `returns/2025_return_gs.yaml`: one sole proprietor's T2042
    statement with every Part 3 and Part 4 line above, and no Area A row, vehicle or partner."""
    farm = {**INCOME, **EXPENSES, **ADJUSTMENTS}
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({"farm": farm},),
        fuel_charge_partnership_credit_on="800",
    )


def statement_gs() -> Worksheet:
    """The worksheet of Return GS's one T2042 statement."""
    return run_gs()["ca/t2042"][0]


def return_gs() -> Worksheet:
    """The return form's worksheet of `run_gs`: T1 lines 14100, 27 and below."""
    return run_gs()["ca-on/return"][0]


def test_return_gss_gross_income_is_122250_on_line_9659() -> None:
    # Grains and oilseeds 24,950 + 1,100 + 1,200 + 1,300 + 1,400 + 1,500 + 1,600 + 1,700 + 1,800 =
    # 36,550; other crops 2,100 + 2,200 + 2,300 + 2,400 + 2,500 + 2,600 + 2,000 = 16,100; livestock
    # 3,100 + 3,200 + 3,300 + 3,400 + 3,000 = 16,000; milk, eggs and other commodities 4,100 +
    # 4,200 + 4,300 = 12,600; program payments 5,100 + 5,200 + 5,000 = 15,300; rebates, custom
    # work, insurance proceeds, patronage dividends and other income 6,100 + 6,200 + 6,300 + 6,400
    # + 700 = 25,700. Line 9659 = 36,550 + 16,100 + 16,000 + 12,600 + 15,300 + 25,700 = 122,250.
    worksheet = statement_gs()

    assert worksheet.get(FARM_OTHER_INCOME_WITH_RECAPTURE).value == D("700")
    assert worksheet.get(FARM_GROSS_INCOME).value == D("122250")
    assert worksheet.get(FARM_GROSS_INCOME_BEFORE_EXPENSES).value == D("122250")


def test_return_gss_expenses_are_51800_and_net_income_before_adjustments_70450() -> None:
    # 4B = 17,800 + 16,500 + 17,500 = 51,800; there is no Area A row, so line 9936 is 0 and line
    # 9898 = 51,800 + 0 = 51,800; line 9899 = 122,250 - 51,800 = 70,450.
    worksheet = statement_gs()

    assert worksheet.get(FARM_EXPENSES_SUBTOTAL).value == D("51800")
    assert worksheet.get(FARM_CCA_CLAIM).value == D("0")
    assert worksheet.get(FARM_TOTAL_EXPENSES).value == D("51800")
    assert worksheet.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("70450")


def test_return_gss_inventory_adjustments_and_line_9951_give_net_income_75250() -> None:
    # 4C = 70,450 + 1,500 (line 9941) + 2,500 (line 9942) = 74,450; 5A is 4C (no partner); 5B =
    # 74,450 + 800 (line 9951) + 0 (line 9974) = 75,250; line 9943 is 0, so 5C = 75,250; there are
    # no home expenses, so line 9945 is 0 and line 9946 = 75,250.
    worksheet = statement_gs()

    assert worksheet.get(FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS).value == D("74450")
    assert worksheet.get(FARM_PARTNERSHIP_TOTAL).value == D("75250")
    assert worksheet.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("75250")
    assert worksheet.get(FARMING_INCOME).value == D("75250")


def test_return_gss_t1_and_tax_figures_are_those_of_return_ey() -> None:
    # Line 14100 is 75,250.00, all of total income, net income and taxable income (no deduction).
    # Return EY has the same 75,250.00 of net self-employment income, so its worked tax applies:
    # federal tax 11,983.76 less the basic personal credit 2,338.71 is 9,645.05; Ontario tax
    # 4,717.05 less 643.72 is 4,073.33 plus the health premium 750; total payable 14,468.38. Line
    # 9951 of 800 is matched by Form T2043 line 67079 of 800, which is line 47556, a refundable
    # credit: 14,468.38 - 800.00 = 13,668.38 owing.
    worksheet = return_gs()

    assert worksheet.get(NET_FARMING_INCOME).value == D("75250.00")
    assert worksheet.get(TOTAL_INCOME).value == D("75250.00")
    assert worksheet.get(NET_INCOME).value == D("75250.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("75250.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("14468.38")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("13668.38")


def test_return_gss_trace_names_the_sums_that_read_the_new_lines() -> None:
    rendered = EnglishTraceRenderer().render_all(run_gs()["ca/t2042"][0].trace)

    for rendered_line in (
        "farm_gross_income_before_expenses: farm_gross_income 122250 = 122250",
        "farm_total_expenses: farm_expenses_subtotal 51800 + farm_cca_claim 0 = 51800",
        "farm_net_income_after_inventory_adjustments: farm_net_income_before_adjustments 70450 "
        "+ farm_optional_inventory_adjustment_current_year 1500 "
        "+ farm_mandatory_inventory_adjustment_current_year 2500 = 74450",
        "farm_partnership_total: farm_share_of_net_income 74450 + farm_fuel_charge_credit 800 "
        "+ farm_partner_gst_hst_rebate 0 = 75250",
    ):
        assert rendered_line in rendered, rendered_line
