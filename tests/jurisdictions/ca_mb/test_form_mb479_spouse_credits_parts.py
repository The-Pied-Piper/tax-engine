"""The MB479 (2025) line 9 to 12 part files: each part's shape.

Form text (Form MB479, CRA 5007-TC, 5007-tc-25e.txt): line 9 "Basic credit for spouse or common-law
partner Claim $195", line 10 "Age credit for spouse or common-law partner ... Claim $113", line 11
"Disability credit for spouse or common-law partner Claim $113" and line 12 "Add lines 9 to 11."
See `end_to_end/test_mb479_spouse_credits.py` for the figures through the engine. Lines 9 to 11 are
optional inputs; line 12 is one sum step.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_mb.support import manitoba_kinds
from tests.kinds import non_negative

MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
KINDS = {
    "ca-mb/mb479_basic_credit_spouse_line_9": "MB479_BASIC_CREDIT_SPOUSE_LINE_9",
    "ca-mb/mb479_age_credit_spouse_line_10": "MB479_AGE_CREDIT_SPOUSE_LINE_10",
    "ca-mb/mb479_disability_credit_spouse_line_11": "MB479_DISABILITY_CREDIT_SPOUSE_LINE_11",
    "ca-mb/mb479_spouse_credits_line_12": "MB479_SPOUSE_CREDITS_LINE_12",
}


def _load(name: str) -> dict[str, Any]:
    part = yaml.safe_load((MB_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_input_part_declares_only_lines_9_to_11_as_optional_blank_inputs() -> None:
    part = _load("mb479_line_12_inputs.yaml")

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-mb/mb479"}
    assert [item["name"] for item in part["inputs"]] == list(KINDS)[:3]
    for declared in part["inputs"]:
        assert declared["required"] is False
        assert declared["default"] is None


def test_line_12_is_one_sum_step_and_the_lump_input_is_gone() -> None:
    part = _load("mb479_line_12.yaml")
    inputs = [item["name"] for item in _load("mb479_line_17_inputs.yaml")["inputs"]]

    assert part["form"] == {"name": "ca-mb/mb479"}
    (step,) = part["capabilities"]
    assert step["name"] == "core/sum"
    assert step["reference"] == "12"
    assert step["produces"] == {"output": "ca-mb/mb479_spouse_credits_line_12"}
    assert "ca-mb/mb479_spouse_credits_line_12" not in inputs


@pytest.mark.parametrize(("identifier", "constant"), list(KINDS.items()))
def test_each_kind_is_a_registered_non_negative_decimal_amount_kind(
    identifier: str, constant: str
) -> None:
    kind = manitoba_kinds().kind(identifier)

    assert kind is getattr(mb_catalog, constant)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
