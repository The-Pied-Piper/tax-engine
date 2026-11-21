"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 22, "Amount included in one of the above
sources of income and entitling you to a deduction on line 293 of your return", as the Quebec
take-home manifest wires it: an optional input that a salary-only caller does not give, so the line
has no step. A blank is read as 0 by line 29, which subtracts it."""

from __future__ import annotations

from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative
from tests.manifest_support import input_named, real_manifest

PART = "schedule_p_line_22_inputs.yaml"
NAME = "ca-qc/schedule_p_deductible_income_line_22"
PRINTED_BASIS = (
    "Amount included in one of the above sources of income and entitling you to a deduction on "
    "line 293 of your return"
)


def test_a_request_that_leaves_out_line_22_is_read_as_blank() -> None:
    declaration = input_named(real_manifest("CA-QC"), NAME)
    default = declaration.default_artifact(quebec_kinds().kind(NAME))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_line_22_input_kind_is_registered_and_non_negative() -> None:
    assert non_negative(quebec_kinds().kind(NAME)) is True
