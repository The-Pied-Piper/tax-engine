"""CA-ON 2025 end to end: return gt (returns/2025_return_gt.yaml).

Return GT has one Form T2042 (farming) statement of a sole proprietor with one Area A row
(Class 6) of which a personal part comes off line 9936 and a business-use-of-home part (amount 7K)
is entered on Part 7. Every figure is worked by hand from the form's lines in the comments below,
not taken from the engine.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARM_CCA_CLAIM,
    FARM_CCA_CLAIM_LESS_PERSONAL_PART,
    FARM_CCA_TABLE_CLAIM,
    FARM_EXPENSES_SUBTOTAL,
    FARM_HOME_CARRY_FORWARD,
    FARM_HOME_EXPENSES,
    FARM_HOME_EXPENSES_AVAILABLE,
    FARM_HOME_EXPENSES_BUSINESS_PART,
    FARM_HOME_EXPENSES_SUBTOTAL,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARM_TOTAL_EXPENSES,
    FARMING_INCOME,
    NET_FARMING_INCOME,
    REFUND_OR_BALANCE_OWING,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Part 3: wheat 9371 82,850 and cattle 9471 20,000. Part 4: fertilizers and lime 9662 6,000 and
# seeds and plants 9664 10,000. Line 9936: the personal part 400 and amount 7K 600 (Part 7).
# Part 7: 7A heat 2,000, 7B electricity 1,500, 7C insurance 400, 7D maintenance 800, 7E mortgage
# interest 3,000, 7F property taxes 2,200, 7G other expenses 600; 7I personal-use part 1,500.
FARM = {
    "wheat": "82850",
    "cattle": "20000",
    "fertilizers_and_lime": "6000",
    "seeds_and_plants": "10000",
    "cca_personal_part": "400",
    "home_cca": "600",
    "home_heat": "2000",
    "home_electricity": "1500",
    "home_insurance": "400",
    "home_maintenance": "800",
    "home_mortgage_interest": "3000",
    "home_property_taxes": "2200",
    "home_other_expenses": "600",
    "home_personal_use_part": "1500",
}
# The Area A row: Class 6 (10%), undepreciated capital cost at the start 30,000, no additions or
# disposals, CCA claimed 3,000 (the 10% maximum of 30,000).
CLASS_6 = ("6", "30000", "0", "0", "0", "0", "3000", 0, "0", "0", "0")


def run_gt() -> dict[str, tuple[Worksheet, ...]]:
    """Return GT's inputs, as in `returns/2025_return_gt.yaml`: one sole proprietor's T2042
    statement with the Class 6 row, a personal part of CCA and amount 7K."""
    statement = {"farm": FARM, "farm_cca_classes_rows": (CLASS_6,)}
    return run("0", (), "0", "0", "0", "0", "0", farm_statements=(statement,))


def statement_gt() -> Worksheet:
    """The worksheet of Return GT's one T2042 statement."""
    return run_gt()["ca/t2042"][0]


def test_return_gts_line_9936_is_amount_ii_less_the_personal_part_and_amount_7k() -> None:
    # Amount ii of Area A is the claim 3,000 (at most 10% x 30,000 = 3,000). Line 9936 is amount ii
    # minus any personal part and any CCA for business-use-of-home expenses: 3,000 - 400 = 2,600,
    # then 2,600 - 600 = 2,000. 4B = 6,000 + 10,000 = 16,000; line 9898 = 16,000 + 2,000 = 18,000.
    worksheet = statement_gt()

    assert worksheet.get(FARM_CCA_TABLE_CLAIM).value == D("3000")
    assert worksheet.get(FARM_CCA_CLAIM_LESS_PERSONAL_PART).value == D("2600")
    assert worksheet.get(FARM_CCA_CLAIM).value == D("2000")
    assert worksheet.get(FARM_EXPENSES_SUBTOTAL).value == D("16000")
    assert worksheet.get(FARM_TOTAL_EXPENSES).value == D("18000")


def test_return_gts_net_income_before_adjustments_is_84850() -> None:
    # Line 9659 = 82,850 + 20,000 = 102,850; line 9899 = 102,850 - 18,000 = 84,850, which is 4C,
    # 5A, 5B and 5C (no inventory adjustment, partner, line 9951 or line 9943).
    worksheet = statement_gt()

    assert worksheet.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("84850")


def test_return_gts_home_expenses_available_are_9600_and_allowable_in_full() -> None:
    # 7H = 2,000 + 1,500 + 400 + 800 + 3,000 + 2,200 + 600 = 10,500; 7J = 10,500 - 1,500 = 9,000;
    # 7M = 9,000 + 600 (7K) + 0 (7L) = 9,600; 7N is 5C, 84,850; 7O = 9,600 - 84,850 is below 0, so
    # 0; 7P = the lesser of 9,600 and 84,850 = 9,600, which is line 9945.
    worksheet = statement_gt()

    assert worksheet.get(FARM_HOME_EXPENSES_SUBTOTAL).value == D("10500")
    assert worksheet.get(FARM_HOME_EXPENSES_BUSINESS_PART).value == D("9000")
    assert worksheet.get(FARM_HOME_EXPENSES_AVAILABLE).value == D("9600")
    assert worksheet.get(FARM_HOME_CARRY_FORWARD).value == D("0")
    assert worksheet.get(FARM_HOME_EXPENSES).value == D("9600")


def test_return_gts_net_farming_income_is_75250_and_the_tax_is_return_eys() -> None:
    # Line 9946 = 84,850 - 9,600 = 75,250, T1 line 14100; Return EY has the same 75,250.00 of net
    # self-employment income, so the total payable is its worked 14,468.38 (a balance owing).
    result = run_gt()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2042"][0].get(FARMING_INCOME).value == D("75250")
    assert worksheet.get(NET_FARMING_INCOME).value == D("75250.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("14468.38")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("14468.38")


def test_return_gts_trace_names_the_personal_part_and_amount_7k() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_gt().trace)

    for rendered_line in (
        "farm_cca_claim_less_personal_part: farm_cca_table_claim 3000 "
        "less farm_cca_personal_part 400 = 2600",
        "farm_cca_claim: farm_cca_claim_less_personal_part 2600 less farm_home_cca 600 = 2000",
        "farm_home_expenses_available: farm_home_expenses_business_part 9000 "
        "+ farm_home_cca 600 + farm_home_carried_forward 0 = 9600",
    ):
        assert rendered_line in rendered, rendered_line
