"""BC479 (2025) manifest part `bc479_line_20.yaml`, its form name and steps pinned.

The part's own header comment states the printed line; the figures it gives are asserted end
to end in `end_to_end/` and the neighbouring line tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tests.jurisdictions.ca_bc.support import british_columbia_kinds

PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests/2025/bc479_line_20.yaml"
OUTPUTS = [
    "ca-bc/bc479_venture_capital_credit_sum_line_20",
    "ca-bc/bc479_venture_capital_credit_line_20",
]


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_these_steps() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc479"}
    assert part["capabilities"] == [
        {
            "name": "core/sum",
            "title": "Line 17 plus line 18",
            "unit": "ca/cad",
            "params": {"rounding": "ca-bc/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-bc/bc479_venture_capital_unused_credit_line_17",
                    "ca-bc/bc479_venture_capital_credit_line_18",
                ]
            },
            "blank": {
                "ca-bc/bc479_venture_capital_unused_credit_line_17": "0",
                "ca-bc/bc479_venture_capital_credit_line_18": "0",
            },
            "produces": {"output": "ca-bc/bc479_venture_capital_credit_sum_line_20"},
        },
        {
            "name": "core/at_most",
            "title": "Venture capital tax credit, lines 17 and 18",
            "reference": "20",
            "unit": "ca/cad",
            "consumes": {
                "amount": "ca-bc/bc479_venture_capital_credit_sum_line_20",
                "bound": "ca-bc/bc479_venture_capital_credit_line_20_maximum",
            },
            "produces": {"output": "ca-bc/bc479_venture_capital_credit_line_20"},
        },
    ]


def test_each_output_is_a_registered_kind() -> None:
    kinds = british_columbia_kinds()

    for output in OUTPUTS:
        assert output in kinds.identifiers()
