"""CA-ON 2025 end to end: return jx, Form T90 "Income Exempt from Tax under the Indian Act" as its
own form, and the Schedule 6 election to include tax-exempt income (line 38105).

The worked return `returns/2025_return_jx.yaml` (employment income of 3,000.00, T90 lines 1 and 3
of 6,000.00 and 4,000.00, the election yes) is checked by `test_worked_returns.py`. This module
computes each example on its own: the form `ca/t90` (run once: lines 4, 14, 16, 18 and 20 and the
check of line 10019 against line 9) and the Schedule 6 election, which adds the T90 line 4 and line
20 amounts
and the T1 line 10105 amount to the working income and to the adjusted family net income only when
the answer is yes. The election answer and the spouse's amounts are refused or ignored as the form
gives them; the printed form gives no bound for line 10019, so it is refused, not capped.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_WORKERS_BENEFIT,
    CWB_FAMILY_WORKING_INCOME,
    CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12,
    CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED,
    CWB_SPOUSE_WORKING_INCOME,
    CWB_TAX_EXEMPT_NET_INCOME,
    CWB_TAX_EXEMPT_WORKING_INCOME,
    T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED,
    T90_EXEMPT_WORKING_INCOME,
    T90_LINE_14,
    T90_LINE_16,
    T90_NET_EXEMPT_INCOME,
    T90_TOTAL_EXEMPT_INCOME,
    WORKING_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

T90 = "ca/t90"
RETURN = "ca-on/return"

# The figures of return JX: T90 line 1 (box 71 of the T4 slips) and line 3 (net self-employment
# income), the only T90 amounts entered; the employment income is 3,000.00.
JX_T90 = {"t4_box_71_employment_income": "6000", "net_self_employment_income": "4000"}


def run(
    *,
    election: int = 1,
    t90: Mapping[str, str] = JX_T90,
    **overrides: Any,
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return JX, with the election (1 yes, 0 no), the T90 amounts and
    the keyword overrides of `starting(...)` given: employment income of 3,000.00 and no other
    income."""
    artifacts = starting(
        "3000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t90_amounts=t90,
        cwb_include_tax_exempt_income=election,
        **overrides,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def return_jx(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[RETURN]
    return worksheet


def t90_form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[T90]
    return worksheet


# --- the election and the benefit of return JX ---------------------------------------------------


def test_the_election_puts_the_t90_line_4_into_column_1_line_4() -> None:
    worksheet = return_jx()

    assert t90_form().get(T90_EXEMPT_WORKING_INCOME).value == D("10000.00")
    assert worksheet.get(CWB_TAX_EXEMPT_WORKING_INCOME).value == D("10000.00")


def test_the_election_takes_working_income_to_13000_and_the_benefit_to_1633() -> None:
    worksheet = return_jx()

    assert worksheet.get(WORKING_INCOME).value == D("13000.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("13000.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1633")


def test_with_the_election_at_0_the_t90_figures_are_ignored_and_the_benefit_is_0() -> None:
    worksheet = return_jx(election=0)

    assert worksheet.get(CWB_TAX_EXEMPT_WORKING_INCOME).value == D("0.00")
    assert worksheet.get(CWB_TAX_EXEMPT_NET_INCOME).value == D("0.00")
    assert worksheet.get(WORKING_INCOME).value == D("3000.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("3000.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")


def test_the_form_t90_is_computed_whatever_the_election_says() -> None:
    assert t90_form(election=0).get(T90_EXEMPT_WORKING_INCOME).value == D("10000.00")
    assert t90_form(election=0).get(T90_NET_EXEMPT_INCOME).value == D("10000.00")


def test_an_election_above_1_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(election=2)


# --- the exports of the form on its worksheet ----------------------------------------------------


def test_the_three_exports_of_the_form_are_on_its_worksheet() -> None:
    found = t90_form()

    assert found.get(T90_EXEMPT_WORKING_INCOME).value == D("10000.00")
    assert found.get(T90_NET_EXEMPT_INCOME).value == D("10000.00")
    assert found.get(T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED).value == D("0.00")


# --- line 10019 ---------------------------------------------------------------------------------


def test_line_10019_above_line_9_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(
            t90={
                "ei_ppip_and_other_benefits": "100",
                "ei_maternity_parental_ppip_benefits": "100.01",
            }
        )


def test_line_10019_equal_to_line_9_is_accepted_and_checked_at_its_amount() -> None:
    found = t90_form(
        t90={
            "ei_ppip_and_other_benefits": "100",
            "ei_maternity_parental_ppip_benefits": "100",
        }
    )

    assert found.get(T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED).value == D("100.00")


# --- the printed lines 14, 16, 18 and 20 with all sixteen amounts distinct -----------------------

DISTINCT = {
    "t4_box_71_employment_income": "1000",
    "other_employment_income": "200",
    "net_self_employment_income": "300",
    "cpp_qpp_benefits": "100",
    "rrsp_rrif_pension_transfer_income": "110",
    "covid_19_payments": "120",
    "other_pensions_and_superannuation": "130",
    "ei_ppip_and_other_benefits": "140",
    "ei_maternity_parental_ppip_benefits": "40",
    "interest_dividends_investment_income": "150",
    "net_rental_income": "160",
    "social_assistance_payments": "170",
    "other_exempt_income": "180",
    "net_rental_losses": "50",
    "net_self_employment_losses": "60",
    "deductions_relating_to_exempt_income": "70",
}


def test_line_14_adds_line_4_and_lines_5_to_13_and_not_line_10019() -> None:
    # Line 4 is 1,000 + 200 + 300 = 1,500.00; lines 5 to 13 but 10019 are 1,260.00 (100 to 180
    # in steps of 10); line 10019 (40) would make 2,800.00 if it were added.
    assert t90_form(t90=DISTINCT).get(T90_LINE_14).value == D("2760.00")


def test_line_16_is_line_14_less_the_net_rental_losses() -> None:
    assert t90_form(t90=DISTINCT).get(T90_LINE_16).value == D("2710.00")


def test_line_18_is_line_16_less_the_net_self_employment_losses() -> None:
    assert t90_form(t90=DISTINCT).get(T90_TOTAL_EXEMPT_INCOME).value == D("2650.00")


def test_line_20_is_line_18_less_the_deductions_and_is_the_net_exempt_income() -> None:
    assert t90_form(t90=DISTINCT).get(T90_NET_EXEMPT_INCOME).value == D("2580.00")


# --- net exempt income below zero and the emergency volunteer amount -----------------------------


def test_negative_net_exempt_income_lowers_the_adjusted_family_net_income() -> None:
    # T90 line 18 10,000.00 less line 19 12,000.00 is (2,000.00) in brackets: line 8 is that
    # signed amount, so line 10 and line 15 are 3,000.00 - 2,000.00 = 1,000.00.
    worksheet = return_jx(t90={**JX_T90, "deductions_relating_to_exempt_income": "12000"})

    assert t90_form(t90={**JX_T90, "deductions_relating_to_exempt_income": "12000"}).get(
        T90_NET_EXEMPT_INCOME
    ).value == D("-2000.00")
    assert worksheet.get(CWB_TAX_EXEMPT_NET_INCOME).value == D("-2000.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("1000.00")


def test_the_emergency_volunteer_amount_adds_to_both_line_4_and_line_8_with_the_election() -> None:
    # T1 line 10105 of 500.00 is added to column 1 line 4 (working income 13,500.00) and to column 1
    # line 8: net exempt income (2,000.00) in brackets and 500.00, so (1,500.00).
    worksheet = return_jx(
        t90={**JX_T90, "deductions_relating_to_exempt_income": "12000"},
        emergency_services_volunteer_exempt_income="500",
    )

    assert worksheet.get(CWB_TAX_EXEMPT_WORKING_INCOME).value == D("10500.00")
    assert worksheet.get(WORKING_INCOME).value == D("13500.00")
    assert worksheet.get(CWB_TAX_EXEMPT_NET_INCOME).value == D("-1500.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("1500.00")


def test_with_the_election_at_0_the_emergency_volunteer_amount_is_ignored_too() -> None:
    worksheet = return_jx(election=0, emergency_services_volunteer_exempt_income="500")

    assert worksheet.get(WORKING_INCOME).value == D("3000.00")
    assert worksheet.get(CWB_TAX_EXEMPT_NET_INCOME).value == D("0.00")


# --- the spouse's column ------------------------------------------------------------------------


def test_the_spouse_s_t90_working_income_counts_with_an_eligible_spouse() -> None:
    worksheet = return_jx(
        cwb_eligible_spouses=1,
        spouse_or_common_law_partner_on_december_31=1,
        cwb_spouse_tax_exempt_working_income="2000",
    )

    assert worksheet.get(CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED).value == D("2000.00")
    assert worksheet.get(CWB_SPOUSE_WORKING_INCOME).value == D("2000.00")
    assert worksheet.get(CWB_FAMILY_WORKING_INCOME).value == D("15000.00")


def test_the_spouse_s_t90_working_income_is_ignored_with_no_eligible_spouse() -> None:
    worksheet = return_jx(cwb_spouse_tax_exempt_working_income="2000")

    assert worksheet.get(CWB_SPOUSE_WORKING_INCOME).value == D("0.00")
    assert worksheet.get(CWB_FAMILY_WORKING_INCOME).value == D("13000.00")


def test_the_spouse_s_t90_working_income_is_ignored_with_the_election_at_0() -> None:
    worksheet = return_jx(
        election=0,
        cwb_eligible_spouses=1,
        spouse_or_common_law_partner_on_december_31=1,
        cwb_spouse_tax_exempt_working_income="2000",
    )

    assert worksheet.get(CWB_SPOUSE_WORKING_INCOME).value == D("0.00")
    assert worksheet.get(CWB_FAMILY_WORKING_INCOME).value == D("3000.00")


def test_the_spouse_s_net_exempt_income_counts_in_column_2_line_12_with_an_eligible_spouse() -> (
    None
):
    worksheet = return_jx(
        cwb_eligible_spouses=1,
        spouse_or_common_law_partner_on_december_31=1,
        cwb_spouse_net_exempt_income="1000",
    )

    assert worksheet.get(CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12).value == D("1000.00")


def test_the_spouse_s_net_exempt_income_is_ignored_with_the_election_at_0() -> None:
    worksheet = return_jx(
        election=0,
        cwb_eligible_spouses=1,
        spouse_or_common_law_partner_on_december_31=1,
        cwb_spouse_net_exempt_income="1000",
    )

    assert worksheet.get(CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12).value == D("0.00")
