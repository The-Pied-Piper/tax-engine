"""The Ontario take-home manifest's T1 input a salary-only caller does not give: line 23500, the
social benefits repayment.

T1 line 23500: "Line 55 and line 23500: If not, enter "0" on line 23500." A salary-only caller has
nothing on lines 11900, 11300 or 14600, so a request that leaves the line out is read as 0, and the
line 23600 part takes that 0 off net income before adjustments.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.jurisdictions.ca_on.conftest import TakeHomeService

LINE_23500 = "ca/social_benefits_repayment"
PRINTED_BASIS = 'Line 55 and line 23500: If not, enter "0" on line 23500.'
PART = "t1_taxable_income_inputs.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/social_benefits_repayment]
capabilities: []
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/social_benefits_repayment
capabilities: []
"""


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    """The temporary take-home folder the shared builder writes, loaded as a manifest."""
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)


def test_a_request_that_leaves_out_line_23500_is_read_as_zero(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(take_home_service, tmp_path).inputs[LINE_23500]
    default = declaration.default_artifact(kinds.kind(LINE_23500))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.value == Decimal(0)
