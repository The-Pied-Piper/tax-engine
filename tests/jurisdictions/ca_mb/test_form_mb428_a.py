"""The Manitoba form `ca-mb/mb428_a` (Schedule MB428-A, CRA 5007-A, 2025) and its export.

Its line 12 reads (CRA 5007-a-25e.txt): "Line 12: Line 10 minus line 11 (if negative, enter "0")
Enter this amount on line 61470 of your Form MB428." The part file declares the form and that one
export; it has no capabilities, no dataset and no lines yet (those come with their own tickets).
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_mb.support import manitoba_kinds
from tests.kinds import non_negative

MB_ROOT = Path(tax_engine.jurisdictions.ca_mb.__file__).parent
PART = MB_ROOT / "manifests" / "2025" / "mb428_a.yaml"
LINE_12 = "ca-mb/mb428_a_family_tax_benefit_line_12"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in the Manitoba catalog."""
    path = Path(tax_engine.jurisdictions.ca_mb.catalog.__file__)
    body = ast.parse(path.read_text(encoding="utf-8")).body
    for statement, following in zip(body, body[1:], strict=False):
        if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
            continue
        constants = [each.value for each in statement.value.args if isinstance(each, ast.Constant)]
        if (
            identifier.rpartition("/")[2] in constants
            and isinstance(following, ast.Expr)
            and isinstance(following.value, ast.Constant)
        ):
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")


def test_the_part_declares_the_form_name_title_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == "ca-mb/mb428_a"
    assert form["title"] == "Schedule MB428-A: Manitoba Family Tax Benefit"
    assert form["required"] is True


def test_the_form_exports_only_the_family_tax_benefit_line_12() -> None:
    assert _part()["form"]["exports"] == [LINE_12]


def test_the_part_declares_no_capabilities_and_no_supplies() -> None:
    part = _part()

    assert part["capabilities"] == []
    assert "supplies" not in part["form"]


def test_the_line_12_kind_is_registered_in_the_manitoba_namespace() -> None:
    kind = manitoba_kinds().kind(LINE_12)

    assert kind.identifier == LINE_12
    assert LINE_12.startswith("ca-mb/")


def test_the_line_12_kind_is_a_non_negative_amount() -> None:
    kind = manitoba_kinds().kind(LINE_12)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_line_12_kind_rejects_a_negative_amount() -> None:
    kind = manitoba_kinds().kind(LINE_12)

    with pytest.raises(NegativeArtifactError):
        Artifact(kind, Decimal("-0.01"))


def test_the_line_12_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(LINE_12))

    assert "Schedule MB428-A" in doc
    assert "line 12" in doc
    assert (
        '"Line 12: Line 10 minus line 11 (if negative, enter "0") Enter this amount on line '
        '61470 of your Form MB428."'
    ) in doc
