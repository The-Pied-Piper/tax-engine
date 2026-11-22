"""SK428 (2025) line 69, line 67 plus line 68, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 69: Line 67 plus line 68 =
^". The form prints no title for the line, so the step is untitled and is one core/sum over line 67
(the tax after credits, never negative, `ca-sk/sk428_tax_after_credits_line_67`) and line 68 (the
additional tax for minimum tax purposes, signed, `ca-sk/sk428_minimum_tax_additional_line_68`).
Both lines are always computed (line 68's Form T691 input is declared by its own part and defaults
to 0), so neither is ever blank and the step has no blank rule. The output is
`ca-sk/sk428_tax_line_69`, a signed kind: the form prints no floor.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the T1
taxable income parts, the real line parts of `ca-sk/sk428_credits` that lines 8 and 57 need, the
real `sk428_line_58.yaml` to `sk428_line_68.yaml` parts (with the T691 form) and the
new `sk428_line_69.yaml`, and types in only the salary (and, in some tests, lines 61 and 64 and the
Form T691 amount of line 68). The two form declarations are made up here: the credits form exports
lines 1, 3 to 8 and 57, and `ca-sk/sk428` exports only line 69.

Figures: line 67 is line 62 less line 66 (not below 0) and line 68 is 50% of the Form T691 amount
rounded half-up to the cent, re-derived here in `_line_62`, `_line_66` and `_line_68` with Decimal
(not a CRA example).
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
from tax_engine.domain.trace import BlankPassedOnLine, SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative
from tests.t691_support import line_1_minus_line_2

D = Decimal
CENT = D("0.01")
ZERO = D(0)
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_PART = SK_PARTS / "sk428_line_69.yaml"
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
    "sk428_credits_line_43.yaml",
    "sk428_credits_line_44.yaml",
    "sk428_credits_line_46.yaml",
    "sk428_credits_line_47.yaml",
    "sk428_credits_line_48.yaml",
    "sk428_credits_line_49.yaml",
    "sk428_credits_line_50.yaml",
    "sk428_credits_line_51.yaml",
    "sk428_credits_line_53.yaml",
    "sk428_credits_line_54.yaml",
    "sk428_credits_line_55.yaml",
    "sk428_credits_line_56.yaml",
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
    "sk428_line_65.yaml",
    "sk428_line_66.yaml",
    "sk428_line_67.yaml",
    "sk428_line_68.yaml",
)
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces", "t691"
)
FORM_NAME = "ca-sk/sk428"
CREDITS_FORM_NAME = "ca-sk/sk428_credits"
LINE_62 = "ca-sk/sk428_tax_line_62"
LINE_64 = "ca-sk/sk428_dividend_tax_credit_line_64"
LINE_66 = "ca-sk/sk428_credits_subtotal_line_66"
LINE_67 = "ca-sk/sk428_tax_after_credits_line_67"
LINE_68 = "ca-sk/sk428_minimum_tax_additional_line_68"
IDENTIFIER = "ca-sk/sk428_tax_line_69"
ROUNDING = "ca-sk/cent_rounding"
BASIC_PERSONAL_AMOUNT = D("19491")

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
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
# The SK428 declaration, test-local: lines 58 to 69 are composed, so it exports only line 69.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 69: line 67 plus line 68 (0.00 when the Form T691 amount is left out).
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


def _line_67(salary: Decimal, line_61: Decimal = ZERO, line_64: Decimal = ZERO) -> Decimal:
    """Line 67 by hand: line 62 less line 66, never below 0."""
    return _cent(max(_line_62(salary, line_61) - _line_66(salary, line_64), ZERO))


def _line_68(amount: Decimal = ZERO) -> Decimal:
    """Line 68 by hand: 50% of the Form T691 amount, rounded half-up to the cent."""
    return _cent(amount * D("0.5"))


def _derived(
    salary: Decimal,
    amount: Decimal = ZERO,
    line_61: Decimal = ZERO,
    line_64: Decimal = ZERO,
) -> Decimal:
    """Line 69 by hand: line 67 plus line 68."""
    return _cent(_line_67(salary, line_61, line_64) + _line_68(amount))


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("schedule_9")
    yield from form_parts("t2204")
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
            part.read_text(encoding="utf-8"),
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
    amount: str | None = None,
    line_61: str | None = None,
    line_64: str | None = None,
) -> Worksheet:
    kinds = saskatchewan_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if amount is not None:
        given.extend(line_1_minus_line_2(amount))
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
def test_the_expected_figures_are_line_67_plus_line_68_derived_independently(
    salary: str, expected: str
) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_69_is_line_67_plus_line_68(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, salary)

    result = _line(sheet, IDENTIFIER)
    assert result == D(expected)
    assert result == _line(sheet, LINE_67) + _line(sheet, LINE_68)
    assert str(result) == expected
    assert result.as_tuple().exponent == -2


@pytest.mark.parametrize(("salary", "line_67"), [("20000", "0.00"), ("70000", "5092.30")])
def test_a_blank_line_68_input_reads_0_so_line_69_equals_line_67(
    tmp_path: Path, salary: str, line_67: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line(sheet, LINE_68) == ZERO
    assert _line(sheet, LINE_67) == D(line_67)
    assert _line(sheet, IDENTIFIER) == D(line_67)


@pytest.mark.parametrize(
    ("salary", "line_67", "expected"),
    [
        ("20000", "0.00", "500.00"),
        ("70000", "5092.30", "5592.30"),
    ],
)
def test_a_t691_amount_of_1000_adds_500_to_line_67(
    tmp_path: Path, salary: str, line_67: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, amount="1000.00")

    assert _line(sheet, LINE_68) == D("500.00")
    assert _line(sheet, LINE_67) == D(line_67)
    assert _line(sheet, IDENTIFIER) == D(expected) == _derived(D(salary), D("1000.00"))
    assert str(_line(sheet, IDENTIFIER)) == expected


def test_a_negative_t691_amount_gives_a_negative_line_68_and_a_signed_line_69(
    tmp_path: Path,
) -> None:
    # The Form T691 input is signed: -1000 x 50% = -500.00, added to line 67 with no floor.
    sheet = _sheet(tmp_path, "70000", amount="-1000")
    assert _line(sheet, LINE_68) == D("-500.00")
    assert _line(sheet, IDENTIFIER) == D("4592.30") == _derived(D("70000"), D("-1000"))

    sheet = _sheet(tmp_path / "low", "20000", amount="-1000")
    assert _line(sheet, LINE_67) == ZERO
    assert _line(sheet, IDENTIFIER) == D("-500.00")
    assert str(_line(sheet, IDENTIFIER)) == "-500.00"
    assert _line(sheet, IDENTIFIER).is_signed()


def test_line_69_reads_lines_61_and_64_through_line_67(tmp_path: Path) -> None:
    # Line 67 at 70,000 with line 61 of 100.00 is 5,192.30; a line 64 of 1,000.00 lowers it to
    # 4,192.30, and line 68 adds 500.00.
    sheet = _sheet(tmp_path, "70000", amount="1000.00", line_61="100.00", line_64="1000.00")

    assert _line(sheet, LINE_67) == D("4192.30")
    assert _line(sheet, IDENTIFIER) == D("4692.30")
    assert _line(sheet, IDENTIFIER) == _derived(
        D("70000"), D("1000.00"), line_61=D("100.00"), line_64=D("1000.00")
    )


def test_line_69_rounds_to_the_cent_half_up(tmp_path: Path) -> None:
    # 50% of 1000.01 is 500.005, rounded half-up to 500.01 by line 68's own step, so line 69 is
    # 5,092.30 plus 500.01 and has two decimals.
    sheet = _sheet(tmp_path, "70000", amount="1000.01")

    assert _line(sheet, LINE_68) == D("500.01")
    result = _line(sheet, IDENTIFIER)
    assert result == D("5592.31")
    assert result == result.quantize(CENT)


def test_line_69_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    output = saskatchewan_kinds().kind(IDENTIFIER)

    assert not sheet.get(output).is_blank
    # The step has no blank rule: both parts are always computed, so no row names line 69.
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine) and t.output is output]


def test_the_step_traces_one_sum_line_over_lines_67_and_68_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", amount="1000.00")
    kinds = saskatchewan_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line == SumLine(
        output=kinds.kind(IDENTIFIER),
        parts=((kinds.kind(LINE_67), D("5092.30")), (kinds.kind(LINE_68), D("500.00"))),
        rounding=_rounding().rounding,
        total=D("5592.30"),
    )


def test_the_sheet_prints_no_title_and_the_reference_of_line_69(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = saskatchewan_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "69"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "69",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_67, LINE_68]},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step


def test_line_69_is_a_registered_signed_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    # The form prints no floor on line 69, and line 68 is signed, so the kind is not non_negative.
    assert not non_negative(kind)
    assert kind is vars(sk_catalog)["SK428_TAX_LINE_69"]
