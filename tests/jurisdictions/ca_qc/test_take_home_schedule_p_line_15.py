"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 15, "Wage Earner Protection Program (WEPP)
payments (line 154, point 12)", as the Quebec take-home manifest wires it: an optional input
that a salary-only caller does not give, so the line has no step. A blank is read as 0 by line
18, which adds it."""

from __future__ import annotations

import yaml

from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS


def test_the_input_is_optional_and_blank_by_default() -> None:
    part = yaml.safe_load(
        (QUEBEC_PARTS / "schedule_p_line_15_inputs.yaml").read_text(encoding="utf-8")
    )

    assert "capabilities" not in part
    (declared,) = part["inputs"]
    assert (declared["name"], declared["required"], declared["default"]) == (
        "ca-qc/schedule_p_wepp_payments_line_15",
        False,
        None,
    )
