"""The `_checked` record lists of the CCA table's Area A rows, Forms T776, T2125, T2042 and T2121:
the rows that passed `ca/cca_vehicle_additions_checks` (a Class 10.1 vehicle's additions are not
more than its limit with tax), passed on unchanged, one list for each business type and for rental.

Each kind holds the fields of its `classes` list in the same order (the checks pass the rows on
unchanged, and the vehicle fields stay until the proceeds adjustment), is a record list, and is
registered under its identifier in the snapshot (`catalog_snapshot.py`).
"""

from __future__ import annotations

import ast
from pathlib import Path

import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLASSES,
    BUSINESS_CCA_CLASSES_ADJUSTED,
    BUSINESS_CCA_CLASSES_CHECKED,
    CCA_SOLD_ZEPVS,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
    FARM_CCA_CLASSES,
    FARM_CCA_CLASSES_CHECKED,
    FISH_CCA_CLASSES,
    FISH_CCA_CLASSES_CHECKED,
    RENTAL_CCA_CLASSES,
    RENTAL_CCA_CLASSES_CHECKED,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED

# (the checked kind, the classes kind it checks, the form named in its docstring)
CHECKED_LISTS = (
    (RENTAL_CCA_CLASSES_CHECKED, RENTAL_CCA_CLASSES, "T776"),
    (BUSINESS_CCA_CLASSES_CHECKED, BUSINESS_CCA_CLASSES, "T2125"),
    (FARM_CCA_CLASSES_CHECKED, FARM_CCA_CLASSES, "T2042"),
    (FISH_CCA_CLASSES_CHECKED, FISH_CCA_CLASSES, "T2121"),
)


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in a catalog module (its
    name is a constant of the declaration's call, which may take the catalog first)."""
    folder = Path(tax_engine.jurisdictions.ca.catalog.__file__).parent
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


def test_the_checked_lists_are_registered_under_their_identifiers(
    registry: ArtifactRegistry,
) -> None:
    for kind, _, _ in CHECKED_LISTS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_checked_lists_are_in_the_snapshot_and_in_the_record_list_group() -> None:
    for kind, _, _ in CHECKED_LISTS:
        assert kind.identifier in REGISTERED, kind.identifier
        assert kind.identifier in RECORD_LISTS, kind.identifier
        assert kind.identifier not in COUNTS, kind.identifier


def test_the_checked_identifiers_are_the_rental_business_farm_and_fish_names() -> None:
    assert RENTAL_CCA_CLASSES_CHECKED.identifier == "ca/rental_cca_classes_checked"
    assert BUSINESS_CCA_CLASSES_CHECKED.identifier == "ca/business_cca_classes_checked"
    assert FARM_CCA_CLASSES_CHECKED.identifier == "ca/farm_cca_classes_checked"
    assert FISH_CCA_CLASSES_CHECKED.identifier == "ca/fish_cca_classes_checked"


def test_each_checked_list_is_a_record_list_kind_of_no_negative_values() -> None:
    for kind, _, _ in CHECKED_LISTS:
        assert isinstance(kind, RecordListKind), kind.identifier
        assert kind.non_negative is False, kind.identifier


def test_each_checked_list_holds_the_fields_of_the_classes_it_checks_in_the_same_order() -> None:
    # The checks pass the rows on unchanged: the same fields, the vehicle's year, cost, assistance
    # and sold vehicles included (the proceeds adjustment, which takes them, comes after).
    for kind, classes, _ in CHECKED_LISTS:
        assert kind.fields == classes.fields, kind.identifier


def test_the_checked_lists_keep_the_vehicle_fields_the_adjusted_lists_leave_out() -> None:
    vehicle_fields = (
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_SOLD_ZEPVS,
    )
    for kind, _, _ in CHECKED_LISTS:
        assert set(vehicle_fields) <= set(kind.fields), kind.identifier
    assert set(vehicle_fields).isdisjoint(BUSINESS_CCA_CLASSES_ADJUSTED.fields)


def test_each_checked_list_docstring_names_its_form_and_the_checks() -> None:
    for kind, _, form in CHECKED_LISTS:
        text = squashed(docstring_of(kind.identifier))
        assert form in text, kind.identifier
        assert "Class 10.1" in text, kind.identifier
        assert "checked" in text.lower(), kind.identifier
