"""Schedule 9 (5000-S9, 2025) line 13: "Enter whichever is less: amount from line 12 or $200."

The $200 is a printed figure, so it is a dataset claimed whole by a step of its own (as Schedule 6
line 21 claims its $1,633), and line 13 is the lesser of line 12 and that figure. The figures
through the engine are in `tests/jurisdictions/test_donations_and_gifts_line_12_taken_once.py`.
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


def test_the_printed_200_is_claimed_whole_from_its_dataset() -> None:
    assert _steps("schedule_9_line_13_limit.yaml") == [
        {
            "name": "core/credit_amount",
            "title": "Maximum amount",
            "reference": "13",
            "unit": "ca/cad",
            "params": {"amount": LIMIT},
            "produces": {"output": LIMIT},
        }
    ]


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
