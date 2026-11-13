"""AB428 (2025) line 54, line 52 multiplied by the line 53 rate of 8%, from the salary alone.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 53: Alberta non-refundable tax credit rate 8%" and
"Line 54 and line 58840: Line 52 multiplied by the percentage from line 53 = ^". Line 53 is a
printed rate, so it is the `ca-ab/credit_rate` dataset figure and has no step of its own; line 54
is one core/apply_rate step over line 52, rounded half-up to the cent by the dataset's own rule, as
Ontario line 46 is over line 45. Line 54 prints no name, so the step has no title.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real line
16, line 25, line 27, line 29, line 32, line 33, line 36, line 39, line 43 and line 52 parts, the
line 34 inputs part, the line 41 input part, the line 51 inputs part and the new
`ab428_credits_line_54.yaml`, and types in only the salary (and, in one test, line 51). The form
declaration is made up here, exporting only line 54. The figures are hand-computed from the
printed forms (not a CRA example): line 52 is 23,467.75, 26,692.23 and 26,756.58 at the three
salaries, times 0.08, half-up to the cent.
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
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_CREDITS_AT_RATE_LINE_54,
    AB428_MEDICAL_EXPENSES_LINE_51,
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
LINE_PART = ALBERTA_PARTS / "ab428_credits_line_54.yaml"
IDENTIFIER = "ca-ab/ab428_credits_at_rate_line_54"

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
        - ca-ab/ab428_credits_at_rate_line_54
    capabilities: []
    """)

# salary, line 54: line 52 (23,467.75, 26,692.23 and 26,756.58, as the line 52 test pins) times
# 0.08, half-up to the cent: 1,877.42 (1,877.4200), 2,135.38 (2,135.3784) and 2,140.53 (2,140.5264).
CASES = [("20000", "1877.42"), ("70000", "2135.38"), ("200000", "2140.53")]


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
    yield ALBERTA_PARTS / "ab428_credits_line_36.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_39.yaml"
    yield ALBERTA_PARTS / "ab428_line_41_input.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_43.yaml"
    yield ALBERTA_PARTS / "ab428_line_51_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_52.yaml"
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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, *given)
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_54_is_line_52_times_8_percent(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(AB428_CREDITS_AT_RATE_LINE_54).value == D(expected)


def test_line_54_follows_line_51_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_MEDICAL_EXPENSES_LINE_51, D("1500.00")))

    # Line 52 is 28,192.23; times 0.08 is 2,255.3784, rounded half-up to 2,255.38.
    assert sheet.get(AB428_CREDITS_AT_RATE_LINE_54).value == D("2255.38")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_apply_rate_step_like_ontario_line_46() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428_credits"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "54",
        "unit": "ca/cad",
        "params": {"rate": "ca-ab/credit_rate"},
        "consumes": {"base": "ca-ab/ab428_credits_total_line_52"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_54_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = alberta_kinds().kind(IDENTIFIER)

    assert kind is AB428_CREDITS_AT_RATE_LINE_54
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
