"""The Alberta form `ca-ab/worksheet_ab428` (Worksheet AB428, CRA 5009-D, 2025) and its export.

Only the section "Line 61545 - Alberta supplemental tax credit" is built. Its line 9 reads (CRA
5009-d-25e.txt): "Line 9: Line 7 multiplied by the percentage from line 8 enter this amount on line
61545 of your Form AB428." The part file declares the form and that one export; it has no
capabilities, no dataset and no lines yet (those come with their own tickets).
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_ab.catalog
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ab.support import alberta_kinds
from tests.kinds import non_negative

AB_ROOT = Path(tax_engine.jurisdictions.ca_ab.__file__).parent
PART = AB_ROOT / "manifests" / "2025" / "worksheet_ab428.yaml"
LINE_9 = "ca-ab/worksheet_ab428_supplemental_credit_line_9"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in the Alberta catalog."""
    path = Path(tax_engine.jurisdictions.ca_ab.catalog.__file__)
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

    assert form["name"] == "ca-ab/worksheet_ab428"
    assert form["title"] == "Worksheet AB428"
    assert form["required"] is True


def test_the_form_exports_only_the_supplemental_credit_line_9() -> None:
    assert _part()["form"]["exports"] == [LINE_9]


def test_the_part_declares_no_capabilities_and_no_supplies() -> None:
    part = _part()

    assert part["capabilities"] == []
    assert "supplies" not in part["form"]


def test_the_line_9_kind_is_registered_in_the_alberta_namespace() -> None:
    kind = alberta_kinds().kind(LINE_9)

    assert kind.identifier == LINE_9
    assert LINE_9.startswith("ca-ab/")


def test_the_line_9_kind_is_a_non_negative_amount() -> None:
    kind = alberta_kinds().kind(LINE_9)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_line_9_kind_rejects_a_negative_amount() -> None:
    kind = alberta_kinds().kind(LINE_9)

    with pytest.raises(NegativeArtifactError):
        Artifact(kind, Decimal("-0.01"))


def test_the_line_9_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(LINE_9))

    assert "Worksheet AB428" in doc
    assert "line 9" in doc
    assert (
        '"Line 9: Line 7 multiplied by the percentage from line 8 enter this amount on line '
        '61545 of your Form AB428."'
    ) in doc
