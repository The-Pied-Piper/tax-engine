"""CA-ON 2025 end to end: return ct."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FARM_CCA_CLAIM,
    FARM_CCA_TABLE_CLAIM,
    FARM_CHART_A_GROSS_EXPENSES,
    FARM_CLOSING_UCC,
    FARM_HOME_CCA,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARM_RECAPTURED_CCA,
    FARM_TERMINAL_LOSS,
    FARM_TOTAL_EXPENSES,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    FUEL_CHARGE_PART_5A_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return CF's T2042, Return BC's with the wheat raised by 2200.68 to 52200.68 (a chosen figure, so
# that line 9946 stays Return BC's 30000): income lines of 82200.68 (wheat 52200.68 on line 9371,
# cattle 30000 on line 9471) and expenses of 50000 (fertilizers and lime 20000 on line 9662, seeds
# and plants 30000 on line 9664), with no inventory adjustment or partner. The farm started on
# August 1, 2025, so its first fiscal period, August 1 to December 31, 2025, is 153 days (Guide
# T4002, "You were asking?", which has 214 days for a start on June 1).
FARM = {
    "wheat": "52200.68",
    "cattle": "30000",
    "fertilizers_and_lime": "20000",
    "seeds_and_plants": "30000",
    # Charts A to C for one leased passenger vehicle that is used for no farming: business
    # kilometres 0 (amount 1), so line 9819 (amount 16 of Chart A) is 0, as in Return BC.
    "vehicle_sales_tax_rate": "13",
}
DAYS = 153
# Charts A to C for one leased passenger vehicle used for no farming, as in Return BC.
VEHICLE = {
    "business_kilometres": "0",
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


def class_row(
    personal_part: str = "5000.00", claim: str = "2200.68"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9, endnote 9's remaining personal part): Return
    CF's Class 10 bought in the year (column 3 35000, nothing at the start), so column 7 is
    35000.00, with the given remaining personal part of the property's cost."""
    return ("10", "0", "35000", "0", "0", "0", claim, 0, "0", "0", "0", personal_part)


def run_ct(
    changes: Mapping[str, Any] | None = None, personal_part: str = "5000.00", **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CT's inputs, as in `returns/2025_return_ct.yaml`: Return CF's T2042 with a
    remaining personal part of 5000.00 on its one class (endnote 9)."""
    statement: dict[str, Any] = {
        "farm": FARM,
        "farm_cca_classes_rows": (class_row(personal_part),),
        "farm_vehicles_rows": (VEHICLE,),
        "farm_fiscal_period_days_entered": DAYS,
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_ct(
    changes: Mapping[str, Any] | None = None, personal_part: str = "5000.00"
) -> Worksheet:
    """The worksheet of Return CT's one T2042 statement: its lines, as the form computes them."""
    return run_ct(changes, personal_part)["ca/t2042"][0]


def closing(statement: Worksheet) -> list[tuple[Any, Any]]:
    records = statement.get(FARM_CLOSING_UCC).value.records
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records]


def test_return_cts_class_10_closes_at_27799_32_after_the_remaining_personal_part() -> None:
    # Column 22 is column 7 less column 21 (35000.00 - 2200.68 = 32799.32), less the remaining
    # personal part of the property's cost (endnote 9): 32799.32 - 5000.00 = 27799.32.
    statement = statement_ct()

    assert closing(statement) == [(D("10"), D("27799.32"))]


def test_return_cts_trace_names_the_remaining_personal_part() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_ct().trace)

    assert (
        "farm_closing_ucc: item 1 class 10: column 7 35000 less claim 2200.68 "
        "(prorated 153/365) less personal part 5000 = 27799.32"
    ) in rendered


def test_return_cts_personal_part_does_not_change_the_claim_or_the_form_lines() -> None:
    # Endnote 9 changes only column 22: the claim (column 21), the recapture, the terminal loss
    # and the income lines are Return CF's.
    with_part = statement_ct()
    without = statement_ct(personal_part="0")

    assert with_part.get(FARM_CCA_TABLE_CLAIM).value == D("2200.68")
    assert with_part.get(FARM_CCA_CLAIM).value == without.get(FARM_CCA_CLAIM).value
    assert with_part.get(FARM_RECAPTURED_CCA).value == D("0")
    assert with_part.get(FARM_TERMINAL_LOSS).value == D("0")
    assert closing(without) == [(D("10"), D("32799.32"))]


def test_a_remaining_personal_part_above_column_7_less_the_claim_is_refused() -> None:
    # 32799.32 is column 7 less the claim, so a part of 32799.33 is refused.
    with pytest.raises(InvalidRecordError, match="item 1: personal part"):
        statement_ct(personal_part="32799.33")


# The personal parts are parts of the amounts they are taken from (T2042 line 9936 and amounts 7I
# and 7K): the form prints no maximum for them, so a part above amount ii is worked as printed
# (signed), and a part equal to its whole is accepted. Return CT's amount ii of Area A is 2200.68
# and its home expenses are 0.


def test_a_cca_personal_part_above_amount_ii_is_worked_as_printed_through_t2043_chart_a() -> None:
    # 99999 is more than amount ii of 2200.68 and no printed bound applies: the claim is
    # 2200.68 less 99999 = -97798.32, so line 9898 is 50000 less 97798.32 = -47798.32 as printed.
    # Chart A's amount 5 is 0, so amount 6 is -47798.32 too; the form prints no floor, and Part 1
    # Note 1 (total gross farming expenses of $25,000 or more) leaves the credit at 0.
    # Line 9369 is 82200.68 - (-47798.32) = 129999.00.
    result = run_ct({"farm": {**FARM, "cca_personal_part": "99999"}})
    statement = result["ca/t2042"][0]
    form = result["ca/t2043"][0]

    assert statement.get(FARM_CCA_CLAIM).value == D("-97798.32")
    assert statement.get(FARM_TOTAL_EXPENSES).value == D("-47798.32")
    assert statement.get(FARM_CHART_A_GROSS_EXPENSES).value == D("-47798.32")
    assert statement.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("129999.00")
    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("-47798.32")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0")


def test_a_cca_personal_part_equal_to_amount_ii_is_accepted() -> None:
    statement = statement_ct({"farm": {**FARM, "cca_personal_part": "2200.68"}})

    assert statement.get(FARM_CCA_CLAIM).value == D("0")
    assert statement.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32200.68")


def test_home_cca_above_amount_ii_less_the_part_is_worked_as_printed_through_t2043_chart_a() -> (
    None
):
    # 99999 is more than the 2200.68 left of amount ii and no printed bound applies: the claim is
    # 2200.68 less 99999 = -97798.32 and line 9898 and Chart A's amount 6 are -47798.32 as printed;
    # the credit stays 0 under Part 1 Note 1.
    result = run_ct({"farm": {**FARM, "home_cca": "99999"}})
    statement = result["ca/t2042"][0]
    form = result["ca/t2043"][0]

    assert statement.get(FARM_CCA_CLAIM).value == D("-97798.32")
    assert statement.get(FARM_CHART_A_GROSS_EXPENSES).value == D("-47798.32")
    assert statement.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("129999.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0")


def test_a_personal_part_and_home_cca_adding_to_more_than_amount_ii_are_not_refused() -> None:
    # The personal part 1000 and home CCA 1200.69 add to 2200.69, more than amount ii of 2200.68:
    # no printed bound applies, so the claim is 2200.68 less 1000 less 1200.69 = -0.01 as printed.
    statement = run_ct({"farm": {**FARM, "cca_personal_part": "1000", "home_cca": "1200.69"}})[
        "ca/t2042"
    ][0]

    assert statement.get(FARM_CCA_CLAIM).value == D("-0.01")
    assert statement.get(FARM_HOME_CCA).value == D("1200.69")


def test_a_personal_part_and_home_cca_adding_to_amount_ii_are_accepted() -> None:
    statement = statement_ct({"farm": {**FARM, "cca_personal_part": "1000", "home_cca": "1200.68"}})

    assert statement.get(FARM_CCA_CLAIM).value == D("0")
    assert statement.get(FARM_HOME_CCA).value == D("1200.68")


def test_a_negative_part_2_credit_flows_through_5a_and_5d_signed() -> None:
    # Chart A amount 5 prints no maximum, so a statement whose personal part of the CCA is far above
    # its expenses has a negative amount 6 and a negative Part 2 credit (-109.46). The other
    # statement's expenses of 100000 open the $25,000 gate (Part 1 Note 1), so 5A and 5D are
    # negative too, and nothing is refused.
    def statement(farm: Mapping[str, Any], province: int, days: int) -> dict[str, Any]:
        return {
            "farm": {**FARM, **farm},
            "farm_cca_classes_rows": (class_row(),),
            "farm_vehicles_rows": (),
            "farm_fiscal_period_days_entered": 365,
            "farm_designated_province": province,
            "farm_days_in_2024": days,
        }

    big = statement({"fertilizers_and_lime": "70000", "seeds_and_plants": "30000"}, 0, 0)
    negative = statement({"cca_personal_part": "99999"}, 2, 365)

    form = run("0", (), "0", "0", "0", "0", "0", farm_statements=(big, negative))["ca/t2043"][0]

    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("-109.46")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("-109.46")
