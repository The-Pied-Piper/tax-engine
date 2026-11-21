"""NL428 (2025) line 61, computed from the real part files through the real engine.

Form text (Form NL428, CRA 5001-C): "Line 61 and line 58969: Line 59 plus line 60 =". The
inputs come from the two line steps, so this test declares them in a header of its own and loads
`nl428_credits_line_61.yaml` beside it. The hand figures are asserted (not a CRA example).
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
FORM_NAME = "ca-nl/nl428_credits"
OUTPUT = "ca-nl/nl428_donations_and_gifts_credit_line_61"
PARTS = ("nl428_credits_line_61.yaml",)
INPUTS = (
    "ca-nl/nl428_donations_credit_at_rate_line_59",
    "ca-nl/nl428_donations_credit_at_rate_line_60",
)

HEADER = (
    "jurisdiction: CA-NL\nversion: 1\nvalid_from_tax_year: 2025\ninputs:\n"
    + "".join(f"  - name: {name}\n    required: true\n" for name in INPUTS)
    + "outputs:\n"
    + "".join(f"  - {name}\n" for name in INPUTS)
)
FORM = dedent("""\
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_donations_and_gifts_credit_line_61
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
    ("line_59", "line_60", "expected"),
    [("87.00", "218.00", "305.00"), ("0.00", "0.00", "0.00"), ("8.70", "0.00", "8.70")],
)
def test_line_61_is_line_59_plus_line_60(
    tmp_path: Path, line_59: str, line_60: str, expected: str
) -> None:
    given = dict(zip(INPUTS, (line_59, line_60), strict=True))

    assert _compute(tmp_path, given) == D(expected)


def test_the_part_is_one_sum_step() -> None:
    part = yaml.safe_load((NL_PARTS / PARTS[-1]).read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/sum",
                "title": "Donations and gifts",
                "reference": "61",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"parts": list(INPUTS)},
                "produces": {"output": OUTPUT},
            }
        ],
    }
