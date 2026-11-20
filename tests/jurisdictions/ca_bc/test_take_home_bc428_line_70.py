"""BC428 (2025) line 70, line 68 plus line 69, from the real parts, real engine.

Form text (Form BC428, CRA 5010-C): Line 70: Line 68 plus line 69 = ^
The form prints no title for the line beyond its label, so the step is untitled.

Line 70 is one core/sum step (`bc428_line_70.yaml`), rounded through `ca-bc/cent_rounding`, adding
line 68 (`ca-bc/bc428_tax_after_credits_line_68`) and line 69
(`ca-bc/bc428_additional_minimum_tax_line_69`), in that order. Both parts are always computed (line
69 reads its optional T691 amount as 0 when left out), so the step has no blank rule and prints no
blank row. The output is `ca-bc/bc428_tax_with_minimum_tax_line_70`, a non-negative kind on the
form `ca-bc/bc428`.

The test composes the real parts that lead to line 68 (the salary, Schedule 8, T2204, the federal
T1 taxable income parts and BC428 lines 1 to 68), the line 69 input part and line 69, plus the new
`bc428_line_70.yaml`. The header and the form declaration (BC428, exporting lines 63, 67, 68, 69 and
70) are made up here, because the shared scaffold owns them.

Figures (hand-computed, not a CRA example). Line 68 is recomputed in the test as the line 68 test
does (line 63 from the British Columbia brackets over the taxable income, less line 67). Line 69 is
0.00 when the T691 amount is left out, so line 70 equals line 68 at a salary of 17,000 /
200,000. With a T691 amount of 1,000.00 line 69 is 349.00 (34.9%), so line 70 is
line 68 plus 349.00.
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
from tax_engine.domain.trace import BlankPassedOnLine, SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
AMOUNT = "ca-bc/bc428_additional_minimum_tax_amount_line_69"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc428_line_70.yaml"
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_10100.yaml",
    "t1_taxable_income_line_10400.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
)
# The real British Columbia parts after the federal ones, in composition order: the line 68 test's
# (lines 1 to 68), then the line 69 input and line 69, then line 70.
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
    capabilities: []
    """)

# salary, taxable income (line 1), line 67 (the line 67 test's figure), line 68 (the line 68 test's
# figure, also the ticket's line 70 figure with line 69 at 0.00).
CASES = [
    ("17000", "16865", "702.28", "151.09"),
    ("200000", "198926", "878.70", "19230.76"),
]
# salary, taxable income, line 67, line 68, T691 amount, line 69 (34.9% of the amount), line 70.
CASES_WITH_AMOUNT = [
    ("17000", "16865", "702.28", "151.09", "1000.00", "349.00", "500.09"),
    # 1,234.56 x 34.9% = 430.86144, rounded half-up to 430.86 on line 69.
    ("70000", "69335", "875.44", "3162.39", "1234.56", "430.86", "3593.25"),
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


def _sheet(tmp_path: Path, salary: str, amount: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if amount is not None:
        given.append(Artifact(_amount_kind(AMOUNT), D(amount)))
    worksheets = _service(tmp_path).compute(CODE, 2025, *given)
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


def _line_68(taxable_income: str, line_67: str) -> Decimal:
    """Line 68 as the line 68 test computes it: the bracket tax less line 67, not below 0."""
    return max(_bracket_tax(taxable_income) - D(line_67), D("0.00"))


@pytest.mark.parametrize(("salary", "taxable_income", "line_67", "line_68"), CASES)
def test_line_70_is_line_68_at_each_salary_when_the_t691_amount_is_left_out(
    tmp_path: Path, salary: str, taxable_income: str, line_67: str, line_68: str
) -> None:
    assert _line_68(taxable_income, line_67) == D(line_68)

    sheet = _sheet(tmp_path, salary)

    got_68 = sheet.get(_amount_kind(LINE_68)).value
    got_69 = sheet.get(_amount_kind(LINE_69)).value
    assert got_68 == D(line_68)
    assert got_69 == D("0.00")
    line_70 = sheet.get(_amount_kind(LINE_70)).value
    assert line_70 == got_68 + got_69
    assert line_70 == D(line_68)
    assert str(line_70) == line_68
    assert line_70.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("salary", "taxable_income", "line_67", "line_68", "amount", "line_69", "expected"),
    CASES_WITH_AMOUNT,
)
def test_line_70_adds_line_69_when_the_t691_amount_is_given(
    tmp_path: Path,
    salary: str,
    taxable_income: str,
    line_67: str,
    line_68: str,
    amount: str,
    line_69: str,
    expected: str,
) -> None:
    assert _line_68(taxable_income, line_67) == D(line_68)
    assert D(line_68) + D(line_69) == D(expected)

    sheet = _sheet(tmp_path, salary, amount)

    got_68 = sheet.get(_amount_kind(LINE_68)).value
    got_69 = sheet.get(_amount_kind(LINE_69)).value
    assert got_68 == D(line_68)
    assert got_69 == D(line_69)
    line_70 = sheet.get(_amount_kind(LINE_70)).value
    assert line_70 == got_68 + got_69
    assert line_70 == D(expected)
    assert str(line_70) == expected
    assert line_70.as_tuple().exponent == -2


def test_line_70_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(_amount_kind(LINE_70)).is_blank
    # The step has no blank rule: both parts are always computed, so no row names line 70.
    assert not [
        t
        for t in sheet.trace
        if isinstance(t, BlankPassedOnLine) and t.output is british_columbia_kinds().kind(LINE_70)
    ]


def test_the_step_traces_one_sum_line_over_lines_68_and_69_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", "1000.00")
    kinds = british_columbia_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(LINE_70)]
    assert line == SumLine(
        output=kinds.kind(LINE_70),
        parts=((kinds.kind(LINE_68), D("3162.39")), (kinds.kind(LINE_69), D("349.00"))),
        rounding=_rounding().rounding,
        total=D("3511.39"),
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
        "name": "core/sum",
        "reference": "70",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_68, LINE_69]},
        "produces": {"output": LINE_70},
    }
    assert "title" not in step


def test_line_70_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_70 in kinds.identifiers()
    kind = kinds.kind(LINE_70)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC428_TAX_WITH_MINIMUM_TAX_LINE_70"]
