"""BC479 (2025) line 13, the sales tax credit, from the salary alone, real parts.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14, as recorded on the ticket): "Line 13: Line 11
minus line 12 (if negative, enter "0") Sales tax credit = ^". So line 13 is one
core/subtract_not_below_zero step (`bc479_line_13.yaml`), rounded through `ca-bc/cent_rounding`,
titled "Sales tax credit" with reference "13". It consumes line 11
(`ca-bc/bc479_credit_before_reduction_line_11`) as the amount and line 12
(`ca-bc/bc479_income_reduction_line_12`) as `less`, and produces
`ca-bc/bc479_sales_tax_credit_line_13`, a non-negative kind. Lines 11 and 12 are never blank, so the
step has no blank declaration.

The test composes the real British Columbia salary part, the real Schedule 8 parts, the real T1
taxable income parts, the real line 1 to line 12 parts and the new line 13 part, and types in only
the salary. The form declaration is made up here, exporting only line 13.

Figures (hand-computed from the printed forms, not a CRA example): line 11 is 75.00 (the spouse
branch of line 10 is not built) and line 12 is 37.30 / 96.70 at 17,000 / 20,000, so line 13 is 37.70
at 17,000 and 0.00 at 20,000 (and every higher salary). At 10,000 line 12 is 0.00, so line 13 is the
whole 75.00.
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
import tax_engine.jurisdictions.ca_bc.catalog as bc_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
)
from tests.federal_forms import form_part_names, form_parts
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
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc479"
LINE_11 = "ca-bc/bc479_credit_before_reduction_line_11"
LINE_12 = "ca-bc/bc479_income_reduction_line_12"
LINE_13 = "ca-bc/bc479_sales_tax_credit_line_13"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc479_line_13.yaml"
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_13}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield _federal(name)
    yield BC_PARTS / "bc479_line_1.yaml"
    yield BC_PARTS / "bc479_line_2_input.yaml"
    yield BC_PARTS / "bc479_line_3.yaml"
    yield BC_PARTS / "bc479_line_4_input.yaml"
    yield BC_PARTS / "bc479_line_5.yaml"
    yield BC_PARTS / "bc479_line_6.yaml"
    yield BC_PARTS / "bc479_line_7.yaml"
    yield BC_PARTS / "bc479_line_8.yaml"
    yield BC_PARTS / "bc479_line_9.yaml"
    yield BC_PARTS / "bc479_line_11.yaml"
    yield BC_PARTS / "bc479_line_12.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _rounding() -> Any:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


# salary, line 13 (line 11 of 75.00 less line 12, not below 0).
CASES = [
    ("17000", "37.70"),
    ("20000", "0.00"),
]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_13_is_line_11_less_line_12_for_a_single_filer(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_13 = _sheet(tmp_path, salary).get(_kind(LINE_13)).value

    assert line_13 == D(expected)
    assert str(line_13) == expected
    assert line_13.as_tuple().exponent == -2
    assert not line_13.is_signed()


def test_line_13_is_the_whole_credit_when_line_12_is_0(tmp_path: Path) -> None:
    # Line 8 is floored at 0 at a salary of 10,000, so line 12 is 0.00 and line 13 is line 11.
    sheet = _sheet(tmp_path, "10000")

    assert sheet.get(_kind(LINE_12)).value == D("0.00")
    assert sheet.get(_kind(LINE_13)).value == D("75.00")


def test_line_13_is_a_computed_zero_when_line_12_exceeds_line_11(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert sheet.get(_kind(LINE_12)).value > sheet.get(_kind(LINE_11)).value
    line_13 = sheet.get(_kind(LINE_13))
    assert not line_13.is_blank
    assert line_13.value == D("0.00")
    assert str(line_13.value) == "0.00"


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "17000")
    kinds = british_columbia_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_13)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_13),
        minuend=kinds.kind(LINE_11),
        minuend_amount=D("75.00"),
        subtrahend=kinds.kind(LINE_12),
        subtrahend_amount=D("37.30"),
        rounding=_rounding().rounding,
        result=D("37.70"),
    )


@pytest.mark.parametrize(
    ("line_11", "line_12", "expected"),
    [
        ("75.00", "37.30", "37.70"),
        ("75.00", "96.70", "0.00"),
    ],
)
def test_line_13_is_line_11_minus_line_12_not_below_zero_to_the_cent(
    line_11: str, line_12: str, expected: str
) -> None:
    kinds = (_kind(LINE_11), _kind(LINE_12), _kind(LINE_13))
    capability = SubtractNotBelowZero(_rounding(), *kinds)
    result = capability.compute((Artifact(kinds[0], D(line_11)), Artifact(kinds[1], D(line_12))))

    (output,) = result.outputs
    assert output.value == D(expected)
    assert D(expected) == max(D(line_11) - D(line_12), D("0.00"))


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_titled_subtract_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "title": "Sales tax credit",
        "reference": "13",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_11, "less": LINE_12},
        "produces": {"output": LINE_13},
    }
    assert "blank" not in step


def test_line_13_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_13 in kinds.identifiers()
    kind = kinds.kind(LINE_13)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC479_SALES_TAX_CREDIT_LINE_13"]
