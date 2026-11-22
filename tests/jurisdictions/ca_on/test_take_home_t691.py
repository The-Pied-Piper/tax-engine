"""The Form T691 declaration: its name, title and the one line it exports."""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

PART = FEDERAL_FORMS / "t691" / "t691.yaml"


def test_the_form_is_required_has_the_t691_title_and_exports_part_7_line_14() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {
        "name": "ca/t691",
        "title": "Alternative Minimum Tax",
        "required": True,
        "exports": ["ca/t691_additional_taxes_for_minimum_tax_carryover_line_14"],
    }
    assert part["capabilities"] == []
