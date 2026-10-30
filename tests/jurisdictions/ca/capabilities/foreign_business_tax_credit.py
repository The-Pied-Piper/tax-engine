"""Shared pieces of the tests of the capabilities of lines 4 to 11 of Form T2209.

Form T2209, "Federal business foreign tax credit": line 4 (43400) "Business income tax paid to a
foreign country (5) for the year, plus any unused foreign tax credits for that country for the 10
years (6) before, and the 3 years after this year"; line 5 "Net foreign business income (7) 43900"
"x Basic federal tax (8)" over "Net income (3)"; line 6 "Federal surtax on income allocated to
"Other (Outside Canada)""; line 7 "Add lines 5 and 6."; line 8 "Add basic federal tax (8) and the
amount from line 6."; line 9 "Enter the amount from line 3, if any."; line 10 "Line 8 minus line
9"; line 11 "Enter whichever is less: the amount from line 4, 7 or 10." "Federal business foreign
tax credit". The made-up output kinds stand in for the ones the wiring gives.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import RoundingMode, RoundingRule, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.catalog import (
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_SURTAX_OUTSIDE_CANADA,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    FOREIGN_TAX_CREDIT_SHEETS,
    NET_FOREIGN_BUSINESS_INCOME,
    NET_FOREIGN_NON_BUSINESS_INCOME,
)

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# The return-wide figures and the outputs come with the wiring; the tests use made-up kinds.
# Signed: T2209 note (3) takes line 23600, which can be negative (a net loss).
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
BASIC_TAX = ArtifactKind("ex/basic_federal_tax_with_dividend_credit", Decimal, non_negative=True)
SHEETS = FOREIGN_TAX_CREDIT_SHEETS

# A sheet is (business tax paid for the year, unused business credits, net foreign business income
# used, line 6, line 3). Its non-business tax paid and income are filled in with figures the
# business lines never read.
Sheet = tuple[str, str, str, str, str]

# Net income 100,000 and basic federal tax (8) 14,500 are the defaults of `sheets_given`.
# A: line 4 = 400 + 50 = 450; line 5 = 6,000 x 14,500 / 100,000 = 870.00; line 6 = 0; line 7 =
# 870.00; line 8 = 14,500; line 9 = 1,400; line 10 = 13,100; line 11 = least(450, 870.00, 13,100)
# = 450.
SHEET_A: Sheet = ("400", "50", "6000", "0", "1400")
# B: line 4 = 900; line 5 = 20,000 x 14,500 / 100,000 = 2,900.00; line 6 = 100; line 7 = 3,000.00;
# line 8 = 14,500 + 100 = 14,600; line 10 = 14,600 - 100 = 14,500; line 11 = least(900, 3,000.00,
# 14,500) = 900.
SHEET_B: Sheet = ("900", "0", "20000", "100", "100")
# C, line 10 is the least: line 4 = 20,000; line 5 = 50,000 x 14,500 / 100,000 = 7,250.00; line 7 =
# 7,250.00; line 8 = 14,500; line 10 = 14,500 - 14,000 = 500; line 11 = 500.
SHEET_C: Sheet = ("20000", "0", "50000", "0", "14000")
# E, line 7 is the least: line 4 = 2,000; line 5 = 6,000 x 14,500 / 100,000 = 870.00; line 7 =
# 870.00; line 8 = 14,500; line 10 = 13,100; line 11 = 870.00.
SHEET_E: Sheet = ("2000", "0", "6000", "0", "1400")
# Z: no business figures at all; line 8 is still the basic federal tax.
SHEET_Z: Sheet = ("0", "0", "0", "0", "0")

# Expected (line 4, 5, 7, 8, 10, 11) of each sheet, by hand as above.
EXPECTED: dict[str, dict[int, Decimal]] = {
    "A": {4: D("450"), 5: D("870.00"), 7: D("870.00"), 8: D("14500"), 10: D("13100"), 11: D("450")},
    "B": {
        4: D("900"),
        5: D("2900.00"),
        7: D("3000.00"),
        8: D("14600"),
        10: D("14500"),
        11: D("900"),
    },
    "C": {
        4: D("20000"),
        5: D("7250.00"),
        7: D("7250.00"),
        8: D("14500"),
        10: D("500"),
        11: D("500"),
    },
    "E": {
        4: D("2000"),
        5: D("870.00"),
        7: D("870.00"),
        8: D("14500"),
        10: D("13100"),
        11: D("870.00"),
    },
    "Z": {4: D("0"), 5: D("0"), 7: D("0"), 8: D("14500"), 10: D("14500"), 11: D("0")},
}
SHEET_BY_NAME: dict[str, Sheet] = {
    "A": SHEET_A,
    "B": SHEET_B,
    "C": SHEET_C,
    "E": SHEET_E,
    "Z": SHEET_Z,
}


def rounding(rule: RoundingRule = CENT) -> ParameterDataset[RoundingOnly]:
    """By default half up to the cent."""
    return ParameterDataset(
        "ex/foreign_business_tax_credit_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def sheet_list(*rows: Sheet) -> Artifact[Any]:
    """A `ca/foreign_tax_credit_sheets` artifact of one record per sheet, in order."""
    records = [
        {
            FOREIGN_NON_BUSINESS_TAX_PAID: D("1500"),
            NET_FOREIGN_NON_BUSINESS_INCOME: D("10000"),
            FOREIGN_TAX_CREDIT_SHEET_LINE_3: D(line_3),
            FOREIGN_BUSINESS_TAX_PAID: D(tax),
            FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D(unused),
            NET_FOREIGN_BUSINESS_INCOME: D(income),
            FOREIGN_SURTAX_OUTSIDE_CANADA: D(surtax),
        }
        for tax, unused, income, surtax, line_3 in rows
    ]
    return Artifact(SHEETS, RecordList(SHEETS.fields, records))


def sheets_given(
    *rows: Sheet, net_income: str = "100000", basic_tax: str = "14500"
) -> tuple[Artifact[Any], ...]:
    return (
        sheet_list(*rows),
        Artifact(NET_INCOME, D(net_income)),
        Artifact(BASIC_TAX, D(basic_tax)),
    )
