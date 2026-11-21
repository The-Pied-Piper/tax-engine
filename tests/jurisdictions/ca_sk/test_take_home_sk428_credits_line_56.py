"""SK428 (2025) line 56, computed from the real part files through the real engine.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 56 and 58969: Line 54 plus line 55 =". The
inputs come from the two line steps, so this test declares them in a header of its own and loads
`sk428_credits_line_56.yaml` beside it. The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FORM_NAME = "ca-sk/sk428_credits"
OUTPUT = "ca-sk/sk428_donations_credit_line_56"
PARTS = ("sk428_credits_line_56.yaml",)
INPUTS = (
    "ca-sk/sk428_donations_credit_at_rate_line_54",
    "ca-sk/sk428_donations_credit_at_rate_line_55",
)

HEADER = (
    "jurisdiction: CA-SK\nversion: 1\nvalid_from_tax_year: 2025\ninputs:\n"
    + "".join(f"  - name: {name}\n    required: true\n" for name in INPUTS)
    + "outputs:\n"
    + "".join(f"  - {name}\n" for name in INPUTS)
)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/sk428_donations_credit_line_56
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, name in enumerate(PARTS, start=2):
        text = (SK_PARTS / name).read_text(encoding="utf-8")
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(),
            saskatchewan_parameter_parsers(),
            saskatchewan_units(),
        ),
        saskatchewan_capabilities(),
    )


def _kind(identifier: str) -> AmountKind:
    kind = saskatchewan_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _compute(tmp_path: Path, given: dict[str, str]) -> Decimal:
    artifacts = [Artifact(_kind(name), D(value)) for name, value in given.items()]
    (sheet,) = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *artifacts)[FORM_NAME]
    value = sheet.get(_kind(OUTPUT)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_54", "line_55", "expected"),
    [("105.00", "290.00", "395.00"), ("0.00", "0.00", "0.00"), ("10.50", "0.00", "10.50")],
)
def test_line_56_is_line_54_plus_line_55(
    tmp_path: Path, line_54: str, line_55: str, expected: str
) -> None:
    given = dict(zip(INPUTS, (line_54, line_55), strict=True))

    assert _compute(tmp_path, given) == D(expected)


def test_the_part_is_one_sum_step() -> None:
    part = yaml.safe_load((SK_PARTS / PARTS[-1]).read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/sum",
                "reference": "56",
                "unit": "ca/cad",
                "params": {"rounding": "ca-sk/cent_rounding"},
                "consumes": {"parts": list(INPUTS)},
                "produces": {"output": OUTPUT},
            }
        ],
    }
