"""Schedule 6 (5000-S6) line 11, as a total of two T1 lines: the part has no input of its own.

The T1 UCCB and RDSP form exports the two lines; another form reads an export only as a record
list, so each is totalled by core/record_total and the printed total is one core/sum of the two,
in line order, rounded to the cent by the dataset's rule. A salary-only caller has neither, so the
total is 0.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca

PART = (
    Path(tax_engine.jurisdictions.ca.__file__).parent
    / "forms"
    / "schedule_6"
    / "schedule_6_line_11.yaml"
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
    assert part["form"] == {"name": "ca/schedule_6"}
    first, second, total = part["capabilities"]
    assert [first["name"], second["name"], total["name"]] == [
        "core/record_total",
        "core/record_total",
        "core/sum",
    ]
    assert (first["consumes"]["records"], second["consumes"]["records"]) == EXPORTS
    assert total["reference"] == "11"
    assert total["params"] == {"rounding": "ca/cent_rounding"}
    assert total["consumes"]["parts"] == [
        first["produces"]["output"],
        second["produces"]["output"],
    ]
    assert "blank" not in total
    assert total["produces"] == {"output": "ca/uccb_and_rdsp_income"}
