"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 14, "Total of lines 22 through 26.1 of Schedule
L. Do not include losses.", as the Quebec take-home manifest wires it: an optional input that a
salary-only caller does not give, so the line has no step. A blank is read as 0 by line 18,
which adds it."""

from __future__ import annotations

from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative
from tests.manifest_support import input_named, real_manifest

PART = "schedule_p_line_14_inputs.yaml"
NAME = "ca-qc/schedule_p_schedule_l_income_line_14"
PRINTED_BASIS = "Total of lines 22 through 26.1 of Schedule L. Do not include losses."


def test_a_request_that_leaves_out_line_14_is_read_as_blank() -> None:
    declaration = input_named(real_manifest("CA-QC"), NAME)
    default = declaration.default_artifact(quebec_kinds().kind(NAME))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_line_14_input_kind_is_registered_and_non_negative() -> None:
    assert non_negative(quebec_kinds().kind(NAME)) is True
