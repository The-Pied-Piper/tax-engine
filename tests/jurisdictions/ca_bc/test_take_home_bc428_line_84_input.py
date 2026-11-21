"""BC428 (2025) line 84's input, as the British Columbia take-home manifest part declares it.

Form text (Form BC428, CRA 5010-C): "Line 84: British Columbia political contribution tax credit
(use Worksheet BC428) (maximum $500)". Worksheet BC428 is not built. The input is
`ca-bc/bc428_political_contribution_tax_credit_line_84`; `bc428_line_84.yaml` checks it against the
printed maximum. A salary-only caller has no British Columbia political contribution tax credit, so
a request that leaves the line out is read as blank, which the line 84 step passes on.

The real part is loaded under a test-local header over the British Columbia package list of
`support.py`.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_BRITISH_COLUMBIA_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_84,
    BC428_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_84,
    BC428_POLITICAL_CONTRIBUTION_TAX_CREDIT_MAXIMUM,
)
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = BC428_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_84.identifier
PRINTED_BASIS = (
    "Line 84: British Columbia political contribution tax credit "
    "(use Worksheet BC428) (maximum $500)"
)
PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / (
    "manifests/2025/bc428_line_84_input.yaml"
)
HEADER = """\
jurisdiction: CA-BC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""


FORM_NAME = "ca-bc/bc428"


def _owner_form() -> str:
    """A declaration of the form the part names as owner of its inputs, exporting one input."""
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    name = part["form"]["name"]
    export = part["inputs"][0]["name"]
    return f"form:\n  name: {name}\n  required: true\n  exports: [{export}]\ncapabilities: []\n"


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    (folder / "form.yaml").write_text(_owner_form())
    shutil.copy(PART, folder / PART.name)
    source = YamlJurisdictionSource(
        british_columbia_packages().roots(), british_columbia_kinds(), british_columbia_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_the_political_contribution_tax_credit_input() -> None:
    part = _part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "British Columbia political contribution tax credit",
            "reference": "84",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]
    assert list(part["inputs"][0]) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]


def test_the_input_is_a_non_negative_amount_kind_without_a_line_number() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert IDENTIFIER == "ca-bc/bc428_political_contribution_tax_credit_line_84"
    assert kind is BC428_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_84
    assert non_negative(kind)


def test_the_line_84_and_maximum_kinds_are_non_negative_amount_kinds() -> None:
    line_84 = british_columbia_kinds().kind(
        "ca-bc/bc428_british_columbia_political_contribution_tax_credit_line_84"
    )
    maximum = british_columbia_kinds().kind("ca-bc/bc428_political_contribution_tax_credit_maximum")

    assert line_84 is BC428_BRITISH_COLUMBIA_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_84
    assert maximum is BC428_POLITICAL_CONTRIBUTION_TAX_CREDIT_MAXIMUM
    assert non_negative(line_84)
    assert non_negative(maximum)


def test_a_request_that_leaves_out_line_84_is_read_as_blank(tmp_path: Path) -> None:
    declaration = input_named(_manifest(tmp_path), IDENTIFIER)
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank
