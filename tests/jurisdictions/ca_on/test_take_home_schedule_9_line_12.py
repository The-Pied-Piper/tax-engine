"""Schedule 9 (5000-S9, 2025) line 12: "Line 12: Line 10 plus line 11 =", read from its input."""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

PART = FEDERAL_FORMS / "schedule_9" / "schedule_9_line_12.yaml"


def test_line_12_is_one_sum_step_that_reads_the_blank_as_zero_and_rounds_to_the_cent() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca/schedule_9"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "12",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": ["ca/donations_and_gifts_line_12"]},
        "blank": {"ca/donations_and_gifts_line_12": "0"},
        "produces": {"output": "ca/donations_and_gifts_amount_line_12"},
    }
