"""AB428 (2025) line 48, from the salary and the optional inputs, from real parts.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 48: Enter whichever is less: $2,884 or the
amount from line 47.". The part is one core/capped_amount step against the printed ceiling; the
figures are hand-computed from the printed form (not a CRA example): a $70,000 salary has net
income 69,335.00 (the salary less the enhanced CPP deduction).
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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab import catalog as ab
from tests.federal_forms import FEDERAL_FORMS, form_parts
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
# The real parts this line needs, beside the salary, Schedule 8 and the T1 taxable income parts.
LINE_PARTS = (
    "ab428_credits_line_45.yaml",
    "ab428_credits_line_47.yaml",
    "ab428_credits_line_48.yaml",
)
INPUTS = {
    "line_44": ab.AB428_MEDICAL_EXPENSES_LINE_44,
    "line_50": ab.AB428_ALLOWABLE_MEDICAL_EXPENSES_FOR_OTHER_DEPENDANTS_LINE_50,
    "line_55": ab.AB428_DONATIONS_AMOUNT_LINE_55,
    "line_56": ab.AB428_DONATIONS_AMOUNT_LINE_56,
}

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/ab428_medical_expenses_limited_amount_line_48
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield ALBERTA_PARTS / "salary.yaml"
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
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
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


def _sheet(tmp_path: Path, salary: str, **given: str) -> Worksheet:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(INPUTS[name], D(value)) for name, value in given.items()]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, *artifacts)
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    value = sheet.get(alberta_kinds().kind(identifier)).value
    assert isinstance(value, Decimal)
    return value


PART = ALBERTA_PARTS / "ab428_credits_line_48.yaml"
KIND = "ca-ab/ab428_medical_expenses_limited_amount_line_48"
STEP: dict[str, Any] = {
    "name": "core/capped_amount",
    "reference": "48",
    "unit": "ca/cad",
    "params": {"cap": "ca-ab/medical_expense_dollar_limit"},
    "consumes": {"base": "ca-ab/ab428_medical_expenses_rate_amount_line_47"},
    "produces": {"output": "ca-ab/ab428_medical_expenses_limited_amount_line_48"},
}

# salary, given inputs, expected line
CASES: list[tuple[str, dict[str, str], str]] = [
    ("20000", {}, "595.05"),
    ("70000", {}, "2080.05"),
    ("200000", {}, "2884.00"),
]


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_the_line_is_ab428_medical_expenses_limited_amount_line_48_at_each_case(
    tmp_path: Path, salary: str, given: dict[str, str], expected: str
) -> None:
    assert _value(_sheet(tmp_path, salary, **given), KIND) == D(expected)


def test_the_part_names_the_form_and_is_one_step_as_the_form_prints_the_line() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part == {"form": {"name": "ca-ab/ab428_credits"}, "capabilities": [STEP]}
    assert list(part) == ["form", "capabilities"]


def test_the_line_is_a_registered_non_negative_amount_kind() -> None:
    kind = alberta_kinds().kind(KIND)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
