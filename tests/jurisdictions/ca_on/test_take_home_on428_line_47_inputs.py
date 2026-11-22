"""ON428 (2025) line 47's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 47: Amount from line 13 of your federal Schedule 9".
A request that leaves the line out is read as blank, and the step that reads it reads that blank
as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_on.catalog import ON428_DONATIONS_AMOUNT_LINE_47
from tax_engine.registrations import artifact_kinds
from tests.manifest_support import input_named, real_manifest

PRINTED_BASIS = "Line 47: Amount from line 13 of your federal Schedule 9"


def test_a_request_that_leaves_out_line_47_is_read_as_blank() -> None:
    kinds = artifact_kinds()
    identifier = ON428_DONATIONS_AMOUNT_LINE_47.identifier
    declaration = input_named(real_manifest("CA-ON"), identifier)
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
