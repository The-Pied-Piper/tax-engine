"""SK428 (2025) line 80, line 78 minus line 79 (not below 0), from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 79: Saskatchewan mineral exploration tax credit
(complete Form T1279)" and "Line 80: Line 78 minus line 79 (if negative, enter "0") =". The form
prints no title for line 80, so the step is untitled.

Line 80 is one core/subtract_not_below_zero step (`sk428_line_80.yaml`), rounded through
`ca-sk/cent_rounding`, with `amount` line 78 (`ca-sk/sk428_tax_line_78`, non-negative) and `less`
line 79 (`ca-sk/sk428_mineral_exploration_credit_line_79`, an optional input). A salary-only caller
has no mineral exploration tax credit, so line 79 is left blank, and the step has a blank rule
reading it as 0 and prints its own "left blank, taken as 0" row, as line 78 does for its line 77.
The output `ca-sk/sk428_tax_line_80` is a non-negative kind on the form `ca-sk/sk428`.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the T1
taxable income parts, the real line parts of `ca-sk/sk428_credits` that lines 8 and 57 need, the
real `sk428_line_58.yaml` to `sk428_line_78.yaml` parts (line 71 consumes line 70, so the line 70
inputs part is composed; line 74 consumes the checked line 73, so the line 73 input part and the
line 73 part are composed; line 78 consumes the checked line 77, so the line 77 input part and the
line 77 part are composed), the line 79 input part and the new `sk428_line_80.yaml`, and types in
only the salary and, in some tests, line 79. The two form declarations are made up here.

Figures: line 78 is line 74 (line 71, line 67, line 68 being 0 here) with blank lines 73 and 77,
re-derived here in `_line_62` and `_line_66` with Decimal (not a CRA example); line 79 is blank
(0), so line 80 is 0.00 / 5,092.30 at a salary of 20,000 / 70,000. With a line 79 of 100.00 line 80
is 0.00 (floored) / 4,992.30.
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
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
)
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
ZERO = D(0)
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_PART = SK_PARTS / "sk428_line_80.yaml"
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
    "sk428_credits_line_54_input.yaml",
    "sk428_credits_line_55_input.yaml",
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
    "sk428_line_64.yaml",
    "sk428_line_65.yaml",
    "sk428_line_66.yaml",
    "sk428_line_67.yaml",
    "sk428_line_68_inputs.yaml",
    "sk428_line_68.yaml",
    "sk428_line_69.yaml",
    "sk428_line_70_inputs.yaml",
    "sk428_line_71.yaml",
    "sk428_line_73_input.yaml",
    "sk428_line_73.yaml",
    "sk428_line_74.yaml",
    "sk428_line_75_input.yaml",
    "sk428_line_76_input.yaml",
    "sk428_line_77.yaml",
    "sk428_line_78.yaml",
    "sk428_line_79_input.yaml",
)
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)
FORM_NAME = "ca-sk/sk428"
CREDITS_FORM_NAME = "ca-sk/sk428_credits"
LINE_62 = "ca-sk/sk428_tax_line_62"
LINE_64 = "ca-sk/sk428_dividend_tax_credit_line_64"
LINE_66 = "ca-sk/sk428_credits_subtotal_line_66"
LINE_67 = "ca-sk/sk428_tax_after_credits_line_67"
LINE_68 = "ca-sk/sk428_minimum_tax_additional_line_68"
LINE_71 = "ca-sk/sk428_tax_line_71"
LINE_73 = "ca-sk/sk428_political_contributions_credit_line_73"
LINE_78 = "ca-sk/sk428_tax_line_78"
LINE_79 = "ca-sk/sk428_mineral_exploration_credit_line_79"
IDENTIFIER = "ca-sk/sk428_tax_line_80"
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
# The SK428 declaration, test-local: lines 58 to 78 are composed, so it exports only line 80.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 80 with line 79 left blank (read as 0).
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


CASES_WITH_LINE_79 = [
    # salary, line 79, line 78, line 80: line 78 minus line 79, not below 0.
    ("20000", "100.00", "0.00", "0.00"),
    ("70000", "100.00", "5092.30", "4992.30"),
]


def _derived(salary: Decimal, line_79: Decimal = ZERO) -> Decimal:
    """Line 80 by hand: line 78 (line 74, which is line 71, which is line 67, the line 68,
    line 70, line 73 and line 77 inputs being blank) less line 79, never below 0."""
    return _cent(max(_line_67(salary) - line_79, ZERO))


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
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


def _amount_kind(identifier: str) -> AmountKind:
    kind = saskatchewan_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _sheet(
    tmp_path: Path,
    salary: str,
    line_79: str | None = None,
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_79 is not None:
        given.append(Artifact(_amount_kind(LINE_79), D(line_79)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(_amount_kind(identifier)).value)


def _rounding() -> Any:
    return YamlParameterSource(
        saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_expected_figures_are_line_78_less_a_blank_line_79_derived_independently(
    salary: str, expected: str
) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_80_is_line_78_when_line_79_is_left_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 78 is recomputed from the real parts, and line 79 is blank, read as 0.
    assert sheet.get(_amount_kind(LINE_79)).is_blank
    line_80 = _line(sheet, IDENTIFIER)
    assert line_80 == D(expected)
    assert line_80 == _line(sheet, LINE_78)
    assert str(line_80) == expected
    assert line_80.as_tuple().exponent == -2
    assert not line_80.is_signed()


@pytest.mark.parametrize(("salary", "line_79", "line_78", "expected"), CASES_WITH_LINE_79)
def test_line_80_is_line_78_minus_line_79_not_below_zero_when_line_79_is_given(
    tmp_path: Path, salary: str, line_79: str, line_78: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_79)

    assert _line(sheet, LINE_78) == D(line_78)
    line_80 = _line(sheet, IDENTIFIER)
    assert line_80 == D(expected) == _derived(D(salary), D(line_79))
    assert str(line_80) == expected
    assert line_80.as_tuple().exponent == -2
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert not line_80.is_signed()


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", "100.00")
    kinds = saskatchewan_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(IDENTIFIER),
        minuend=kinds.kind(LINE_78),
        minuend_amount=D("5092.30"),
        subtrahend=kinds.kind(LINE_79),
        subtrahend_amount=D("100.00"),
        rounding=_rounding().rounding,
        result=D("4992.30"),
    )


def _line_80_at(line_78_amount: str, line_79_amount: str) -> Artifact[Decimal]:
    """Line 80 over given lines 78 and 79: the capability the part builds, with the real dataset."""
    line_78, line_79, line_80 = (
        _amount_kind(LINE_78),
        _amount_kind(LINE_79),
        _amount_kind(IDENTIFIER),
    )
    capability = SubtractNotBelowZero(_rounding(), line_78, line_79, line_80)
    result = capability.compute(
        (Artifact(line_78, D(line_78_amount)), Artifact(line_79, D(line_79_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_78", "line_79", "expected"),
    [
        ("5092.30", "100.00", "4992.30"),
        ("100.00", "700.00", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01, 0.004 to 0.00.
        ("100.005", "100.00", "0.01"),
        ("100.004", "100.00", "0.00"),
    ],
)
def test_line_80_is_line_78_minus_line_79_not_below_zero_to_the_cent(
    line_78: str, line_79: str, expected: str
) -> None:
    line_80 = _line_80_at(line_78, line_79).value

    assert line_80 == D(expected)
    assert str(line_80) == expected
    assert line_80.as_tuple().exponent == -2
    assert not line_80.is_signed()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_a_blank_rule_on_line_79() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "80",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_78, "less": LINE_79},
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step


def test_the_sheet_prints_no_title_and_the_reference_of_line_80(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = _amount_kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "80"


def test_line_80_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = _amount_kind(IDENTIFIER)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(sk_catalog)["SK428_TAX_LINE_80"]


def test_line_78_and_line_80_are_both_non_negative() -> None:
    assert non_negative(_amount_kind(LINE_78))
    assert non_negative(_amount_kind(IDENTIFIER))
