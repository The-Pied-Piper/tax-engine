"""AB428 (2025) line 64's input, as the Alberta take-home manifest part declares it.

Form text (AB428, CRA 5009-c-25e.txt in cra-docs/docs/cra-forms-2025): "Line 64 and line 61540:
Amount from
line 40427 of your return" is the line's basis in the part. The input is the amount from the T1
(line 40427), which the engine does not compute; the 35% is computed by the next part, not by the
caller. A caller with no minimum tax carryover leaves the input out, so the request is read as 0,
not blank (the $20,000, $70,000 and $200,000 figures of the ticket are 0.00).

The real part is loaded under a test-local header, as the Alberta manifest cannot be built yet.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_ab.catalog import AB428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_64
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units

D = Decimal
IDENTIFIER = "ca-ab/ab428_minimum_tax_carryover_amount_line_64"
PRINTED_BASIS = "Line 64 and line 61540: Amount from line 40427 of your return"
PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / (
    "manifests/2025/ab428_line_64_inputs.yaml"
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


def test_the_kind_is_in_the_alberta_catalog() -> None:
    assert AB428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_64.identifier == IDENTIFIER
    assert alberta_kinds().kind(IDENTIFIER) is AB428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_64


def test_the_part_declares_the_one_untitled_input_as_printed() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "reference": "64 box A",
            "unit": "ca/cad",
            "required": False,
            "default": "0",
            "basis": PRINTED_BASIS,
        }
    ]
    assert list(part["inputs"][0]) == ["name", "reference", "unit", "required", "default", "basis"]


def test_a_request_that_leaves_out_line_64_is_read_as_zero(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(alberta_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and not default.is_blank
    assert default.value == D("0")
