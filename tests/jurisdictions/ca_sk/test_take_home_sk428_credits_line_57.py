"""SK428 (2025) line 57, line 53 plus line 56, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c): "Line 57 and line 61500: Line 53 plus line 56 Enter this amount
on line 63. Saskatchewan non-refundable tax credits =". Line 56, "Line 56 and 58969: Line 54 plus
line 55", is computed from the two Schedule 9 donation lines and is 0.00 for a salary-only filer.
Line 57 is one core/sum over line 53 and line 56 with no blank rule. The form prints the label
"Saskatchewan non-refundable tax credits" on line 57, so the step is titled.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the T1
taxable income parts, the real line parts up to line 53 (the medical lines 43 to 50 left blank),
the real line 54 and 55 input and step parts, `sk428_credits_line_56.yaml` and
`sk428_credits_line_57.yaml`, and types in only the salary and, in some tests, the two Schedule 9
amounts. The form declaration is made up here, exporting only lines 53, 56 and 57. The figures are
re-derived below with Decimal (not a CRA example): line 53 is 2,166.75 and 2,512.08 at the two
salaries (line 51 times 10.5%, half-up to the cent); line 56 is 0.00 for a salary-only caller.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_sk.catalog import (
    SK428_CREDITS_AT_RATE_LINE_53,
    SK428_DONATIONS_AMOUNT_LINE_54,
    SK428_DONATIONS_AMOUNT_LINE_55,
    SK428_DONATIONS_CREDIT_LINE_56,
    SK428_NON_REFUNDABLE_CREDITS_LINE_57,
)
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_PART = SK_PARTS / "sk428_credits_line_57.yaml"
IDENTIFIER = "ca-sk/sk428_non_refundable_credits_line_57"
FORM_NAME = "ca-sk/sk428_credits"
RATE = D("0.105")
BASIC_PERSONAL_AMOUNT = D("19491")

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/sk428_credits_at_rate_line_53
        - ca-sk/sk428_donations_credit_line_56
        - ca-sk/sk428_non_refundable_credits_line_57
    capabilities: []
    """)

# salary, line 57: line 53 (2,166.75 and 2,512.08, as the line 53 test pins) plus a line 56 of 0.00.
CASES = [("20000", "2166.75"), ("200000", "2512.08")]


def _cpp(salary: str) -> Decimal:
    """Line 22 by hand: 4.95% of the salary above the $3,500 basic exemption, at most $3,356.10."""
    above = max(D(salary) - D("3500"), D("0"))
    return min((above * D("0.0495")).quantize(D("0.01"), ROUND_HALF_UP), D("3356.10"))


def _ei(salary: str) -> Decimal:
    """Line 24 by hand: 1.64% of the salary to the $65,700 maximum, at most $1,077.48."""
    return min(D(salary), D("65700")) * D("0.0164")


def _line_51(salary: str) -> Decimal:
    """Line 51 by hand: line 42 (equal to line 32 here), line 50 being blank."""
    line_31 = (_cpp(salary) + _ei(salary)).quantize(D("0.01"), ROUND_HALF_UP)
    line_32 = BASIC_PERSONAL_AMOUNT.quantize(D("0.01")) + line_31
    return line_32


def _line_53(salary: str) -> Decimal:
    """Line 53 by hand: line 51 times 10.5%, half-up to the cent."""
    return (_line_51(salary) * RATE).quantize(D("0.01"), ROUND_HALF_UP)


def _line_56(line_54: str = "0", line_55: str = "0") -> Decimal:
    """Line 56 by hand: line 54 (10.5% of its amount) plus line 55 (14.5%), each to the cent."""
    first = (D(line_54) * D("0.105")).quantize(D("0.01"), ROUND_HALF_UP)
    second = (D(line_55) * D("0.145")).quantize(D("0.01"), ROUND_HALF_UP)
    return first + second


def _expected(salary: str, line_54: str = "0", line_55: str = "0") -> Decimal:
    """Line 57 by hand: line 53 plus line 56, half-up to the cent."""
    return (_line_53(salary) + _line_56(line_54, line_55)).quantize(D("0.01"), ROUND_HALF_UP)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield from form_parts(
        "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
    )
    yield SK_PARTS / "sk428_credits_line_9.yaml"
    yield SK_PARTS / "sk428_credits_line_20.yaml"
    yield SK_PARTS / "sk428_credits_line_22.yaml"
    yield SK_PARTS / "sk428_credits_line_24.yaml"
    yield SK_PARTS / "sk428_line_33_inputs.yaml"
    yield SK_PARTS / "sk428_credits_line_31.yaml"
    yield SK_PARTS / "sk428_credits_line_32.yaml"
    yield SK_PARTS / "sk428_credits_line_33.yaml"
    yield SK_PARTS / "sk428_credits_line_35.yaml"
    yield SK_PARTS / "sk428_credits_line_38.yaml"
    yield SK_PARTS / "sk428_credits_line_42.yaml"
    for name in (
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
    ):
        yield SK_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, a form declaration and
    the real part files, every other namespace being the Saskatchewan package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(),
            saskatchewan_parameter_parsers(),
            saskatchewan_units(),
        ),
        saskatchewan_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_57_is_line_53_when_there_are_no_donations(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _expected(salary) == D(expected)
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(SK428_DONATIONS_CREDIT_LINE_56).value == D("0.00")
    assert sheet.get(SK428_NON_REFUNDABLE_CREDITS_LINE_57).value == D(expected)
    assert sheet.get(SK428_CREDITS_AT_RATE_LINE_53).value == D(expected)


def test_line_57_adds_line_56_from_lines_54_and_55(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(SK428_DONATIONS_AMOUNT_LINE_54, D("1000")),
        Artifact(SK428_DONATIONS_AMOUNT_LINE_55, D("2000")),
    )

    # Line 54 is 1,000 at 10.5%, 105.00; line 55 is 2,000 at 14.5%, 290.00; line 56 is 395.00.
    assert _line_56("1000", "2000") == D("395.00")
    assert _expected("70000", "1000", "2000") == D("2900.32")
    assert sheet.get(SK428_DONATIONS_CREDIT_LINE_56).value == D("395.00")
    assert sheet.get(SK428_CREDITS_AT_RATE_LINE_53).value == D("2505.32")
    assert sheet.get(SK428_NON_REFUNDABLE_CREDITS_LINE_57).value == D("2900.32")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_like_alberta_line_58() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "title": "Saskatchewan non-refundable tax credits",
        "reference": "57",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-sk/sk428_credits_at_rate_line_53",
                "ca-sk/sk428_donations_credit_line_56",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_line_57_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert kind is SK428_NON_REFUNDABLE_CREDITS_LINE_57
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
