"""Registered and money kinds of the federal catalog family `income`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    CREDITS_AGAINST_BASIC_FEDERAL_TAX,
    EMPLOYMENT_INCOME,
    FUEL_CHARGE_FARM_STATEMENT_COUNT,
    FUEL_CHARGE_FARMS_IN_PROVINCE_AB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_MB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NL,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NS,
    FUEL_CHARGE_FARMS_IN_PROVINCE_ON,
    FUEL_CHARGE_FARMS_IN_PROVINCE_PE,
    FUEL_CHARGE_FARMS_IN_PROVINCE_SK,
    FUEL_CHARGE_FARMS_OUTSIDE_EIGHT,
    FUEL_CHARGE_MULTIPLE_PROVINCES_BOX,
    OTHER_EMPLOYMENT_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca.catalog_snapshot import (
    COUNTS,
    REGISTERED,
    SIGNED,
)
from tests.kinds import non_negative as declared_non_negative

T2043_FUEL_CHARGE_PLACE_TOTALS = (
    FUEL_CHARGE_FARMS_IN_PROVINCE_ON,
    FUEL_CHARGE_FARMS_IN_PROVINCE_MB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_SK,
    FUEL_CHARGE_FARMS_IN_PROVINCE_AB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NS,
    FUEL_CHARGE_FARMS_IN_PROVINCE_PE,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NL,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NB,
    FUEL_CHARGE_FARMS_OUTSIDE_EIGHT,
)


def test_the_fuel_charge_place_totals_are_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    for kind in T2043_FUEL_CHARGE_PLACE_TOTALS:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert declared_non_negative(kind), kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_statement_count_and_the_box_are_registered_non_negative_ints(
    registry: ArtifactRegistry,
) -> None:
    for kind in (FUEL_CHARGE_FARM_STATEMENT_COUNT, FUEL_CHARGE_MULTIPLE_PROVINCES_BOX):
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is int, kind.identifier
        assert declared_non_negative(kind), kind.identifier
        assert kind.identifier in COUNTS, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier


def test_the_income_kinds_are_money() -> None:
    for kind in (
        EMPLOYMENT_INCOME,
        TOTAL_INCOME,
        OTHER_EMPLOYMENT_INCOME,
        CREDITS_AGAINST_BASIC_FEDERAL_TAX,
    ):
        assert kind.value_type is Decimal, kind.identifier


# --- Schedule 3 (form 5000-S3) Parts 3 and 4 --------------------------------------------------


def test_the_t2125_chart_lines_are_no_longer_artifacts(registry: ArtifactRegistry) -> None:
    # Each vehicle's lines 12, 13, 19, 26, 28 and the rest are worked inside the capability.
    for name in (
        "list_price_limit_tax",
        "lease_charge_limit_tax",
        "lease_cost_limit_tax",
        "list_price_limit_with_tax",
        "lease_charge_limit_with_tax",
        "lease_cost_limit_with_tax",
        "total_expenses",
        "business_use_part",
        "interest_for_period",
        "available_interest",
        "lease_price_base",
        "lease_price_85_percent",
        "lease_charge_portion",
        "lease_charges_net",
        "lease_cost_portion",
        "leasing_cost",
    ):
        assert f"ca/business_vehicle_{name}" not in registry.identifiers(), name


def test_the_t2042_chart_lines_are_no_longer_artifacts(registry: ArtifactRegistry) -> None:
    # Each vehicle's lines of Charts A to C are worked inside the capability, as on T2125.
    for name in (
        "list_price_limit_tax",
        "lease_charge_limit_tax",
        "lease_cost_limit_tax",
        "list_price_limit_with_tax",
        "lease_charge_limit_with_tax",
        "lease_cost_limit_with_tax",
        "total_expenses",
        "business_use_part",
        "interest_for_period",
        "available_interest",
        "lease_price_base",
        "lease_price_85_percent",
        "lease_charge_portion",
        "lease_charges_net",
        "lease_cost_portion",
        "leasing_cost",
    ):
        assert f"ca/farm_vehicle_{name}" not in registry.identifiers(), name


def test_the_t2121_chart_lines_are_no_longer_artifacts(registry: ArtifactRegistry) -> None:
    # Each vehicle's lines of Charts A to C are worked inside the capability, as on T2125.
    for name in (
        "list_price_limit_tax",
        "lease_charge_limit_tax",
        "lease_cost_limit_tax",
        "list_price_limit_with_tax",
        "lease_charge_limit_with_tax",
        "lease_cost_limit_with_tax",
        "total_expenses",
        "business_use_part",
        "interest_for_period",
        "available_interest",
        "lease_price_base",
        "lease_price_85_percent",
        "lease_charge_portion",
        "lease_charges_net",
        "lease_cost_portion",
        "leasing_cost",
    ):
        assert f"ca/fish_vehicle_{name}" not in registry.identifiers(), name


# --- the immediate expensing limit checks: a yes or no answer checked to be 0 or 1, and a
# business's own percentage checked against the total of column 3 (the forms are silent on both).


# --- Schedule 3 Part 1, flipped property: the answer to line 17905 and the nine tick boxes of line
# 17906 are the inputs (each a 0 or 1 count), and the flag the form exports is a count of 1 or 0
# that `ca/count_by_conditions` gives from the ten answers checked by `ca/yes_or_no_count`. The
# flag is not a printed line of the form; it is the form's answer to whether the unit is a flipped
# property.


# --- Form T2043 Chart B: the statement's starting amounts and the Chart B totals ----------


# --- Form T2125 statement lines: the T1 line each statement goes on ----------------------------
# Form T2125 "Report the net income amount from line 9946 on the applicable line of your income tax
# and benefit return as indicated below: business income on line 13500, professional income on line
# 13700, commission income on line 13900". The statement's code for that choice is a count (1
# business, 2 professional, 3 commission; the form names no codes). Each statement's net (line 9946)
# and gross (line 8299) go to the line of its code, as a routed export per line, and the T1 lines
# total the routed exports over the statements.


def _kind(registry: ArtifactRegistry, identifier: str) -> ArtifactKind[Any]:
    kind = registry.get(identifier)
    assert isinstance(kind, ArtifactKind), identifier
    return kind
