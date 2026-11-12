"""AB428 (2025) line 41's input, as the Alberta take-home manifest part declares it.

Form text (Form AB428, CRA 5009-c-25e.txt in docs/cra-forms-2025): "Line 41 and line 58560: Your
unused tuition and education amounts (attach Schedule AB(S11))". A salary-only caller has no
Schedule AB(S11), so a request that leaves the line out is read as blank, and its consumers (line 43
and line 2 of Worksheet AB428) read that blank as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
Alberta is not yet listed in the registrations, so the source is built over the Alberta package
list of `support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_ab.catalog import AB428_UNUSED_TUITION_LINE_41
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units

PRINTED_BASIS = "Line 41 and line 58560: Your unused tuition and education amounts"
PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / (
    "manifests/2025/ab428_line_41_input.yaml"
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
    source = YamlJurisdictionSource(alberta_packages().roots(), alberta_kinds(), alberta_units())
    return source.load(folder)


def _declarations() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["inputs"]
    return list(part["inputs"])


def test_a_request_that_leaves_out_line_41_is_read_as_blank(tmp_path: Path) -> None:
    kinds = alberta_kinds()
    identifier = AB428_UNUSED_TUITION_LINE_41.identifier
    declaration = _manifest(tmp_path).inputs[identifier]
    default = declaration.default_artifact(kinds.kind(identifier))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_part_declares_only_line_41_as_printed_in_canadian_dollars() -> None:
    assert _declarations() == [
        {
            "name": "ca-ab/ab428_unused_tuition_line_41",
            "title": "Your unused tuition and education amounts",
            "reference": "41",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]
    assert list(_declarations()[0]) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]
