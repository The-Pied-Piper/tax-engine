"""Registered kinds of Form T777 as its own form, `ca/t777` (capital cost allowance schedule for
employees, Parts A and B), in the federal catalog family `t777`.

The form has two row lists of Part A (Class 8, which feeds line 13, and the vehicle classes 10, 54
and 55, which feed line 25), one row list of Part B (Class 10.1 vehicles), the GST/HST rate of the
Class 54 sold-vehicle step, and its exports: line 13, line 25 and the closing UCC of Parts A and B.
The columns of a row are the CCA table's own kinds (`ca/cca_*`), read by identifier.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import tax_calculator.jurisdictions.ca.catalog
from tax_calculator.domain.artifact import ArtifactRegistry
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_CHANGE_IN_USE,
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_NO_PROPERTY_LEFT,
    CCA_PROCEEDS,
    CCA_RIIP_ADDITIONS,
    CCA_SOLD_ZEPVS,
    CCA_UCC_AT_END,
    CCA_UCC_AT_START,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS,
    T777_CLASS_8_CHECKED_ROWS,
    T777_CLASS_8_CLOSING_UCC,
    T777_CLASS_8_ROWS,
    T777_LINE_13,
    T777_LINE_25,
    T777_PART_B_ADDITIONS_CHECKED_ROWS,
    T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS,
    T777_PART_B_CHECKED_ROWS,
    T777_PART_B_CLASS_CHECKED_ROWS,
    T777_PART_B_CLOSING_UCC,
    T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS,
    T777_PART_B_ROWS,
    T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS,
    T777_VEHICLE_CHECKED_ROWS,
    T777_VEHICLE_CLOSING_UCC,
    T777_VEHICLE_ROWS,
    T777_VEHICLE_SALES_TAX_RATE,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# T777 Part A columns 1 to 6, the ones the form lets the user enter: the class number, UCC at the
# start of the year (2), cost of additions (3), AIIP or ZEV acquired before 2025 (4), RIIP or ZEV
# acquired after 2024 (5) and proceeds of dispositions (6). Columns 7 to 16 are computed.
PART_A_INPUT_COLUMNS = {
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_START,
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_RIIP_ADDITIONS,
    CCA_PROCEEDS,
}
PART_A_LISTS = (T777_CLASS_8_ROWS, T777_VEHICLE_ROWS)
# The Part A rows that passed the checks of `ca/cca_part_a_checks`: the same fields as the rows.
PART_A_CHECKED_LISTS = (T777_CLASS_8_CHECKED_ROWS, T777_VEHICLE_CHECKED_ROWS)
# The Part A rows that passed the change in use check of `ca/cca_change_in_use_checks`: the Class 8
# rows and the vehicle rows, with the same fields as the rows.
PART_A_CHANGE_IN_USE_CHECKED_LISTS = (
    T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS,
    T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS,
)
CHANGE_IN_USE_COLUMNS = {CCA_CHANGE_IN_USE, CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE}
MONEY = (T777_VEHICLE_SALES_TAX_RATE, T777_LINE_13, T777_LINE_25)
CLOSING_LISTS = (T777_CLASS_8_CLOSING_UCC, T777_VEHICLE_CLOSING_UCC, T777_PART_B_CLOSING_UCC)
# The Part B rows that passed the Class 10.1 additions check: the same fields as the Part B rows.
PART_B_ADDITIONS_CHECKED_LISTS = (T777_PART_B_ADDITIONS_CHECKED_ROWS,)
# The Part B rows that passed the Class 10.1 class condition check: the same fields as the rows.
PART_B_CLASS_CHECKED_LISTS = (T777_PART_B_CLASS_CHECKED_ROWS,)
# The Part B rows that passed the non-arm's-length purchase check and the change in use check.
PART_B_COST_CHECKED_LISTS = (
    T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS,
    T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS,
)
ALL_KINDS = (
    *PART_A_LISTS,
    *PART_A_CHECKED_LISTS,
    *PART_A_CHANGE_IN_USE_CHECKED_LISTS,
    T777_PART_B_ROWS,
    *PART_B_ADDITIONS_CHECKED_LISTS,
    *PART_B_CLASS_CHECKED_LISTS,
    *PART_B_COST_CHECKED_LISTS,
    *MONEY,
    *CLOSING_LISTS,
)


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in a catalog module (its
    name is a constant of the declaration's call, which may take the catalog first)."""
    folder = Path(tax_calculator.jurisdictions.ca.catalog.__file__).parent
    for path in sorted(folder.glob("*.py")):
        body = ast.parse(path.read_text()).body
        for statement, following in zip(body, body[1:], strict=False):
            if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
                continue
            constants = [
                each.value for each in statement.value.args if isinstance(each, ast.Constant)
            ]
            if not (
                identifier.rpartition("/")[2] in constants
                and isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
            ):
                continue
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")


def test_the_t777_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t777_kinds_are_in_the_snapshot_and_in_the_right_groups() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED
    for kind in (
        PART_A_LISTS
        + PART_A_CHECKED_LISTS
        + PART_A_CHANGE_IN_USE_CHECKED_LISTS
        + (T777_PART_B_ROWS,)
        + PART_B_ADDITIONS_CHECKED_LISTS
        + PART_B_CLASS_CHECKED_LISTS
        + PART_B_COST_CHECKED_LISTS
        + CLOSING_LISTS
    ):
        assert kind.identifier in RECORD_LISTS, kind.identifier
    for amount in MONEY:
        assert amount.identifier not in RECORD_LISTS | COUNTS, amount.identifier


def test_the_t777_row_lists_are_record_list_kinds() -> None:
    for kind in (
        PART_A_LISTS
        + PART_A_CHECKED_LISTS
        + PART_A_CHANGE_IN_USE_CHECKED_LISTS
        + (T777_PART_B_ROWS,)
        + PART_B_ADDITIONS_CHECKED_LISTS
        + PART_B_CLASS_CHECKED_LISTS
        + PART_B_COST_CHECKED_LISTS
        + CLOSING_LISTS
    ):
        assert isinstance(kind, RecordListKind), kind.identifier


def test_the_t777_amounts_are_non_negative_money() -> None:
    for kind in MONEY:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_part_a_lists_hold_the_six_input_columns_and_no_computed_column() -> None:
    for kind in PART_A_LISTS + PART_A_CHECKED_LISTS:
        fields = set(kind.fields)

        assert PART_A_INPUT_COLUMNS <= fields, kind.identifier
        # The claim (column 15) is the filer's election within the maximum; the closing UCC is
        # computed by the form, never entered.
        assert CCA_CLAIMED in fields, kind.identifier
        assert CCA_UCC_AT_END not in fields, kind.identifier


def test_each_checked_list_holds_the_fields_of_the_row_list_it_checks() -> None:
    # The checks pass the rows on unchanged, so a checked list has the fields of its row list.
    assert T777_CLASS_8_CHECKED_ROWS.fields == T777_CLASS_8_ROWS.fields
    assert T777_VEHICLE_CHECKED_ROWS.fields == T777_VEHICLE_ROWS.fields


def test_the_part_b_additions_checked_rows_hold_the_fields_of_the_part_b_rows() -> None:
    # The Class 10.1 additions check passes the Part B rows on unchanged, the UCC at the start and
    # the additions included, for the Part B claim to read.
    assert T777_PART_B_ADDITIONS_CHECKED_ROWS.fields == T777_PART_B_ROWS.fields
    assert T777_PART_B_ADDITIONS_CHECKED_ROWS.identifier == "ca/t777_part_b_additions_checked_rows"


def test_the_part_b_class_checked_rows_hold_the_fields_of_the_part_b_rows() -> None:
    # The Class 10.1 class condition check passes the Part B rows on unchanged, the date acquired
    # and the cost of vehicle included, for the Part B claim to read.
    assert T777_PART_B_CLASS_CHECKED_ROWS.fields == T777_PART_B_ROWS.fields
    assert T777_PART_B_CLASS_CHECKED_ROWS.identifier == "ca/t777_part_b_class_checked_rows"


def test_the_part_b_cost_checked_rows_hold_the_fields_of_the_part_b_rows() -> None:
    # The non-arm's-length purchase check and the change in use check pass the Part B rows on
    # unchanged, the answers and figures of column 3 included, for the Part B claim to read.
    for kind in PART_B_COST_CHECKED_LISTS:
        assert kind.fields == T777_PART_B_ROWS.fields, kind.identifier
    assert T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS.identifier == (
        "ca/t777_part_b_non_arms_length_checked_rows"
    )
    assert T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS.identifier == (
        "ca/t777_part_b_change_in_use_checked_rows"
    )


def test_the_part_b_list_holds_the_non_arms_length_and_change_in_use_answers_and_figures() -> None:
    # Guide T4044, Part B column 3: bought from a non-arm's-length person (fair market value and
    # seller's cost) and change in use (fair market value), each in its own field of the row.
    fields = {field.identifier for field in T777_PART_B_ROWS.fields}

    assert {
        "ca/cca_vehicle_from_non_arms_length",
        "ca/cca_vehicle_non_arms_length_fair_market_value",
        "ca/cca_vehicle_seller_cost",
        "ca/cca_vehicle_change_in_use",
        "ca/cca_vehicle_change_in_use_fair_market_value",
    } <= fields


def test_the_part_a_rows_hold_the_change_in_use_answer_and_fair_market_value() -> None:
    # Guide T4044 2025, Part A column 3: every Part A row, and each of its checked lists, carries
    # the yes or no change in use answer and the fair market value the change in use check reads.
    for kind in PART_A_LISTS + PART_A_CHECKED_LISTS:
        assert CHANGE_IN_USE_COLUMNS <= set(kind.fields), kind.identifier


def test_the_part_a_change_in_use_checked_rows_hold_the_fields_of_the_rows() -> None:
    # The change in use check passes each row on with the same fields as the rows it reads.
    for kind, rows in (
        (T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS, T777_CLASS_8_ROWS),
        (T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS, T777_VEHICLE_ROWS),
    ):
        assert kind.fields == rows.fields, kind.identifier


def test_the_part_a_change_in_use_checked_rows_have_their_identifiers() -> None:
    assert (
        T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS.identifier
        == "ca/t777_class_8_change_in_use_checked_rows"
    )
    assert (
        T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS.identifier
        == "ca/t777_vehicle_change_in_use_checked_rows"
    )


def test_only_the_vehicle_list_holds_the_sold_vehicles_of_class_54() -> None:
    assert CCA_SOLD_ZEPVS in set(T777_VEHICLE_ROWS.fields)
    assert CCA_SOLD_ZEPVS not in set(T777_CLASS_8_ROWS.fields)
    assert CCA_SOLD_ZEPVS not in set(T777_PART_B_ROWS.fields)


def test_the_part_b_list_holds_the_six_columns_and_the_sold_in_year_tick() -> None:
    fields = set(T777_PART_B_ROWS.fields)

    # Part B columns 1 (class number), 2 (UCC at the start), 3 (additions), 4 (proceeds), and the
    # AIIP and RIIP additions of notes (8) and (9); the tick is the table's no-property-left.
    assert PART_A_INPUT_COLUMNS <= fields
    assert CCA_PROCEEDS in fields
    assert CCA_NO_PROPERTY_LEFT in fields
    assert CCA_CLAIMED in fields


def test_the_part_b_list_holds_the_date_acquired_year_and_the_cost_of_vehicle() -> None:
    # Form T777 Part B prints "Date acquired (yyyy-mm-dd)" and "Cost of vehicle" before column 1; no
    # column reads them, so the checked lists carry them unchanged.
    for kind in (
        T777_PART_B_ROWS,
        T777_PART_B_CHECKED_ROWS,
        T777_PART_B_ADDITIONS_CHECKED_ROWS,
        T777_PART_B_CLASS_CHECKED_ROWS,
        *PART_B_COST_CHECKED_LISTS,
    ):
        assert CCA_VEHICLE_ACQUIRED_YEAR in kind.fields, kind.identifier
        assert CCA_VEHICLE_COST in kind.fields, kind.identifier


def test_each_closing_list_is_the_class_and_its_ucc_at_the_end() -> None:
    for kind in CLOSING_LISTS:
        assert set(kind.fields) == {CCA_CLASS_NUMBER, CCA_UCC_AT_END}, kind.identifier


def test_the_exports_are_the_money_of_lines_13_and_25() -> None:
    assert T777_LINE_13.identifier == "ca/t777_line_13"
    assert T777_LINE_25.identifier == "ca/t777_line_25"
    assert T777_VEHICLE_SALES_TAX_RATE.identifier == "ca/t777_vehicle_sales_tax_rate"


def test_each_t777_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T777" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_part_b_additions_checked_rows_docstring_names_part_b_and_the_class_10_1_check() -> (
    None
):
    text = squashed(docstring_of(T777_PART_B_ADDITIONS_CHECKED_ROWS.identifier))

    assert "Part B" in text
    assert "Class 10.1" in text
    assert "checked" in text.lower()


def test_the_part_b_class_checked_rows_docstring_names_part_b_and_the_class_10_1_condition() -> (
    None
):
    text = squashed(docstring_of(T777_PART_B_CLASS_CHECKED_ROWS.identifier))

    assert "Part B" in text
    assert "Class 10.1" in text
    assert "checked" in text.lower()


def test_the_part_b_cost_checked_rows_docstrings_name_part_b_and_their_rule() -> None:
    non_arms_length = squashed(docstring_of(T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS.identifier))
    change_in_use = squashed(docstring_of(T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS.identifier))

    assert "Part B" in non_arms_length
    assert "non-arm's-length" in non_arms_length
    assert "Part B" in change_in_use
    assert "change in use" in change_in_use


def test_the_part_a_change_in_use_checked_rows_docstrings_name_part_a_and_their_rule() -> None:
    for kind in PART_A_CHANGE_IN_USE_CHECKED_LISTS:
        text = squashed(docstring_of(kind.identifier))

        assert "Part A" in text, kind.identifier
        assert "change in use" in text, kind.identifier


def test_the_part_a_change_in_use_kinds_docstrings_quote_the_part_a_guide_text() -> None:
    # The Guide's Part A column 3 text, quoted as the guide prints it (docs/cra-forms-2025).
    quote = (
        "If you owned property for personal use and then started using it for employment in 2025, "
        "there is a change in use. In most cases when this happens, the amount you will enter in "
        "this column is the fair market value of the property at the time you start using the "
        "property for employment."
    )

    assert quote in squashed(docstring_of(CCA_CHANGE_IN_USE.identifier))
    assert quote in squashed(docstring_of(CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE.identifier))


# --- the lines of page 1 to 3, the relocation form and the line 22900 total (#446) ---------------
# The kinds of this ticket are looked up by identifier, so that the tests above keep their own
# imports while the kinds are missing (each new test then fails with the missing identifier).

PAGE_1_INPUTS = (
    "ca/t777_accounting_and_legal_fees",  # line 1 "Accounting and legal fees" 8862
    "ca/t777_advertising_and_promotion",  # line 2 "Advertising and promotion" 8520
    "ca/t777_food_beverages_entertainment",  # line 4, the amount before "× 50%" 8523
    "ca/t777_lodging",  # line 5 "Lodging" 9200
    "ca/t777_parking",  # line 6 "Parking" 8910
    "ca/t777_office_supplies",  # line 7 "Office supplies" 8810
    "ca/t777_other_expenses",  # line 8 "Other expenses ... (specify)" 9270
    "ca/t777_tradespersons_tools",  # line 9, the amount before "(maximum $1,000)" 1770
    "ca/t777_apprentice_mechanic_tools",  # line 10 "Apprentice mechanic tools expenses" 9131
    "ca/t777_musical_instrument_expenses",  # line 12 "Musical instrument expenses" 1776
    "ca/t777_artists_employment_expenses",  # line 14 "Artists' employment expenses" 9973
)
LINE_3_INPUTS = (
    "ca/t777_employment_kilometres",  # line 18 "Enter the number of kilometres you drove"
    "ca/t777_total_kilometres",  # line 19 "Enter the total number of kilometres you drove"
    "ca/t777_vehicle_fuel",  # line 21 "Fuel (such as gasoline, propane, and oil) and electricity"
    "ca/t777_vehicle_maintenance",  # line 22 "Maintenance and repairs"
    "ca/t777_vehicle_insurance",  # line 23 "Insurance"
    "ca/t777_vehicle_licence_and_registration",  # line 24 "Licence and registration"
    "ca/t777_vehicle_interest",  # line 26 "Interest expense"
    "ca/t777_vehicle_leasing_costs",  # line 27 "Leasing costs"
    "ca/t777_vehicle_other_expenses",  # line 28 "Other expenses (specify)"
    "ca/t777_vehicle_allowances",  # line 31 "rebates, motor vehicle allowances, and reimbursements"
)
LEASE_AMOUNTS = (
    "ca/t777_lease_charges",
    "ca/t777_lease_deposits_total",  # guide "Repayments and imputed interest", third condition
    "ca/t777_lease_payments_before",
    "ca/t777_lease_list_price",
    "ca/t777_lease_list_price_limit",
    "ca/t777_lease_list_price_tax",
    "ca/t777_lease_line_5",
    "ca/t777_lease_line_6_amount",
    "ca/t777_lease_line_6",
    "ca/t777_lease_charge_limit",
    "ca/t777_lease_charge_tax",
    "ca/t777_lease_charge_with_tax",
    "ca/t777_lease_line_7_times_days",
    "ca/t777_lease_line_7_divided",
    "ca/t777_lease_payments_before_checked",
    "ca/t777_lease_line_7",
    "ca/t777_lease_cost_limit",
    "ca/t777_lease_cost_tax",
    "ca/t777_lease_cost_with_tax",
    "ca/t777_lease_line_8",
    "ca/t777_lease_eligible_cost",
)
LEASE_COUNTS = (
    "ca/t777_lease_days",  # chart line 3
    "ca/t777_lease_year",  # the year of the lease
    "ca/t777_passenger_vehicle",  # the passenger vehicle answer, read by lines 26 and 27
    "ca/t777_passenger_vehicle_checked",
    "ca/t777_lease_repayment_owing",  # guide "Repayments and imputed interest": a repayment owing
    "ca/t777_lease_repayment_owing_checked",
    "ca/t777_lease_deposits_made",  # imputed interest, first condition
    "ca/t777_lease_deposits_made_checked",
    "ca/t777_lease_deposits_refundable",  # imputed interest, second condition ("All deposits")
    "ca/t777_lease_deposits_refundable_checked",
    "ca/t777_lease_chart_conflict",  # 1 when the chart cannot be used
    "ca/t777_lease_chart_conflict_checked",  # the conflict, refused when it is 1
    "ca/t777_interest_days",  # interest chart line B "days for which interest was paid"
)
LINE_16_INPUTS = (
    "ca/t777_work_space_electricity_heat_water_internet",  # line 42
    # line 43 "Maintenance (cleaning supplies, light bulbs, etc.)"
    "ca/t777_work_space_maintenance",
    "ca/t777_work_space_home_insurance",  # line 44 "Home insurance (commission employees only)"
    "ca/t777_work_space_property_taxes",  # line 45 "Property taxes (commission employees only)"
    "ca/t777_work_space_other_expenses",  # line 46 "Other expenses (rent, etc.) (specify)"
    "ca/t777_work_space_employment_use_amount",  # line 48 "Total employment-use amount"
    "ca/t777_work_space_carried_forward",  # line 49 "Amount carried forward from the previous year"
)
RELOCATION_FIELDS = (
    "ca/t777_relocation_carried_forward",  # line 33
    "ca/t777_relocation_transportation",  # line 34
    "ca/t777_relocation_meals",  # line 35
    "ca/t777_relocation_lodging",  # line 36
    "ca/t777_relocation_tradesperson_income",  # line 38, the employment income before "× 50%"
    "ca/t777_relocation_claim",  # line 39, "the amount you are claiming for this relocation"
)
LINE_AMOUNTS = (
    "ca/t777_interest_limit",  # interest chart line B "$10 multiplied by the number of days"
    "ca/t777_interest_available",  # "the lesser of amount A and amount B"
    "ca/t777_line_26",  # line 26 "Interest expense"
    "ca/t777_line_4",
    "ca/t777_line_9",
    "ca/t777_line_11",
    "ca/t777_line_15",
    "ca/t777_line_16",
    "ca/t777_line_17",
    "ca/t777_vehicle_total_expenses",  # line 29 "Add lines 21 to 28."
    "ca/t777_vehicle_employment_use",  # line 30 "Line 20 multiplied by line 29"
    "ca/t777_work_space_expenses",  # line 47 "Add lines 42 to 46."
    "ca/t777_work_space_total_amount",  # line 50 "Line 48 plus line 49"
    "ca/t777_work_space_employment_income",  # line 51 "Enter your employment income."
    "ca/t777_work_space_employment_offsets",  # line 52
    "ca/t777_work_space_income_limit",  # line 53 "(if negative, enter "0")"
    "ca/t777_work_space_carried_forward_out",  # line 55, carried to the next year's line 49
    "ca/t777_relocation_total",  # relocation line 37 "Total eligible temporary relocation expenses"
    "ca/t777_relocation_income_limit",  # relocation line 38
    "ca/t777_relocation_deduction",  # relocation line 39, the amount available for deduction
    "ca/t777_relocation_carried_forward_out",  # relocation line 40
    "ca/t777_relocation_deduction_total",  # the total of line 39 over the relocation copies
    "ca/t777_line_11_maximum",  # the $4,000 maximum of line 11 and line 41
)


def test_the_page_1_inputs_are_registered_non_negative_money(registry: ArtifactRegistry) -> None:
    for identifier in (
        PAGE_1_INPUTS + LINE_3_INPUTS + LEASE_AMOUNTS + LINE_16_INPUTS + RELOCATION_FIELDS
    ):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is True, identifier


def test_the_lease_chart_days_and_year_are_non_negative_counts(registry: ArtifactRegistry) -> None:
    for identifier in LEASE_COUNTS:
        kind = registry.kind(identifier)
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier


def test_the_kilometres_and_the_work_space_use_are_money_not_counts(
    registry: ArtifactRegistry,
) -> None:
    # Kilometres and the employment-use amount are dollars and kilometres, not counts of items.
    for identifier in ("ca/t777_employment_kilometres", "ca/t777_work_space_employment_use_amount"):
        assert registry.kind(identifier).value_type is Decimal, identifier


def test_the_line_amounts_are_registered_decimals(registry: ArtifactRegistry) -> None:
    for identifier in LINE_AMOUNTS:
        assert registry.kind(identifier).value_type is Decimal, identifier


def test_line_3_is_signed_as_the_form_prints_no_floor_on_line_32(
    registry: ArtifactRegistry,
) -> None:
    # Form T777 line 32 "Line 30 minus line 31. Enter this amount on line 3 of page 1.": no floor
    # is printed, so the figure may be negative (as T2125's line 9 is).
    kind = registry.kind("ca/t777_line_3")

    assert kind.value_type is Decimal
    assert kind.non_negative is False
    assert "ca/t777_line_3" in SIGNED


def test_the_line_31_allowances_check_is_registered_beside_its_input(
    registry: ArtifactRegistry,
) -> None:
    # Form T777 line 31 "rebates, motor vehicle allowances, and reimbursements", at most line 30
    # (`core/at_most`); the checked amount is the one line 32 subtracts.
    kind = registry.kind("ca/t777_vehicle_allowances_checked")

    assert kind.value_type is Decimal
    assert kind.non_negative is True
    assert kind is not registry.kind("ca/t777_vehicle_allowances")


def test_the_relocation_record_list_holds_the_six_fields_of_lines_33_to_36_38_and_39(
    registry: ArtifactRegistry,
) -> None:
    kind = registry.kind("ca/t777_relocations")

    assert isinstance(kind, RecordListKind)
    assert tuple(field.identifier for field in kind.fields) == RELOCATION_FIELDS
    assert "ca/t777_relocations" in RECORD_LISTS


def test_the_relocation_form_exports_are_the_line_39_and_line_40_amounts(
    registry: ArtifactRegistry,
) -> None:
    for identifier in ("ca/t777_relocation_deduction", "ca/t777_relocation_carried_forward_out"):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is True, identifier


def test_the_work_space_carried_forward_out_is_registered_and_listed(
    registry: ArtifactRegistry,
) -> None:
    assert "ca/t777_work_space_carried_forward_out" in REGISTERED
    assert registry.kind("ca/t777_work_space_carried_forward_out").non_negative is True


def test_the_new_lines_and_inputs_are_in_the_snapshot(registry: ArtifactRegistry) -> None:
    new = (
        PAGE_1_INPUTS
        + LINE_3_INPUTS
        + LEASE_AMOUNTS
        + LEASE_COUNTS
        + LINE_16_INPUTS
        + RELOCATION_FIELDS
        + LINE_AMOUNTS
        + ("ca/t777_relocations",)
    )
    for identifier in new:
        assert identifier in REGISTERED, identifier
        assert identifier in registry.identifiers(), identifier


def test_each_new_line_kind_has_a_docstring_that_quotes_its_form_line() -> None:
    # Docstring shape: "Name, Form T777 line N "quoted form text": what it is."
    for identifier, quoted in (
        ("ca/t777_line_17", "Total expenses"),
        ("ca/t777_line_16", "Work-space-in-the-home expenses"),
        ("ca/t777_line_11", "Total labour mobility deduction for the year"),
        ("ca/t777_line_4", "Food, beverages, and entertainment expenses"),
        ("ca/t777_line_9", "Tradesperson's tools expenses"),
        ("ca/t777_line_3", "Allowable motor vehicle expenses"),
    ):
        text = squashed(docstring_of(identifier))
        assert "T777" in text, identifier
        assert quoted in text, identifier


def test_the_line_22900_kind_is_computed_and_its_docstring_is_no_starting_amount() -> None:
    text = squashed(docstring_of("ca/other_employment_expenses"))

    assert "starting amount" not in text
    assert "22900" in text
    assert "T777" in text
    assert "RC359" in text


def test_the_rc359_line_7_total_is_registered_money(registry: ArtifactRegistry) -> None:
    kind = registry.kind("ca/rc359_excess_epsp_total")

    assert kind.value_type is Decimal
    assert kind.non_negative is True
    assert "ca/rc359_excess_epsp_total" in REGISTERED
