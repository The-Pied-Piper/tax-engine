"""BC479 (2025) line 3, line 1 plus line 2, from the salary alone, real parts.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14): "Line 3: Line 1 plus line 2". Line 1 is the
signed net income (`ca-bc/bc479_net_income_line_1`) and line 2 is the UCCB and RDSP repayments
input (`ca-bc/bc479_uccb_rdsp_repayments_line_2`), which a salary-only caller leaves out, read as
blank and then as 0 by the step's own blank rule, as the line 58 step reads its line 57. Line 3 is
one core/sum over line 1 and line 2; the result is signed, because line 1 is.

The test composes the real British Columbia salary part, the real Schedule 8 parts, the real T1
taxable income parts, the real line 1 and line 2 parts and the new `bc479_line_3.yaml`, and types in
only the salary (and, in one test, line 2, and in another, line 23500 for a negative line 1). The
form declaration is made up here, exporting only line 3. The figures are hand-computed from the
printed forms (not a CRA example): with line 2 blank, line 3 is line 1.
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
    BC479_INCOME_WITH_REPAYMENTS_LINE_3,
    BC479_UCCB_RDSP_REPAYMENTS_LINE_2,
)
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
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc479_line_3.yaml"
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)

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
      name: ca-bc/bc479
      required: true
      exports:
        - ca-bc/bc479_income_with_repayments_line_3
    capabilities: []
    """)

# salary, line 3 (line 1 with line 2 blank). The figures are line 1 of the same salary.
CASES = [
    ("17000", "16865.00"),
    ("200000", "198926.00"),
]


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield BC_PARTS / "bc479_line_1.yaml"
    yield BC_PARTS / "bc479_line_2_input.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{part.name}").write_text(text, encoding="utf-8")
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
    (sheet,) = worksheets["ca-bc/bc479"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_3_is_line_1_when_line_2_is_blank(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(BC479_INCOME_WITH_REPAYMENTS_LINE_3).value == D(expected)


def test_line_3_adds_line_2_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(BC479_UCCB_RDSP_REPAYMENTS_LINE_2, D("100.50")),
    )

    assert sheet.get(BC479_INCOME_WITH_REPAYMENTS_LINE_3).value == D("69435.50")


def test_line_3_stays_negative_when_line_1_is_negative(tmp_path: Path) -> None:
    # Line 23500 of 75,000 is more than line 23400 of 69,335.00, so line 1 is -5,665.00. Line 3 is
    # line 1 plus a blank line 2, so it keeps the negative sum: the kind is signed.
    kinds = british_columbia_kinds()
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(kinds.kind("ca/social_benefits_repayment"), D("75000")),
    )

    assert sheet.get(BC479_INCOME_WITH_REPAYMENTS_LINE_3).value == D("-5665.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_line_1_and_line_2() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc479"}
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
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "reference": "3",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-bc/bc479_net_income_line_1",
                "ca-bc/bc479_uccb_rdsp_repayments_line_2",
            ]
        },
        "blank": {"ca-bc/bc479_uccb_rdsp_repayments_line_2": "0"},
        "produces": {"output": BC479_INCOME_WITH_REPAYMENTS_LINE_3.identifier},
    }


def test_line_3_is_a_registered_signed_amount_kind() -> None:
    kind = british_columbia_kinds().kind(BC479_INCOME_WITH_REPAYMENTS_LINE_3.identifier)

    assert kind is BC479_INCOME_WITH_REPAYMENTS_LINE_3
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert not non_negative(kind)
