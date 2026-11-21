"""BC479 (5010-TC) line 4, as a total of two T1 lines: the part has no input of its own.

The T1 UCCB and RDSP form exports the two lines; another form reads an export only as a record
list, so each is totalled by core/record_total and the printed total is one core/sum of the two,
in line order, rounded to the cent by the dataset's rule. A salary-only caller has neither, so the
total is 0.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc

PART = (
    Path(tax_engine.jurisdictions.ca_bc.__file__).parent
    / "manifests"
    / "2025"
    / "bc479_line_4.yaml"
)
EXPORTS = (
    "ca/t1_uccb_rdsp.uccb_income_line_11700",
    "ca/t1_uccb_rdsp.rdsp_income_line_12500",
)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_two_record_totals_and_a_sum_with_no_input_of_its_own() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc479"}
    first, second, total = part["capabilities"]
    assert [first["name"], second["name"], total["name"]] == [
        "core/record_total",
        "core/record_total",
        "core/sum",
    ]
    assert (first["consumes"]["records"], second["consumes"]["records"]) == EXPORTS
    assert total["reference"] == "4"
    assert total["params"] == {"rounding": "ca-bc/cent_rounding"}
    assert total["consumes"]["parts"] == [
        first["produces"]["output"],
        second["produces"]["output"],
    ]
    assert "blank" not in total
    assert total["produces"] == {"output": "ca-bc/bc479_uccb_rdsp_income_line_4"}
