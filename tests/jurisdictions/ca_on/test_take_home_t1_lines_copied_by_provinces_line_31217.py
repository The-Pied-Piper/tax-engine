"""T1 line 31217 part of the lines the provinces copy: one sum step reading the blank as 0."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS
from tests.kinds import bundled_kinds, non_negative

T1 = FEDERAL_FORMS / "t1_lines_copied_by_provinces"

LINE = "31217"
NAME = "ca/ei_premiums_on_self_employment"
OUTPUT = "ca/ei_premiums_on_self_employment_line_31217"
BASIC = (
    "Line 89 and line 31217: on self-employment and other eligible earnings (complete Schedule 13)"
)
TITLE = "Employment insurance premiums on self-employment and other eligible earnings"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_t1_line_is_one_sum_step_that_reads_its_blank_as_zero() -> None:
    part = _part(T1 / f"t1_lines_copied_by_provinces_line_{LINE}.yaml")

    assert part["form"] == {"name": "ca/t1_lines_copied_by_provinces"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": TITLE,
        "reference": LINE,
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": [NAME]},
        "blank": {NAME: "0"},
        "produces": {"output": OUTPUT},
    }


def test_the_exported_line_is_a_registered_non_negative_amount_kind() -> None:
    # Non-negative: premiums are never below nothing, and the form prints no sign to enter.
    kind = bundled_kinds().kind(OUTPUT)

    assert kind.identifier == OUTPUT
    assert non_negative(kind) is True
