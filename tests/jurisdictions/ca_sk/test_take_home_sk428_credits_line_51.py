"""SK428 (2025) line 51, line 42 plus line 50, from the salary and the medical inputs, real parts.

Form text (Form SK428, CRA 5008-c): "Line 51 and line 58800: Line 42 plus line 50 = ^". Line 50,
"Line 50 and line 58769: Line 48 plus line 49 =", is a printed step (`sk428_credits_line_50.yaml`)
over lines 43 to 49, so it is always a figure, 0.00 for a salary-only filer, and line 51 has no
blank rule. Line 51 is one core/sum over line 42 and line 50, as Alberta line 52 is over line 43
and line 51. The form prints no label for line 51, so the step has no title.

The test composes the real Saskatchewan salary part, the real Schedule 8, T2204 and T1 taxable
income parts, the real line parts (`sk428_credits_line_9.yaml`, `_line_20.yaml`, `_line_22.yaml`,
`_line_24.yaml`, `_line_31.yaml`, `_line_32.yaml`, `_line_33.yaml`, `_line_35.yaml`,
`_line_38.yaml`, `_line_42.yaml`, `_line_43_input.yaml`, `_line_44.yaml`, `_line_46.yaml`,
`_line_47.yaml`, `_line_48.yaml`, `_line_49_input.yaml`, `_line_50.yaml`), the real
`sk428_line_33_inputs.yaml` and the new `sk428_credits_line_51.yaml`, and types in the salary and,
where a case gives them, lines 43 and 49. The form declaration is made up here, exporting only
line 51. The figures are not a CRA example: they are re-derived below with Decimal from the printed
basic personal amount dataset (19,491), CPP at 4.95% of the salary above the $3,500 basic
exemption to a maximum of $3,356.10, and EI at 1.64% to the $65,700 maximum insurable earnings,
each rounded half-up to the cent. Line 42 is 20,635.75, 23,860.23 and 23,924.58 at the three
salaries, plus line 50 of 0.00 when no medical expenses are given.
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
    SK428_CREDITS_TOTAL_LINE_51,
    SK428_MEDICAL_EXPENSES_LINE_43,
    SK428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49,
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
from tests.manifest_support import T1_LINE_10100_INPUT

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
PART = SK_PARTS / "sk428_credits_line_51.yaml"
IDENTIFIER = "ca-sk/sk428_credits_total_line_51"
BASIC_PERSONAL_AMOUNT = D("19491")

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/sk428_credits_total_line_51
    capabilities: []
    """)

# salary, line 51: line 42 (20,635.75 and 23,924.58, re-derived by hand below) plus line 50 of
# 0.00, as a salary-only filer has no medical expenses.
CASES = [("20000", "20635.75"), ("200000", "23924.58")]


def _cpp(salary: str) -> Decimal:
    """Line 22 by hand: 4.95% of the salary above the $3,500 basic exemption, at most $3,356.10."""
    above = max(D(salary) - D("3500"), D("0"))
    return min((above * D("0.0495")).quantize(D("0.01"), ROUND_HALF_UP), D("3356.10"))


def _ei(salary: str) -> Decimal:
    """Line 24 by hand: 1.64% of the salary to the $65,700 maximum, at most $1,077.48."""
    return min(D(salary), D("65700")) * D("0.0164")


def _line_50(salary: str, line_43: str, line_49: str) -> Decimal:
    """Line 50 by hand: line 48 (line 43 less line 47, not below 0) plus line 49, where line 47 is
    the lesser of $2,681 and 3% of the net income (the salary less the enhanced CPP deduction)."""
    salary_amount = D(salary)
    enhanced = max(min(salary_amount, D("71300")) - D("3500"), D(0)) * D("0.01")
    second = max(min(salary_amount, D("81200")) - D("71300"), D(0)) * D("0.04")
    net_income = salary_amount - enhanced.quantize(D("0.01"), ROUND_HALF_UP)
    net_income -= second.quantize(D("0.01"), ROUND_HALF_UP)
    line_47 = min(D("2681"), (net_income * D("0.03")).quantize(D("0.01"), ROUND_HALF_UP))
    return max(D(line_43) - line_47, D(0)) + D(line_49)


def _expected(salary: str, medical: str = "0") -> Decimal:
    """Line 51 by hand: line 42 (equal to line 32 here) plus line 50."""
    line_31 = (_cpp(salary) + _ei(salary)).quantize(D("0.01"), ROUND_HALF_UP)
    line_32 = BASIC_PERSONAL_AMOUNT.quantize(D("0.01")) + line_31
    return line_32 + D(medical)


def _part_files() -> Iterator[Path]:
    yield T1_LINE_10100_INPUT
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield from form_parts("t1_taxable_income", "t1_employment_income")
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
    yield SK_PARTS / "sk428_credits_line_43_input.yaml"
    yield SK_PARTS / "sk428_credits_line_44.yaml"
    yield SK_PARTS / "sk428_credits_line_46.yaml"
    yield SK_PARTS / "sk428_credits_line_47.yaml"
    yield SK_PARTS / "sk428_credits_line_48.yaml"
    yield SK_PARTS / "sk428_credits_line_49_input.yaml"
    yield SK_PARTS / "sk428_credits_line_50.yaml"
    yield PART


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


def _sheet(
    tmp_path: Path, salary: str, line_43: str | None = None, line_49: str | None = None
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_43 is not None:
        given.append(Artifact(SK428_MEDICAL_EXPENSES_LINE_43, D(line_43)))
    if line_49 is not None:
        given.append(Artifact(SK428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49, D(line_49)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets["ca-sk/sk428_credits"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_51_is_line_42_for_a_salary_only_filer(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _expected(salary) == D(expected)
    assert _sheet(tmp_path, salary).get(SK428_CREDITS_TOTAL_LINE_51).value == D(expected)


def test_line_51_adds_line_50_from_the_medical_inputs(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "5000.00", "100.00")

    # Line 42 at a 70,000 salary: CPP 3,291.75 plus EI 1,077.48 is 4,369.23, plus 19,491.00 is
    # 23,860.23. Line 47 is 3% of net income 69,335.00, 2,080.05; line 48 is 5,000.00 - 2,080.05 =
    # 2,919.95; line 50 is 2,919.95 + 100.00 = 3,019.95; line 51 is 23,860.23 + 3,019.95 =
    # 26,880.18.
    assert _line_50("70000", "5000.00", "100.00") == D("3019.95")
    assert _expected("70000", "3019.95") == D("26880.18")
    assert sheet.get(SK428_CREDITS_TOTAL_LINE_51).value == D("26880.18")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_line_51_is_one_untitled_sum_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-sk/sk428_credits"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "51",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-sk/sk428_credits_subtotal_line_42",
                "ca-sk/sk428_medical_expenses_line_50",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_line_51_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert kind is SK428_CREDITS_TOTAL_LINE_51
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
