"""ON428 (2025) line 72's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 72: If you entered an amount on
line 11 of Part 5 of Form T691, use Worksheet ON428 to calculate your additional tax for minimum tax
purposes" is the line's printed text, and it is the basis in the take-home part. A caller with no
minimum tax leaves the line out, so the request is read as blank, and the line 73 part reads that
blank as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_on.catalog import ON428_ADDITIONAL_TAX_FOR_MINIMUM_TAX_LINE_72
from tax_engine.registrations import artifact_kinds
from tests.manifest_support import input_named, real_manifest

PRINTED_BASIS = (
    "Line 72: If you entered an amount on line 11 of Part 5 of Form T691, use Worksheet ON428 to "
    "calculate your additional tax for minimum tax purposes"
)


def test_a_request_that_leaves_out_line_72_is_read_as_blank() -> None:
    kinds = artifact_kinds()
    identifier = ON428_ADDITIONAL_TAX_FOR_MINIMUM_TAX_LINE_72.identifier
    declaration = input_named(real_manifest("CA-ON"), identifier)
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
