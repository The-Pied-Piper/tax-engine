"""AB428 (2025) line 36, add lines 33 to 35, from the salary alone, real parts.

Form text (Form AB428, CRA 5009-c-25e.txt, read 2026-11-12): "Line 34 and line 58360: Pension
income amount (maximum $1,719)", "Line 35 and line 58400: Caregiver amount (use Worksheet AB428)"
and "Line 36: Add lines 33 to 35 = ^". Line 35, the caregiver amount, is not built (Ontario skips
its equivalent), so line 36 is one core/sum over line 33 then the line 34 pension income amount
input, which a salary-only caller leaves out and the input part reads as 0.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real line
16, line 25, line 27, line 29, line 32 and line 33 parts, the line 34 inputs part and the new
`ab428_credits_line_36.yaml`, and types in only the salary (and, in one test, the pension income
amount). The form declaration is made up here, exporting only line 36. The figures are
hand-computed from the printed forms (not a CRA example): line 33 is 22,323.00 plus line 32 at
every salary, plus the pension income amount of 0.
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
import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_CREDITS_SUBTOTAL_LINE_36,
    AB428_PENSION_INCOME_AMOUNT,
)
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
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = ALBERTA_PARTS / "ab428_credits_line_36.yaml"
IDENTIFIER = "ca-ab/ab428_credits_subtotal_line_36"

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
        - ca-ab/ab428_credits_subtotal_line_36
    capabilities: []
    """)

# salary, line 36: line 33 (22,323.00 plus line 32 of 1,144.75, 4,369.23 and 4,433.58) plus line 34
# of 0 (left out); line 35 is not built.
CASES = [("20000", "23467.75"), ("70000", "26692.23"), ("200000", "26756.58")]


def _part_files() -> Iterator[Path]:
    yield ALBERTA_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    yield ALBERTA_PARTS / "ab428_line_16.yaml"
    yield ALBERTA_PARTS / "ab428_line_25.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_27.yaml"
    yield ALBERTA_PARTS / "ab428_line_29.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_32.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_33.yaml"
    yield ALBERTA_PARTS / "ab428_line_34_inputs.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, a form declaration and the
    real part files, every other namespace being the Alberta package list's own."""
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
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _line_36(tmp_path: Path, salary: str, pension: str | None = None) -> Decimal:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if pension is not None:
        given.append(Artifact(AB428_PENSION_INCOME_AMOUNT, D(pension)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, *given)
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    return sheet.get(AB428_CREDITS_SUBTOTAL_LINE_36).value


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_36_adds_line_33_and_the_blank_line_34_read_as_0(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _line_36(tmp_path, salary) == D(expected)


def test_line_36_adds_a_given_pension_income_amount_to_line_33(tmp_path: Path) -> None:
    # Line 33 at a 70,000 salary is 26,692.23; line 34 of 1,000.00 makes 27,692.23.
    assert _line_36(tmp_path, "70000", "1000.00") == D("27692.23")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_like_ontario_line_28() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428_credits"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "36",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ab/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-ab/ab428_credits_subtotal_line_33",
                "ca-ab/ab428_pension_income_amount",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_line_36_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = alberta_kinds().kind(IDENTIFIER)

    assert kind is AB428_CREDITS_SUBTOTAL_LINE_36
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
