"""The Quebec form `ca-qc/solidarity_credit` (the solidarity tax credit) and the six kinds it
exports: the QST base amount, the living-alone amount, the two housing amounts and the reduction
threshold of Table C.9 of fiche 110201 (July 2026 to June 2027), and the credit after the
reduction, the yearly amount.

The part file names the form and its exports; the amounts part carries the capabilities. Quebec is
not yet listed in the bundled package list, so the part is read as YAML and the kinds are taken
from the Quebec package list in `support.py`, not from the engine.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = QUEBEC_PARTS / "solidarity_credit.yaml"

EXPORTS = [
    "ca-qc/solidarity_qst_base_amount",
    "ca-qc/solidarity_living_alone_amount",
    "ca-qc/solidarity_housing_single_amount",
    "ca-qc/solidarity_housing_multiple_amount",
    "ca-qc/solidarity_reduction_threshold",
    "ca-qc/solidarity_credit_after_reduction",
]


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_and_required() -> None:
    form = _part()["form"]

    assert list(form) == ["name", "title", "required", "exports"]
    assert form["name"] == "ca-qc/solidarity_credit"
    assert form["title"] == "Crédit d'impôt remboursable pour la solidarité"
    assert form["required"] is True


def test_the_form_exports_the_six_amounts_in_order() -> None:
    assert _part()["form"]["exports"] == EXPORTS


def test_the_form_supplies_nothing_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert "supplies" not in part["form"]
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_credits_parts_of_the_other_provinces() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert list(part) == ["form", "capabilities"]


@pytest.mark.parametrize("identifier", EXPORTS)
def test_each_export_is_a_registered_non_negative_amount_kind(identifier: str) -> None:
    kinds = quebec_kinds()

    assert identifier in kinds.identifiers()
    kind = kinds.kind(identifier)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
