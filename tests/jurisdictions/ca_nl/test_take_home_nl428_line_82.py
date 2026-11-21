"""NL428 (2025) line 82, computed from the real part files through the real engine.

Form text (Form NL428, CRA 5001-C): "Line 82 and line 61820: Venture capital tax credit from
Certificate(s) NL VCTC"; guide (5001-PC, line 82): "The lifetime maximum you can claim is $75,000."
The amount is the optional input `nl428_line_82_input.yaml`; the step is `nl428_line_82.yaml`, which
reads a blank amount as 0 and refuses an amount above the maximum, never capping it. The hand
figures are asserted (not a CRA example).
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
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import AtMostLine
from tax_engine.domain.worksheet import Worksheet
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
OUTPUT = "ca-nl/nl428_venture_capital_tax_credit_checked_line_82"
MAXIMUM = "ca-nl/nl428_venture_capital_tax_credit_lifetime_maximum"
PARTS = ("nl428_line_82_input.yaml", "nl428_line_82.yaml")
LINE_82 = "ca-nl/nl428_venture_capital_tax_credit_from_certificates_line_82"

HEADER = dedent(f"""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - {LINE_82}
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


def _sheet(tmp_path: Path, given: dict[str, str]) -> Worksheet:
    artifacts = [Artifact(_kind(name), D(value)) for name, value in given.items()]
    (sheet,) = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *artifacts)[FORM_NAME]
    return sheet


def _compute(tmp_path: Path, given: dict[str, str]) -> Decimal:
    value = _sheet(tmp_path, given).get(_kind(OUTPUT)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("amount", "expected"),
    [("1500.00", "1500.00"), ("0.00", "0.00"), ("75000.00", "75000.00"), ("74999.99", "74999.99")],
)
def test_line_82_is_the_amount_up_to_the_lifetime_maximum(
    tmp_path: Path, amount: str, expected: str
) -> None:
    assert _compute(tmp_path, {LINE_82: amount}) == D(expected)


def test_line_82_is_blank_when_the_amount_is_left_blank(tmp_path: Path) -> None:
    # A blank amount passes on as blank; the line 84 sum reads it as 0.
    assert _sheet(tmp_path, {}).get(_kind(OUTPUT)).is_blank


@pytest.mark.parametrize("amount", ["75000.01", "100000.00"])
def test_an_amount_above_the_lifetime_maximum_is_refused_not_capped(
    tmp_path: Path, amount: str
) -> None:
    with pytest.raises(InputAboveBoundError):
        _compute(tmp_path, {LINE_82: amount})


def test_the_sheet_prints_the_reference_of_line_82_and_the_plain_title_of_the_maximum(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, {LINE_82: "1500.00"})
    kinds = newfoundland_kinds()

    assert sheet.title(kinds.kind(OUTPUT).label) is None
    assert sheet.reference(kinds.kind(OUTPUT).label) == "82"
    assert (
        sheet.title(kinds.kind(MAXIMUM).label)
        == "Most you can claim for venture capital tax credits over your lifetime"
    )
    assert sheet.reference(kinds.kind(MAXIMUM).label) is None


def test_the_trace_has_one_at_most_line_against_the_maximum(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, {LINE_82: "1500.00"})
    kinds = newfoundland_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, AtMostLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert line.amount_kind is kinds.kind(LINE_82)
    assert line.amount_value == D("1500.00")
    assert line.bound is kinds.kind(MAXIMUM)
    assert line.bound_value == D("75000.00")


def test_the_part_is_a_maximum_step_and_a_check_step() -> None:
    part = yaml.safe_load((NL_PARTS / PARTS[-1]).read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM_NAME},
        "capabilities": [
            {
                "name": "core/credit_amount",
                "title": "Most you can claim for venture capital tax credits over your lifetime",
                "unit": "ca/cad",
                "params": {"amount": "ca-nl/venture_capital_credit_lifetime_maximum"},
                "produces": {"output": MAXIMUM},
            },
            {
                "name": "core/at_most",
                "reference": "82",
                "unit": "ca/cad",
                "consumes": {"amount": LINE_82, "bound": MAXIMUM},
                "blank": {"amount": "pass_on"},
                "produces": {"output": OUTPUT},
            },
        ],
    }
