"""BC428 (2025) manifest part `bc428_line_50.yaml`, its form name and steps pinned.

The part's own header comment states the printed line; the figures it gives are asserted end
to end in `end_to_end/` and the neighbouring line tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tests.jurisdictions.ca_bc.support import british_columbia_kinds

PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests/2025/bc428_line_50.yaml"
OUTPUTS = ["ca-bc/bc428_medical_expenses_limited_amount_line_50"]


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_these_steps() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    assert part["capabilities"] == [
        {
            "name": "core/capped_amount",
            "reference": "50",
            "unit": "ca/cad",
            "params": {"cap": "ca-bc/medical_expense_dollar_limit"},
            "consumes": {"base": "ca-bc/bc428_medical_expenses_rate_amount_line_49"},
            "produces": {"output": "ca-bc/bc428_medical_expenses_limited_amount_line_50"},
        }
    ]


def test_each_output_is_a_registered_kind() -> None:
    kinds = british_columbia_kinds()

    for output in OUTPUTS:
        assert output in kinds.identifiers()
