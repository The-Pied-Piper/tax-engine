"""The MB479 (2025) line 14 to 16 part files: each part's shape.

Form text (Form MB479, CRA 5007-TC, 5007-tc-25e.txt): line 14 "Number of disability claims ...
multiplied by $113 =", line 15 "Number of disabled dependants ... multiplied by $62 =" and line 16
"Number of dependent children ... multiplied by $26 =". See
`end_to_end/test_mb479_credits_14_to_16.py` for the figures through the engine. Each line is an
optional count input (box A), the printed amount (a dataset figure) and one product step (box B).
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
FORM = {"name": "ca-mb/mb479"}
LINES = {
    "14": ("disability_claims_number", "disability_credit_amount_line_14", "disability_credit"),
    "15": (
        "disabled_dependants_number",
        "disabled_dependants_credit_amount_line_15",
        "disabled_dependants_credit",
    ),
    "16": (
        "dependent_children_number",
        "dependent_children_credit_amount_line_16",
        "dependent_children_credit",
    ),
}


def _load(name: str) -> dict[str, Any]:
    part = yaml.safe_load((MB_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


@pytest.mark.parametrize("line", LINES)
def test_the_product_is_one_multiply_step_on_the_form(line: str) -> None:
    number, amount, out = LINES[line]

    assert _load(f"mb479_line_{line}.yaml") == {
        "form": FORM,
        "capabilities": [
            {
                "name": "core/multiply",
                "reference": f"{line} box B",
                "unit": "ca/cad",
                "params": {"rounding": "ca-mb/cent_rounding"},
                "consumes": {
                    "multiplicand": f"ca-mb/mb479_{number}_line_{line}",
                    "multiplier": f"ca-mb/{amount}",
                },
                "produces": {"output": f"ca-mb/mb479_{out}_line_{line}"},
            }
        ],
    }


AMOUNT_TITLES = {
    "14": "Amount for each disability claim",
    "15": "Amount for each disabled dependant",
    "16": "Amount for each dependent child",
}


@pytest.mark.parametrize("line", LINES)
def test_the_printed_amount_is_one_credit_amount_step(line: str) -> None:
    _, amount, _ = LINES[line]

    assert _load(f"mb479_line_{line}_amount.yaml") == {
        "form": FORM,
        "capabilities": [
            {
                "name": "core/credit_amount",
                "title": AMOUNT_TITLES[line],
                "unit": "ca/cad",
                "params": {"amount": f"ca-mb/{amount}"},
                "produces": {"output": f"ca-mb/{amount}"},
            }
        ],
    }


@pytest.mark.parametrize("line", LINES)
def test_the_input_part_declares_only_the_optional_number_defaulting_to_0(line: str) -> None:
    number, _, _ = LINES[line]
    part = _load(f"mb479_line_{line}_inputs.yaml")

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-mb/mb479"}
    (declared,) = part["inputs"]
    assert declared["name"] == f"ca-mb/mb479_{number}_line_{line}"
    assert declared["reference"] == f"{line} box A"
    assert declared["required"] is False
    assert declared["default"] == "0"
    assert declared["unit"] == "ca/cad"


def test_the_old_product_inputs_are_gone_from_the_line_17_inputs_part() -> None:
    names = [item["name"] for item in _load("mb479_line_17_inputs.yaml")["inputs"]]

    assert names == ["ca-mb/mb479_eligible_dependant_credit_line_13"]


@pytest.mark.parametrize("line", LINES)
def test_each_kind_is_a_registered_non_negative_decimal_amount_kind(line: str) -> None:
    number, amount, out = LINES[line]
    declared = {
        f"ca-mb/mb479_{number}_line_{line}": getattr(
            mb_catalog, f"MB479_{number.upper()}_LINE_{line}"
        ),
        f"ca-mb/{amount}": getattr(mb_catalog, f"MB479_{out.upper()}_AMOUNT_LINE_{line}"),
        f"ca-mb/mb479_{out}_line_{line}": getattr(mb_catalog, f"MB479_{out.upper()}_LINE_{line}"),
    }

    for identifier, constant in declared.items():
        kind = manitoba_kinds().kind(identifier)
        assert kind is constant
        assert isinstance(kind, AmountKind)
        assert kind.value_type is Decimal
        assert non_negative(kind)
