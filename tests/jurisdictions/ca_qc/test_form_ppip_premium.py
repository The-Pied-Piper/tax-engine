"""The Quebec form `ca-qc/ppip_premium` (the PPIP premium) and the kind it exports: the PPIP
premiums paid, 5005-R line 91.

The part file names the form and its export; the inputs part and the line 91 part carry the input
and the capability. Quebec is not yet listed in the bundled package list, so the part is read as
YAML and the kind is taken from the Quebec package list in `support.py`, not from the engine.
"""

from __future__ import annotations

from typing import Any

import yaml

from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = QUEBEC_PARTS / "ppip_premium.yaml"
EXPORT = "ca-qc/ppip_premiums_paid"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_and_required_and_shares_the_return_title() -> None:
    form = _part()["form"]

    assert list(form) == ["name", "title", "required", "exports"]
    assert form["name"] == "ca-qc/ppip_premium"
    assert form["title"] == "T1 Income Tax and Benefit Return"
    assert form["required"] is True


def test_the_form_exports_line_91() -> None:
    assert EXPORT in _part()["form"]["exports"]


def test_the_form_supplies_nothing_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert "supplies" not in part["form"]
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_credits_parts_of_the_other_provinces() -> None:
    assert list(_part()) == ["form", "capabilities"]


def test_the_export_is_a_registered_non_negative_amount_kind() -> None:
    kinds = quebec_kinds()

    assert EXPORT in kinds.identifiers()
    kind = kinds.kind(EXPORT)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
