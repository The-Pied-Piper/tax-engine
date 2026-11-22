"""SK428 (2025) line 55, computed from the real part files through the real engine.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 55 Amount from line 14 of your federal Schedule
9 multiplied by 14.5% =". The amount is the optional input `ca-sk/sk428_donations_amount_line_55`
(`sk428_credits_line_55_input.yaml`); the step is `sk428_credits_line_55.yaml`, which reads a
blank amount as 0. The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
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
OUTPUT = "ca-sk/sk428_donations_credit_at_rate_line_55"
PARTS = ("sk428_credits_line_55_input.yaml", "sk428_credits_line_55.yaml")
INPUT = "ca-sk/sk428_donations_amount_line_55"
RATE = D("0.145")

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/sk428_donations_credit_at_rate_line_55
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
    ("amount", "expected"),
    [("2000", "290.00"), ("333.33", "48.33")],
)
def test_line_55_is_the_schedule_9_amount_at_the_printed_rate(
    tmp_path: Path, amount: str, expected: str
) -> None:
    # The expected figure is derived by hand: amount times 14.5%, half-up to the cent.
    hand = (D(amount) * RATE).quantize(D("0.01"), ROUND_HALF_UP)
    assert hand == D(expected)
    assert _compute(tmp_path, {INPUT: amount}) == D(expected)


def test_line_55_is_0_when_the_amount_is_left_blank(tmp_path: Path) -> None:
    assert _compute(tmp_path, {}) == D("0.00")


def test_the_part_is_one_rate_step() -> None:
    part = yaml.safe_load((SK_PARTS / PARTS[-1]).read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/apply_rate",
                "reference": "55 box B",
                "unit": "ca/cad",
                "params": {"rate": "ca-sk/donations_credit_rate_line_55"},
                "consumes": {"base": INPUT},
                "blank": {"base": "0"},
                "produces": {"output": OUTPUT},
            }
        ],
    }
