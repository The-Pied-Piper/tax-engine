"""SK428 (2025) line 77, the labour-sponsored venture capital tax credit, from lines 75 and 76,
real parts.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 77 and line 63557: Line 75 plus line 76 (maximum
$875) =". The part `sk428_line_77.yaml` has three steps: a first `core/credit_amount` that supplies
the printed maximum (a plain-words title, no reference), a `core/sum` of lines 75 and 76 (a
plain-words title, no reference, blanks read as 0) and a `core/at_most`, which is line 77
(reference "77"). A sum above the maximum is refused, not capped.

The real parts `sk428_line_75_input.yaml`, `sk428_line_76_input.yaml` and `sk428_line_77.yaml` are
loaded under a test-local header and form, and only the salary and, in some tests, lines 75 and 76
are typed in. The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import AtMostLine, SumLine
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
INPUT_PARTS = (SK_PARTS / "sk428_line_75_input.yaml", SK_PARTS / "sk428_line_76_input.yaml")
LINE_PART = SK_PARTS / "sk428_line_77.yaml"
MAXIMUM = "ca-sk/sk428_labour_sponsored_credit_maximum"
LINE_77 = "ca-sk/sk428_labour_sponsored_credit_checked_line_77"
CREDIT = "ca-sk/sk428_labour_sponsored_credit_line_77"
LINE_75 = "ca-sk/sk428_venture_capital_credit_saskatchewan_line_75"
LINE_76 = "ca-sk/sk428_venture_capital_credit_federal_line_76"
FORM_NAME = "ca-sk/sk428"

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428
      required: true
      exports:
        - ca-sk/sk428_labour_sponsored_credit_checked_line_77
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate((*INPUT_PARTS, LINE_PART), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
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


def _sheet(tmp_path: Path, line_75: str | None = None, line_76: str | None = None) -> Worksheet:
    given: list[Artifact[Any]] = []
    for name, value in ((LINE_75, line_75), (LINE_76, line_76)):
        if value is not None:
            given.append(Artifact(saskatchewan_kinds().kind(name), D(value)))
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-SK"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line_77(tmp_path: Path, line_75: str | None = None, line_76: str | None = None) -> Decimal:
    value = _sheet(tmp_path, line_75, line_76).get(saskatchewan_kinds().kind(LINE_77)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_75", "line_76", "expected"),
    [
        (None, None, "0.00"),
        ("400.00", None, "400.00"),
        (None, "300.00", "300.00"),
        ("400.00", "300.00", "700.00"),
        ("500.00", "375.00", "875.00"),
    ],
)
def test_line_77_is_line_75_plus_line_76_with_a_blank_read_as_0(
    tmp_path: Path, line_75: str | None, line_76: str | None, expected: str
) -> None:
    # By hand: each line left out is 0, and the sum is at most the printed $875.
    hand = D(line_75 or "0") + D(line_76 or "0")
    assert hand == D(expected)
    assert hand <= D("875")

    assert _line_77(tmp_path, line_75, line_76) == D(expected)


@pytest.mark.parametrize(
    ("line_75", "line_76"), [("875.01", None), ("500.00", "375.01"), ("500.00", "500.00")]
)
def test_a_sum_above_the_maximum_is_refused_not_capped(
    tmp_path: Path, line_75: str, line_76: str | None
) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_77(tmp_path, line_75, line_76)


def test_the_sheet_prints_the_plain_title_of_the_sum_and_the_reference_of_line_77(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "400.00", "300.00")
    kinds = saskatchewan_kinds()

    assert sheet.title(kinds.kind(LINE_77).label) is None
    assert sheet.reference(kinds.kind(LINE_77).label) == "77"
    assert sheet.title(kinds.kind(CREDIT).label) == "Lines 75 and 76 added up"
    assert sheet.reference(kinds.kind(CREDIT).label) is None


def test_the_trace_has_one_sum_line_and_one_at_most_line_against_the_maximum(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "400.00", "300.00")
    kinds = saskatchewan_kinds()

    (total,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(CREDIT)]
    assert total.parts == ((kinds.kind(LINE_75), D("400.00")), (kinds.kind(LINE_76), D("300.00")))
    assert total.total == D("700.00")
    (line,) = [
        t for t in sheet.trace if isinstance(t, AtMostLine) and t.output is kinds.kind(LINE_77)
    ]
    assert line.amount_kind is kinds.kind(CREDIT)
    assert line.amount_value == D("700.00")
    assert line.bound is kinds.kind(MAXIMUM)
    assert line.bound_value == D("875.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_has_three_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    maximum, total, line = part["capabilities"]
    assert maximum == {
        "name": "core/credit_amount",
        "title": "Most you can claim for labour-sponsored venture capital credits",
        "unit": "ca/cad",
        "params": {"amount": "ca-sk/labour_sponsored_credit_maximum"},
        "produces": {"output": MAXIMUM},
    }
    assert total == {
        "name": "core/sum",
        "title": "Lines 75 and 76 added up",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {"parts": [LINE_75, LINE_76]},
        "blank": {LINE_75: "0", LINE_76: "0"},
        "produces": {"output": CREDIT},
    }
    assert "reference" not in total
    assert line == {
        "name": "core/at_most",
        "reference": "77",
        "unit": "ca/cad",
        "consumes": {"amount": CREDIT, "bound": MAXIMUM},
        "produces": {"output": LINE_77},
    }
    assert "title" not in line
