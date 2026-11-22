"""Schedule 9 (5000-S9, 2025) line 13: "Enter whichever is less: amount from line 12 or $200."

Line 13 is the lesser of line 12 and the printed $200 (the dataset step is in
`test_take_home_schedule_9_line_13_limit.py`). The figures through the engine are in
`tests/jurisdictions/test_donations_and_gifts_line_12_taken_once.py`.
"""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

FOLDER = FEDERAL_FORMS / "schedule_9"
LIMIT = "ca/donations_and_gifts_line_13_limit"


def _steps(name: str) -> list[dict[str, Any]]:
    part: Any = yaml.safe_load((FOLDER / name).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca/schedule_9"}
    steps: list[dict[str, Any]] = part["capabilities"]
    return steps


def test_line_13_is_the_lesser_of_line_12_and_the_printed_200() -> None:
    assert _steps("schedule_9_line_13.yaml") == [
        {
            "name": "core/lesser_of",
            "reference": "13",
            "unit": "ca/cad",
            "consumes": {"amounts": ["ca/donations_and_gifts_amount_line_12", LIMIT]},
            "produces": {"output": "ca/donations_and_gifts_line_13"},
        }
    ]
