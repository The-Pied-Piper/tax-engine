"""SK428 (2025) line 82, line 80 minus line 81 (not below 0), from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 81: Line 81 and line 63640: Saskatchewan graduate
tuition tax credit (complete Form RC360)" and "Line 82: Line 80 minus line 81 (if negative, enter
\"0\") Enter this amount on line 42800 of your return. Saskatchewan tax =". The form prints no
title for line 82, so the step is untitled.

Line 82 is one core/subtract_not_below_zero step (`sk428_line_82.yaml`), rounded through
`ca-sk/cent_rounding`, with `amount` line 80 (`ca-sk/sk428_tax_line_80`, non-negative) and `less`
line 81 (`ca-sk/sk428_graduate_tuition_credit_line_81`, an optional input). A salary-only caller
has no graduate tuition credit, so line 81 is left blank, and the step has a blank rule reading
it as 0 and prints its own "left blank, taken as 0" row, as line 80 does for its line 79. The
output `ca-sk/sk428_saskatchewan_tax_line_82` is a non-negative kind on the form `ca-sk/sk428`.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T2204 parts, the T1
taxable income parts, the real line parts of `ca-sk/sk428_credits` that lines 8 and 57 need, the
real `sk428_line_58.yaml` to `sk428_line_80.yaml` parts (with the inputs parts the lines read),
the line 81 input part and the new `sk428_line_82.yaml`, and types in only the salary and, in some
tests, line 81. The two form declarations are made up here.

Figures: line 80 is line 78 with a blank line 79, re-derived here in `_line_62` and `_line_66`
with Decimal (not a CRA example); line 81 is blank (0), so line 82 is 0.00 / 5,092.30
at a salary of 20,000 / 70,000. With a line 81 of 100.00 line 82 is 0.00 (floored) / 4,992.30.
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
LINE_PART = SK_PARTS / "sk428_line_82.yaml"
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
    "sk428_line_67.yaml",
    "sk428_line_68_inputs.yaml",
    "sk428_line_68.yaml",
    "sk428_line_69.yaml",
    "sk428_line_70_inputs.yaml",
    "sk428_line_71.yaml",
    "sk428_line_73_input.yaml",
    "sk428_line_73.yaml",
    "sk428_line_74.yaml",
    "sk428_line_77_input.yaml",
    "sk428_line_77.yaml",
    "sk428_line_78.yaml",
    "sk428_line_79_input.yaml",
    "sk428_line_80.yaml",
    "sk428_line_81_input.yaml",
)
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
FORM_NAME = "ca-sk/sk428"
CREDITS_FORM_NAME = "ca-sk/sk428_credits"
LINE_62 = "ca-sk/sk428_tax_line_62"
LINE_64 = "ca-sk/sk428_dividend_tax_credit_line_64"
LINE_66 = "ca-sk/sk428_credits_subtotal_line_66"
LINE_67 = "ca-sk/sk428_tax_after_credits_line_67"
LINE_68 = "ca-sk/sk428_minimum_tax_additional_line_68"
LINE_71 = "ca-sk/sk428_tax_line_71"
LINE_73 = "ca-sk/sk428_political_contributions_credit_line_73"
LINE_80 = "ca-sk/sk428_tax_line_80"
LINE_81 = "ca-sk/sk428_graduate_tuition_credit_line_81"
IDENTIFIER = "ca-sk/sk428_saskatchewan_tax_line_82"
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
# The SK428 declaration, test-local: lines 58 to 80 are composed, so it exports only line 82.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 82 with line 81 left blank (read as 0).
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


CASES_WITH_LINE_81 = [
    # salary, line 81, line 80, line 82: line 80 minus line 81, not below 0.
    ("20000", "100.00", "0.00", "0.00"),
    ("70000", "100.00", "5092.30", "4992.30"),
]


def _derived(salary: Decimal, line_81: Decimal = ZERO) -> Decimal:
    """Line 82 by hand: line 80 (line 78, line 74, which is line 71, which is line 67, the line 68,
    line 70, line 73 and line 77 inputs being blank) less line 81, never below 0."""
    return _cent(max(_line_67(salary) - line_81, ZERO))


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


def _amount_kind(identifier: str) -> AmountKind:
    kind = saskatchewan_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _sheet(
    tmp_path: Path,
    salary: str,
    line_81: str | None = None,
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_81 is not None:
        given.append(Artifact(_amount_kind(LINE_81), D(line_81)))
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
def test_the_expected_figures_are_line_80_less_a_blank_line_81_derived_independently(
    salary: str, expected: str
) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_82_is_line_80_when_line_81_is_left_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 80 is recomputed from the real parts, and line 81 is blank, read as 0.
    assert sheet.get(_amount_kind(LINE_81)).is_blank
    line_82 = _line(sheet, IDENTIFIER)
    assert line_82 == D(expected)
    assert line_82 == _line(sheet, LINE_80)
    assert str(line_82) == expected
    assert line_82.as_tuple().exponent == -2
    assert not line_82.is_signed()


@pytest.mark.parametrize(("salary", "line_81", "line_80", "expected"), CASES_WITH_LINE_81)
def test_line_82_is_line_80_minus_line_81_not_below_zero_when_line_81_is_given(
    tmp_path: Path, salary: str, line_81: str, line_80: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_81)

    assert _line(sheet, LINE_80) == D(line_80)
    line_82 = _line(sheet, IDENTIFIER)
    assert line_82 == D(expected) == _derived(D(salary), D(line_81))
    assert str(line_82) == expected
    assert line_82.as_tuple().exponent == -2
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert not line_82.is_signed()


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
        minuend=kinds.kind(LINE_80),
        minuend_amount=D("5092.30"),
        subtrahend=kinds.kind(LINE_81),
        subtrahend_amount=D("100.00"),
        rounding=_rounding().rounding,
        result=D("4992.30"),
    )


def _line_82_at(line_80_amount: str, line_81_amount: str) -> Artifact[Decimal]:
    """Line 80 over given lines 80 and 81: the capability the part builds, with the real dataset."""
    line_80, line_81, line_82 = (
        _amount_kind(LINE_80),
        _amount_kind(LINE_81),
        _amount_kind(IDENTIFIER),
    )
    capability = SubtractNotBelowZero(_rounding(), line_80, line_81, line_82)
    result = capability.compute(
        (Artifact(line_80, D(line_80_amount)), Artifact(line_81, D(line_81_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_80", "line_81", "expected"),
    [
        ("5092.30", "100.00", "4992.30"),
        ("100.00", "700.00", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01, 0.004 to 0.00.
        ("100.005", "100.00", "0.01"),
        ("100.004", "100.00", "0.00"),
    ],
)
def test_line_82_is_line_80_minus_line_81_not_below_zero_to_the_cent(
    line_80: str, line_81: str, expected: str
) -> None:
    line_82 = _line_82_at(line_80, line_81).value

    assert line_82 == D(expected)
    assert str(line_82) == expected
    assert line_82.as_tuple().exponent == -2
    assert not line_82.is_signed()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_a_blank_rule_on_line_81() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "82",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_80, "less": LINE_81},
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step


def test_the_sheet_prints_no_title_and_the_reference_of_line_82(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = _amount_kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "82"


def test_line_82_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = _amount_kind(IDENTIFIER)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(sk_catalog)["SK428_SASKATCHEWAN_TAX_LINE_82"]


def test_line_80_and_line_82_are_both_non_negative() -> None:
    assert non_negative(_amount_kind(LINE_80))
    assert non_negative(_amount_kind(IDENTIFIER))
