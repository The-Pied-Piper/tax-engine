"""The Ontario take-home manifest's T2204 inputs a salary-only caller does not give: line 2, the
self-employment earnings, line 4, the premiums deducted as given on the T4 slips, and line 5, the
Schedule 13 premium.

T2204 line 2: "Total self-employment and other earnings eligible for the EI program for access to EI
special benefits". A salary-only caller has none, so a request that leaves the line out is read as
blank, and the line 1 part reads that blank as 0.

T2204 line 4: "Total premiums deducted: Residents of other than Quebec (box 18 and box 55 of your T4
slips)". A request that leaves it out is read as blank, and the line 4 part computes it from line 1.

T2204 line 5: "Residents of other than Quebec (amount from line 9 of Schedule 13)". A salary-only
caller has no Schedule 13 premium, so a request that leaves the line out is read as blank, and the
line 6 part reads that blank as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds
from tests.jurisdictions.ca_on.conftest import TakeHomeService

LINE_2 = "ca/t2204_self_employment_earnings"
LINE_4_GIVEN = "ca/t2204_premiums_deducted_given"
PRINTED_BASIS = (
    "Total self-employment and other earnings eligible for the EI program for access to EI "
    "special benefits"
)
LINE_5 = "ca/t2204_line_5"
PRINTED_BASIS_LINE_5 = "Residents of other than Quebec (amount from line 9 of Schedule 13)"
PART = "t2204_inputs.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/t2204_line_1]
capabilities: []
"""


FORM = """\
form:
  name: ca/t2204
  required: true
  exports:
    - ca/t2204_line_1
capabilities: []
"""


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    """The temporary take-home folder the shared builder writes, loaded as a manifest."""
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds()).load(folder)


def test_a_request_that_leaves_out_the_self_employment_earnings_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(take_home_service, tmp_path).inputs[LINE_2]
    default = declaration.default_artifact(kinds.kind(LINE_2))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_a_request_that_leaves_out_line_5_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(take_home_service, tmp_path).inputs[LINE_5]
    default = declaration.default_artifact(kinds.kind(LINE_5))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS_LINE_5
    assert default is not None and default.is_blank


def test_a_request_that_leaves_out_the_premiums_deducted_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(take_home_service, tmp_path).inputs[LINE_4_GIVEN]
    default = declaration.default_artifact(kinds.kind(LINE_4_GIVEN))
    assert not declaration.required
    assert declaration.basis is not None and "premiums deducted" in declaration.basis.lower()
    assert default is not None and default.is_blank
