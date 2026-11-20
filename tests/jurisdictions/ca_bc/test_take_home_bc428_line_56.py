"""BC428 (2025) line 56, line 54 multiplied by the line 55 rate of 5.06%, from the salary alone.

Form text (Form BC428, CRA 5010-c-25e.txt, read 2026-11-14): "Line 55: British Columbia
non-refundable tax credit rate 5.06%" and "Line 56 and line 58840: Line 54 multiplied by the
percentage from line 55 = ^". Line 55 is a printed rate, so it is the `ca-bc/credit_rate` dataset
figure and has no step of its own; line 56 is one core/apply_rate step over line 54, rounded
half-up to the cent by the dataset's own rule, as Alberta line 54 and Ontario line 46 are.

The test composes everything the line 54 test composes plus `bc428_line_54.yaml` and the new
`bc428_line_56.yaml`, and types in only the salary (and, in one test, line 53). The form declaration
is made up here, exporting only line 56. The figures are hand-computed from the printed forms (not a
CRA example): salary-only line 54 times 0.0506, rounded half-up to the cent.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import RateAppliedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_AT_RATE_LINE_56,
    BC428_MEDICAL_EXPENSES_LINE_53,
)
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_FORM, inputs_without_form

D = Decimal
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_54_PART = BC_PARTS / "bc428_line_54.yaml"
LINE_PART = BC_PARTS / "bc428_line_56.yaml"
LINE_54 = "ca-bc/bc428_total_line_54"
IDENTIFIER = "ca-bc/bc428_at_rate_line_56"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_at_rate_line_56
    capabilities: []
    """)

# salary, line 56 (line 54, which is line 45, times 0.0506). At $200,000 lines 27 and 29 are at
# their maximums.
CASES = [
    ("17000", "702.28"),
    ("200000", "878.70"),
]


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    yield T1_LINE_10100_FORM
    yield FEDERAL_FORMS / "t1_taxable_income" / "t1_taxable_income_line_10100.yaml"
    yield BC_PARTS / "bc428_line_16.yaml"
    yield BC_PARTS / "bc428_line_25.yaml"
    yield BC_PARTS / "bc428_line_27.yaml"
    yield BC_PARTS / "bc428_line_29.yaml"
    yield BC_PARTS / "bc428_line_33.yaml"
    yield BC_PARTS / "bc428_line_35.yaml"
    yield BC_PARTS / "bc428_line_36_input.yaml"
    yield BC_PARTS / "bc428_line_36.yaml"
    yield BC_PARTS / "bc428_line_37.yaml"
    yield BC_PARTS / "bc428_line_40.yaml"
    yield BC_PARTS / "bc428_line_45.yaml"
    yield BC_PARTS / "bc428_line_53_inputs.yaml"
    yield LINE_54_PART
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-BC"), 2025, *given)
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_56_is_line_54_times_5_06_percent(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(BC428_AT_RATE_LINE_56).value == D(expected)


def test_line_56_follows_line_53_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(BC428_MEDICAL_EXPENSES_LINE_53, D("1500.00")))

    # Line 54 is 18,801.23; times 0.0506 is 951.342238, rounded half-up to 951.34.
    assert sheet.get(BC428_AT_RATE_LINE_56).value == D("951.34")


def test_the_product_is_traced_with_its_base_and_the_rate(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = (
        each
        for each in sheet.trace
        if isinstance(each, RateAppliedLine) and each.output is BC428_AT_RATE_LINE_56
    )
    assert line.base_amount == D("17301.23")
    assert line.rate == Rate(D("0.0506"))
    assert line.result == D("875.44")
    assert "5.06% of" in EnglishTraceRenderer().render(line)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_apply_rate_step_over_line_54() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "56",
        "unit": "ca/cad",
        "params": {"rate": "ca-bc/credit_rate"},
        "consumes": {"base": LINE_54},
        "produces": {"output": IDENTIFIER},
    }


def test_line_56_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert kind is BC428_AT_RATE_LINE_56
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
