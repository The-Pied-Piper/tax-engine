"""BC428 (2025) line 68, line 63 minus line 67 (not below 0), from the real parts, real engine.

Form text (Form BC428, CRA 5010-C): Line 68: Line 63 minus line 67 (if negative, enter "0") = ^
The form prints no title for the line beyond its label, so the step is untitled.

Line 68 is one core/subtract_not_below_zero step (`bc428_line_68.yaml`), rounded through
`ca-bc/cent_rounding`, with `amount` line 63 (`ca-bc/bc428_tax_with_split_income_line_63`, signed)
and `less` line 67 (`ca-bc/bc428_total_line_67`, non-negative). Both inputs are always computed, so
the step has no blank rule and prints no blank row. The form floors line 68 at 0 (printed), so the
output `ca-bc/bc428_tax_after_credits_line_68` is a non-negative kind on the form `ca-bc/bc428`.

The test composes the real salary, Schedule 8, T2204 and T1 taxable income parts, the real BC428
parts that lead to line 63 (lines 1 to 15, 61 to 63) and to line 67 (lines 16 to 60, 65 and 66) plus
the new `bc428_line_68.yaml`, and types in only the salary. The header and the form declaration
(BC428, exporting lines 63, 67 and 68) are made up here, because the shared scaffold owns them.

Figures (hand-computed, not a CRA example). Line 63 is recomputed in the test from the British
Columbia brackets over the taxable income (16,865 / 198,926 for a salary
of 17,000 / 200,000); line 67 is the line 67 test's figure (line 60, with
lines 65 and 66 blank). Line 68 is their difference in Decimal.
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
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc import catalog as bc_catalog
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_TAX_WITH_SPLIT_INCOME_LINE_63,
    BC428_TOTAL_LINE_67,
)
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
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
CODE = JurisdictionCode("CA-BC")
TAX = "ca-bc/bc428"
LINE_63 = "ca-bc/bc428_tax_with_split_income_line_63"
LINE_67 = "ca-bc/bc428_total_line_67"
LINE_68 = "ca-bc/bc428_tax_after_credits_line_68"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc428_line_68.yaml"
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
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)
# The real British Columbia parts after the federal ones, in composition order: the line 63 test's
# (lines 1 to 15, 61 to 63), then the line 67 test's (lines 16 to 60, 65 and 66, 67), then line 68.
BC_LINE_PARTS = (
    *(f"bc428_line_{number}.yaml" for number in (1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15)),
    "bc428_line_61.yaml",
    "bc428_line_62_input.yaml",
    "bc428_line_63.yaml",
    "bc428_line_16.yaml",
    "bc428_line_25.yaml",
    "bc428_line_27.yaml",
    "bc428_line_29.yaml",
    "bc428_line_33.yaml",
    "bc428_line_35.yaml",
    "bc428_line_36_input.yaml",
    "bc428_line_36.yaml",
    "bc428_line_37.yaml",
    "bc428_line_40.yaml",
    "bc428_line_45.yaml",
    "bc428_line_53_inputs.yaml",
    "bc428_line_54.yaml",
    "bc428_line_56.yaml",
    "bc428_line_57_input.yaml",
    "bc428_line_58.yaml",
    "bc428_line_59_input.yaml",
    "bc428_line_59.yaml",
    "bc428_line_60.yaml",
    "bc428_line_65_input.yaml",
    "bc428_line_66_input.yaml",
    "bc428_line_66.yaml",
    "bc428_line_67.yaml",
    LINE_PART.name,
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
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_tax_with_split_income_line_63
        - ca-bc/bc428_total_line_67
        - ca-bc/bc428_tax_after_credits_line_68
    capabilities: []
    """)

# salary, taxable income (line 1), line 67 (the line 67 test's figure), line 68. Line 63 is
# recomputed below from the brackets, not typed in.
CASES = [
    ("17000", "16865", "702.28", "151.09"),
    ("200000", "198926", "878.70", "19230.76"),
]
# Line 63 as the ticket hand-computed it (line 61 with line 62 blank), the line 63 test's figures.
LINE_63_FIGURES = {
    "17000": "853.37",
    "200000": "20109.46",
}
# The 2025 British Columbia brackets: lower bound and rate.
BRACKETS = [
    (D("0"), D("0.0506")),
    (D("49279"), D("0.077")),
    (D("98560"), D("0.105")),
    (D("113158"), D("0.1229")),
    (D("137407"), D("0.147")),
    (D("186306"), D("0.168")),
    (D("259829"), D("0.205")),
]


def _bracket_tax(taxable_income: str) -> Decimal:
    """British Columbia tax on a taxable income, computed here independently of the engine."""
    income = D(taxable_income)
    total = D("0")
    for index, (lower, rate) in enumerate(BRACKETS):
        upper = BRACKETS[index + 1][0] if index + 1 < len(BRACKETS) else income
        if income > lower:
            total += (min(income, upper) - lower) * rate
    return total.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    for name in T1_PARTS:
        yield _federal(name)
    for name in BC_LINE_PARTS:
        yield BC_PARTS / name


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


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[TAX]
    return sheet


def _rounding() -> Any:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _amount_kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("salary", "taxable_income", "line_67", "expected"), CASES)
def test_line_68_is_line_63_minus_line_67_not_below_zero_at_each_salary(
    tmp_path: Path, salary: str, taxable_income: str, line_67: str, expected: str
) -> None:
    line_63 = _bracket_tax(taxable_income)
    assert line_63 == D(LINE_63_FIGURES[salary])
    assert line_63 - D(line_67) == D(expected)

    sheet = _sheet(tmp_path, salary)

    # Lines 63 and 67 are recomputed from the real parts, not only taken from the ticket.
    assert sheet.get(BC428_TAX_WITH_SPLIT_INCOME_LINE_63).value == line_63
    assert sheet.get(BC428_TOTAL_LINE_67).value == D(line_67)
    line_68 = sheet.get(_amount_kind(LINE_68)).value
    assert line_68 == D(expected)
    assert line_68.as_tuple().exponent == -2


def test_line_68_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(_amount_kind(LINE_68)).is_blank
    # The step has no blank rule: no blank row names line 68.
    assert not [
        t
        for t in sheet.trace
        if isinstance(t, BlankPassedOnLine) and t.output is british_columbia_kinds().kind(LINE_68)
    ]


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = british_columbia_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_68)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_68),
        minuend=kinds.kind(LINE_63),
        minuend_amount=D("4037.83"),
        subtrahend=kinds.kind(LINE_67),
        subtrahend_amount=D("875.44"),
        rounding=_rounding().rounding,
        result=D("3162.39"),
    )


def _line_68_at(line_63_amount: str, line_67_amount: str) -> Artifact[Decimal]:
    """Line 68 over given lines 63 and 67: the capability the part builds, with the real dataset."""
    line_63, line_67, line_68 = _amount_kind(LINE_63), _amount_kind(LINE_67), _amount_kind(LINE_68)
    capability = SubtractNotBelowZero(_rounding(), line_63, line_67, line_68)
    result = capability.compute(
        (Artifact(line_63, D(line_63_amount)), Artifact(line_67, D(line_67_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_63", "line_67", "expected"),
    [
        # Line 63 above line 67: the difference.
        ("4037.83", "875.44", "3162.39"),
        # Line 63 below line 67: the floor.
        ("500.00", "702.28", "0.00"),
        # Line 63 is signed, so the floor also catches a negative minuend.
        ("-266.50", "875.44", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01.
        ("100.005", "100.00", "0.01"),
    ],
)
def test_line_68_is_line_63_minus_line_67_not_below_zero_to_the_cent(
    line_63: str, line_67: str, expected: str
) -> None:
    line_68 = _line_68_at(line_63, line_67).value

    assert line_68 == D(expected)
    assert str(line_68) == expected
    assert line_68.as_tuple().exponent == -2
    assert not line_68.is_signed()


def test_a_floored_zero_and_an_exact_equal_are_the_same_positive_cent_zero() -> None:
    below = _line_68_at("100.00", "4800.00").value
    equal = _line_68_at("4800.00", "4800.00").value

    assert str(below) == str(equal) == "0.00"
    assert not below.is_signed()
    assert not equal.is_signed()


def test_the_positive_row_traces_the_subtraction_with_the_rounding_named() -> None:
    kinds = british_columbia_kinds()
    line_63, line_67, line_68 = _amount_kind(LINE_63), _amount_kind(LINE_67), _amount_kind(LINE_68)
    result = SubtractNotBelowZero(_rounding(), line_63, line_67, line_68).compute(
        (Artifact(line_63, D("20109.46")), Artifact(line_67, D("878.70")))
    )

    (line,) = result.trace
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_68),
        minuend=kinds.kind(LINE_63),
        minuend_amount=D("20109.46"),
        subtrahend=kinds.kind(LINE_67),
        subtrahend_amount=D("878.70"),
        rounding=_rounding().rounding,
        result=D("19230.76"),
    )


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": TAX}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "68",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_63, "less": LINE_67},
        "produces": {"output": LINE_68},
    }
    assert "title" not in step


def test_line_68_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_68 in kinds.identifiers()
    kind = kinds.kind(LINE_68)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is bc_catalog.BC428_TAX_AFTER_CREDITS_LINE_68


def test_line_63_stays_signed_while_line_68_is_floored() -> None:
    assert not non_negative(BC428_TAX_WITH_SPLIT_INCOME_LINE_63)
    assert non_negative(_amount_kind(LINE_68))
