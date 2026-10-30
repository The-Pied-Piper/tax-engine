"""CA-ON 2025 end to end: return ae."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.trace import (
    ChosenByRangeLine,
)
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CREDITS_AGAINST_FEDERAL_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LESS_CREDITS,
    LABOUR_SPONSORED_FUNDS_CREDIT,
    NET_FEDERAL_TAX,
    POLITICAL_CONTRIBUTIONS,
    POLITICAL_CREDIT,
    POLITICAL_CREDIT_BEFORE_MAXIMUM,
    POLITICAL_CREDIT_CHOSEN_COLUMN,
    POLITICAL_CREDIT_COLUMN_1_LINE_7,
    POLITICAL_CREDIT_COLUMN_2_LINE_7,
    POLITICAL_CREDIT_COLUMN_3_LINE_2,
    POLITICAL_CREDIT_COLUMN_3_LINE_3,
    POLITICAL_CREDIT_COLUMN_3_LINE_5,
    POLITICAL_CREDIT_COLUMN_3_LINE_6,
    POLITICAL_CREDIT_COLUMN_3_LINE_7,
    POLITICAL_CREDIT_SHORTCUT_AMOUNT,
    POLITICAL_CREDIT_SHORTCUT_THRESHOLD,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import FEDERAL_POLITICAL_COLUMN_LINES, D, compute


def return_ae(**overrides: Any) -> Worksheet:
    """Return AE's inputs, as in `returns/2025_return_ae.yaml`: Return P's with federal ones.

    Return P's filer (employment income of 48000, the federal tax after credits of 3909.94, the
    Ontario tax of 1934.56, Ontario political contributions of 3000 and 4800 deducted) with
    federal political contributions of 1000 (T1 line 135, line 40900).
    """
    inputs: dict[str, Any] = {
        "income_tax_deducted": "4800",
        "political_contributions": "3000",
        "federal_political_contributions": "1000",
    }
    return compute("48000", (), "0", "0", "8640", "0", "0", **{**inputs, **overrides})


def test_return_aes_federal_political_contribution_credit_is_558_33_and_lowers_the_refund() -> None:
    # Return AE is Return P with federal political contributions of 1000 (T1 line 135, line
    # 40900): the federal tax after credits is 3909.94 and the Ontario tax 1934.56, as for Return P.
    # Federal Worksheet "Line 41000": 1000 is more than 750, so column 3 applies. Line 2 is 750.00,
    # line 3 is 1000 - 750.00 = 250.00, line 5 is 250.00 x 33.33% = 83.325, rounded half-up to the
    # cent: 83.33, line 6 is the printed 475.00 and line 7 is 83.33 + 475.00 = 558.33. (Columns 1
    # and 2 are also built: column 1 line 7 is 75% x 1000 = 750.00 and column 2 line 7 is 50% x
    # 600.00 = 300.00, + 300.00 = 600.00; neither applies.) 1000 is less than the $1,275 of the
    # shortcut, so the column's 558.33 stands, at most the maximum of $650: line 41000 is 558.33.
    # Line 138 adds lines 135 and 137, 558.33 + 0, and line 139 is 3909.94 - 558.33 = 3351.61, the
    # net federal tax; the total payable is 3351.61 + 1934.56 = 5286.17 and, with total credits of
    # 4800 + 0 + 1402.76 = 6202.76 as for Return P, line 167 is 5286.17 - 6202.76 = -916.59.
    worksheet = return_ae()

    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3909.94")
    assert worksheet.get(POLITICAL_CONTRIBUTIONS).value == D("1000")
    assert worksheet.get(POLITICAL_CREDIT_COLUMN_3_LINE_2).value == D("750.00")
    assert worksheet.get(POLITICAL_CREDIT_COLUMN_3_LINE_3).value == D("250.00")
    assert worksheet.get(POLITICAL_CREDIT_COLUMN_3_LINE_5).value == D("83.33")
    assert worksheet.get(POLITICAL_CREDIT_COLUMN_3_LINE_6).value == D("475.00")
    assert worksheet.get(POLITICAL_CREDIT_COLUMN_3_LINE_7).value == D("558.33")
    assert worksheet.get(POLITICAL_CREDIT_COLUMN_1_LINE_7).value == D("750.00")
    assert worksheet.get(POLITICAL_CREDIT_COLUMN_2_LINE_7).value == D("600.00")
    assert worksheet.get(POLITICAL_CREDIT_CHOSEN_COLUMN).value == D("558.33")
    assert worksheet.get(POLITICAL_CREDIT_SHORTCUT_THRESHOLD).value == D("1275")
    assert worksheet.get(POLITICAL_CREDIT_SHORTCUT_AMOUNT).value == D("650")
    assert worksheet.get(POLITICAL_CREDIT_BEFORE_MAXIMUM).value == D("558.33")
    assert worksheet.get(POLITICAL_CREDIT).value == D("558.33")
    assert worksheet.get(CREDITS_AGAINST_FEDERAL_TAX).value == D("558.33")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("3351.61")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("3351.61")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5286.17")
    assert worksheet.get(ontario.POLITICAL_CREDIT).value == D("1402.76")
    assert worksheet.get(TOTAL_CREDITS).value == D("6202.76")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-916.59")
    assert worksheet.get(REFUND).value == D("916.59")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "political_credit_column_3_line_3: political_contributions 1000 "
        "less political_credit_column_3_line_2 750, not below 0 = 250"
    ) in rendered
    assert (
        "political_credit_column_3_line_5: 33.33% of political_credit_column_3_line_3 250 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "political_credit_column_3_line_7: political_credit_column_3_line_5 83.33 "
        "+ political_credit_column_3_line_6 475 = 558.33"
    ) in rendered
    assert (
        "political_credit_chosen_column: political_credit_column_3_line_7 558.33, "
        "chosen as political_contributions is 1000"
    ) in rendered
    assert (
        "political_credit_before_maximum: political_credit_chosen_column 558.33, "
        "chosen as political_credit_shortcut_threshold is 1275"
    ) in rendered
    assert (
        "political_credit: lesser of political_credit_before_maximum 558.33 and 650 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "credits_against_federal_tax: political_credit 558.33 "
        "+ investment_tax_credit 0 + labour_sponsored_funds_credit 0 = 558.33"
    ) in rendered
    assert (
        "federal_tax: federal_tax_with_itc_recapture 3909.94 "
        "less federal_logging_tax_credit 0, not below 0 = 3909.94"
    ) in rendered
    assert (
        "federal_tax_less_credits: federal_tax 3909.94 "
        "less credits_against_federal_tax 558.33, not below 0 = 3351.61"
    ) in rendered


@pytest.mark.parametrize(
    ("contributions", "column", "credit"),
    [
        # The acceptance figures.
        ("0", 1, "0.00"),
        ("400", 1, "300.00"),
        ("750", 2, "475.00"),
        ("1000", 3, "558.33"),
        ("1275", None, "650"),
        ("5000", None, "650"),
        # The ends of the columns: column 1 line 7 at 400 is 300.00; a cent over, column 2 line 5
        # is 0.01 x 50% = 0.005, up to 0.01; a cent over 750, column 3 line 5 is 0.003333, down to
        # 0.00.
        ("400.01", 2, "300.01"),
        ("750.01", 3, "475.00"),
        # A cent under the $1,275: column 3 line 3 is 524.99, line 5 is 174.9792, down to 174.98.
        ("1274.99", 3, "649.98"),
        ("1275.01", None, "650"),
    ],
)
def test_line_41000_is_the_applicable_column_or_the_shortcut_at_most_650(
    contributions: str, column: int | None, credit: str
) -> None:
    worksheet = return_ae(federal_political_contributions=contributions)

    (chosen,) = [
        line
        for line in worksheet.trace
        if isinstance(line, ChosenByRangeLine) and line.output == POLITICAL_CREDIT_BEFORE_MAXIMUM
    ]
    if column is None:
        assert chosen.chosen_kind == POLITICAL_CREDIT_SHORTCUT_AMOUNT
    else:
        assert chosen.chosen_kind == POLITICAL_CREDIT_CHOSEN_COLUMN
        (column_pick,) = [
            line
            for line in worksheet.trace
            if isinstance(line, ChosenByRangeLine) and line.output == POLITICAL_CREDIT_CHOSEN_COLUMN
        ]
        assert column_pick.chosen_kind == FEDERAL_POLITICAL_COLUMN_LINES[column][7]
    assert worksheet.get(POLITICAL_CREDIT).value == D(credit)
    assert worksheet.get(CREDITS_AGAINST_FEDERAL_TAX).value == D(credit)


def test_the_federal_credit_does_not_change_the_ontario_credit() -> None:
    # Ontario contributions of 0 leave ON479 line 16 at 0, whatever the federal contributions.
    worksheet = return_ae(political_contributions="0")

    assert worksheet.get(POLITICAL_CREDIT).value == D("558.33")
    assert worksheet.get(ontario.POLITICAL_CREDIT).value == D("0")
    assert worksheet.get(ontario.ONTARIO_CREDITS).value == D("0")
    assert worksheet.get(TOTAL_CREDITS).value == D("4800")


def test_line_138_adds_the_political_credit_and_the_labour_sponsored_funds_credit() -> None:
    # 558.33 + 600.00 (15% of a net cost of 4000), in line order; line 139 is 3909.94 - 1158.33.
    worksheet = return_ae(labour_sponsored_funds_net_cost="4000")

    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT).value == D("600.00")
    assert worksheet.get(CREDITS_AGAINST_FEDERAL_TAX).value == D("1158.33")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("2751.61")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "credits_against_federal_tax: political_credit 558.33 "
        "+ investment_tax_credit 0 + labour_sponsored_funds_credit 600 = 1158.33"
    ) in rendered


def test_a_credit_above_the_federal_tax_leaves_zero_on_line_139() -> None:
    # Employment income of 10000 leaves the federal tax after credits at 0; contributions of 5000
    # give the credit of 650, which is more than that: line 139 is 0, not -650, and it is lost.
    worksheet = compute(
        "10000", (), "0", "0", "1800", "0", "0", federal_political_contributions="5000"
    )

    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("0")
    assert worksheet.get(POLITICAL_CREDIT).value == D("650")
    assert worksheet.get(CREDITS_AGAINST_FEDERAL_TAX).value == D("650")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("0")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("0")
