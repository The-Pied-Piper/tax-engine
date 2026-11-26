"""PE428 (2025) line 17's input, as the Prince Edward Island take-home manifest part declares it.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 17 and line 58200: Amount for infirm dependants
age 18 or older (use Worksheet PE428)". A salary-only caller has none, so a request that leaves the
line out is read as blank. The real part is loaded under a test-local header and form, as the take-
home header is another part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_pe
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_pe.catalog import PE428_INFIRM_DEPENDANTS_AMOUNT_LINE_17
from tests.jurisdictions.ca_pe.credits_support import HEADER
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_kinds,
    prince_edward_island_packages,
    prince_edward_island_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named, inputs_of

IDENTIFIER = "ca-pe/pe428_infirm_dependants_amount_line_17"
PRINTED_BASIS = (
    "Line 17 and line 58200: Amount for infirm dependants age 18 or older (use Worksheet PE428)"
)
PART = (
    Path(tax_engine.jurisdictions.ca_pe.__file__).parent
    / "manifests"
    / "2025"
    / "pe428_credits_line_17_input.yaml"
)
FORM = """\
form:
  name: ca-pe/pe428_credits
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
    assert declaration.title == "Amount for infirm dependants age 18 or older (use Worksheet PE428)"
    assert declaration.reference == "17"
    assert declaration.unit == "ca/cad"


def test_a_request_that_leaves_the_line_out_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(prince_edward_island_kinds().kind(IDENTIFIER))

    assert default is not None and default.is_blank


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(IDENTIFIER)

    assert kind is PE428_INFIRM_DEPENDANTS_AMOUNT_LINE_17
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
