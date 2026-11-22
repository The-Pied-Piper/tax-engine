"""ON428 (2025) line 27's input, as the Ontario take-home manifest part declares it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 27 and line 58360: Pension
income amount (maximum $1,762)". A salary-only caller has no pension income amount, so a request
that leaves the line out is read as 0, not blank.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tax_engine.jurisdictions.ca_on.catalog import ON428_PENSION_INCOME_AMOUNT
from tax_engine.registrations import artifact_kinds
from tests.manifest_support import input_named, real_manifest

D = Decimal
PRINTED_BASIS = "Line 27 and line 58360: Pension income amount (maximum $1,762)"


def test_a_request_that_leaves_out_the_pension_income_amount_is_read_as_zero(
    tmp_path: Path,
) -> None:
    kinds = artifact_kinds()
    declaration = input_named(real_manifest("CA-ON"), ON428_PENSION_INCOME_AMOUNT.identifier)
    default = declaration.default_artifact(kinds.kind(ON428_PENSION_INCOME_AMOUNT.identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
