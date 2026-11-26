"""PE428 (2025) line 37's input, as the Prince Edward Island take-home manifest part declares it.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 37 and line 58600: Tuition and education amounts
transferred from a child or grandchild". A salary-only caller has none. A request that leaves the
line out is read as blank. The real part is loaded under a test-local header and form, as the
take-home header is another part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_pe
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_pe.catalog import (
    PE428_TUITION_TRANSFERRED_FROM_CHILD_OR_GRANDCHILD_LINE_37,
)
from tests.jurisdictions.ca_pe.credits_support import HEADER
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_kinds,
    prince_edward_island_packages,
    prince_edward_island_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named, inputs_of

IDENTIFIER = "ca-pe/pe428_tuition_transferred_from_child_or_grandchild_line_37"
PRINTED_BASIS = (
    "Line 37 and line 58600: Tuition and education amounts transferred from a child or grandchild"
)
TITLE = "Tuition and education amounts transferred from a child or grandchild"
PART = (
    Path(tax_engine.jurisdictions.ca_pe.__file__).parent
    / "manifests"
    / "2025"
    / "pe428_line_37_input.yaml"
)
FORM = """\
form:
  name: ca-pe/pe428
  required: true
  exports:
    - ca/total_income
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    (folder / "form.yaml").write_text(FORM)
    source = YamlJurisdictionSource(
        prince_edward_island_packages().roots(),
        prince_edward_island_kinds(),
        prince_edward_island_units(),
    )
    return source.load(folder)


def test_the_part_declares_the_one_optional_input_as_printed(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)

    assert list(inputs_of(manifest)) == [IDENTIFIER]
    declaration = input_named(manifest, IDENTIFIER)
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert declaration.title == TITLE
    assert declaration.reference == "37"
    assert declaration.unit == "ca/cad"


def test_a_request_that_leaves_the_line_out_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(prince_edward_island_kinds().kind(IDENTIFIER))

    assert default is not None and default.is_blank


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(IDENTIFIER)

    assert kind is PE428_TUITION_TRANSFERRED_FROM_CHILD_OR_GRANDCHILD_LINE_37
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
