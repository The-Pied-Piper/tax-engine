"""Schedule 9 (5000-S9, 2025): the form's declaration and exports.

The form is split from the T1 forms so the provincial forms can import it without a loop. It
exports lines 13 and 14, which AB428, MB428, NL428, ON428 and SK428 total as record lists.
"""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

PART = FEDERAL_FORMS / "schedule_9" / "schedule_9.yaml"


def test_the_form_is_required_has_its_printed_title_and_exports_lines_13_and_14() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {
        "name": "ca/schedule_9",
        "title": "Schedule 9: Donations and Gifts",
        "required": True,
        "exports": ["ca/donations_and_gifts_line_13", "ca/donations_and_gifts_line_14"],
    }
    assert part["capabilities"] == []
