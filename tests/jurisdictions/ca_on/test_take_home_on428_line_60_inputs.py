"""ON428 (2025) line 60's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 60 and line 61540: Enter
whichever is less: amount from line 58 or line 59." A salary-only caller has no Ontario minimum tax
carryover, so a request that leaves the line out is read as blank, and the line 61 part reads that
blank as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_on.catalog import ON428_MINIMUM_TAX_CARRYOVER_LINE_60
from tax_engine.registrations import artifact_kinds
from tests.manifest_support import input_named, real_manifest

PRINTED_BASIS = "Line 60 and line 61540: Enter whichever is less: amount from line 58 or line 59"


def test_a_request_that_leaves_out_line_60_is_read_as_blank() -> None:
    kinds = artifact_kinds()
    identifier = ON428_MINIMUM_TAX_CARRYOVER_LINE_60.identifier
    declaration = input_named(real_manifest("CA-ON"), identifier)
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
