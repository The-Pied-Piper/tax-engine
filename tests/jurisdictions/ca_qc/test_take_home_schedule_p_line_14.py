"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 14, "Total of lines 22 through 26.1 of Schedule
L. Do not include losses.", as the Quebec take-home manifest wires it: an optional input that a
salary-only caller does not give, so the line has no step. A blank is read as 0 by line 18,
which adds it."""

from __future__ import annotations

import yaml

from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS


def test_the_input_is_optional_and_blank_by_default() -> None:
    part = yaml.safe_load(
        (QUEBEC_PARTS / "schedule_p_line_14_inputs.yaml").read_text(encoding="utf-8")
    )

    assert "capabilities" not in part
    (declared,) = part["inputs"]
    assert (declared["name"], declared["required"], declared["default"]) == (
        "ca-qc/schedule_p_schedule_l_income_line_14",
        False,
        None,
    )
