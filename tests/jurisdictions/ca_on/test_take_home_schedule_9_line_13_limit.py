"""Schedule 9 (5000-S9, 2025) line 13, the printed $200 ("Enter whichever is less ... $200.").

The $200 is a printed figure, so it is a dataset claimed whole by a step of its own, as Schedule 6
line 21 claims its $1,633. Line 13 takes the lesser of it and line 12.
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
