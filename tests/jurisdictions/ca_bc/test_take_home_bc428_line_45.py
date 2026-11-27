"""BC428 (2025) line 45, add lines 40 to 44, from the salary alone, real parts.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 45: Add lines 40 to 44. = ^". Lines 41
to 44 (student loan interest, tuition and transfers) are not built, so line 45 is one core/sum over
line 40 alone, as Alberta line 43 is over its built lines only; the sum of one part reads it back
unchanged, the trace recording the step.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the
real line 16, 25, 27, 29, 33, 35, 37 and 40 parts, the line 36 input part and the new
`bc428_line_45.yaml`, and types in only the salary. The form declaration is made up here, exporting
only line 45. The figures are hand-computed from the printed forms (not a CRA example): line 40 is
line 37, which is line 35 plus the pension income amount of 0.
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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_SUBTOTAL_LINE_45,
)
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc428_line_45.yaml"
IDENTIFIER = "ca-bc/bc428_subtotal_line_45"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_subtotal_line_45
    capabilities: []
    """)

# salary, line 40 (line 37, line 35 plus a blank line 36). At $200,000 lines 27 and 29 are at their
# maximums.
CASES = [
    ("17000", "13879.05"),
    ("200000", "17365.58"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("t1_employment_income")
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield from form_parts("t1_taxable_income", "t1_lines_copied_by_provinces")
    yield BC_PARTS / "bc428_line_16.yaml"
    yield BC_PARTS / "bc428_line_17_worksheet_lines_1_to_3.yaml"
    yield BC_PARTS / "bc428_line_17_worksheet_lines_4_to_7.yaml"
    yield BC_PARTS / "bc428_line_17.yaml"
    yield BC_PARTS / "bc428_line_25.yaml"
    yield BC_PARTS / "bc428_line_27.yaml"
    yield BC_PARTS / "bc428_line_29.yaml"
    yield BC_PARTS / "bc428_line_33.yaml"
    yield BC_PARTS / "bc428_line_35.yaml"
    yield BC_PARTS / "bc428_line_36_input.yaml"
    yield BC_PARTS / "bc428_line_36.yaml"
    yield BC_PARTS / "bc428_line_37.yaml"
    yield BC_PARTS / "bc428_line_40.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(dict.fromkeys(_part_files()), start=2):
        text = found.read_text(encoding="utf-8")
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


def _line_45(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-BC"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet.get(BC428_SUBTOTAL_LINE_45).value


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_45_reads_line_40_back_unchanged(tmp_path: Path, salary: str, expected: str) -> None:
    assert _line_45(tmp_path, salary) == D(expected)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_line_40_alone() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "45",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {"parts": ["ca-bc/bc428_subtotal_line_40"]},
        "produces": {"output": IDENTIFIER},
    }


def test_line_45_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert kind is BC428_SUBTOTAL_LINE_45
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
