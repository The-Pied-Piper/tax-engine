"""ON428 (2025) line 82's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt):
"Line 82: Provincial foreign tax credit (complete Form T2036)" is the line's basis in the
take-home part. A salary-only caller has no foreign income, so a request that leaves the line out
is read as blank, and the line 83 part reads that blank as 0.

The part is loaded from the test data folder under a test-local header, as the take-home header is
another part's.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_on.catalog import ON428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_82
from tax_engine.registrations import artifact_kinds
from tests.manifest_support import input_named, real_manifest

PRINTED_BASIS = "Line 82: Provincial foreign tax credit (complete Form T2036)"


def test_a_request_that_leaves_out_line_82_is_read_as_blank() -> None:
    kinds = artifact_kinds()
    identifier = ON428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_82.identifier
    declaration = input_named(real_manifest("CA-ON"), identifier)
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
