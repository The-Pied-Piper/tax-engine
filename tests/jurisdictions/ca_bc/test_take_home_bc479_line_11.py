"""BC479 (2025) line 11, line 9 plus line 10, from the salary alone, real parts.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14): "Line 11: Line 9 plus line 10 = ^". Line 9 is
the basic sales tax credit (`ca-bc/bc479_basic_sales_tax_credit_line_9`, claim $75). Line 10, the
spouse or common-law partner additional credit (claim $75, the `ca-bc/sales_tax_credit_spouse`
dataset), is the spouse branch and is not built for a single filer, as line 7's $18,000 branch is
not. Line 11 is one core/sum over line 9, untitled because the form prints no title after the line
number.

The test composes the real line 9 part, the T1's copied-lines form (line 9 reads the year of
birth from it; none is typed in, so line 9 is claimed in full) and the new `bc479_line_11.yaml`, and
types in only the salary. The form declaration is made up here, exporting only line 11. The figures
are hand-computed from the printed form (not a CRA example): line 11 is line 9, 75.00, at every
salary.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_bc.catalog import BC479_CREDIT_BEFORE_REDUCTION_LINE_11
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
LINE_PART = BC_PARTS / "bc479_line_11.yaml"
PARTS = (
    *form_parts("t1_lines_copied_by_provinces"),
    BC_PARTS / "bc479_line_9.yaml",
    LINE_PART,
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc479
      required: true
      exports:
        - ca-bc/bc479_credit_before_reduction_line_11
    """)

SALARIES = ["17000", "200000"]


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(dict.fromkeys(PARTS), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
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


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(TaxCalculationRequest(JurisdictionCode("CA-BC"), 2025))
    (sheet,) = worksheets["ca-bc/bc479"]
    return sheet


@pytest.mark.parametrize("salary", SALARIES)
def test_line_11_is_line_9_for_a_single_filer(tmp_path: Path, salary: str) -> None:
    value = _sheet(tmp_path, salary).get(BC479_CREDIT_BEFORE_REDUCTION_LINE_11).value

    assert value == D("75.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_over_line_9() -> None:
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
        "produces",
    ]
    assert "title" not in step
    assert step == {
        "name": "core/sum",
        "reference": "11",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-bc/bc479_basic_sales_tax_credit_line_9",
            ]
        },
        "produces": {"output": BC479_CREDIT_BEFORE_REDUCTION_LINE_11.identifier},
    }


def test_line_11_is_a_registered_non_negative_amount_kind() -> None:
    identifier = "ca-bc/bc479_credit_before_reduction_line_11"
    kind = british_columbia_kinds().kind(identifier)

    assert BC479_CREDIT_BEFORE_REDUCTION_LINE_11.identifier == identifier
    assert kind is BC479_CREDIT_BEFORE_REDUCTION_LINE_11
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
