"""The Newfoundland and Labrador form `ca-nl/nl428_worksheet` (Worksheet NL428, CRA 5001-D, 2025)
and its exports.

Only the sections "Line 58080 - Age amount" and "Line 58440 - Disability amount for self" are
built. The age amount's line 7 reads (CRA 5001-D-25e.txt): "Line 7: Line 1 minus line 6 (if
negative, enter "0") Enter this amount on line 58080 of your Form NL428." The disability amount's
line 7 reads: "Line 7: Line 1 plus line 6 Enter this amount on line 58440 of your Form NL428.
(maximum $10,981)". The part file declares the form and those two exports; it has no capabilities,
no dataset and no supplies. The other sections are skipped blocks whose NL428 lines are optional
inputs.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.catalog
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_nl.support import newfoundland_kinds
from tests.kinds import non_negative

NL_ROOT = Path(tax_engine.jurisdictions.ca_nl.__file__).parent
PART = NL_ROOT / "manifests" / "2025" / "nl428_worksheet.yaml"
LINE_7 = "ca-nl/worksheet_nl428_age_amount_line_7"
DISABILITY_LINE_7 = "ca-nl/worksheet_nl428_disability_self_line_7"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in the Newfoundland and
    Labrador catalog."""
    path = Path(tax_engine.jurisdictions.ca_nl.catalog.__file__)
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

    assert form["name"] == "ca-nl/nl428_worksheet"
    assert form["title"] == "Worksheet NL428"
    assert form["required"] is True


def test_the_form_exports_the_age_maximum_and_the_two_line_7_amounts() -> None:
    assert _part()["form"]["exports"] == [
        "ca-nl/worksheet_nl428_age_amount_maximum_line_1",
        LINE_7,
        DISABILITY_LINE_7,
    ]


def test_the_part_declares_no_capabilities_and_no_supplies() -> None:
    part = _part()

    assert part["capabilities"] == []
    assert "supplies" not in part["form"]


def test_the_line_7_kind_is_registered_in_the_newfoundland_and_labrador_namespace() -> None:
    kind = newfoundland_kinds().kind(LINE_7)

    assert kind.identifier == LINE_7
    assert LINE_7.startswith("ca-nl/")


def test_the_line_7_kind_is_a_non_negative_amount() -> None:
    kind = newfoundland_kinds().kind(LINE_7)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_line_7_kind_rejects_a_negative_amount() -> None:
    kind = newfoundland_kinds().kind(LINE_7)

    with pytest.raises(NegativeArtifactError):
        Artifact(kind, Decimal("-0.01"))


def test_the_line_7_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(LINE_7))

    assert "Worksheet NL428" in doc
    assert "line 7" in doc
    assert (
        '"Line 7: Line 1 minus line 6 (if negative, enter "0") Enter this amount on line '
        '58080 of your Form NL428."'
    ) in doc


def test_the_disability_line_7_kind_is_a_non_negative_amount_in_the_namespace() -> None:
    kind = newfoundland_kinds().kind(DISABILITY_LINE_7)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert DISABILITY_LINE_7.startswith("ca-nl/")


def test_the_disability_line_7_kind_rejects_a_negative_amount() -> None:
    kind = newfoundland_kinds().kind(DISABILITY_LINE_7)

    with pytest.raises(NegativeArtifactError):
        Artifact(kind, Decimal("-0.01"))


def test_the_disability_line_7_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(DISABILITY_LINE_7))

    assert "Worksheet NL428" in doc
    assert (
        '"Line 7: Line 1 plus line 6 Enter this amount on line 58440 of your Form NL428. '
        '(maximum $10,981)"'
    ) in doc
