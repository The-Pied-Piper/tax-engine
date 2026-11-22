"""Schedule 9 (5000-S9, 2025) line 12's input: one optional amount, blank for a salary-only filer.

Lines 1 to 11 (the donation chart and the 75% net-income limits) feed nothing else the engine
uses, so line 12 is typed in once, as the form's own total of line 10 plus line 11.
"""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

PART = FEDERAL_FORMS / "schedule_9" / "schedule_9_line_12_inputs.yaml"


def test_line_12_is_one_optional_input_read_as_blank_when_left_out() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca/schedule_9"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": "ca/donations_and_gifts_line_12",
        "title": "Donations and gifts",
        "reference": "12",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": "Line 12: Line 10 plus line 11 =",
    }
