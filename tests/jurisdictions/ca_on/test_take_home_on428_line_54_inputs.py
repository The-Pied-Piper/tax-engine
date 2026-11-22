"""ON428 (2025) line 54's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 54 and line 61510: Ontario tax
on split income (complete Form T1206)" is the line's basis in the take-home part. A caller with no
split income leaves the line out, so the request is read as blank, and the line 55 part reads that
blank as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_on.catalog import ON428_TAX_ON_SPLIT_INCOME_LINE_54
from tax_engine.registrations import artifact_kinds
from tests.manifest_support import input_named, real_manifest

PRINTED_BASIS = "Line 54 and line 61510: Ontario tax on split income (complete Form T1206)"


def test_a_request_that_leaves_out_line_54_is_read_as_blank() -> None:
    kinds = artifact_kinds()
    identifier = ON428_TAX_ON_SPLIT_INCOME_LINE_54.identifier
    declaration = input_named(real_manifest("CA-ON"), identifier)
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
