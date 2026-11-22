"""NL428 (2025) line 84, computed from the real part files through the real engine.

Form text (Form NL428, CRA 5001-C): "Line 84: Line 82 plus line 83 =". Line 82 (venture capital tax
credit from Certificate(s) NL VCTC) and line 83 (unused credit from the most recent notice of
assessment or reassessment) are the optional inputs `nl428_line_82_input.yaml` and
`nl428_line_83_input.yaml`; line 82 is checked against its lifetime maximum by
`nl428_line_82.yaml`; the step is `nl428_line_84.yaml`, which reads a blank line 83 as 0.
The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FORM_NAME = "ca-nl/nl428"
OUTPUT = "ca-nl/nl428_venture_capital_tax_credit_line_84"
PARTS = (
    "nl428_line_82_input.yaml",
    "nl428_line_83_input.yaml",
    "nl428_line_82.yaml",
    "nl428_line_84.yaml",
)
LINE_82 = "ca-nl/nl428_venture_capital_tax_credit_from_certificates_line_82"
LINE_83 = "ca-nl/nl428_unused_venture_capital_tax_credit_line_83"
CHECKED_LINE_82 = "ca-nl/nl428_venture_capital_tax_credit_checked_line_82"

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {OUTPUT}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, name in enumerate(PARTS, start=2):
        text = (NL_PARTS / name).read_text(encoding="utf-8")
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(),
            newfoundland_parameter_parsers(),
            newfoundland_units(),
        ),
        newfoundland_capabilities(),
    )


def _kind(identifier: str) -> AmountKind:
    kind = newfoundland_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _compute(tmp_path: Path, given: dict[str, str]) -> Decimal:
    artifacts = [Artifact(_kind(name), D(value)) for name, value in given.items()]
    (sheet,) = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *artifacts)[FORM_NAME]
    value = sheet.get(_kind(OUTPUT)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_82", "line_83", "expected"),
    [("1500.00", "250.50", "1750.50"), ("0.00", "0.00", "0.00"), ("300.25", "0.00", "300.25")],
)
def test_line_84_is_line_82_plus_line_83(
    tmp_path: Path, line_82: str, line_83: str, expected: str
) -> None:
    assert _compute(tmp_path, {LINE_82: line_82, LINE_83: line_83}) == D(expected)


@pytest.mark.parametrize(
    ("given", "expected"),
    [({LINE_82: "1500.00"}, "1500.00"), ({LINE_83: "250.50"}, "250.50"), ({}, "0.00")],
)
def test_line_84_reads_a_blank_line_as_0(
    tmp_path: Path, given: dict[str, str], expected: str
) -> None:
    assert _compute(tmp_path, given) == D(expected)


def test_the_part_is_one_sum_step() -> None:
    part = yaml.safe_load((NL_PARTS / PARTS[-1]).read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/sum",
                "reference": "84",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"parts": [CHECKED_LINE_82, LINE_83]},
                "blank": {CHECKED_LINE_82: "0", LINE_83: "0"},
                "produces": {"output": OUTPUT},
            }
        ],
    }
