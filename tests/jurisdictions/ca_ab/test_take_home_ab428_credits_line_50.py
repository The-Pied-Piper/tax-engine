"""AB428 (2025) line 50, from the salary and the optional inputs, from real parts.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 50 and line 58729: Allowable amount of medical
expenses for other dependants (use Worksheet AB428)". The part is one core/sum step that reads a
blank as 0 and rounds to the cent; the figures are hand-computed from the printed form (not a CRA
example): a $70,000 salary has net income 69,335.00 (the salary less the enhanced CPP deduction).
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab import catalog as ab
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative

D = Decimal
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
# The real parts this line needs, beside the salary, Schedule 8 and the T1 taxable income parts.
LINE_PARTS = (
    "ab428_credits_line_50_input.yaml",
    "ab428_credits_line_50.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/ab428_allowable_medical_expenses_for_other_dependants_rounded_line_50
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t1_employment_income", "t1_taxable_income")
    for name in LINE_PARTS:
        yield ALBERTA_PARTS / name


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, one form declaration and
    the real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(dict.fromkeys(_part_files()), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-AB"), 2025, tuple(artifacts))
    )
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    value = sheet.get(alberta_kinds().kind(identifier)).value
    assert isinstance(value, Decimal)
    return value


PART = ALBERTA_PARTS / "ab428_credits_line_50.yaml"
KIND = "ca-ab/ab428_allowable_medical_expenses_for_other_dependants_rounded_line_50"
STEP: dict[str, Any] = {
    "name": "core/sum",
    "reference": "50",
    "unit": "ca/cad",
    "params": {"rounding": "ca-ab/cent_rounding"},
    "consumes": {"parts": ["ca-ab/ab428_allowable_medical_expenses_for_other_dependants_line_50"]},
    "blank": {"ca-ab/ab428_allowable_medical_expenses_for_other_dependants_line_50": "0"},
    "produces": {
        "output": "ca-ab/ab428_allowable_medical_expenses_for_other_dependants_rounded_line_50"
    },
}

# salary, given optional inputs, expected line
CASES: list[tuple[str, list[Artifact[Decimal]], str]] = [
    ("70000", [], "0.00"),
    (
        "70000",
        [Artifact(ab.AB428_ALLOWABLE_MEDICAL_EXPENSES_FOR_OTHER_DEPENDANTS_LINE_50, D("250.505"))],
        "250.51",
    ),
]


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_the_rounded_line_50_is_the_input_to_the_cent_at_each_case(
    tmp_path: Path, salary: str, given: list[Artifact[Decimal]], expected: str
) -> None:
    assert _value(_sheet(tmp_path, salary, *given), KIND) == D(expected)


def test_the_part_names_the_form_and_is_one_step_as_the_form_prints_the_line() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part == {"form": {"name": "ca-ab/ab428_credits"}, "capabilities": [STEP]}
    assert list(part) == ["form", "capabilities"]


def test_the_line_is_a_registered_non_negative_amount_kind() -> None:
    kind = alberta_kinds().kind(KIND)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
