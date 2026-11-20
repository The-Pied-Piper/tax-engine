"""SK428 (2025) line 67, line 62 minus line 66 (not below 0), from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 67: Line 62 minus line 66 (if negative, enter "0")
=". The form prints no title for the line, so the step is untitled and is one
core/subtract_not_below_zero over line 62 (the tax after line 61, signed,
`ca-sk/sk428_tax_line_62`) and line 66 (the credits subtotal, never negative,
`ca-sk/sk428_credits_subtotal_line_66`), floored at 0. Both lines are always computed (line 62 is
a sum with its own blank rule for line 61, line 66 a sum with its own blank rule for line 64), so
neither is ever blank and the step has no blank rule. The output is
`ca-sk/sk428_tax_after_credits_line_67`.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T2204 parts, the T1
taxable income parts, the real line parts of `ca-sk/sk428_credits` that lines 8 and 57 need, the
real `sk428_line_58.yaml` to `sk428_line_66.yaml` parts and the new `sk428_line_67.yaml`, and types
in only the salary (and, in some tests, lines 61 and 64). The two form declarations are made up
here: the credits form exports lines 1, 3 to 8 and 57, and `ca-sk/sk428` exports only line 67.

Figures: line 62 is line 60 (line 58, the tax on taxable income, less a blank line 59) plus a
blank line 61, and line 66 is line 63 (line 57) plus a blank line 64 plus a line 65 of 0.00, both
re-derived here in `_line_62` and `_line_66` with Decimal (not a CRA example).
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
import tax_engine.jurisdictions.ca_sk
import tax_engine.jurisdictions.ca_sk.catalog as sk_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CENT = D("0.01")
ZERO = D(0)
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = SK_PARTS / "sk428_line_67.yaml"
TOP_CREDITS_PARTS = tuple(f"sk428_credits_line_{n}.yaml" for n in (1, 3, 4, 5, 6, 7, 8))
CREDITS_PARTS = (
    "sk428_credits_line_9.yaml",
    "sk428_credits_line_20.yaml",
    "sk428_credits_line_22.yaml",
    "sk428_credits_line_24.yaml",
    "sk428_line_33_inputs.yaml",
    "sk428_credits_line_31.yaml",
    "sk428_credits_line_32.yaml",
    "sk428_credits_line_33.yaml",
    "sk428_credits_line_35.yaml",
    "sk428_credits_line_38.yaml",
    "sk428_credits_line_42.yaml",
    "sk428_credits_line_50_input.yaml",
    "sk428_credits_line_51.yaml",
    "sk428_credits_line_53.yaml",
    "sk428_credits_line_56_input.yaml",
    "sk428_credits_line_57.yaml",
)
SK_LINE_PARTS = (
    "sk428_line_58.yaml",
    "sk428_line_59_input.yaml",
    "sk428_line_60.yaml",
    "sk428_line_61_input.yaml",
    "sk428_line_62.yaml",
    "sk428_line_63.yaml",
    "sk428_line_64_input.yaml",
    "sk428_line_65_inputs.yaml",
    "sk428_line_65.yaml",
    "sk428_line_66.yaml",
)
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
FORM_NAME = "ca-sk/sk428"
CREDITS_FORM_NAME = "ca-sk/sk428_credits"
LINE_62 = "ca-sk/sk428_tax_line_62"
LINE_64 = "ca-sk/sk428_dividend_tax_credit_line_64"
LINE_66 = "ca-sk/sk428_credits_subtotal_line_66"
IDENTIFIER = "ca-sk/sk428_tax_after_credits_line_67"
ROUNDING = "ca-sk/cent_rounding"
BASIC_PERSONAL_AMOUNT = D("19491")

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The credits form declaration, test-local: lines 1, 3 to 8 and 57 are exported.
CREDITS_FORM = dedent(f"""\
    form:
      name: {CREDITS_FORM_NAME}
      required: true
      exports:
        - ca-sk/sk428_taxable_income_line_1
        - ca-sk/sk428_bracket_lower_bound_line_3
        - ca-sk/sk428_taxable_income_over_lower_bound_line_4
        - ca-sk/sk428_bracket_rate_line_5
        - ca-sk/sk428_tax_on_excess_line_6
        - ca-sk/sk428_bracket_tax_at_start_line_7
        - ca-sk/sk428_tax_on_taxable_income_line_8
        - ca-sk/sk428_non_refundable_credits_line_57
    capabilities: []
    """)
# The SK428 declaration, test-local: lines 58 to 67 are composed, so it exports only line 67.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 67: line 62 less line 66, floored at 0. At 20,000 line 62 is 2,082.68 and line 66
# is 2,166.75, so the difference is negative and the line is 0.
CASES = [
    ("20000", "0.00"),
    ("70000", "5092.30"),
]


def _cent(value: Decimal) -> Decimal:
    return value.quantize(CENT, ROUND_HALF_UP)


def _line_62(salary: Decimal, line_61: Decimal = ZERO) -> Decimal:
    """Line 62 by the form's arithmetic: line 60 (line 58, the tax on taxable income, where
    taxable income is the salary less the enhanced CPP deduction, with line 59 blank) plus line
    61."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    line_1 = salary - enhanced - second
    if line_1 <= D("53463"):
        lower, rate, line_7 = D("0"), D("0.105"), D("0.00")
    elif line_1 <= D("152750"):
        lower, rate, line_7 = D("53463"), D("0.125"), D("5613.62")
    else:
        lower, rate, line_7 = D("152750"), D("0.145"), D("18024.49")
    line_58 = _cent(max(line_1 - lower, D(0)) * rate) + line_7
    return _cent(line_58 + line_61)


def _line_66(salary: Decimal, line_64: Decimal = ZERO) -> Decimal:
    """Line 66 by the form's arithmetic: line 63 (line 57, which is line 53, line 51 times 10.5%,
    with line 56 blank; line 51 is line 32 here: the basic personal amount plus line 31, the CPP
    (4.95% above the $3,500 exemption, at most $3,356.10) and EI (1.64% to $65,700)) plus line 64
    plus a line 65 of 0.00."""
    cpp = min(_cent(max(salary - D("3500"), D(0)) * D("0.0495")), D("3356.10"))
    ei = min(salary, D("65700")) * D("0.0164")
    line_32 = BASIC_PERSONAL_AMOUNT + _cent(cpp + ei)
    return _cent(_cent(line_32 * D("0.105")) + line_64)


def _derived(salary: Decimal, line_61: Decimal = ZERO, line_64: Decimal = ZERO) -> Decimal:
    """Line 67 by hand: line 62 less line 66, never below 0."""
    return _cent(max(_line_62(salary, line_61) - _line_66(salary, line_64), ZERO))


def _part_files() -> Iterator[Path]:
    yield SK_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in (*TOP_CREDITS_PARTS, *CREDITS_PARTS):
        yield SK_PARTS / name
    for name in SK_LINE_PARTS:
        yield SK_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, form declarations and
    the real part files, every other namespace being the Saskatchewan package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=3):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def _sheet(
    tmp_path: Path,
    salary: str,
    line_61: str | None = None,
    line_64: str | None = None,
) -> Worksheet:
    kinds = saskatchewan_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_61 is not None:
        given.append(Artifact(sk_catalog.SK428_TAX_ON_SPLIT_INCOME_LINE_61, D(line_61)))
    if line_64 is not None:
        given.append(Artifact(kinds.kind(LINE_64), D(line_64)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(saskatchewan_kinds().kind(identifier)).value)


def _rounding() -> Any:
    return YamlParameterSource(
        saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_expected_figures_are_line_62_less_line_66_derived_independently(
    salary: str, expected: str
) -> None:
    assert _derived(D(salary)) == D(expected)


def test_the_unfloored_difference_at_20000_is_negative() -> None:
    assert _line_62(D("20000")) - _line_66(D("20000")) == D("-84.07")


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_67_is_line_62_less_line_66_not_below_zero(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line(sheet, IDENTIFIER) == D(expected)
    assert _line(sheet, IDENTIFIER) == max(_line(sheet, LINE_62) - _line(sheet, LINE_66), ZERO)
    if D(expected) != ZERO:
        assert str(_line(sheet, IDENTIFIER)) == expected


def test_line_67_is_zero_and_not_negative_when_line_66_exceeds_line_62(tmp_path: Path) -> None:
    # A salary of 0: line 62 is 0.00 and line 66 is 2,046.56 (10.5% of the basic personal amount),
    # so the difference is negative and the line is floored.
    sheet = _sheet(tmp_path, "0")

    assert _line(sheet, LINE_62) == ZERO
    assert _line(sheet, LINE_66) == D("2046.56")
    assert _line(sheet, IDENTIFIER) == ZERO
    assert not _line(sheet, IDENTIFIER).is_signed()


def test_a_large_line_64_floors_line_67_at_zero(tmp_path: Path) -> None:
    # Line 62 at 70,000 is 7,597.62; line 66 is 2,505.32 plus 5,000.00 (line 64) = 7,505.32.
    sheet = _sheet(tmp_path, "70000", line_64="5000.00")
    assert _line(sheet, IDENTIFIER) == D("92.30") == _derived(D("70000"), line_64=D("5000.00"))

    sheet = _sheet(tmp_path / "over", "70000", line_64="6000.00")
    assert _line(sheet, LINE_66) == D("8505.32")
    assert _line(sheet, IDENTIFIER) == ZERO
    assert not _line(sheet, IDENTIFIER).is_signed()


def test_line_67_is_zero_when_line_66_equals_line_62(tmp_path: Path) -> None:
    # Line 62 at 70,000 is 7,597.62 and line 66 is 2,505.32 plus 5,092.30 (line 64).
    sheet = _sheet(tmp_path, "70000", line_64="5092.30")

    assert _line(sheet, LINE_62) == _line(sheet, LINE_66) == D("7597.62")
    assert _line(sheet, IDENTIFIER) == ZERO


def test_line_67_reads_a_given_line_61_through_line_62(tmp_path: Path) -> None:
    # Line 62 at 70,000 is 7,597.62 plus 100.00 (line 61) = 7,697.62; less line 66 of 2,505.32.
    sheet = _sheet(tmp_path, "70000", line_61="100.00")

    assert _line(sheet, LINE_62) == D("7697.62")
    assert _line(sheet, IDENTIFIER) == D("5192.30") == _derived(D("70000"), line_61=D("100.00"))


def test_line_67_rounds_to_the_cent(tmp_path: Path) -> None:
    # Line 61 of 0.005 gives a line 62 of 7,597.625, rounded half-up to 7,597.63 by line 62's own
    # step, so line 67 is 7,597.63 less 2,505.32 and has two decimals.
    sheet = _sheet(tmp_path, "70000", line_61="0.005")

    result = _line(sheet, IDENTIFIER)
    assert result == D("5092.31")
    assert result == result.quantize(CENT)


def test_the_step_traces_one_floored_subtraction_with_the_cent_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", line_61="100.00")
    kinds = saskatchewan_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(IDENTIFIER),
        minuend=kinds.kind(LINE_62),
        minuend_amount=D("7697.62"),
        subtrahend=kinds.kind(LINE_66),
        subtrahend_amount=D("2505.32"),
        rounding=_rounding().rounding,
        result=D("5192.30"),
    )


def test_at_20000_the_trace_shows_the_floored_step_with_a_zero_result(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")
    kinds = saskatchewan_kinds()

    (line,) = [t for t in sheet.trace if getattr(t, "output", None) is kinds.kind(IDENTIFIER)]
    assert isinstance(line, SubtractedNotBelowZeroLine)
    assert not isinstance(line, SubtractedLine)
    assert line.minuend_amount == D("2082.68")
    assert line.subtrahend_amount == D("2166.75")
    assert line.result == ZERO
    assert not line.result.is_signed()


def test_the_sheet_prints_no_title_and_the_reference_of_line_67(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = saskatchewan_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "67"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_floored_subtract_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    # No blank rule: line 62 and line 66 are always computed, so neither is ever blank.
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "67",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_62, "less": LINE_66},
        "produces": {"output": IDENTIFIER},
    }


def test_line_67_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(sk_catalog)["SK428_TAX_AFTER_CREDITS_LINE_67"]
