"""NL428 (2025) line 91's column 2 input, as the Newfoundland and Labrador take-home part declares.

Form text (Form NL428, CRA 5001-C): "Line 91: Total of the UCCB income (line 11700 of the return)
and the RDSP income (line 12500 of the return)", column 2: your spouse or common-law partner. A
salary-only caller has no spouse or common-law partner, so a request that leaves the line out is
read as blank. The line is taken as one optional input, as the form takes it.

The real part is loaded under a test-local header over the Newfoundland and Labrador package list
of `support.py`.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_nl.catalog import NL428_SPOUSE_UCCB_RDSP_INCOME_LINE_91
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)
from tests.kinds import non_negative

KIND = NL428_SPOUSE_UCCB_RDSP_INCOME_LINE_91
IDENTIFIER = KIND.identifier
PRINTED_LABEL = (
    "Total of the UCCB income (line 11700 of the return) and the RDSP income (line 12500 of the "
    "return)"
)
PRINTED_BASIS = f"Line 91: {PRINTED_LABEL}"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/nl428_line_91_column_2_input.yaml"
)
HEADER = """\
jurisdiction: CA-NL
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
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_spouse_uccb_rdsp_income_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": PRINTED_LABEL,
            "reference": "91 (column 2)",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]


def test_a_request_that_leaves_out_line_91_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(newfoundland_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_spouse_uccb_rdsp_income_line_91_is_a_non_negative_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nl/nl428_spouse_uccb_rdsp_income_line_91"
    assert kind is KIND
    assert non_negative(kind)


def test_an_amount_for_line_91_is_taken_as_given() -> None:
    assert Artifact(KIND, Decimal("1234.56")).value == Decimal("1234.56")
