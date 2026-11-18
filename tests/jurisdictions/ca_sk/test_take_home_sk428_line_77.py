"""SK428 (2025) line 77, the labour-sponsored venture capital tax credit, rejected above its
printed maximum.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 77 and line 63557: Line 75 plus line 76 (maximum
$875) =". The form prints no label for line 77, so the input and the step are untitled. Line 77 is
an entry line: the entered amount is rejected above the printed maximum, not capped. The maximum is
the `ca-sk/labour_sponsored_credit_maximum` dataset, supplied by a first `core/credit_amount` step
that carries no title and no line number (it is not a line of the form); the second step,
`core/at_most`, is line 77, carries no title and the reference "77". A blank input (the default) is
passed on as blank.

The real input part and the new `sk428_line_77.yaml` are loaded under a test-local header and form,
and only the salary is typed in (plus, in some tests, the credit).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_sk
import tax_engine.jurisdictions.ca_sk.catalog as sk_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_sk.catalog import SK428_LABOUR_SPONSORED_CREDIT_LINE_77
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
INPUT_PART = SK_PARTS / "sk428_line_77_input.yaml"
LINE_PART = SK_PARTS / "sk428_line_77.yaml"
MAXIMUM = "ca-sk/sk428_labour_sponsored_credit_maximum"
LINE_77 = "ca-sk/sk428_labour_sponsored_credit_checked_line_77"
CREDIT = "ca-sk/sk428_labour_sponsored_credit_line_77"
FORM_NAME = "ca-sk/sk428"

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
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
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_77.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
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


def _sheet(tmp_path: Path, credit: str | None = None) -> Worksheet:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if credit is not None:
        given.append(Artifact(SK428_LABOUR_SPONSORED_CREDIT_LINE_77, D(credit)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line_77(tmp_path: Path, credit: str | None = None) -> Artifact[Any]:
    return _sheet(tmp_path, credit).get(saskatchewan_kinds().kind(LINE_77))


def test_an_amount_at_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_77(tmp_path, "875").value) == D("875.00")


def test_an_amount_below_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_77(tmp_path, "250.50").value) == D("250.50")


def test_an_amount_of_zero_passes(tmp_path: Path) -> None:
    assert D(_line_77(tmp_path, "0").value) == D("0")


def test_one_cent_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_77(tmp_path, "875.01")


def test_a_salary_only_run_leaves_line_77_blank(tmp_path: Path) -> None:
    assert _line_77(tmp_path).is_blank


def test_the_sheet_prints_no_title_and_the_reference_of_line_77(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "250.50")
    label = saskatchewan_kinds().kind(LINE_77).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "77"


def test_the_step_traces_one_at_most_line_against_the_printed_maximum(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "250.50")
    kinds = saskatchewan_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, AtMostLine) and t.output is kinds.kind(LINE_77)
    ]
    assert line.amount_kind is kinds.kind(CREDIT)
    assert line.amount_value == D("250.50")
    assert line.bound is kinds.kind(MAXIMUM)
    assert line.bound_value == D("875.00")


def test_the_trace_row_for_line_77_reads_at_most_the_printed_maximum(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "250.50")
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    (row,) = [r for r in rows if ", at most " in r and "(CA$250.50)" in r]
    assert row.index("(CA$250.50)") < row.index(", at most ")
    assert "(CA$875.00)" in row.split(", at most ")[1]


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_two_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    first, second = part["capabilities"]
    assert first["name"] == "core/credit_amount"
    assert second["name"] == "core/at_most"


def test_the_first_step_supplies_the_printed_maximum_with_no_title_and_no_reference() -> None:
    first, _ = _part()["capabilities"]

    assert "title" not in first
    assert "reference" not in first
    assert first == {
        "name": "core/credit_amount",
        "unit": "ca/cad",
        "params": {"amount": "ca-sk/labour_sponsored_credit_maximum"},
        "produces": {"output": MAXIMUM},
    }


def test_the_second_step_is_line_77_untitled_and_referenced() -> None:
    _, second = _part()["capabilities"]

    assert second == {
        "name": "core/at_most",
        "reference": "77",
        "unit": "ca/cad",
        "consumes": {"amount": CREDIT, "bound": MAXIMUM},
        "blank": {"amount": "pass_on"},
        "produces": {"output": LINE_77},
    }
    assert "title" not in second


@pytest.mark.parametrize("identifier", [MAXIMUM, LINE_77])
def test_each_new_kind_is_a_registered_non_negative_decimal_amount_kind(identifier: str) -> None:
    kind = saskatchewan_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_the_checked_line_77_is_the_catalog_constant() -> None:
    assert (
        saskatchewan_kinds().kind(LINE_77)
        is vars(sk_catalog)["SK428_LABOUR_SPONSORED_CREDIT_CHECKED_LINE_77"]
    )
