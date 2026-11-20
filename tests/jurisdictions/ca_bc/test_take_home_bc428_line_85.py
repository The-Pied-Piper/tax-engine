"""BC428 (2025) line 85, line 82 minus line 84 (not below 0), from the real parts, real engine.

Form text (Form BC428, CRA 5010-C): Line 85: Line 82 minus line 84 (if negative, enter "0") = ^
The form prints no title for the line beyond its label, so the step is untitled.

Line 85 is one core/subtract_not_below_zero step (`bc428_line_85.yaml`), rounded through
`ca-bc/cent_rounding`, taking line 84 (the `core/at_most` output
`ca-bc/bc428_british_columbia_political_contribution_tax_credit_line_84`, over the input
`ca-bc/bc428_political_contribution_tax_credit_line_84`, which a salary-only caller leaves out)
off line 82 (`ca-bc/bc428_tax_after_logging_credit_line_82`).
Line 84 left blank is taken as 0 by the
step's own blank rule (`blank: less: "0"`), which prints its own
"left blank, taken as 0" row. The output is `ca-bc/bc428_tax_after_political_credit_line_85`, a
non-negative kind on the form `ca-bc/bc428`.

The test composes the real parts that lead to line 82 (the salary, Schedule 8, T2204, the federal
T1 taxable income parts and BC428 lines 1 to 82), the line 84 input, maximum and line parts,
plus the new
`bc428_line_85.yaml`. The header and the form declaration are made up here, because the shared
scaffold owns them.

Figures (hand-computed, not a CRA example). Line 82 is the line 82 test's: line 80 (line 72 less
line 79, not below 0) less a blank line 81. With line 84 blank, line 85 equals line 82 at a salary
of 17,000 / 30,000: 0.00 / 364.81. With
line 84 of 100.00 at 70,000, line 85 is 3,062.39; with line 84 above line 82 it is floored at 0.00.
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
from tax_engine.domain.trace import BlankFallbackLine, SubtractedNotBelowZeroLine
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
LINE_81 = "ca-bc/bc428_logging_tax_credit_line_81"
LINE_82 = "ca-bc/bc428_tax_after_logging_credit_line_82"
LINE_84_INPUT = "ca-bc/bc428_political_contribution_tax_credit_line_84"
LINE_84 = "ca-bc/bc428_british_columbia_political_contribution_tax_credit_line_84"
LINE_85 = "ca-bc/bc428_tax_after_political_credit_line_85"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc428_line_85.yaml"
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
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)
# The real British Columbia parts after the federal ones, in composition order: the line 72 test's
# (lines 1 to 72), then the line 79 test's (lines 74, 75, 76, 78, 73 and 79), then lines 80, 81,
# 82, 84 and 85.
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
    *(f"bc428_line_{number}.yaml" for number in (74, 75, 76, 78, 73, 79, 80)),
    "bc428_line_81_input.yaml",
    "bc428_line_82.yaml",
    "bc428_line_84_input.yaml",
    "bc428_political_contribution_tax_credit_maximum.yaml",
    "bc428_line_84.yaml",
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
        - ca-bc/bc428_tax_after_logging_credit_line_82
        - ca-bc/bc428_tax_after_political_credit_line_85
    capabilities: []
    """)

# salary, taxable income (line 1 and line 74), line 67 (the line 67 test's figure), line 72 (line 70
# with line 71 blank), line 79 and the ticket's line 82 figure (line 81 blank, so line 80).
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


def _sheet(tmp_path: Path, salary: str, credit: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if credit is not None:
        given.append(Artifact(_amount_kind(LINE_84_INPUT), D(credit)))
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


@pytest.mark.parametrize(
    ("salary", "taxable_income", "line_67", "line_72", "line_79", "expected"), CASES
)
def test_line_85_is_line_82_at_each_salary_when_line_84_is_left_blank(
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

    assert sheet.get(_amount_kind(LINE_84)).is_blank
    assert sheet.get(_amount_kind(LINE_82)).value == D(expected)
    result = sheet.get(_amount_kind(LINE_85))
    assert not result.is_blank
    assert result.value == D(expected)
    assert str(result.value) == expected
    assert result.value.as_tuple().exponent == -2
    assert not result.value.is_signed()


def test_line_85_takes_line_84_off_line_82_when_line_84_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "100.00")

    assert sheet.get(_amount_kind(LINE_82)).value == D("3162.39")
    line_85 = sheet.get(_amount_kind(LINE_85)).value
    assert line_85 == D("3062.39")
    assert str(line_85) == "3062.39"
    assert not line_85.is_signed()


def test_line_85_is_0_when_line_84_is_above_line_82(tmp_path: Path) -> None:
    # Line 82 is 364.81 at 30,000 and line 84 is 500.00: the floor.
    sheet = _sheet(tmp_path, "30000", "500.00")

    line_85 = sheet.get(_amount_kind(LINE_85)).value
    assert line_85 == D("0.00")
    assert str(line_85) == "0.00"
    assert not line_85.is_signed()


def test_line_85_is_0_when_line_84_equals_line_82(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "30000", "364.81")

    assert sheet.get(_amount_kind(LINE_85)).value == D("0.00")


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "30000", "100.00")
    kinds = british_columbia_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_85)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_85),
        minuend=kinds.kind(LINE_82),
        minuend_amount=D("364.81"),
        subtrahend=kinds.kind(LINE_84),
        subtrahend_amount=D("100.00"),
        rounding=_rounding().rounding,
        result=D("264.81"),
    )


def test_the_blank_fallback_row_names_line_84_only_when_line_84_is_blank(tmp_path: Path) -> None:
    given_dir = tmp_path / "given"
    given_dir.mkdir()
    kinds = british_columbia_kinds()

    def fallbacks(sheet: Worksheet) -> list[BlankFallbackLine]:
        return [
            t
            for t in sheet.trace
            if isinstance(t, BlankFallbackLine) and t.kind is kinds.kind(LINE_84)
        ]

    (row,) = fallbacks(_sheet(tmp_path, "70000"))
    assert row.fallback == D("0")
    assert not fallbacks(_sheet(given_dir, "70000", "100.00"))


@pytest.mark.parametrize(
    ("line_82", "line_84", "expected"),
    [
        ("364.81", "100.00", "264.81"),
        ("151.09", "562.00", "0.00"),
    ],
)
def test_line_85_is_line_82_minus_line_84_not_below_zero_to_the_cent(
    line_82: str, line_84: str, expected: str
) -> None:
    kinds = (_amount_kind(LINE_82), _amount_kind(LINE_84), _amount_kind(LINE_85))
    capability = SubtractNotBelowZero(_rounding(), *kinds)
    result = capability.compute((Artifact(kinds[0], D(line_82)), Artifact(kinds[1], D(line_84))))

    (output,) = result.outputs
    assert output.value == D(expected)
    assert D(expected) == max(D(line_82) - D(line_84), D("0.00"))


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_subtract_step_with_a_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": TAX}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "85",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_82, "less": LINE_84},
        "blank": {"less": "0"},
        "produces": {"output": LINE_85},
    }
    assert "title" not in step


def test_line_85_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_85 in kinds.identifiers()
    kind = kinds.kind(LINE_85)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC428_TAX_AFTER_POLITICAL_CREDIT_LINE_85"]
