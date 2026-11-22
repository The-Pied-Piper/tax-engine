"""The Manitoba form `ca-mb/worksheet_mb428` (Worksheet MB428, CRA 5007-D, 2025) and its exports.

Only the section "Line 58040 - Basic personal amount" is built. Its line 9 reads (CRA 5007-D):
"Line 9: Line 1 minus line 8 (if negative, enter "0") Enter this amount on line 58040 of your Form
MB428." The part file declares the form and its exports: line 9, which Form MB428 reads, and lines
5, 7 and 8 ("Line 5: Income threshold 200,000.00", "Line 7: Base amount 15,780.00", "Line 8: Line 6
multiplied by line 7 = ^"), which the return summary reads for the slope of the basic personal
amount's phase-out in the marginal tax rate. It has no capabilities of its own, no dataset and no
supplies (the lines have their own parts).
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
PART = MB_ROOT / "manifests" / "2025" / "worksheet_mb428.yaml"
LINE_5 = "ca-mb/worksheet_mb428_line_5"
LINE_7 = "ca-mb/worksheet_mb428_line_7"
LINE_8 = "ca-mb/worksheet_mb428_line_8"
LINE_9 = "ca-mb/worksheet_mb428_basic_personal_amount_line_9"


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

    assert form["name"] == "ca-mb/worksheet_mb428"
    assert form["title"] == "Worksheet MB428"
    assert form["required"] is True


def test_the_form_exports_lines_5_7_8_and_9() -> None:
    assert _part()["form"]["exports"] == [LINE_5, LINE_7, LINE_8, LINE_9]


@pytest.mark.parametrize("identifier", [LINE_5, LINE_7, LINE_8])
def test_the_other_exported_lines_are_registered_non_negative_amounts(identifier: str) -> None:
    kind = manitoba_kinds().kind(identifier)

    assert kind.identifier == identifier
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_part_declares_no_capabilities_and_no_supplies() -> None:
    part = _part()

    assert part["capabilities"] == []
    assert "supplies" not in part["form"]


def test_the_line_9_kind_is_registered_in_the_manitoba_namespace() -> None:
    kind = manitoba_kinds().kind(LINE_9)

    assert kind.identifier == LINE_9
    assert LINE_9.startswith("ca-mb/")


def test_the_line_9_kind_is_a_non_negative_amount() -> None:
    kind = manitoba_kinds().kind(LINE_9)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_line_9_kind_rejects_a_negative_amount() -> None:
    kind = manitoba_kinds().kind(LINE_9)

    with pytest.raises(NegativeArtifactError):
        Artifact(kind, Decimal("-0.01"))


def test_the_line_9_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(LINE_9))

    assert "Worksheet MB428" in doc
    assert "line 9" in doc
    assert (
        '"Line 9: Line 1 minus line 8 (if negative, enter "0") Enter this amount on line 58040 '
        'of your Form MB428."'
    ) in doc
