"""Registered and money kinds of the federal catalog family `refund`."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_calculator.jurisdictions.ca.catalog import (
    EI_OVERPAYMENT,
    FARM_FUEL_CHARGE_CREDIT_TOTAL,
    FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED,
    FUEL_CHARGE_CREDIT_AB,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_CREDIT_FARMERS_TOTAL,
    FUEL_CHARGE_CREDIT_MB,
    FUEL_CHARGE_CREDIT_NB,
    FUEL_CHARGE_CREDIT_NL,
    FUEL_CHARGE_CREDIT_NS,
    FUEL_CHARGE_CREDIT_ON,
    FUEL_CHARGE_CREDIT_PE,
    FUEL_CHARGE_CREDIT_SK,
    FUEL_CHARGE_EXPENSES_AB,
    FUEL_CHARGE_EXPENSES_MB,
    FUEL_CHARGE_EXPENSES_NB,
    FUEL_CHARGE_EXPENSES_NL,
    FUEL_CHARGE_EXPENSES_NS,
    FUEL_CHARGE_EXPENSES_ON,
    FUEL_CHARGE_EXPENSES_PE,
    FUEL_CHARGE_EXPENSES_SK,
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    FUEL_CHARGE_PART_2_TOTAL,
    FUEL_CHARGE_PART_5A_CREDIT,
    FUEL_CHARGE_PART_5B_CREDIT,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_AB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_MB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NL,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NS,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_ON,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_PE,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_SK,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    T2204_EXEMPTION,
    T2204_INSURABLE_EARNINGS,
    T2204_LINE_1,
    T2204_LINE_1_COUNT,
    T2204_LINE_1_PLUS_2,
    T2204_LINE_3,
    T2204_LINE_6,
    T2204_LINE_7,
    T2204_LINE_8,
    T2204_LINE_9,
    T2204_LINE_10,
    T2204_LINE_12,
    T2204_LINE_13,
    T2204_LINE_14,
    T2204_LINE_15,
    T2204_LINE_15_COUNT,
    T2204_LINE_16,
    T2204_PPIP_PREMIUMS,
    T2204_PPIP_PREMIUMS_CHECKED,
    T2204_PREMIUMS_DEDUCTED,
    T2204_SELF_EMPLOYMENT_EARNINGS,
    TOTAL_CREDITS,
)
from tests.jurisdictions.ca.catalog_snapshot import REGISTERED

T2204_MONEY = (
    T2204_INSURABLE_EARNINGS,
    T2204_SELF_EMPLOYMENT_EARNINGS,
    T2204_PREMIUMS_DEDUCTED,
    T2204_PPIP_PREMIUMS,
    T2204_PPIP_PREMIUMS_CHECKED,
    T2204_LINE_1,
    T2204_LINE_1_PLUS_2,
    T2204_LINE_3,
    T2204_EXEMPTION,
    T2204_LINE_6,
    T2204_LINE_7,
    T2204_LINE_8,
    T2204_LINE_9,
    T2204_LINE_10,
    T2204_LINE_12,
    T2204_LINE_13,
    T2204_LINE_14,
    T2204_LINE_15,
    T2204_LINE_16,
    EI_OVERPAYMENT,
)
T2204_COUNTS = (T2204_LINE_1_COUNT, T2204_LINE_15_COUNT)


def test_the_refund_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/total_credits") is TOTAL_CREDITS
    assert registry.get("ca/refund_or_balance_owing") is REFUND_OR_BALANCE_OWING
    assert registry.get("ca/refund") is REFUND


def test_the_refund_kinds_are_money() -> None:
    for kind in (
        TOTAL_CREDITS,
        REFUND_OR_BALANCE_OWING,
        REFUND,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_t2204_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    # T2204 (Employee Overpayment of Employment Insurance Premiums): the caller's three inputs,
    # the lines 1 to 16 that are computed, and the overpayment on T1 line 45000.
    for kind in T2204_MONEY + T2204_COUNTS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t2204_kinds_are_money() -> None:
    for kind in T2204_MONEY:
        assert kind.value_type is Decimal, kind.identifier


def test_the_t2204_counts_are_int_kinds() -> None:
    # The count of note (1) and the count of line 45000, each 0 or 1.
    for kind in T2204_COUNTS:
        assert kind.value_type is int, kind.identifier


# --- Form T2043, Return of Fuel Charge Proceeds to Farmers Tax Credit, Parts 1, 2 and 5 ----------

PROVINCES = ("on", "mb", "sk", "ab", "ns", "pe", "nl", "nb")
FUEL_CHARGE_EXPENSES = (
    FUEL_CHARGE_EXPENSES_ON,
    FUEL_CHARGE_EXPENSES_MB,
    FUEL_CHARGE_EXPENSES_SK,
    FUEL_CHARGE_EXPENSES_AB,
    FUEL_CHARGE_EXPENSES_NS,
    FUEL_CHARGE_EXPENSES_PE,
    FUEL_CHARGE_EXPENSES_NL,
    FUEL_CHARGE_EXPENSES_NB,
)
FUEL_CHARGE_CREDITS = (
    FUEL_CHARGE_CREDIT_ON,
    FUEL_CHARGE_CREDIT_MB,
    FUEL_CHARGE_CREDIT_SK,
    FUEL_CHARGE_CREDIT_AB,
    FUEL_CHARGE_CREDIT_NS,
    FUEL_CHARGE_CREDIT_PE,
    FUEL_CHARGE_CREDIT_NL,
    FUEL_CHARGE_CREDIT_NB,
)
FUEL_CHARGE_PARTNERSHIP_CREDITS = (
    FUEL_CHARGE_PARTNERSHIP_CREDIT_ON,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_MB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_SK,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_AB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NS,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_PE,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NL,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NB,
)
FUEL_CHARGE_KINDS = (
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    *FUEL_CHARGE_EXPENSES,
    *FUEL_CHARGE_CREDITS,
    FUEL_CHARGE_PART_2_TOTAL,
    FUEL_CHARGE_PART_5A_CREDIT,
    FUEL_CHARGE_PART_5B_CREDIT,
    *FUEL_CHARGE_PARTNERSHIP_CREDITS,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL,
    FARM_FUEL_CHARGE_CREDIT_TOTAL,
    FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_CREDIT_FARMERS_TOTAL,
)


def test_the_fuel_charge_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    for kind in FUEL_CHARGE_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_fuel_charge_kinds_are_registered_in_the_snapshot_as_money() -> None:
    for kind in FUEL_CHARGE_KINDS:
        assert kind.identifier in REGISTERED, kind.identifier
        assert kind.value_type is Decimal, kind.identifier


def test_the_province_lines_are_one_kind_for_each_line_of_the_form() -> None:
    # Lines 67063 to 67066 and 67091 to 67094 (the expenses), 2A to 2H (the credits) and 67079 to
    # 67082 and 67103 to 67106 (the partnership credits): eight kinds for each province, in the
    # form's order ON, MB, SK, AB, NS, PE, NL, NB.
    assert [kind.identifier for kind in FUEL_CHARGE_EXPENSES] == [
        f"ca/fuel_charge_expenses_{province}" for province in PROVINCES
    ]
    assert [kind.identifier for kind in FUEL_CHARGE_CREDITS] == [
        f"ca/fuel_charge_credit_{province}" for province in PROVINCES
    ]
    assert [kind.identifier for kind in FUEL_CHARGE_PARTNERSHIP_CREDITS] == [
        f"ca/fuel_charge_partnership_credit_{province}" for province in PROVINCES
    ]


def test_the_partnership_credit_tie_kinds_are_non_negative_money() -> None:
    # Form T2043 note 2 ties amount 5C to line 9951 of Form T2042 over the statements: the total of
    # line 9951 and that total after the `core/at_most` check against amount 5C.
    assert FARM_FUEL_CHARGE_CREDIT_TOTAL.identifier == "ca/farm_fuel_charge_credit_total"
    assert (
        FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED.identifier
        == "ca/farm_fuel_charge_credit_total_checked"
    )
    for kind in (
        FARM_FUEL_CHARGE_CREDIT_TOTAL,
        FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative, kind.identifier


def test_the_fuel_charge_credit_is_the_5d_total_and_is_signed() -> None:
    # Part 5 line 5D, the total credit of all businesses, which is line 47556 of the return.
    assert FUEL_CHARGE_CREDIT_FARMERS.identifier == "ca/fuel_charge_credit_farmers"
    # The 5D line prints no floor and amounts 5A and 5B can be below zero, so it may be too.
    assert not FUEL_CHARGE_CREDIT_FARMERS.non_negative


def test_the_fuel_charge_credit_total_is_line_47556_read_into_line_48200() -> None:
    # The 5D credit is read by the return's line 48200 sum through its total (one record of the
    # Form's export, totalled by the return), so the total is the line 47556 money kind.
    assert FUEL_CHARGE_CREDIT_FARMERS_TOTAL.identifier == "ca/fuel_charge_credit_farmers_total"
    assert FUEL_CHARGE_CREDIT_FARMERS_TOTAL.value_type is Decimal
    assert not FUEL_CHARGE_CREDIT_FARMERS_TOTAL.non_negative


def test_the_gross_farming_expenses_line_67061_is_registered_and_signed(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/fuel_charge_gross_farming_expenses") is FUEL_CHARGE_GROSS_FARMING_EXPENSES
    )
    # Line 67061 adds amount 6 of every Chart A, which prints no floor, so it may be below zero.
    assert not FUEL_CHARGE_GROSS_FARMING_EXPENSES.non_negative


PROVINCE_CODES = ("on", "mb", "sk", "ab", "ns", "pe", "nl", "nb")

# --- Form T2043 Parts 3 and 4 (#191): the Chart B and Chart C totals -----------------------------

PARTS_3_AND_4_ARTIFACTS = (
    *(f"ca/fuel_charge_chart_b_gross_income_{c}" for c in PROVINCE_CODES),
    *(f"ca/fuel_charge_chart_b_salaries_{c}" for c in PROVINCE_CODES),
    "ca/fuel_charge_chart_b_total_gross_income",
    "ca/fuel_charge_chart_b_total_salaries",
    *(f"ca/fuel_charge_chart_c_total_{c}" for c in PROVINCE_CODES),
    "ca/fuel_charge_part_4_total",
)


def test_the_part_3_and_part_4_totals_are_registered_decimal_amounts(
    registry: ArtifactRegistry,
) -> None:
    for identifier in PARTS_3_AND_4_ARTIFACTS:
        kind = registry.get(identifier)
        assert isinstance(kind, ArtifactKind)
        assert kind.value_type is Decimal, identifier
        assert identifier in REGISTERED, identifier
