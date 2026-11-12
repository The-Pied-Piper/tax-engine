"""AB428 (2025) line 57's input, as the Alberta take-home manifest part declares it.

Form text (Form AB428, CRA 5009-c-25e.txt in cra-docs/docs/cra-forms-2025): "Line 57 and line 58969:
Line 55
plus line 56 =". Line 57 is the donations and gifts credit, taken as one input figure (lines 55 and
56 are not built). A salary-only caller gives no donations, so a request that leaves the line out
is read as blank, not as 0: the lines that read it take the blank as 0.

The part is loaded from the package under a test-local header, as the take-home header is another
part's. Alberta is not yet listed in the registrations, so the part is read over the Alberta
package list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_ab.catalog import AB428_DONATIONS_CREDIT_LINE_57
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units
from tests.kinds import non_negative

IDENTIFIER = "ca-ab/ab428_donations_credit_line_57"
PRINTED_BASIS = "Line 57 and line 58969: Line 55 plus line 56"
PART = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent
    / "manifests"
    / "2025"
    / "ab428_line_57_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-AB
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    return YamlJurisdictionSource(
        alberta_packages().roots(), alberta_kinds(), alberta_units()
    ).load(folder)


def test_the_catalog_kind_is_the_non_negative_amount_of_the_input() -> None:
    kind = alberta_kinds().kind(IDENTIFIER)

    assert AB428_DONATIONS_CREDIT_LINE_57.identifier == IDENTIFIER
    assert kind is AB428_DONATIONS_CREDIT_LINE_57
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_part_declares_the_one_optional_input_as_printed(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]

    assert declaration.name == IDENTIFIER
    assert declaration.title == "Donations and gifts"
    assert declaration.reference == "57"
    assert declaration.unit == "ca/cad"
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS


def test_a_request_that_leaves_out_line_57_is_read_as_blank(tmp_path: Path) -> None:
    kinds = alberta_kinds()
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(kinds.kind(IDENTIFIER))

    assert default is not None and default.is_blank
