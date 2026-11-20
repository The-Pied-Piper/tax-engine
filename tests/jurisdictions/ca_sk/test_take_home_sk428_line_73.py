"""SK428 (2025) line 73, the political contribution tax credit, rejected above its printed maximum.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 73: Saskatchewan political contribution tax
credit (use Worksheet SK428) (maximum $650)". No arithmetic is printed, so line 73 is an entry
line: the entered amount is rejected above the printed maximum, not capped. The maximum is the
`ca-sk/political_contribution_credit_maximum` dataset, supplied by a first `core/credit_amount`
step that carries no title and no line number (it is not a line of the form); the second step,
`core/at_most`, is line 73 and carries the title "Saskatchewan political contribution tax credit"
and the reference "73". The input is optional and blank when left out, so a blank is passed on as
blank, never read as 0 here.

The real input part and the new `sk428_line_73.yaml` are loaded under a test-local header and form,
and only the salary is typed in (plus, in some tests, the political contribution tax credit).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_sk
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
from tax_engine.jurisdictions.ca_sk.catalog import SK428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_73
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
INPUT_PART = SK_PARTS / "sk428_line_73_input.yaml"
LINE_PART = SK_PARTS / "sk428_line_73.yaml"
MAXIMUM = "ca-sk/sk428_political_contribution_credit_maximum"
LINE_73 = "ca-sk/sk428_political_contributions_credit_checked_line_73"
CREDIT = "ca-sk/sk428_political_contributions_credit_line_73"
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
        - ca-sk/sk428_political_contributions_credit_checked_line_73
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_73.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
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


def _sheet(tmp_path: Path, credit: str | None = None, salary: str = "70000") -> Worksheet:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if credit is not None:
        given.append(Artifact(SK428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_73, D(credit)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line_73(tmp_path: Path, credit: str | None = None) -> Artifact[Any]:
    return _sheet(tmp_path, credit).get(saskatchewan_kinds().kind(LINE_73))


def test_an_amount_at_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_73(tmp_path, "650").value) == D("650.00")


def test_an_amount_below_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_73(tmp_path, "250.50").value) == D("250.50")


def test_an_amount_of_zero_passes(tmp_path: Path) -> None:
    assert D(_line_73(tmp_path, "0").value) == D("0")


def test_one_cent_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_73(tmp_path, "650.01")


def test_a_salary_only_run_passes_the_credit_on_as_blank(tmp_path: Path) -> None:
    assert _line_73(tmp_path).is_blank


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_the_salary_does_not_change_the_checked_amount(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, "250.50", salary)

    assert D(sheet.get(saskatchewan_kinds().kind(LINE_73)).value) == D("250.50")


def test_the_sheet_prints_the_title_and_the_reference_of_line_73(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "250.50")
    label = saskatchewan_kinds().kind(LINE_73).label

    assert sheet.title(label) == "Saskatchewan political contribution tax credit"
    assert sheet.reference(label) == "73"


def test_the_step_traces_one_at_most_line_against_the_printed_maximum(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "250.50")
    kinds = saskatchewan_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, AtMostLine) and t.output is kinds.kind(LINE_73)
    ]
    assert line.amount_kind is kinds.kind(CREDIT)
    assert line.amount_value == D("250.50")
    assert line.bound is kinds.kind(MAXIMUM)
    assert line.bound_value == D("650.00")


def test_the_trace_row_for_line_73_reads_at_most_the_printed_maximum(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "250.50")
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    (row,) = [r for r in rows if ", at most " in r and "(CA$250.50)" in r]
    assert row.index("(CA$250.50)") < row.index(", at most ")
    assert "(CA$650.00)" in row.split(", at most ")[1]


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
        "params": {"amount": "ca-sk/political_contribution_credit_maximum"},
        "produces": {"output": MAXIMUM},
    }


def test_the_second_step_is_line_73_titled_and_referenced() -> None:
    _, second = _part()["capabilities"]

    assert second == {
        "name": "core/at_most",
        "title": "Saskatchewan political contribution tax credit",
        "reference": "73",
        "unit": "ca/cad",
        "consumes": {"amount": CREDIT, "bound": MAXIMUM},
        "blank": {"amount": "pass_on"},
        "produces": {"output": LINE_73},
    }


@pytest.mark.parametrize("identifier", [MAXIMUM, LINE_73])
def test_each_new_kind_is_a_registered_non_negative_decimal_amount_kind(identifier: str) -> None:
    kind = saskatchewan_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
