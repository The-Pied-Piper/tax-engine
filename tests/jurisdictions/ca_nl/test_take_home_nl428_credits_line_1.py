"""NL428 (2025) line 1, taxable income, from the salary alone, real parts.

Form text (Form NL428, CRA 5001-C, confirmed 2026-11-18): "Line 1: Enter your taxable income from
line 26000 of your return." Line 1 is a calculation, not an input: its one step is a
core/record_total over the T1 export that gives taxable income
(`ca/t1_taxable_income.taxable_income`), as Saskatchewan's and Manitoba's line 1 are. The form
prints no label for the line, so the step has no title. Line 2 in each column is a copy of line 1
and has no step.

The test composes the real Schedule 8 parts, the real T1 taxable income parts and the real line
part (`nl428_credits_line_1.yaml`), and types in only the salary. The header, the salary input and
the form declaration are made up here (Newfoundland and Labrador has no salary part), the form
exporting the line read, because the real form part exports only the lines already built.

The expected figures are computed here, not typed: taxable income (equal to net income) is the
salary less the enhanced CPP deduction, 1% of the pensionable earnings between the $3,500 basic
exemption and the $71,300 year's maximum pensionable earnings, plus the second additional CPP
contribution, 4% of the earnings between $71,300 and $81,200, each rounded half-up to the cent.
The two hand figures are asserted too (not a CRA example).
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.catalog as nl_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CENT = D("0.01")
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = NL_PARTS / "nl428_credits_line_1.yaml"
FORM_NAME = "ca-nl/nl428_credits"
KIND = "ca-nl/nl428_taxable_income_line_1"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_taxable_income_line_1
    capabilities: []
    """)

CASES = [
    ("20000", "19835.00"),
    ("200000", "198926.00"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-NL"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line_1(tmp_path: Path, salary: str) -> Decimal:
    return D(_sheet(tmp_path, salary).get(newfoundland_kinds().kind(KIND)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _taxable_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_1_is_the_t1_taxable_income(tmp_path: Path, salary: str, expected: str) -> None:
    assert _taxable_income(D(salary)) == D(expected)
    line_1 = _line_1(tmp_path, salary)

    assert line_1 == _taxable_income(D(salary))
    assert line_1 == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_record_total_step_over_the_t1_taxable_income() -> None:
    assert _step() == {
        "name": "core/record_total",
        "reference": "1",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.taxable_income"},
        "produces": {"output": KIND},
    }


def test_line_1_is_a_registered_non_negative_amount_kind() -> None:
    kinds = newfoundland_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is nl_catalog.NL428_TAXABLE_INCOME_LINE_1
