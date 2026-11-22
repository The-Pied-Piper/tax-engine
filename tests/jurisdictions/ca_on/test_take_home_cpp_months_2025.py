"""The Ontario take-home manifest's Schedule 8 line A: the months CPP applied.

Schedule 8 (form 5000-S8), Part 2: "Enter "12" on line A below unless any of the following
conditions apply". A salary-only caller meets none of conditions a) to h), so a request that
leaves the months out is read as 12, which `amount_by_count` needs (it refuses a blank count).
The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from tax_engine.registrations import artifact_kinds
from tests.manifest_support import input_named, real_manifest

LINE_A = "ca/cpp_months"
PRINTED_BASIS = 'Enter "12" on line A below unless any of the following conditions apply:'


def test_a_request_that_leaves_out_the_months_is_read_as_twelve() -> None:
    kinds = artifact_kinds()
    declaration = input_named(real_manifest("CA-ON"), LINE_A)
    default = declaration.default_artifact(kinds.kind(LINE_A))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.value == 12
