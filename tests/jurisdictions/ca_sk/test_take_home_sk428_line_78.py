"""SK428 (2025) line 78, line 74 minus line 77 (not below 0), from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 77 and line 63557: Line 75 plus line 76 (maximum
$875) =" and "Line 78: Line 74 minus line 77 (if negative, enter "0") =". The form prints no title
for line 78, so the step is untitled.

Line 78 is one core/subtract_not_below_zero step (`sk428_line_78.yaml`), rounded through
`ca-sk/cent_rounding`, with `amount` line 74 (`ca-sk/sk428_tax_line_74`, non-negative) and `less`
line 77 (`ca-sk/sk428_labour_sponsored_credit_checked_line_77`, the sum of lines 75 and 76 checked
against its printed maximum). Line 77 is always a figure (0.00 for a caller without the credit), so
the step has no blank rule. The output `ca-sk/sk428_tax_line_78` is a non-negative kind on the form
`ca-sk/sk428`. The $875 maximum of line 77 is tested with `sk428_line_77.yaml`, not here.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the T1
taxable income parts, the real line parts of `ca-sk/sk428_credits` that lines 8 and 57 need, the
real `sk428_line_58.yaml` to `sk428_line_74.yaml` parts (line 71 consumes line 70, so the line 70
inputs part is composed; line 74 consumes the checked line 73, so the line 73 input part and the
line 73 part are composed), the line 75 and 76 input parts, `sk428_line_77.yaml` and the new
`sk428_line_78.yaml`, and types in only the salary and, in some tests, lines 75 and 76. The two form
declarations are made up here.

Figures: line 74 is line 71 (line 67, line 68 being 0 here) with a blank line 73, re-derived here
in `_line_62` and `_line_66` with Decimal (not a CRA example); line 77 is 0.00, so line 78 is
0.00 / 5,092.30 at a salary of 20,000 / 70,000. With a line 77 of 100.00 line 78 is 0.00 (floored)
/ 4,992.30.
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
from tax_engine.domain.errors import InputAboveBoundError
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
LINE_PART = SK_PARTS / "sk428_line_78.yaml"
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
    "sk428_line_71.yaml",
    "sk428_line_73_input.yaml",
    "sk428_line_73.yaml",
    "sk428_line_74.yaml",
    "sk428_line_75_input.yaml",
    "sk428_line_76_input.yaml",
    "sk428_line_77.yaml",
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
LINE_71 = "ca-sk/sk428_tax_line_71"
LINE_73 = "ca-sk/sk428_political_contributions_credit_line_73"
LINE_74 = "ca-sk/sk428_tax_line_74"
LINE_77 = "ca-sk/sk428_labour_sponsored_credit_checked_line_77"
LINE_75 = "ca-sk/sk428_venture_capital_credit_saskatchewan_line_75"
LINE_76 = "ca-sk/sk428_venture_capital_credit_federal_line_76"
IDENTIFIER = "ca-sk/sk428_tax_line_78"
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
# The SK428 declaration, test-local: lines 58 to 78 are composed, so it exports only line 78.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 78 with lines 75 and 76 left out (line 77 is 0.00).
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


CASES_WITH_LINE_77 = [
    # salary, line 77, line 74, line 78: line 74 minus line 77, not below 0.
    ("20000", "100.00", "0.00", "0.00"),
    ("70000", "100.00", "5092.30", "4992.30"),
]


def _derived(salary: Decimal, line_77: Decimal = ZERO) -> Decimal:
    """Line 78 by hand: line 74 (line 71, which is line 67, the line 68, line 70 and line 73
    inputs being blank) less line 77, never below 0."""
    return _cent(max(_line_67(salary) - line_77, ZERO))


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
    line_75: str | None = None,
    line_76: str | None = None,
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    for name, value in ((LINE_75, line_75), (LINE_76, line_76)):
        if value is not None:
            given.append(Artifact(_amount_kind(name), D(value)))
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
def test_the_expected_figures_are_line_74_less_a_blank_line_77_derived_independently(
    salary: str, expected: str
) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_78_is_line_74_when_lines_75_and_76_are_left_out(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 74 is recomputed from the real parts, and line 77 is 0.00 (lines 75 and 76 read as 0).
    assert _line(sheet, LINE_77) == ZERO
    line_78 = _line(sheet, IDENTIFIER)
    assert line_78 == D(expected)
    assert line_78 == _line(sheet, LINE_74)
    assert str(line_78) == expected
    assert line_78.as_tuple().exponent == -2
    assert not line_78.is_signed()


@pytest.mark.parametrize(("salary", "line_77", "line_74", "expected"), CASES_WITH_LINE_77)
def test_line_78_is_line_74_minus_line_77_not_below_zero_when_line_77_is_given(
    tmp_path: Path, salary: str, line_77: str, line_74: str, expected: str
) -> None:
    # Line 77 is typed through lines 75 and 76: 40.00 plus 60.00.
    assert D("40.00") + D("60.00") == D(line_77)
    sheet = _sheet(tmp_path, salary, "40.00", "60.00")

    assert _line(sheet, LINE_77) == D(line_77)

    assert _line(sheet, LINE_74) == D(line_74)
    line_78 = _line(sheet, IDENTIFIER)
    assert line_78 == D(expected) == _derived(D(salary), D(line_77))
    assert str(line_78) == expected
    assert line_78.as_tuple().exponent == -2
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert not line_78.is_signed()


def _line_78_through(service: TaxComputationService, line_75: str, line_76: str) -> Decimal:
    given = [
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(_amount_kind(LINE_75), D(line_75)),
        Artifact(_amount_kind(LINE_76), D(line_76)),
    ]
    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-SK"), 2025, tuple(given))
    )[FORM_NAME]
    return _line(sheet, IDENTIFIER)


def test_lines_75_and_76_above_the_maximum_are_rejected_through_line_78(tmp_path: Path) -> None:
    service = _service(tmp_path)

    assert _line_78_through(service, "400.00", "300.00") == D("4392.30")
    assert _line_78_through(service, "875.00", "0.00") == D("4217.30")
    with pytest.raises(InputAboveBoundError):
        _line_78_through(service, "500.00", "375.01")


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
        minuend=kinds.kind(LINE_74),
        minuend_amount=D("5092.30"),
        subtrahend=kinds.kind(LINE_77),
        subtrahend_amount=D("100.00"),
        rounding=_rounding().rounding,
        result=D("4992.30"),
    )


def _line_78_at(line_74_amount: str, line_77_amount: str) -> Artifact[Decimal]:
    """Line 78 over given lines 74 and 77: the capability the part builds, with the real dataset."""
    line_74, line_77, line_78 = (
        _amount_kind(LINE_74),
        _amount_kind(LINE_77),
        _amount_kind(IDENTIFIER),
    )
    capability = SubtractNotBelowZero(_rounding(), line_74, line_77, line_78)
    result = capability.compute(
        (Artifact(line_74, D(line_74_amount)), Artifact(line_77, D(line_77_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_74", "line_77", "expected"),
    [
        ("5092.30", "100.00", "4992.30"),
        ("100.00", "700.00", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01, 0.004 to 0.00.
        ("100.005", "100.00", "0.01"),
        ("100.004", "100.00", "0.00"),
    ],
)
def test_line_78_is_line_74_minus_line_77_not_below_zero_to_the_cent(
    line_74: str, line_77: str, expected: str
) -> None:
    line_78 = _line_78_at(line_74, line_77).value

    assert line_78 == D(expected)
    assert str(line_78) == expected
    assert line_78.as_tuple().exponent == -2
    assert not line_78.is_signed()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "78",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_74, "less": LINE_77},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step


def test_the_sheet_prints_no_title_and_the_reference_of_line_78(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = _amount_kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "78"


def test_line_78_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = _amount_kind(IDENTIFIER)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(sk_catalog)["SK428_TAX_LINE_78"]


def test_line_74_and_line_78_are_both_non_negative() -> None:
    assert non_negative(_amount_kind(LINE_74))
    assert non_negative(_amount_kind(IDENTIFIER))
