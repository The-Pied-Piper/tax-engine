"""NL428 (2025) line 89's input, as the Newfoundland and Labrador take-home manifest declares it.

Form NL428 (CRA 5001-C), line 89, as printed on the form: "Line 89: Total of the universal child
care benefit (UCCB) repayment (line 21300 of the return) and the registered disability savings plan
(RDSP) income repayment (included on line 23200 of the return)", column 1 (you). The line is taken
as one optional input, as the form takes it; a salary-only caller has no such repayment, so a
request that leaves the line out is read as blank.

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
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_UCCB_RDSP_REPAYMENTS_LINE_89,
)
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)
from tests.kinds import non_negative

KIND = NL428_UCCB_RDSP_REPAYMENTS_LINE_89
IDENTIFIER = KIND.identifier
PRINTED_LABEL = (
    "Total of the universal child care benefit (UCCB) repayment (line 21300 of the return) and "
    "the registered disability savings plan (RDSP) income repayment (included on line 23200 of "
    "the return)"
)
PRINTED_BASIS = f"Line 89: {PRINTED_LABEL}"
PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / (
    "manifests/2025/nl428_line_89_input.yaml"
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
    declared = yaml.safe_load(PART.read_text(encoding="utf-8"))
    exports = "".join(f"    - {each['name']}\n" for each in declared["inputs"])
    (folder / "form.yaml").write_text(
        f"form:\n  name: {declared['form']['name']}\n  required: true\n  exports:\n{exports}"
        "capabilities: []\n"
    )
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_uccb_rdsp_repayments_input() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-nl/nl428"}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": PRINTED_LABEL,
            "reference": "89",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]


def test_the_uccb_rdsp_repayments_line_89_is_a_non_negative_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-nl/nl428_uccb_rdsp_repayments_line_89"
    assert kind is KIND
    assert non_negative(kind)


def test_a_request_that_leaves_out_line_89_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(newfoundland_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_an_amount_for_line_89_is_taken_as_given() -> None:
    assert Artifact(KIND, Decimal("1234.56")).value == Decimal("1234.56")
