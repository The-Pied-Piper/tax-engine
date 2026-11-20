"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 15, "Wage Earner Protection Program (WEPP)
payments (line 154, point 12)", as the Quebec take-home manifest wires it: an optional input
that a salary-only caller does not give, so the line has no step. A blank is read as 0 by line
18, which adds it."""

from __future__ import annotations

from pathlib import Path

from tests.jurisdictions.ca_qc.support import quebec_kinds, schedule_p_input
from tests.kinds import non_negative

PART = "schedule_p_line_15_inputs.yaml"
NAME = "ca-qc/schedule_p_wepp_payments_line_15"
PRINTED_BASIS = "Wage Earner Protection Program (WEPP) payments (line 154, point 12)"


def test_a_request_that_leaves_out_line_15_is_read_as_blank(tmp_path: Path) -> None:
    declaration = schedule_p_input(tmp_path, PART, NAME)
    default = declaration.default_artifact(quebec_kinds().kind(NAME))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_line_15_input_kind_is_registered_and_non_negative() -> None:
    assert non_negative(quebec_kinds().kind(NAME)) is True
