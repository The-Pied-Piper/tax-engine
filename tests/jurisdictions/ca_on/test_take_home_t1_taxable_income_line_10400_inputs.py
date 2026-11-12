"""The Ontario take-home manifest's T1 input a salary-only caller does not give: line 10400, other
employment income.

T1 line 10400: "Line 2 and line 10400: Other employment income". A salary-only caller has no slips,
tips or other employment income, so a request that leaves the line out is read as 0, not blank.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
OTHER_EMPLOYMENT_INCOME = "ca/other_employment_income"
PRINTED_BASIS = "Line 2 and line 10400: Other employment income"
PART = "t1_taxable_income_line_10400_inputs.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/other_employment_income]
capabilities: []
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/other_employment_income
capabilities: []
"""


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    """The temporary take-home folder the shared builder writes, loaded as a manifest."""
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)


def test_a_request_that_leaves_out_other_employment_income_is_read_as_zero(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(take_home_service, tmp_path).inputs[OTHER_EMPLOYMENT_INCOME]
    default = declaration.default_artifact(kinds.kind(OTHER_EMPLOYMENT_INCOME))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
