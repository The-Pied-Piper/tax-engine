"""CA-ON 2025 end to end: return FR, the net self-employment income lines of Form T929 line 4.

Return FR is `returns/2025_return_fr.yaml`: a filer whose only income is five statements of $600.00
each (a business, a professional and a commission statement of Form T2125, a Form T2042 farming
statement and a Form T2121 fishing statement), with $5,000.00 of disability supports paid and
$1,000.00 reimbursed and no weeks attended. Each of the five net self-employment lines of the
form's line 4 is non-zero, which no other worked return reaches. The figures are chosen (no CRA
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
    T929_NET_BUSINESS_INCOME,
    T929_NET_COMMISSION_INCOME,
    T929_NET_FARMING_INCOME,
    T929_NET_FISHING_INCOME,
    T929_NET_PROFESSIONAL_INCOME,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_fr(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return FR's inputs, as in `returns/2025_return_fr.yaml`, over the keyword overrides given."""
    inputs: dict[str, Any] = {
        "business_statements": (
            {"business": {"gross_sales": "600"}, "business_income_line": 1},
            {"business": {"gross_sales": "600"}, "business_income_line": 2},
            {"business": {"gross_sales": "600"}, "business_income_line": 3},
        ),
        "farm_statements": ({"farm": {"wheat": "600"}},),
        "fish_statements": ({"fish": {"fish_products": "1000", "salt_bait_and_ice": "400"}},),
        "t929_expenses_paid": "5000",
        "t929_expenses_reimbursed": "1000",
        "t929_weeks_attended": 0,
        "t929_copies": 1,
        "resident_in_canada_throughout_2025": 1,
        "aged_18_or_older_at_end_of_2025": 1,
    }
    return run("0", (), "0", "0", "0", "0", "0", **{**inputs, **overrides})


def test_each_kind_of_self_employment_income_is_600_in_line_4_of_the_form() -> None:
    form = run_fr()["ca/t929"][0]

    # Each statement's net income is its income less its expenses; the fishing statement is
    # 1000.00 - 400.00. A loss would count 0; each is a gain here.
    assert form.get(T929_NET_BUSINESS_INCOME).value == D("600.00")
    assert form.get(T929_NET_PROFESSIONAL_INCOME).value == D("600.00")
    assert form.get(T929_NET_COMMISSION_INCOME).value == D("600.00")
    assert form.get(T929_NET_FARMING_INCOME).value == D("600.00")
    assert form.get(T929_NET_FISHING_INCOME).value == D("600.00")
    assert form.get(T929_LINE_4).value == D("3000.00")


def test_the_claim_is_limited_to_the_3000_earned_income_of_line_11() -> None:
    form = run_fr()["ca/t929"][0]

    # Line 3 is 5000.00 - 1000.00 = 4000.00. Line 5 is 3000.00, so line 7 is 3000.00 - 3000.00 = 0
    # and with no weeks attended lines 9 and 10 are 0.00; line 11 is 3000.00 + 0.00 and line 12,
    # the lesser of 4000.00 and 3000.00, is 3000.00.
    assert form.get(T929_LINE_3).value == D("4000.00")
    assert form.get(NET_INCOME).value == D("3000.00")
    assert form.get(T929_LINE_7).value == D("0.00")
    assert form.get(T929_LINE_9).value == D("0.00")
    assert form.get(T929_LINE_10).value == D("0.00")
    assert form.get(T929_LINE_11).value == D("3000.00")
    assert form.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("3000.00")


def test_the_deduction_takes_net_income_and_taxable_income_to_zero() -> None:
    worksheet = run_fr()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("3000.00")
    assert worksheet.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("3000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("3000.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("0.00")
    assert worksheet.get(NET_INCOME).value == D("0.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("0.00")


def test_a_loss_on_the_farming_statement_counts_0_in_line_4() -> None:
    result = run_fr(farm_statements=({"farm": {"wheat": "0", "office_expenses": "200"}},))
    form = result["ca/t929"][0]

    # The farming statement's net is -200.00, a loss, which counts 0 in the form's line 4.
    assert form.get(T929_NET_FARMING_INCOME).value == D("0.00")
    assert form.get(T929_LINE_4).value == D("2400.00")
