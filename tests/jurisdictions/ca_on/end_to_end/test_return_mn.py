"""CA-ON 2025 end to end: return mn, the pension income amount worksheet (line 31400) reading line
11500 of the return with the Form T2205 amount beside the typed other pensions.

The worked return `returns/2025_return_mn.yaml` (return MG's Form T2205 amounts for a filer born in
1960 or earlier, so the SPP part and line 22 are 5,000.00 on line 11500) is checked by
`test_worked_returns.py`. This module computes the worksheet on its own: line 1 "Amount from line
11500 of your return" is the typed other pensions and superannuation plus the T2205 amount on line
11500. The U.S. Social Security benefits (bounded by the typed line 11500 amounts they are part of),
the exploration recovery income and the Form T1032 box 17 amounts (parts of the typed line 13000
other income) are not Form T2205 amounts, so those bounds stay on the typed lines.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    PENSION_CHART_LINE_1,
    PENSION_INCOME_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

RETURN = "ca-on/return"

# The Form T2205 amounts of return MG: the SPP part of line 11 of 1,000.00 and line 22 of 4,000.00.
MN_T2205 = {
    "line_1": "5000",
    "line_6": "2000",
    "line_11_spp_part": "1000",
    "line_12": "4000",
    "line_20": "4000",
}


def return_mn(**overrides: Any) -> Worksheet:
    """Return MN: no income but the Form T2205 amounts and the keyword overrides given."""
    artifacts = starting("0", (), "0", "0", "0", "0", "0", t2205_amounts=MN_T2205, **overrides)
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts)[RETURN]
    return worksheet


def test_line_11500_of_the_return_adds_the_t2205_amount_to_the_typed_pensions() -> None:
    # 1,500.00 typed + 5,000.00 (the SPP part and line 22 of a filer 65 or older).
    worksheet = return_mn(born_in_1960_or_earlier=1, other_pensions_and_superannuation="1500")

    assert worksheet.get(PENSION_CHART_LINE_1).value == D("6500")


def test_line_11500_of_the_return_is_the_typed_pensions_alone_for_a_filer_under_65() -> None:
    # The same T2205 amounts go to line 13000, so line 11500 holds only the 1,500.00 typed.
    worksheet = return_mn(other_pensions_and_superannuation="1500")

    assert worksheet.get(PENSION_CHART_LINE_1).value == D("1500")


def test_the_pension_income_amount_worksheet_reads_the_t2205_amount_on_line_11500() -> None:
    # Line 1 is 5,000.00, lines 2 to 5 and line 7 are 0, so line 8 is 5,000.00 and the credit is
    # whichever is less of that and 2,000.00. The typed pensions alone (0.00) would give 0.00.
    worksheet = return_mn(born_in_1960_or_earlier=1)

    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("2000")


def test_the_pension_income_amount_is_0_when_the_t2205_amount_is_on_line_13000() -> None:
    assert return_mn().get(PENSION_INCOME_CREDIT).value == D("0")


def test_the_pension_income_amount_adds_a_typed_pension_below_the_maximum() -> None:
    # No T2205 amount on line 11500 (under 65): 1,500.00 typed gives 1,500.00.
    worksheet = return_mn(other_pensions_and_superannuation="1500")

    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("1500")


def test_a_negative_t2205_line_22_leaves_worksheet_line_1_at_0_and_no_input_error() -> None:
    # Line 12 of 4,000.00 and line 20 of 1,000.00 with line 17 of 5,000.00 and line 18 of 0.00:
    # line 21 is the lesser of line 16 and line 19 (4,000.00), so line 22 = 1,000.00 - 4,000.00 =
    # -3,000.00 on line 11500; line 1 of the worksheet is taken as 0.00, line 5 of 0.00 is not
    # above it, and the pension income amount is 0.00. Other income of 5,000.00 keeps total income
    # (2,000.00) above zero.
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t2205_amounts={
            "line_12": "4000",
            "line_17": "5000",
            "line_18": "0",
            "line_20": "1000",
        },
        born_in_1960_or_earlier=1,
        other_income="5000",
    )
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts)[RETURN]

    assert worksheet.get(PENSION_CHART_LINE_1).value == D("0")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("0")
