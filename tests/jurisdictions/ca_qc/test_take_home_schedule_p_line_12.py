"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 12, "Amount from line 107 of the return", as the
Quebec take-home manifest wires it: a copy of TP-1 line 107, an optional input of the return, so the
line has no step. A blank is read as 0 by line 18, which adds it."""

from __future__ import annotations

import yaml

from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS


def test_the_input_is_optional_and_blank_by_default() -> None:
    part = yaml.safe_load(
        (QUEBEC_PARTS / "schedule_p_line_12_inputs.yaml").read_text(encoding="utf-8")
    )

    assert "capabilities" not in part
    (declared,) = part["inputs"]
    assert (declared["name"], declared["required"], declared["default"]) == (
        "ca-qc/tp1_line_107",
        False,
        None,
    )
