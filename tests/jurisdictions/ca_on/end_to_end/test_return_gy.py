"""CA-ON 2025 end to end: return gy."""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FEDERAL_BASIC_TAX,
    FISH_CCA_CLAIM,
    FISH_CCA_CLAIM_LESS_PERSONAL_PART,
    FISH_CCA_TABLE_CLAIM,
    FISH_CLOSING_UCC,
    FISH_EXPENSES_SUBTOTAL,
    FISH_GROSS_INCOME,
    FISH_GROSS_INCOME_BEFORE_EXPENSES,
    FISH_HOME_ALLOWABLE_CLAIM,
    FISH_HOME_CARRY_FORWARD,
    FISH_HOME_EXPENSES,
    FISH_HOME_EXPENSES_AVAILABLE,
    FISH_HOME_INCOME_LIMIT,
    FISH_NET_INCOME_AFTER_ADJUSTMENTS,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISH_RECAPTURED_CCA,
    FISH_TOTAL_EXPENSES,
    FISHING_INCOME,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return GY's T2121, as in `returns/2025_return_gy.yaml`: the five lines no other return sets,
# other marine products 3000 (3B), grants, credits, and rebates 1200 (3C), compensation for loss
# 800 (3E), a CCA personal part of 600 and the business-use-of-home CCA (7K) of 900, on top of
# Return BD's fish products of 40000 and expenses of 25000 (salt, bait and ice 10000 on line 9138,
# fishing gear 15000 on line 9136).
FISH = {
    "fish_products": "40000",
    "other_marine_products": "3000",
    "grants_credits_and_rebates": "1200",
    "compensation_for_loss": "800",
    "salt_bait_and_ice": "10000",
    "fishing_gear": "15000",
    "vehicle_sales_tax_rate": "13",
    "cca_personal_part": "600",
    "home_cca": "900",
}
# The one Area A row: Class 8 with an undepreciated capital cost at the start of the year of 20000,
# no additions or dispositions, and the full 20% claimed: 4000 (column 21).
FISH_CLASS_8 = ("8", "20000", "0", "0", "0", "0", "4000", 0, "0", "0", "0")


def run_gy() -> dict[str, tuple[Worksheet, ...]]:
    """Return GY's inputs, as in `returns/2025_return_gy.yaml`: a sole proprietor whose only
    activity is a fishing business, one T2121 statement for it: income of 45000 (line 8299 and T1
    line 14299), expenses of 25000 (4Q) and a CCA claim of 2500 (line 9936), so line 9369 is 17500
    and, after the business-use-of-home CCA of 900, line 9946 and T1 line 14300 are 16600.
    """
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        fish_statements=({"fish": FISH, "fish_cca_classes_rows": (FISH_CLASS_8,)},),
    )


def return_gy() -> Worksheet:
    """The return form's worksheet of `run_gy`: T1 lines 14300, 27 and below."""
    return run_gy()["ca-on/return"][0]


def statement_gy() -> Worksheet:
    """The worksheet of Return GY's one T2121 statement: its lines, as the form computes them."""
    return run_gy()["ca/t2121"][0]


def test_return_gys_gross_income_adds_amounts_3b_3c_and_3e_to_3a() -> None:
    # Part 3: amounts 3A to 3F and line 9600 add to 40000 + 3000 + 1200 + 0 + 800 + 0 + 0 = 45000
    # with no recapture (Class 8's column 7, 20000, is not negative), so line 8299, "Gross income",
    # is 45000, which is T1 line 14299 and amount 4A.
    worksheet = statement_gy()

    assert worksheet.get(FISH_RECAPTURED_CCA).value == D("0")
    assert worksheet.get(FISH_GROSS_INCOME).value == D("45000")
    assert worksheet.get(FISH_GROSS_INCOME_BEFORE_EXPENSES).value == D("45000")


def test_return_gys_cca_line_9936_is_the_claim_less_the_personal_part_and_the_home_cca() -> None:
    # Area A: Class 8's base amount (column 19) is 20000 and 20% of it is 4000, claimed in full, so
    # amount ii is 4000. Line 9936 is amount ii minus the personal part (600) and the CCA for
    # business-use-of-home expenses (7K, 900): 4000 - 600 - 900 = 2500.
    worksheet = statement_gy()

    assert worksheet.get(FISH_CCA_TABLE_CLAIM).value == D("4000")
    assert worksheet.get(FISH_CCA_CLAIM_LESS_PERSONAL_PART).value == D("3400")
    assert worksheet.get(FISH_CCA_CLAIM).value == D("2500")


def test_return_gys_expenses_are_27500_and_net_income_before_adjustments_17500() -> None:
    # Part 4: amount 4Q is 10000 + 15000 = 25000; line 9368 is 4Q plus line 9936, 25000 + 2500 =
    # 27500; line 9369 is 45000 - 27500 = 17500.
    worksheet = statement_gy()

    assert worksheet.get(FISH_EXPENSES_SUBTOTAL).value == D("25000")
    assert worksheet.get(FISH_TOTAL_EXPENSES).value == D("27500")
    assert worksheet.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("17500")
    assert worksheet.get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value == D("17500")


def test_return_gys_closing_ucc_is_20000_less_the_claim_of_4000() -> None:
    # Column 22 is column 7 minus column 21: 20000 - 4000 = 16000, whatever the personal part.
    closing = statement_gy().get(FISH_CLOSING_UCC).value

    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in closing.records] == [
        (D("8"), D("16000"))
    ]


def test_return_gys_home_cca_7k_is_all_of_7m_and_is_allowed_in_full() -> None:
    # Part 7: amounts 7A to 7L other than 7K are 0, so 7M is 900; amount 7N is amount 5C, 17500, so
    # 7O is 0 and 7P, the lesser of 7M and 7N, is 900, which is line 9945.
    worksheet = statement_gy()

    assert worksheet.get(FISH_HOME_EXPENSES_AVAILABLE).value == D("900")
    assert worksheet.get(FISH_HOME_INCOME_LIMIT).value == D("17500")
    assert worksheet.get(FISH_HOME_CARRY_FORWARD).value == D("0")
    assert worksheet.get(FISH_HOME_ALLOWABLE_CLAIM).value == D("900")
    assert worksheet.get(FISH_HOME_EXPENSES).value == D("900")


def test_return_gys_net_fishing_income_is_16600_on_line_9946_and_t1_line_14300() -> None:
    # Line 9946 is amount 5C minus line 9945: 17500 - 900 = 16600, T1 line 26 and line 14300; the
    # net self-employment income (line 27) is 0 + 0 + 0 + 0 + 16600.
    result = run_gy()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2121"][0].get(FISHING_INCOME).value == D("16600")
    assert worksheet.get(FISHING_INCOME).value == D("16600")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("16600")


def test_return_gys_line_27_is_in_total_income_and_flows_down() -> None:
    # Total income, net income and taxable income are 16600.00. Federal basic tax is 16600.00 x
    # 14.5% = 2407.00, less the credits of 2338.71 (16129.00 x 14.5%): 68.29. Ontario basic tax is
    # 16600.00 x 5.05% = 838.30; less 643.72 it is 194.58, and the Ontario tax reduction (588.00
    # less 194.58 = 393.42) takes the Ontario tax to 0. The total payable is 68.29; the Canada
    # workers benefit is capped at 1633.00 (27% of 13600.00 is 3672.00), so the refund is
    # 1633.00 - 68.29 = 1564.71.
    worksheet = return_gy()

    assert worksheet.get(TOTAL_INCOME).value == D("16600.00")
    assert worksheet.get(NET_INCOME).value == D("16600.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("16600.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("2407.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("838.30")
    assert worksheet.get(TOTAL_PAYABLE).value == D("68.29")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1564.71")


def test_return_gys_trace_names_each_line_of_the_five_figures() -> None:
    # The lines of the one T2121 statement, then those of the return form.
    result = run_gy()
    trace = (*result["ca/t2121"][0].trace, *result["ca-on/return"][0].trace)
    rendered = EnglishTraceRenderer().render_all(trace)

    for rendered_line in (
        "fish_gross_income: fish_fish_products 40000 + fish_other_marine_products 3000 "
        "+ fish_grants_credits_and_rebates 1200 + fish_subsidies 0 "
        "+ fish_compensation_for_loss 800 + fish_sharesperson_income 0 "
        "+ fish_other_income_with_recapture 0 = 45000",
        "fish_cca_claim_less_personal_part: fish_cca_table_claim 4000 "
        "less fish_cca_personal_part 600 = 3400",
        "fish_cca_claim: fish_cca_claim_less_personal_part 3400 less fish_home_cca 900 = 2500",
        "fish_total_expenses: fish_expenses_subtotal 25000 + fish_cca_claim 2500 = 27500",
        "fish_net_income_before_adjustments: fish_gross_income_before_expenses 45000 "
        "less fish_total_expenses_deductible 27500 = 17500",
        "fish_home_expenses_available: fish_home_expenses_business_part 0 "
        "+ fish_home_cca 900 + fish_home_carried_forward 0 = 900",
        "fish_home_allowable_claim: lesser of fish_home_expenses_available 900 "
        "and fish_home_income_limit 17500 = 900",
        "fishing_income: fish_net_income_after_adjustments 17500 less fish_home_expenses 900 "
        "= 16600",
    ):
        assert rendered_line in rendered, rendered_line
