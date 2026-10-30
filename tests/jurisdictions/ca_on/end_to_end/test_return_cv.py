"""CA-ON 2025 end to end: return cv."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_FISCAL_PERIOD_DAYS,
    BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
    BUSINESS_IMMEDIATE_EXPENSING_CAP,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIM,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    BUSINESS_INCOME,
    BUSINESS_INCOME_BEFORE_CCA,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_TOTAL_EXPENSES,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return CV's T2125, Return BT's with the gross sales raised to 676767.12 (a chosen figure, so
# that line 9946 stays Return BB's 30000 after the 628767.12 of capital cost allowance): the same
# seven expense lines (16000, the motor vehicle line 2500 from Charts A to C) and the same
# business-use-of-home expenses (2000).
BUSINESS = {
    "gross_sales": "676767.12",
    "advertising": "1500",
    "insurance": "1200",
    "office_expenses": "800",
    "professional_fees": "2500",
    "rent": "6000",
    "utilities": "1500",
    # Charts A to C: the sales tax rate of the province (the HST of 13%); the vehicle is in
    # `VEHICLE`.
    "vehicle_sales_tax_rate": "13",
    "home_heat": "600",
    "home_electricity": "500",
    "home_insurance": "300",
    "home_maintenance": "200",
    "home_property_taxes": "400",
}
# Charts A to C for one leased passenger vehicle used half for business: Chart A line 16 (line
# 9281) is 2500, from the interest of Chart B (400) and the leasing cost of Chart C (2147), as in
# Return BB.
VEHICLE = {
    "business_kilometres": "5000",
    "total_kilometres": "10000",
    "fuel_and_oil": "1000",
    "insurance": "600",
    "maintenance_and_repairs": "200",
    "other_expenses_10": "653",
    "interest_payable": "400",
    "interest_days": "153",
    "lease_charges": "2550",
    "lease_days": "183",
    "list_price": "60000",
}
# The fiscal period from August 1 to December 31, 2025 (Form T2125 "Fiscal period From / to"):
# 31 + 30 + 31 + 30 + 31 = 153 days.
FROM = 20250801
TO = 20251231
# Area G is not answered: not associated with any other EPOP (the count 0), so the limit is the
# $1.5 million before proration.
NOT_ASSOCIATED = {
    "business_epop_associated": 0,
    "business_epop_agreement_filed": 0,
    "business_epop_percentage": "0",
    "business_epop_percentage_total": "0",
}
# Associated with one other EPOP (1) under an agreement that was filed (1), the percentage
# assigned to the business 40 and the total of column 3 100: amount iii is 1500000 x 40% =
# 600000.00 before proration.
ASSOCIATED = {
    "business_epop_associated": 1,
    "business_epop_agreement_filed": 1,
    "business_epop_percentage": "40",
    "business_epop_percentage_total": "100",
}


def class_8_row(
    expensed: str, claim: str | None = None
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9): Return CV's Class 8 with nothing at the start and
    additions of 700000, all DIEPs (column 4 700000), of which `expensed` is expensed at once
    (column 9); the claim (column 21) is column 9 unless given."""
    return ("8", "0", "700000", "0", "0", "0", claim or expensed, 0, "700000", "0", expensed)


def run_cv(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CV's inputs, as in `returns/2025_return_cv.yaml`: Return BT's sole proprietor with a
    fiscal period of 153 days and one DIEP expensed at the whole prorated limit.

    One T2125 statement for the business: gross sales of 676767.12 (amount 3A, and so line 8299
    and T1 line 13499), expenses of 16000 on seven lines (the motor vehicle line, 2500, from
    Charts A to C) and 628767.12 of capital cost allowance (Class 8, additions 700000, all DIEPs,
    628767.12 expensed at once, claim 628767.12), 644767.12 in all (line 9368), so line 9369 is
    32000.00; business-use-of-home expenses of 2000, so line 9945 is 2000 and line 9946 and T1
    line 13500 are 30000.00, Return BB's.
    """
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (class_8_row("628767.12"),),
        "business_vehicles_rows": (VEHICLE,),
        "business_fiscal_period_from": FROM,
        "business_fiscal_period_to": TO,
        **NOT_ASSOCIATED,
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_cv(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return CV's one T2125 statement: its lines, as the form computes them."""
    return run_cv(changes)["ca/t2125"][0]


def test_return_cvs_fiscal_period_is_the_153_days_from_its_dates() -> None:
    # August 1 to December 31, 2025 is 31 + 30 + 31 + 30 + 31 = 153 days; the caller enters the two
    # dates, and the days are derived from them.
    statement = statement_cv()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_FISCAL_PERIOD_DAYS).value == 153
    assert (
        "business_fiscal_period_days: from 20250801 to 20251231, fiscal period 153 days" in rendered
    )


def test_return_cvs_limit_is_the_1_5_million_prorated_to_628767_12() -> None:
    # Endnote 5 "$1.5 million, if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year", then Income Tax Regulations 1104(3.5)(b): "where an
    # eligible person or partnership has a taxation year that is less than 51 weeks, its immediate
    # expensing limit for the year is that proportion of its immediate expensing limit for the year
    # determined without reference to this paragraph that the number of days in the year is of 365":
    # 1500000 x 153 / 365 = 229500000 / 365 = 628767.1232..., rounded half-up to the cent, 628767.12
    # (365 x 628767 = 229499955, remainder 45, and 45 / 365 is 0.1232...). No amount is allocated by
    # the minister, so the limit is the prorated one.
    statement = statement_cv()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CAP).value == D("1500000")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER).value == D("1500000")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION).value == D("1500000")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("628767.12")
    for line in (
        "business_immediate_expensing_limit_before_minister: "
        "business_immediate_expensing_cap 1500000, chosen as business_epop_associated_checked is 0",
        "business_immediate_expensing_limit_before_proration: "
        "business_immediate_expensing_limit_before_minister 1500000, chosen as "
        "business_minister_allocation_given_checked is 0",
        "business_immediate_expensing_limit: business_immediate_expensing_limit_before_proration "
        "1500000 × business_fiscal_period_days 153 / 365 = 628767.12, as "
        "business_fiscal_period_days 153 is below 357 days",
    ):
        assert line in rendered, line


def test_return_cvs_line_i_is_628767_12_the_total_of_column_9_equal_to_the_limit() -> None:
    # Line i "Total immediate expensing claim for the year: Total of column 9" is 628767.12, the
    # least of endnote 5's three amounts: the immediate expensing limit 628767.12, the UCC of
    # DIEPs in column 8 (700000) and the income before CCA, 660767.12. A total equal to the limit is
    # not above it.
    statement = statement_cv()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("628767.12")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("660767.12")
    assert (
        "business_immediate_expensing_claim: item 1 class 8: column 4 700000 less column 6 0, "
        "column 7 700000: column 8 700000, column 9 628767.12"
    ) in rendered


def test_return_cvs_class_8_works_the_diep_columns_to_a_claim_of_628767_12() -> None:
    # Area A, class 8: column 7 is 0 + 700000 - 0 = 700000; column 8 is 700000 - 0 = 700000, not
    # more than column 7; column 9 is 628767.12, not more than column 8; column 10 is 700000 -
    # 628767.12 = 71232.88 and column 13 is 700000 - 628767.12 = 71232.88; columns 11, 12, 14, 15,
    # 16 and 17 are 0; column 18 is one half x (71232.88 - 0 - 0 - 0) = 35616.44; column 19 is
    # 71232.88 + 0 + 0 - 35616.44 = 35616.44. The maximum of a full year is 35616.44 x 20% =
    # 7123.288, which is 7123.29 to the cent; for 153 days it is 7123.29 x 153 / 365 = 2985.93,
    # so column 21 is at most 2985.93 + 628767.12 = 631753.05. The claim is 628767.12, column 9.
    statement = statement_cv()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "business_cca_table_claim: item 1 class 8: column 7 700000, column 9 628767.12, "
        "column 14 0, column 15 0, column 16 0, column 17 0, column 18 35616.44, "
        "column 19 35616.44, maximum 20% of column 19 = 7123.29 (half-up to 0.01), "
        "prorated 153/365 = 2985.93, claim 628767.12"
    ) in rendered
    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("628767.12")


def test_return_cvs_claim_up_to_the_maximum_of_631753_05_is_allowed() -> None:
    # Column 21 includes column 9: 2985.93 + 628767.12 = 631753.05, one cent more is refused.
    statement = statement_cv(
        {"business_cca_classes_rows": (class_8_row("628767.12", "631753.05"),)}
    )

    assert statement.get(BUSINESS_CCA_CLAIM).value == D("631753.05")
    with pytest.raises(InputAboveBoundError) as raised:
        run_cv({"business_cca_classes_rows": (class_8_row("628767.12", "631753.06"),)})
    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 631753.06 is above the maximum 631753.05"
    )


def test_return_cvs_closing_ucc_is_71232_88_for_class_8() -> None:
    # Column 22 is column 7 less column 21: 700000 - 628767.12 = 71232.88, next year's column 2.
    statement = statement_cv()

    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("8"), D("71232.88")),
    ]


def test_return_cvs_line_ii_and_line_9936_are_628767_12_and_line_9369_is_32000() -> None:
    # Line ii, the total of column 21, is 628767.12, so is line 9936 (no personal part of CCA, no
    # CCA for business-use-of-home expenses). Line 9368 is 16000 + 628767.12 + 0 = 644767.12 and
    # line 9369 is 676767.12 - 644767.12 = 32000.00. The income before CCA is line 9369 plus line
    # 9936: 32000.00 + 628767.12 = 660767.12, the gross profit less the 16000 of other expenses.
    statement = statement_cv()

    assert statement.get(BUSINESS_GROSS_INCOME_BEFORE_EXPENSES).value == D("676767.12")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("628767.12")
    assert statement.get(BUSINESS_TOTAL_EXPENSES).value == D("644767.12")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32000.00")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("660767.12")


def test_return_cvs_net_business_income_is_30000_on_line_9946_and_t1_line_13500() -> None:
    # Part 7: the business-use-of-home expenses are 2000 (amount 7P, line 9945), the lesser of
    # 2000 and amount 5D, 32000.00. Line 9946 is 32000.00 - 2000 = 30000.00, T1 line 22 and line
    # 13500; the net self-employment income (line 27) is 30000.00 + 0 + 0 + 0 + 0.
    result = run_cv()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")


def test_return_cvs_figures_that_depend_on_income_are_return_bbs() -> None:
    # Line 9946 is Return BB's 30000.00, so total income, net income and taxable income are
    # 30000.00 and the tax lines are Return BB's: the federal tax 30000.00 x 14.5% = 4350.00, the
    # Ontario tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57.
    worksheet = run_cv()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_a_column_9_one_cent_above_the_prorated_limit_is_refused_naming_the_limit() -> None:
    # 628767.13 is above the limit 628767.12 (and within the UCC of DIEPs 700000 and the income
    # before CCA 660767.12), so only the limit refuses it. Without proration the limit would be
    # 1500000 and it would pass.
    with pytest.raises(InputAboveBoundError) as raised:
        run_cv({"business_cca_classes_rows": (class_8_row("628767.13"),)})

    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (628767.13) is above the immediate expensing "
        "limit (628767.12)"
    )


def test_a_full_fiscal_period_is_not_prorated() -> None:
    # No dates entered (0 and 0) is a full year, and so is 1 January to 31 December 2025 (365 days):
    # the limit is the 1500000 of Area A endnote 5, as 1500000 x 365 / 365 is 1500000.00. A column 9
    # of 660767.12, the income before CCA, is allowed, which the 153 days would refuse.
    for start, end in ((0, 0), (20250101, 20251231)):
        statement = statement_cv(
            {
                "business_fiscal_period_from": start,
                "business_fiscal_period_to": end,
                "business_cca_classes_rows": (class_8_row("660767.12"),),
            }
        )

        assert statement.get(BUSINESS_FISCAL_PERIOD_DAYS).value == 365
        assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION).value == D(
            "1500000"
        )
        assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000.00")
        assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("660767.12")


def test_a_year_of_51_weeks_or_more_is_not_prorated() -> None:
    # Income Tax Regulations 1104(3.5)(b) prorates "a taxation year that is less than 51 weeks":
    # 51 weeks of 7 days is 357 days, so 357 and 364 days keep the whole 1500000 of endnote 5.
    for end, days in ((20251223, 357), (20251230, 364)):
        statement = statement_cv(
            {"business_fiscal_period_from": 20250101, "business_fiscal_period_to": end}
        )

        assert statement.get(BUSINESS_FISCAL_PERIOD_DAYS).value == days
        assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION).value == D(
            "1500000"
        )
        assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")


def test_a_year_of_356_days_is_prorated_to_1463013_70() -> None:
    # The longest year that is prorated: 1500000 x 356 / 365 = 534000000 / 365 = 1463013.6986...,
    # rounded half-up to the cent, 1463013.70. Its column 9 is not tested here: the income before
    # CCA of this return, 660767.12, is below the limit.
    statement = statement_cv(
        {"business_fiscal_period_from": 20250101, "business_fiscal_period_to": 20251222}
    )

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION).value == D("1500000")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("1463013.70")


def test_one_day_gives_a_limit_of_4109_59() -> None:
    # 1500000 x 1 / 365 = 4109.5890..., rounded half-up to the cent, 4109.59; one cent more is
    # refused. The vehicle is left out: its 153 interest days do not fit a one-day period.
    statement = statement_cv(
        {
            "business_vehicles_rows": (),
            "business_fiscal_period_from": 20250101,
            "business_fiscal_period_to": 20250101,
            "business_cca_classes_rows": (class_8_row("4109.59"),),
        }
    )

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("4109.59")
    with pytest.raises(InputAboveBoundError) as raised:
        run_cv(
            {
                "business_vehicles_rows": (),
                "business_fiscal_period_from": 20250101,
                "business_fiscal_period_to": 20250101,
                "business_cca_classes_rows": (class_8_row("4109.60"),),
            }
        )
    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (4109.60) is above the immediate expensing "
        "limit (4109.59)"
    )


def test_an_associated_business_has_its_share_of_the_limit_prorated() -> None:
    # Area G amount iii is 1500000 x 40% = 600000.00 (the other EPOP's 60% makes the total 100%);
    # for 153 days it is 600000.00 x 153 / 365 = 91800000 / 365 = 251506.8493..., rounded half-up
    # to the cent, 251506.85. A column 9 of 251506.85 passes and one of 251506.86 is refused.
    statement = statement_cv(
        {**ASSOCIATED, "business_cca_classes_rows": (class_8_row("251506.85"),)}
    )

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER).value == D("600000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION).value == D(
        "600000.00"
    )
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("251506.85")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("251506.85")
    with pytest.raises(InputAboveBoundError) as raised:
        run_cv({**ASSOCIATED, "business_cca_classes_rows": (class_8_row("251506.86"),)})
    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (251506.86) is above the immediate expensing "
        "limit (251506.85)"
    )


def test_an_associated_business_with_no_agreement_filed_still_has_a_limit_of_zero() -> None:
    # Endnote 5 "zero, if you are associated with one or more EPOPs and an agreement ... was not
    # filed": 0 x 153 / 365 is 0.00, below the 628767.12 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        run_cv({**ASSOCIATED, "business_epop_agreement_filed": 0})

    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (628767.12) is above the immediate expensing "
        "limit (0.00)"
    )


def test_an_amount_allocated_by_the_minister_is_prorated_by_the_days() -> None:
    # Income Tax Regulations 1104(3.5)(b): the limit "determined without reference to this
    # paragraph" includes the amount the Minister allocates under subsection 1104(3.4), so for 153
    # days 5000 is 5000 x 153 / 365 = 765000 / 365 = 2095.8904..., rounded half-up to the cent,
    # 2095.89. A column 9 of 2095.89 passes and one of 2095.90 is refused.
    minister = {"business_minister_allocation_given": 1, "business_minister_allocation": "5000"}
    statement = statement_cv({**minister, "business_cca_classes_rows": (class_8_row("2095.89"),)})

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION).value == D("5000")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("2095.89")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("2095.89")
    with pytest.raises(InputAboveBoundError) as raised:
        run_cv({**minister, "business_cca_classes_rows": (class_8_row("2095.90"),)})
    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (2095.90) is above the immediate expensing "
        "limit (2095.89)"
    )
