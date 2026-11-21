"""BC428 (2025) line 80, line 72 minus line 79 (not below 0), from the real parts, real engine.

Form text (Form BC428, CRA 5010-C): Line 80: Line 72 minus line 79 (if negative, enter "0") = ^
The form prints no title for the line beyond its label, so the step is untitled.

Line 80 is one core/subtract_not_below_zero step (`bc428_line_80.yaml`), rounded through
`ca-bc/cent_rounding`, taking the British Columbia tax reduction on line 79
(`ca-bc/bc428_british_columbia_tax_reduction_line_79`) off the tax on line 72
(`ca-bc/bc428_tax_after_foreign_credit_line_72`). Neither input is ever blank (line 72 and line 79
are both calculated), so the step has no blank rule. The output is
`ca-bc/bc428_tax_after_reduction_line_80`, a non-negative kind on the form `ca-bc/bc428`.

The test composes the real parts that lead to line 72 (the salary, Schedule 8, T2204, the federal T1
taxable income parts, BC428 lines 1 to 72) and to line 79 (lines 74, 75, 76, 78, 73 and 79), plus
the new `bc428_line_80.yaml`. The header and the form declaration are made up here, because the
shared scaffold owns them.

Figures (hand-computed, not a CRA example), re-derived here. Line 72 equals line 70 with line 71
blank: the British Columbia bracket tax on the taxable income (line 1) less line 67, not below 0.
Line 79 is 562.00 less line 78, not below 0, where line 78 is (line 74 less 25,020.00, not below 0)
times 3.56%. At salaries of 17,000 / 30,000: line 72 is 151.09 / 758.96, line 79 is 562.00 / 394.15,
and line 80 is 0.00 / 364.81. A reduction above line 72 is floored at 0.00.
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
LINE_69 = "ca-bc/bc428_additional_minimum_tax_line_69"
LINE_70 = "ca-bc/bc428_tax_with_minimum_tax_line_70"
LINE_72 = "ca-bc/bc428_tax_after_foreign_credit_line_72"
LINE_73 = "ca-bc/bc428_basic_reduction_line_73"
LINE_74 = "ca-bc/bc428_net_income_line_74"
LINE_78 = "ca-bc/bc428_reduction_clawback_line_78"
LINE_79 = "ca-bc/bc428_british_columbia_tax_reduction_line_79"
LINE_80 = "ca-bc/bc428_tax_after_reduction_line_80"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc428_line_80.yaml"
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
# The real British Columbia parts after the federal ones, in composition order: the line 72 test's
# (lines 1 to 72), then the line 79 test's (lines 74, 75, 76, 78, 73 and 79), then line 80.
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
    "bc428_line_68.yaml",
    "bc428_line_69_input.yaml",
    "bc428_line_69.yaml",
    "bc428_line_70.yaml",
    "bc428_line_71_input.yaml",
    "bc428_line_72.yaml",
    *(f"bc428_line_{number}.yaml" for number in (74, 75, 76, 78, 73, 79)),
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
        - ca-bc/bc428_additional_minimum_tax_line_69
        - ca-bc/bc428_tax_with_minimum_tax_line_70
        - ca-bc/bc428_tax_after_foreign_credit_line_72
        - ca-bc/bc428_basic_reduction_line_73
        - ca-bc/bc428_net_income_line_74
        - ca-bc/bc428_reduction_clawback_line_78
        - ca-bc/bc428_british_columbia_tax_reduction_line_79
        - ca-bc/bc428_tax_after_reduction_line_80
    capabilities: []
    """)

# salary, taxable income (line 1 and line 74), line 67 (the line 67 test's figure), line 72 (line 70
# with line 71 blank), line 79 and the ticket's line 80 figure.
CASES = [
    ("17000", "16865", "702.28", "151.09", "562.00", "0.00"),
    ("30000", "29735", "745.63", "758.96", "394.15", "364.81"),
]
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


def _cent(value: Decimal) -> Decimal:
    return value.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def _bracket_tax(taxable_income: str) -> Decimal:
    """British Columbia tax on a taxable income, computed here independently of the engine."""
    income = D(taxable_income)
    total = D("0")
    for index, (lower, rate) in enumerate(BRACKETS):
        upper = BRACKETS[index + 1][0] if index + 1 < len(BRACKETS) else income
        if income > lower:
            total += (min(income, upper) - lower) * rate
    return _cent(total)


def _line_72(taxable_income: str, line_67: str) -> Decimal:
    """Line 72 with lines 69 and 71 at 0.00: the bracket tax less line 67, not below 0."""
    return max(_bracket_tax(taxable_income) - D(line_67), D("0.00"))


def _line_79(taxable_income: str) -> Decimal:
    """Line 79 re-derived: 562.00 less line 78, not below 0, line 78 being (line 74 less 25,020.00,
    not below 0) x 3.56% to the cent."""
    line_78 = _cent(max(D(taxable_income) - D("25020.00"), D("0.00")) * D("0.0356"))
    return max(D("562.00") - line_78, D("0.00"))


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


@pytest.mark.parametrize(
    ("salary", "taxable_income", "line_67", "line_72", "line_79", "expected"), CASES
)
def test_line_80_is_line_72_minus_line_79_not_below_zero_at_each_salary(
    tmp_path: Path,
    salary: str,
    taxable_income: str,
    line_67: str,
    line_72: str,
    line_79: str,
    expected: str,
) -> None:
    assert _line_72(taxable_income, line_67) == D(line_72)
    assert _line_79(taxable_income) == D(line_79)
    assert max(D(line_72) - D(line_79), D("0.00")) == D(expected)

    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_amount_kind(LINE_72)).value == D(line_72)
    assert sheet.get(_amount_kind(LINE_79)).value == D(line_79)
    result = sheet.get(_amount_kind(LINE_80))
    assert not result.is_blank
    assert result.value == D(expected)
    assert str(result.value) == expected
    assert result.value.as_tuple().exponent == -2
    assert not result.value.is_signed()


def test_line_80_is_0_when_line_79_is_above_line_72(tmp_path: Path) -> None:
    # At 17,000 line 72 is 151.09 and line 79 is 562.00: the floor.
    sheet = _sheet(tmp_path, "17000")

    assert sheet.get(_amount_kind(LINE_79)).value > sheet.get(_amount_kind(LINE_72)).value
    line_80 = sheet.get(_amount_kind(LINE_80)).value
    assert line_80 == D("0.00")
    assert str(line_80) == "0.00"
    assert not line_80.is_signed()


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "30000")
    kinds = british_columbia_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_80)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_80),
        minuend=kinds.kind(LINE_72),
        minuend_amount=D("758.96"),
        subtrahend=kinds.kind(LINE_79),
        subtrahend_amount=D("394.15"),
        rounding=_rounding().rounding,
        result=D("364.81"),
    )


@pytest.mark.parametrize(
    ("line_72", "line_79", "expected"),
    [
        ("758.96", "394.15", "364.81"),
        ("151.09", "562.00", "0.00"),
    ],
)
def test_line_80_is_line_72_minus_line_79_not_below_zero_to_the_cent(
    line_72: str, line_79: str, expected: str
) -> None:
    kinds = (_amount_kind(LINE_72), _amount_kind(LINE_79), _amount_kind(LINE_80))
    capability = SubtractNotBelowZero(_rounding(), *kinds)
    result = capability.compute((Artifact(kinds[0], D(line_72)), Artifact(kinds[1], D(line_79))))

    (output,) = result.outputs
    assert output.value == D(expected)
    assert D(expected) == max(D(line_72) - D(line_79), D("0.00"))


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_subtract_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": TAX}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "80",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_72, "less": LINE_79},
        "produces": {"output": LINE_80},
    }
    assert "title" not in step
    assert "blank" not in step


def test_line_80_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_80 in kinds.identifiers()
    kind = kinds.kind(LINE_80)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC428_TAX_AFTER_REDUCTION_LINE_80"]
