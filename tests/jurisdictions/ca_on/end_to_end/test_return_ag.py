"""CA-ON 2025 end to end: return ag."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    MEDICAL_CLAIM,
    NET_FEDERAL_TAX,
    NET_INCOME,
    PROVINCIAL_CREDITS,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    SPOUSE_AMOUNT,
    SPOUSE_NET_INCOME,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.catalog import (
    ONTARIO_CREDITS,
    ONTARIO_CREDITS_SUBTOTAL,
    SENIORS_CARE_AMOUNT,
    SENIORS_CARE_BASE_AMOUNT,
    SENIORS_CARE_BEFORE_CLAIM,
    SENIORS_CARE_BEFORE_MAXIMUM,
    SENIORS_CARE_CREDIT,
    SENIORS_CARE_FAMILY_NET_INCOME,
    SENIORS_CARE_INCOME_OVER_BASE,
    SENIORS_CARE_REDUCTION,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ag(**overrides: Any) -> Worksheet:
    """Return AG's inputs, as in `returns/2025_return_ag.yaml`: a retiree with a spouse.

    Other pensions and superannuation of 30000 are the whole income, so the net income is
    30000.00; the filer, born in 1960 or earlier, claims the spouse amount for a spouse of net
    income 10000 and 4900 of medical expenses (line 58769 of 4000.00), claims the Ontario seniors
    care at home tax credit and has 3000 deducted.
    """
    inputs: dict[str, Any] = {
        "other_pensions_and_superannuation": "30000",
        "born_in_1960_or_earlier": 1,
        "spouse_net_income": "10000",
        "spouses_claimed": 1,
        "medical_expenses": "4900",
        "income_tax_deducted": "3000",
        "claims_seniors_care_credit": 1,
    }
    return compute("0", (), "0", "0", "0", "0", "0", **{**inputs, **overrides})


def test_return_ags_seniors_care_at_home_credit_is_750_and_lowers_the_refund() -> None:
    # Return AG has other pensions and superannuation of 30000 and no other income: total income
    # and net income are 30000.00, and taxable income too. Its medical expenses of 4900 (T1 line
    # 107, ON428 line 36) less the lesser of 2885 and 3% of 30000.00 (900.00) are 4000.00: ON428
    # line 41, and with no other dependants line 43 (line 58769) is 4000.00.
    # ON479 line 3 is that 4000.00; line 5 is 25% of it, 1000.00, at most 1500; line 6 is the net
    # income 30000.00 and line 7 the spouse's 10000, so line 8 is 40000.00; line 9 is 35000.00,
    # line 10 is 40000.00 - 35000.00 = 5000.00, line 12 is 5% of it, 250.00, and line 13 is
    # 1000.00 - 250.00 = 750.00, claimed once. Line 18 adds lines 1, 13, 14, 16 and 17: 0 + 750.00
    # + 0 + 0 + 0, line 21 is that 750.00 with no co-operative education credit, and so is T1 line
    # 47900. The total credits (line 166) are the 3000 deducted plus 750.00, 3750.00; the total
    # payable is the Ontario tax of 300.00 (the health premium alone, the rest taken off by the
    # credits) with no federal tax: line 167 is 300.00 - 3750.00 = -3450.00, a refund.
    worksheet = return_ag()

    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(MEDICAL_CLAIM).value == D("4000.00")
    assert worksheet.get(ontario.MEDICAL_CLAIM).value == D("4000.00")
    assert worksheet.get(SENIORS_CARE_BEFORE_MAXIMUM).value == D("1000.00")
    assert worksheet.get(SENIORS_CARE_AMOUNT).value == D("1000.00")
    assert worksheet.get(SENIORS_CARE_FAMILY_NET_INCOME).value == D("40000.00")
    assert worksheet.get(SENIORS_CARE_BASE_AMOUNT).value == D("35000.00")
    assert worksheet.get(SENIORS_CARE_INCOME_OVER_BASE).value == D("5000.00")
    assert worksheet.get(SENIORS_CARE_REDUCTION).value == D("250.00")
    assert worksheet.get(SENIORS_CARE_BEFORE_CLAIM).value == D("750.00")
    assert worksheet.get(SENIORS_CARE_CREDIT).value == D("750.00")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("750.00")
    assert worksheet.get(ONTARIO_CREDITS).value == D("750.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("750.00")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("300.00")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("0")
    assert worksheet.get(TOTAL_PAYABLE).value == D("300.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("3750.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-3450.00")
    assert worksheet.get(REFUND).value == D("3450.00")
    assert worksheet.get(ontario.NET_REFUND).value == D("3450.00")


def test_return_ags_trace_names_each_line_of_the_seniors_care_at_home_credit() -> None:
    rendered = EnglishTraceRenderer().render_all(return_ag().trace)

    for line in (
        "seniors_care_before_maximum: 25% of medical_claim 4000 (half-up to 0.01)",
        "seniors_care_amount: lesser of seniors_care_before_maximum 1000 and 1500 "
        "(half-up to 0.01)",
        "seniors_care_family_net_income: tosi_adjusted_net_income_not_below_zero 30000 "
        "+ spouse_net_income 10000 = 40000",
        "seniors_care_base_amount: credit amount 35000 (half-up to 0.01)",
        "seniors_care_income_over_base: seniors_care_family_net_income 40000 "
        "less seniors_care_base_amount 35000, not below 0 = 5000",
        "seniors_care_reduction: 5% of seniors_care_income_over_base 5000 (half-up to 0.01)",
        "seniors_care_before_claim: seniors_care_amount 1000 "
        "less seniors_care_reduction 250, not below 0 = 750",
        "seniors_care_credit: seniors_care_before_claim 750 "
        "for each of 1 claims_seniors_care_credit_checked = 750",
        "ontario_credits_subtotal: fertility_credit 0 + care_credit 0 + seniors_care_credit 750 "
        "+ seniors_transit_credit 0 + political_credit 0 + flow_through_share_credit 0 = 750",
        "ontario_credits: ontario_credits_subtotal 750 + coop_education_credit 0 = 750",
        "provincial_credits: ontario_credits 750 = 750",
    ):
        assert line in rendered, line


def test_a_filer_who_does_not_claim_the_credit_gets_none_whatever_line_13_is() -> None:
    # The count is the caller's: the engine checks no eligibility condition. Line 13 is still
    # worked out, 750.00, but the credit is 0 and so are lines 18 and 21 and the provincial credits.
    worksheet = return_ag(claims_seniors_care_credit=0)

    assert worksheet.get(SENIORS_CARE_BEFORE_CLAIM).value == D("750.00")
    assert worksheet.get(SENIORS_CARE_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("0")
    assert worksheet.get(ONTARIO_CREDITS).value == D("0")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("0")
    assert worksheet.get(TOTAL_CREDITS).value == D("3000")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2700.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "seniors_care_credit: seniors_care_before_claim 750 "
        "for each of 0 claims_seniors_care_credit_checked = 0"
    ) in rendered


@pytest.mark.parametrize(
    ("spouse_net_income", "medical_expenses", "line_5", "line_12", "credit"),
    [
        # The acceptance figures: family net income 40000 gives 750.00; 30000 (no spouse income)
        # gives 1000.00; 70000 gives 0.
        ("10000", "4900", "1000.00", "250.00", "750.00"),
        ("0", "4900", "1000.00", "0", "1000.00"),
        ("40000", "4900", "1000.00", "1750.00", "0"),
        # Line 58769 of 8000 (medical expenses of 8900 less 900.00) gives line 5 of 1500, the
        # maximum: 25% of 8000 is 2000.00.
        ("0", "8900", "1500", "0", "1500.00"),
        ("10000", "8900", "1500", "250.00", "1250.00"),
        # A spouse's 5000 makes the family net income 35000, where nothing comes off. At 65000
        # line 12 is 5% of 30000, 1500.00, and at 65000.01 it is 1500.0005, down to 1500.00: line
        # 13 is 0 at both, whatever the spouse's net income above.
        ("5000", "8900", "1500", "0", "1500.00"),
        ("35000", "8900", "1500", "1500.00", "0"),
        ("35000.01", "8900", "1500", "1500.00", "0"),
        ("35000", "4900", "1000.00", "1500.00", "0"),
    ],
)
def test_the_credit_follows_the_family_net_income_and_the_maximum(
    spouse_net_income: str, medical_expenses: str, line_5: str, line_12: str, credit: str
) -> None:
    worksheet = return_ag(spouse_net_income=spouse_net_income, medical_expenses=medical_expenses)

    assert worksheet.get(SENIORS_CARE_AMOUNT).value == D(line_5)
    assert worksheet.get(SENIORS_CARE_REDUCTION).value == D(line_12)
    assert worksheet.get(SENIORS_CARE_CREDIT).value == D(credit)
    assert worksheet.get(ONTARIO_CREDITS).value == D(credit)


def test_line_7_is_the_spouses_net_income_that_the_spouse_amount_reads_too() -> None:
    # The same caller input as T1 line 30300 and ON428 line 58120: a spouse of net income 10000
    # takes 10000 off the spouse amount (16129 - 10000 = 6129.00; 11905 - 10000 = 1905.00) and
    # adds 10000 to ON479 line 8.
    worksheet = return_ag()

    assert worksheet.get(SPOUSE_NET_INCOME).value == D("10000")
    assert worksheet.get(SPOUSE_AMOUNT).value == D("6129.00")
    assert worksheet.get(ontario.SPOUSE_AMOUNT).value == D("1905.00")
    assert worksheet.get(SENIORS_CARE_FAMILY_NET_INCOME).value == D("40000.00")


def test_line_3_is_the_ontario_medical_claim_and_not_the_federal_one() -> None:
    # ON479 line 3 reads line 58769 of the ON428, so a figure only the ON428 changes moves it: two
    # other dependants' expenses are the same on both forms, but the Ontario per-dependant maximum
    # of 15551 is not on the T1. A dependant with expenses of 20000 and no income: 15551 on ON428,
    # 20000 on the T1.
    worksheet = return_ag(other_dependants=(("20000", "0"),))

    assert worksheet.get(MEDICAL_CLAIM).value == D("24000.00")
    assert worksheet.get(ontario.MEDICAL_CLAIM).value == D("19551.00")
    assert worksheet.get(SENIORS_CARE_BEFORE_MAXIMUM).value == D("4887.75")
    assert worksheet.get(SENIORS_CARE_AMOUNT).value == D("1500")
    assert worksheet.get(SENIORS_CARE_BEFORE_CLAIM).value == D("1250.00")
