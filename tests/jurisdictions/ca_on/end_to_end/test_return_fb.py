"""CA-ON 2025 end to end: return fb, the T1 slip and investment income lines.

Return FB is `returns/2025_return_fb.yaml`: a filer with no spouse who has taxable dividends on
T3, T4PS and T5013 slips, investment income, a partnership share, a listed personal property
gain, a pension and an RRSP annuity, so that the lines no other worked return sets are non-zero:
line 12000, 12010, 12100, 12200, 12700, 12900, 13000 and the federal and Ontario dividend credits.
The figures are chosen (no CRA example exists) and worked out by hand from the form text, as the
description of the return shows. The tests check the hand figure of each line; the engine's tax
figures are checked in the YAML only.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ADDITIONAL_DEDUCTIONS,
    DIVIDEND_TAX_CREDIT,
    INTEREST_AND_OTHER_INVESTMENT_INCOME,
    INVESTMENT_INCOME_BEFORE_PRIOR_YEARS,
    LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS,
    LISTED_PERSONAL_PROPERTY_NET_GAIN,
    NET_INCOME,
    NET_PARTNERSHIP_INCOME,
    PENSION_ANNUITY_CONDITIONS_MET,
    PENSION_ANNUITY_PAYMENTS,
    PENSION_CHART_LINE_5,
    PENSION_CHART_LINE_6,
    PENSION_CHART_LINE_7,
    PENSION_CHART_LINE_8,
    PENSION_FOREIGN_INCOME,
    PENSION_RRIF_TRANSFERRED,
    PENSION_US_IRA_INCOME,
    PENSION_WORKSHEET_AMOUNT,
    SLIP_DIVIDEND_TAX_CREDIT,
    SLIP_TAXABLE_DIVIDENDS,
    SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_DIVIDENDS,
    TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting


def return_fb() -> Worksheet:
    """The worksheet of return FB: the inputs of `returns/2025_return_fb.yaml`, no spouse.

    The pension inputs of the pension chart (line 31400) are not keywords of `starting(...)`, so
    they are given as artifacts that replace the zero ones `starting(...)` gives.
    """
    overrides: list[Artifact[Any]] = [
        Artifact(PENSION_FOREIGN_INCOME, D("1000")),
        # The foreign pension income is deducted on line 25600 (Federal Worksheet, line 2).
        Artifact(ADDITIONAL_DEDUCTIONS, D("1000")),
        Artifact(PENSION_US_IRA_INCOME, D("500")),
        Artifact(PENSION_RRIF_TRANSFERRED, D("700")),
        Artifact(PENSION_ANNUITY_PAYMENTS, D("1200")),
        Artifact(PENSION_ANNUITY_CONDITIONS_MET, 1),
    ]
    base = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="40000",
        other_pensions_and_superannuation="9000",
        rrsp_income="1200",
        t3_taxable_dividends="1500",
        t3_taxable_dividends_other_than_eligible="400",
        t3_dividend_tax_credit="201.34",
        t4ps_taxable_dividends="1000",
        t4ps_taxable_dividends_other_than_eligible="250",
        t4ps_dividend_tax_credit="135.23",
        t5013_taxable_dividends="800",
        t5013_taxable_dividends_other_than_eligible="300",
        t5013_dividend_tax_credit="102.19",
        t3_investment_income="600",
        t5013_investment_income="450",
        investment_income_credited_not_received="200",
        tax_refund_interest="150",
        investment_royalties="350",
        net_partnership_income="2500",
        listed_personal_property_dispositions=(("5000", "3200", "0"),),
        unapplied_listed_personal_property_losses="300",
    )
    given = {artifact.kind for artifact in overrides}
    rest = [artifact for artifact in base if artifact.kind not in given]
    return service().compute(CA_ON, 2025, *rest, *overrides)["ca-on/return"][0]


def test_the_three_slips_give_taxable_dividends_of_3300_and_950_other_than_eligible() -> None:
    # Line 12000 is the taxable dividends of the three slips: 1,500 + 1,000 + 800 = 3,300. Line
    # 12010 is the part other than eligible: 400 + 250 + 300 = 950.
    worksheet = return_fb()

    assert worksheet.get(SLIP_TAXABLE_DIVIDENDS).value == D("3300.00")
    assert worksheet.get(TAXABLE_DIVIDENDS).value == D("3300.00")
    assert worksheet.get(SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE).value == D("950.00")
    assert worksheet.get(TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE).value == D("950.00")


def test_the_three_slip_dividend_credits_give_438_76_on_line_40425() -> None:
    # The boxes as entered: 201.34 + 135.23 + 102.19 = 438.76 (line 40425 takes the slips' total,
    # and with no slip the form's 15.0198% and 9.0301% would apply instead).
    worksheet = return_fb()

    assert worksheet.get(SLIP_DIVIDEND_TAX_CREDIT).value == D("438.76")
    assert worksheet.get(DIVIDEND_TAX_CREDIT).value == D("438.76")


def test_the_ontario_dividend_credit_is_263_37_from_the_dividends_on_the_worksheet() -> None:
    # Amount A is line 12000 (3,300) and amount B is line 12010 (950). Other than eligible:
    # 950 x 2.9863% = 28.37. Amount A less B: 3,300 - 950 = 2,350; eligible credit: 2,350 x 10% =
    # 235.00. Ontario dividend tax credit: 235.00 + 28.37 = 263.37.
    worksheet = return_fb()

    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_A).value == D("3300.00")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_B).value == D("950.00")
    assert worksheet.get(ontario.OTHER_DIVIDENDS_CREDIT).value == D("28.37")
    assert worksheet.get(ontario.DIVIDENDS_AMOUNT_A_LESS_B).value == D("2350.00")
    assert worksheet.get(ontario.ELIGIBLE_DIVIDENDS_CREDIT).value == D("235.00")
    assert worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value == D("263.37")


def test_interest_and_other_investment_income_of_1750_is_on_line_12100() -> None:
    # Line 12100: 600 (T3 investment income) + 450 (T5013 investment income) + 200 (investment
    # income credited not received) + 150 (tax refund interest) + 350 (royalties) = 1,750.
    worksheet = return_fb()

    assert worksheet.get(INVESTMENT_INCOME_BEFORE_PRIOR_YEARS).value == D("1750.00")
    assert worksheet.get(INTEREST_AND_OTHER_INVESTMENT_INCOME).value == D("1750.00")


def test_the_partnership_share_of_2500_is_on_line_12200_and_the_capital_gain_is_750() -> None:
    # Line 12200: the net partnership income is 2,500. Listed personal property: proceeds 5,000 -
    # adjusted cost base 3,200 = a gain of 1,800; less the unapplied losses of 300 = a net gain of
    # 1,500. The taxable capital gain is the net gain at the inclusion rate of 50%: 1,500 x 1/2 =
    # 750 (line 12700).
    worksheet = return_fb()

    assert worksheet.get(NET_PARTNERSHIP_INCOME).value == D("2500.00")
    assert worksheet.get(LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS).value == D("1800.00")
    assert worksheet.get(LISTED_PERSONAL_PROPERTY_NET_GAIN).value == D("1500.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("750.00")


def test_the_pension_chart_gives_a_pension_income_amount_of_2000() -> None:
    # Line 31400 chart, line 5: 1,000 + 500 + 700 = 2,200. Line 6: 9,000 - 2,200 = 6,800. Line 7:
    # 1,200 x 1 (the payments because of the death of a spouse) = 1,200. Line 8: 6,800 + 1,200 =
    # 8,000. Line 31400 is the lesser of line 8 (8,000) and 2,000, that is 2,000.
    worksheet = return_fb()

    assert worksheet.get(PENSION_CHART_LINE_5).value == D("2200.00")
    assert worksheet.get(PENSION_CHART_LINE_6).value == D("6800.00")
    assert worksheet.get(PENSION_CHART_LINE_7).value == D("1200.00")
    assert worksheet.get(PENSION_CHART_LINE_8).value == D("8000.00")
    assert worksheet.get(PENSION_WORKSHEET_AMOUNT).value == D("2000.00")


def test_total_income_of_58500_and_taxable_income_of_57500_after_line_25600() -> None:
    # Total income: 40,000 (line 13000) + 9,000 (line 11500) + 3,300 (dividends, line 12000) +
    # 1,750 (line 12100) + 2,500 (line 12200) + 750 (line 12700) + 1,200 (line 12900) = 58,500.
    # Line 25600 "Additional deductions" of 1,000 (the foreign pension income) is taken after net
    # income, so net income is 58,500 and taxable income is 58,500 less 1,000, 57,500.
    worksheet = return_fb()

    assert worksheet.get(TOTAL_INCOME).value == D("58500.00")
    assert worksheet.get(NET_INCOME).value == D("58500.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("57500.00")
