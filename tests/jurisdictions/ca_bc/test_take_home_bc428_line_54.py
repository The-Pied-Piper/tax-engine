"""BC428 (2025) line 54, line 45 plus line 53, from the salary alone, real parts.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 54 and line 58800: Line 45 plus line 53
= ^". Line 53 (medical expenses) is computed from lines 46 to 52 and is 0.00 for a salary-only caller;
line 54 is one core/sum over line 45 and line 53.

The test composes the real British Columbia salary part, the real Schedule 8 and T2204 parts, the
real line 16, 25, 27, 29, 33, 35, 37, 40 and 45 parts, the line 36 and line 53 input parts and the
new `bc428_line_54.yaml`, and types in only the salary (and, in one test, line 53). The form
declaration is made up here, exporting only line 54. The figures are hand-computed from the printed
forms (not a CRA example): with line 53 at 0.00, line 54 is line 45, which is line 40.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_52,
    BC428_TOTAL_LINE_54,
)
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc428_line_54.yaml"
IDENTIFIER = "ca-bc/bc428_total_line_54"

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
        - ca-bc/bc428_total_line_54
    capabilities: []
    """)

# salary, line 54 (line 45, which is line 40, plus a line 53 of 0.00). At $200,000 lines 27 and 29 are
# at their maximums.
CASES = [
    ("17000", "13879.05"),
    ("200000", "17365.58"),
]


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
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
    yield BC_PARTS / "bc428_line_46_input.yaml"
    yield BC_PARTS / "bc428_line_47.yaml"
    yield BC_PARTS / "bc428_line_49.yaml"
    yield BC_PARTS / "bc428_line_50.yaml"
    yield BC_PARTS / "bc428_line_51.yaml"
    yield BC_PARTS / "bc428_line_52_input.yaml"
    yield BC_PARTS / "bc428_line_53.yaml"
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
def test_line_54_is_line_45_when_line_53_is_zero(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(BC428_TOTAL_LINE_54).value == D(expected)


def test_line_54_adds_line_53_when_line_52_is_given(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path, "70000", Artifact(BC428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_52, D("1500.00"))
    )

    assert sheet.get(BC428_TOTAL_LINE_54).value == D("18801.23")


def _part() -> dict[str, object]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_line_45_and_line_53() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    capabilities = part["capabilities"]
    assert isinstance(capabilities, list)
    (step,) = capabilities
    assert isinstance(step, dict)
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "reference": "54",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {
            "parts": ["ca-bc/bc428_subtotal_line_45", "ca-bc/bc428_medical_expenses_line_53"]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_line_54_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert kind is BC428_TOTAL_LINE_54
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
