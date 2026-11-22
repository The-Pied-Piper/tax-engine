"""Schedule 9 (5000-S9, 2025) line 14, printed "Line 12 minus line 13 =", from lines 12 and 13."""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

PART = FEDERAL_FORMS / "schedule_9" / "schedule_9_line_14.yaml"


def test_line_14_is_line_12_less_line_13_rounded_to_the_cent() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca/schedule_9"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract",
        "reference": "14",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {
            "amount": "ca/donations_and_gifts_amount_line_12",
            "less": "ca/donations_and_gifts_line_13",
        },
        "produces": {"output": "ca/donations_and_gifts_line_14"},
    }
