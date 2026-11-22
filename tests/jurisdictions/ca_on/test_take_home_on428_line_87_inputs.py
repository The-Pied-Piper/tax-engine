"""ON428 (2025) line 87's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 87 and line 62150: Enter the
amount of qualifying donations that have also been claimed as a charitable donation. ^". The
input is the qualifying donations, as the form takes them; the 25% is computed by the line 87
part, not by the caller. A salary-only caller makes no community food program donation, so a
request that leaves the input out is read as 0, not blank.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.jurisdictions.ca_on.catalog import ON428_QUALIFYING_FOOD_DONATIONS_LINE_87
from tax_engine.registrations import artifact_kinds
from tests.manifest_support import input_named, real_manifest

D = Decimal
PRINTED_BASIS = (
    "Line 87 and line 62150: Enter the amount of qualifying donations that have also been claimed "
    "as a charitable donation"
)


def test_a_request_that_leaves_out_line_87_is_read_as_zero() -> None:
    kinds = artifact_kinds()
    identifier = ON428_QUALIFYING_FOOD_DONATIONS_LINE_87.identifier
    declaration = input_named(real_manifest("CA-ON"), identifier)
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
