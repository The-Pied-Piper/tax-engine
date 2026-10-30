"""CA-ON 2025 end to end: return FS, the other items of the earned income of Form T929 line 4.

Return FS is `returns/2025_return_fs.yaml`: a student who attended for 10 weeks, with $1,000.00 of
employment income, $12,500.00 of other income, $9,000.00 of disability supports paid and nothing
reimbursed. The six other items of the form's definition of earned income (net research grants,
earnings supplements, Part II Employment Insurance Act support, income replacement support, Wage
Earner Protection Program Act amounts and COVID-19 payments) are $1,000.00, $500.00, $400.00,
$300.00, $200.00 and $100.00, which no other worked return sets. The figures are chosen (no CRA
example exists) and worked out by hand from the form text, as the description of the return shows.
The tests check the hand figure of each line; the tax lines are checked in the YAML only.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    DISABILITY_SUPPORTS_DEDUCTION,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    T929_LINE_3,
    T929_LINE_4,
    T929_LINE_7,
    T929_LINE_9,
    T929_LINE_10,
    T929_LINE_11,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_fs(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return FS's inputs, as in `returns/2025_return_fs.yaml`, over the keyword overrides given."""
    inputs: dict[str, Any] = {
        "other_income": "12500",
        "t929_expenses_paid": "9000",
        "t929_expenses_reimbursed": "0",
        "t929_weeks_attended": 10,
        "t929_net_research_grants": "1000",
        "t929_earnings_supplements": "500",
        "t929_employment_insurance_part_2_support": "400",
        "t929_income_replacement_support": "300",
        "t929_wage_earner_protection_amounts": "200",
        "t929_covid_19_payments": "100",
        "t929_copies": 1,
        "resident_in_canada_throughout_2025": 1,
        "aged_18_or_older_at_end_of_2025": 1,
    }
    return run("1000", (), "0", "0", "0", "0", "0", **{**inputs, **overrides})


def test_the_six_other_items_make_line_4_3500() -> None:
    form = run_fs()["ca/t929"][0]

    # 1000.00 of employment income + 1000.00 + 500.00 + 400.00 + 300.00 + 200.00 + 100.00.
    assert form.get(T929_LINE_4).value == D("3500.00")


def test_each_item_adds_its_own_amount_to_line_4() -> None:
    items = (
        ("t929_net_research_grants", "1000.00"),
        ("t929_earnings_supplements", "500.00"),
        ("t929_employment_insurance_part_2_support", "400.00"),
        ("t929_income_replacement_support", "300.00"),
        ("t929_wage_earner_protection_amounts", "200.00"),
        ("t929_covid_19_payments", "100.00"),
    )
    for name, amount in items:
        zeros = {other: "0" for other, _ in items}
        form = run_fs(**{**zeros, name: amount})["ca/t929"][0]

        # Only the employment income of 1000.00 and this one item are in line 4.
        assert form.get(T929_LINE_4).value == D("1000.00") + D(amount), name


def test_the_student_claims_the_7250_of_line_11_over_the_9000_of_expenses() -> None:
    form = run_fs()["ca/t929"][0]

    # Line 5 is 13500.00 and line 7 is 13500.00 - 3500.00 = 10000.00. Line 9 is 10 x 375 =
    # 3750.00 and line 10, the lesser of the two, is 3750.00. Line 11 is 3500.00 + 3750.00 =
    # 7250.00 and line 12, the lesser of line 3 (9000.00) and line 11, is 7250.00.
    assert form.get(T929_LINE_3).value == D("9000.00")
    assert form.get(NET_INCOME).value == D("13500.00")
    assert form.get(T929_LINE_7).value == D("10000.00")
    assert form.get(T929_LINE_9).value == D("3750.00")
    assert form.get(T929_LINE_10).value == D("3750.00")
    assert form.get(T929_LINE_11).value == D("7250.00")
    assert form.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("7250.00")


def test_the_deduction_takes_taxable_income_to_6250() -> None:
    worksheet = run_fs()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("13500.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("7250.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("6250.00")
    assert worksheet.get(NET_INCOME).value == D("6250.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("6250.00")
