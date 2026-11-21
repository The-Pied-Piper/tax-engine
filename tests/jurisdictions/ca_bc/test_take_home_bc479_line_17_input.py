"""BC479 (2025) line 17's input, as the British Columbia take-home manifest part declares it.

Form text: 'Line 17: Enter your unused venture capital tax credit from your most recent notice
of assessment or reassessment' (5010-TC). The line is an optional input, so a request that
leaves it out is read as blank, and the printed sum that reads it reads that blank as 0.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)
from tests.kinds import non_negative

IDENTIFIER = "ca-bc/bc479_venture_capital_unused_credit_line_17"
PART = (
    Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests/2025/bc479_line_17_input.yaml"
)
HEADER = """\
jurisdiction: CA-BC
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
        british_columbia_packages().roots(), british_columbia_kinds(), british_columbia_units()
    )
    return source.load(folder)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_declares_only_this_optional_input() -> None:
    part = _part()

    assert list(part) == ["inputs"]
    assert part["inputs"] == [
        {
            "name": "ca-bc/bc479_venture_capital_unused_credit_line_17",
            "title": "Unused venture capital tax credit",
            "reference": "17",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": "Line 17: Enter your unused venture capital tax credit from your most recent notice "
            "of assessment or reassessment",
        }
    ]


def test_the_input_is_a_registered_non_negative_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert non_negative(kind)


def test_a_request_that_leaves_out_the_line_is_read_as_blank(tmp_path: Path) -> None:
    declaration = _manifest(tmp_path).inputs[IDENTIFIER]
    default = declaration.default_artifact(british_columbia_kinds().kind(IDENTIFIER))

    assert not declaration.required
    assert default is not None and default.is_blank
