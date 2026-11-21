"""BC428 (2025) line 37, add lines 35 and 36, from the salary alone, real parts.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 36 and line 58360: Pension income
amount (maximum $1,000)" and "Line 37: Line 35 plus line 36 = ^". Line 36, the pension income
amount, is an entry rejected above its printed maximum by `bc428_line_36.yaml`; line 37 is one
core/sum over line 35 then the line 36 kind that step passes on. A salary-only caller leaves line 36
out, the input part reads it as blank, line 36 passes it on as blank, and line 37 reads that as 0.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the
real line 16, 25, 27, 29, 33 and 35 parts, the line 36 input part and the new `bc428_line_37.yaml`,
and types in only the salary (and, in one test, the pension income amount). The form declaration
is made up here, exporting only line 37. The figures are hand-computed from the printed forms (not
a CRA example): line 35 plus the pension income amount of 0.
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
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_PENSION_INCOME_AMOUNT,
    BC428_SUBTOTAL_LINE_37,
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
LINE_PART = BC_PARTS / "bc428_line_37.yaml"
IDENTIFIER = "ca-bc/bc428_subtotal_line_37"

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
        - ca-bc/bc428_subtotal_line_37
    capabilities: []
    """)

# salary, line 35 (12,932.00 plus line 33). At $200,000 lines 27 and 29 are at their maximums.
CASES = [
    ("17000", "13879.05"),
    ("200000", "17365.58"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("t1_employment_income")
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield BC_PARTS / "bc428_line_16.yaml"
    yield BC_PARTS / "bc428_line_25.yaml"
    yield BC_PARTS / "bc428_line_27.yaml"
    yield BC_PARTS / "bc428_line_29.yaml"
    yield BC_PARTS / "bc428_line_33.yaml"
    yield BC_PARTS / "bc428_line_35.yaml"
    yield BC_PARTS / "bc428_line_36_input.yaml"
    yield BC_PARTS / "bc428_line_36.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
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


def _line_37(tmp_path: Path, salary: str, pension: str | None = None) -> Decimal:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if pension is not None:
        given.append(Artifact(BC428_PENSION_INCOME_AMOUNT, D(pension)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-BC"), 2025, *given)
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet.get(BC428_SUBTOTAL_LINE_37).value


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_37_adds_line_35_and_the_blank_line_36_read_as_0(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _line_37(tmp_path, salary) == D(expected)


def test_line_37_adds_a_given_pension_income_amount_to_line_35(tmp_path: Path) -> None:
    # Line 35 at a 70,000 salary is 17,301.23; line 36 of 1,000.00 makes 18,301.23.
    assert _line_37(tmp_path, "70000", "1000.00") == D("18301.23")


def test_line_37_is_refused_a_pension_income_amount_above_the_maximum(tmp_path: Path) -> None:
    # Line 36 is rejected above its printed maximum of 1,000.00, so line 37 never adds it.
    with pytest.raises(InputAboveBoundError):
        _line_37(tmp_path, "70000", "1000.01")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_line_35_and_the_line_36_kind() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "37",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-bc/bc428_subtotal_line_35",
                "ca-bc/bc428_pension_income_amount_line_36",
            ]
        },
        "blank": {"ca-bc/bc428_pension_income_amount_line_36": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_37_consumes_the_line_36_kind_not_the_input_kind() -> None:
    (step,) = _part()["capabilities"]

    assert "ca-bc/bc428_pension_income_amount" not in step["consumes"]["parts"]
    assert "ca-bc/bc428_pension_income_amount" not in step["blank"]
    assert step["consumes"]["parts"][1] == "ca-bc/bc428_pension_income_amount_line_36"
    assert step["blank"] == {"ca-bc/bc428_pension_income_amount_line_36": "0"}


def test_line_37_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert kind is BC428_SUBTOTAL_LINE_37
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
