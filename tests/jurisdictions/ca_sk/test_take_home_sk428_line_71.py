"""SK428 (2025) line 71, line 69 minus line 70 (not below 0), from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 70: Provincial foreign tax credit (complete Form
T2036) ^" and "Line 71: Line 69 minus line 70 (if negative, enter "0") = ^". The form prints no
title for line 71, so the step is untitled.

Line 71 is one core/subtract_not_below_zero step (`sk428_line_71.yaml`), rounded through
`ca-sk/cent_rounding`, with `amount` line 69 (`ca-sk/sk428_tax_line_69`, signed) and `less` line 70
(`ca-sk/sk428_provincial_foreign_tax_credit_line_70`, an optional input). A salary-only caller has
no foreign tax credit, so line 70 is left blank, and the step has a blank rule reading it as 0 and
prints its own "left blank, taken as 0" row, as Alberta's AB428 line 70 does for its line 69. The
form floors line 71 at 0 (printed), unlike signed line 69, so the output `ca-sk/sk428_tax_line_71`
is a non-negative kind on the form `ca-sk/sk428`.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the T1
taxable income parts, the real line parts of `ca-sk/sk428_credits` that lines 8 and 57 need, the
real `sk428_line_58.yaml` to `sk428_line_69.yaml` parts, the line 70 inputs part and the new
`sk428_line_71.yaml`, and types in only the salary (and, in some tests, lines 61 and 64, the Form
T691 amount of line 68 and line 70). The two form declarations are made up here.

Figures: line 69 is line 67 plus line 68, re-derived here in `_line_62`, `_line_66` and `_line_68`
with Decimal (not a CRA example); line 70 is blank (0), so line 71 is 0.00 / 5,092.30 at a
salary of 20,000 / 70,000. With a line 70 of 1,000.00 line 71 is 4,092.30 at 70,000.
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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import CapabilityContractError
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
from tests.t691_support import line_1_minus_line_2

D = Decimal
CENT = D("0.01")
ZERO = D(0)
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_PART = SK_PARTS / "sk428_line_71.yaml"
TOP_CREDITS_PARTS = tuple(f"sk428_credits_line_{n}.yaml" for n in (1, 3, 4, 5, 6, 7, 8))
CREDITS_PARTS = (
    "sk428_credits_line_9.yaml",
    "sk428_credits_line_10_worksheet_lines_1_to_3.yaml",
    "sk428_credits_line_10_worksheet_lines_4_to_7.yaml",
    "sk428_credits_line_10.yaml",
    "sk428_credits_line_19.yaml",
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
    "sk428_line_64.yaml",
    "sk428_line_65.yaml",
    "sk428_line_66.yaml",
    "sk428_line_67.yaml",
    "sk428_line_68.yaml",
    "sk428_line_69.yaml",
    "sk428_line_70_inputs.yaml",
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
LINE_69 = "ca-sk/sk428_tax_line_69"
LINE_70 = "ca-sk/sk428_provincial_foreign_tax_credit_line_70"
IDENTIFIER = "ca-sk/sk428_tax_line_71"
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
# The SK428 declaration, test-local: lines 58 to 71 are composed, so it exports only line 71.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 71 with line 70 left blank (read as 0).
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


CASES_WITH_LINE_70 = [
    # salary, line 70, line 69, line 71: line 69 minus line 70, not below 0.
    ("70000", "1000.00", "5092.30", "4092.30"),
    # Exactly equal: the cent zero.
    ("70000", "5092.30", "5092.30", "0.00"),
]


def _derived(salary: Decimal, line_70: Decimal = ZERO, amount: Decimal = ZERO) -> Decimal:
    """Line 71 by hand: line 69 (line 67 plus line 68) less line 70, never below 0."""
    line_69 = _cent(_line_67(salary) + _line_68(amount))
    return _cent(max(line_69 - line_70, ZERO))


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


def _amount_kind(identifier: str) -> AmountKind:
    kind = saskatchewan_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _sheet(
    tmp_path: Path,
    salary: str,
    line_70: str | None = None,
    amount: str | None = None,
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_70 is not None:
        given.append(Artifact(_amount_kind(LINE_70), D(line_70)))
    if amount is not None:
        given.extend(line_1_minus_line_2(amount))
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-SK"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(_amount_kind(identifier)).value)


def _rounding() -> Any:
    return YamlParameterSource(
        saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_expected_figures_are_line_69_less_a_blank_line_70_derived_independently(
    salary: str, expected: str
) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_71_is_line_69_when_line_70_is_left_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 69 is recomputed from the real parts, and line 70 is blank, read as 0.
    assert sheet.get(_amount_kind(LINE_70)).is_blank
    line_71 = _line(sheet, IDENTIFIER)
    assert line_71 == D(expected)
    assert line_71 == _line(sheet, LINE_69)
    assert str(line_71) == expected
    assert line_71.as_tuple().exponent == -2
    assert not line_71.is_signed()


@pytest.mark.parametrize(("salary", "line_70", "line_69", "expected"), CASES_WITH_LINE_70)
def test_line_71_is_line_69_minus_line_70_not_below_zero_when_line_70_is_given(
    tmp_path: Path, salary: str, line_70: str, line_69: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_70)

    assert _line(sheet, LINE_69) == D(line_69)
    line_71 = _line(sheet, IDENTIFIER)
    assert line_71 == D(expected) == _derived(D(salary), D(line_70))
    assert str(line_71) == expected
    assert line_71.as_tuple().exponent == -2
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert not line_71.is_signed()


def test_a_negative_t691_amount_is_refused_at_the_t691_figure(tmp_path: Path) -> None:
    with pytest.raises(CapabilityContractError, match="t691_line_1_minus_line_2_of_part_7 -1000"):
        _sheet(tmp_path, "70000", "1000.00", amount="-1000")


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", "1000.00")
    kinds = saskatchewan_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(IDENTIFIER),
        minuend=kinds.kind(LINE_69),
        minuend_amount=D("5092.30"),
        subtrahend=kinds.kind(LINE_70),
        subtrahend_amount=D("1000.00"),
        rounding=_rounding().rounding,
        result=D("4092.30"),
    )


def _line_71_at(line_69_amount: str, line_70_amount: str) -> Artifact[Decimal]:
    """Line 71 over given lines 69 and 70: the capability the part builds, with the real dataset."""
    line_69, line_70, line_71 = (
        _amount_kind(LINE_69),
        _amount_kind(LINE_70),
        _amount_kind(IDENTIFIER),
    )
    capability = SubtractNotBelowZero(_rounding(), line_69, line_70, line_71)
    result = capability.compute(
        (Artifact(line_69, D(line_69_amount)), Artifact(line_70, D(line_70_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_69", "line_70", "expected"),
    [
        ("5092.30", "1000.00", "4092.30"),
        ("1000.00", "5092.30", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01, 0.004 to 0.00.
        ("100.005", "100.00", "0.01"),
        ("100.004", "100.00", "0.00"),
    ],
)
def test_line_71_is_line_69_minus_line_70_not_below_zero_to_the_cent(
    line_69: str, line_70: str, expected: str
) -> None:
    line_71 = _line_71_at(line_69, line_70).value

    assert line_71 == D(expected)
    assert str(line_71) == expected
    assert line_71.as_tuple().exponent == -2
    assert not line_71.is_signed()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_a_blank_rule_on_line_70() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "71",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_69, "less": LINE_70},
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step


def test_the_sheet_prints_no_title_and_the_reference_of_line_71(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = _amount_kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "71"


def test_line_71_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = _amount_kind(IDENTIFIER)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(sk_catalog)["SK428_TAX_LINE_71"]


def test_line_69_stays_signed_while_line_71_is_floored() -> None:
    assert not non_negative(_amount_kind(LINE_69))
    assert non_negative(_amount_kind(IDENTIFIER))
