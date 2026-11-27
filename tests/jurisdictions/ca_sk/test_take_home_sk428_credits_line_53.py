"""SK428 (2025) line 53, line 51 multiplied by the line 52 rate of 10.5%, real parts.

Form text (Form SK428, CRA 5008-c): "Line 52: Saskatchewan non-refundable tax credit rate 10.5%"
and "Line 53 and line 58840: Line 51 multiplied by the percentage from line 52 = ^". Line 52 is a
printed rate, so it is the `ca-sk/credit_rate` dataset figure and has no step of its own; line 53
is one core/apply_rate step over line 51, rounded half-up to the cent by the dataset's own rule, as
Manitoba's line 53 is over its line 51. The form prints no label for line 53, so the step has no
title.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the real
line parts (`sk428_credits_line_9.yaml`, `_line_20.yaml`, `_line_22.yaml`, `_line_24.yaml`,
`_line_31.yaml`, `_line_32.yaml`, `_line_33.yaml`, `_line_35.yaml`, `_line_38.yaml`,
`_line_42.yaml`, `_line_51.yaml`), the real `sk428_line_33_inputs.yaml`, the real
`sk428_credits_line_43.yaml`, `_line_44.yaml`, `_line_46.yaml`, `_line_47.yaml`,
`_line_48.yaml`, `_line_49.yaml`, `_line_50.yaml` and the new `sk428_credits_line_53.yaml`,
and types in the salary and, where a case gives them, lines 43 and 49. The form declaration is
made up here, exporting only line 53. The figures are line 51 as the engine produces it, re-
derived below with Decimal from the printed basic personal amount dataset (19,491), CPP at 4.95%
of the salary above the $3,500 basic exemption to a maximum of $3,356.10, and EI at 1.64% to the
$65,700 maximum insurable earnings (20,635.75 and 23,924.58 at the two salaries, line 50 of 0.00
with no medical expenses), times 10.5%, each rounded half-up to the cent.
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
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative
from tests.medical_support import medical_expenses, other_dependants_medical_expenses

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_PART = SK_PARTS / "sk428_credits_line_53.yaml"
IDENTIFIER = "ca-sk/sk428_credits_at_rate_line_53"
LINE_51 = "ca-sk/sk428_credits_total_line_51"
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
    capabilities: []
    """)

# salary, line 53: line 51 as the engine produces it, times 10.5%, half-up to the cent. Line 51 is
# 20,635.75 / 23,924.58 (line 50 of 0.00): 2,166.75375 and 2,512.0809, rounded to
# 2,166.75 / 2,512.08.
CASES = [("20000", "2166.75"), ("200000", "2512.08")]


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


def _line_51(salary: str, medical: str = "0") -> Decimal:
    """Line 51 by hand: line 42 (equal to line 32 here) plus line 50."""
    line_31 = (_cpp(salary) + _ei(salary)).quantize(D("0.01"), ROUND_HALF_UP)
    line_32 = BASIC_PERSONAL_AMOUNT.quantize(D("0.01")) + line_31
    return line_32 + D(medical)


def _expected(salary: str, medical: str = "0") -> Decimal:
    """Line 53 by hand: line 51 times 10.5%, half-up to the cent."""
    return (_line_51(salary, medical) * RATE).quantize(D("0.01"), ROUND_HALF_UP)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield from form_parts(
        "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
    )
    yield SK_PARTS / "sk428_credits_line_9.yaml"
    yield SK_PARTS / "sk428_credits_line_10_worksheet_lines_1_to_3.yaml"
    yield SK_PARTS / "sk428_credits_line_10_worksheet_lines_4_to_7.yaml"
    yield SK_PARTS / "sk428_credits_line_10.yaml"
    yield SK_PARTS / "sk428_credits_line_19.yaml"
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
    yield SK_PARTS / "sk428_credits_line_43.yaml"
    yield SK_PARTS / "sk428_credits_line_44.yaml"
    yield SK_PARTS / "sk428_credits_line_46.yaml"
    yield SK_PARTS / "sk428_credits_line_47.yaml"
    yield SK_PARTS / "sk428_credits_line_48.yaml"
    yield SK_PARTS / "sk428_credits_line_49.yaml"
    yield SK_PARTS / "sk428_credits_line_50.yaml"
    yield SK_PARTS / "sk428_credits_line_51.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, a form declaration and
    the real part files, every other namespace being the Saskatchewan package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(dict.fromkeys(_part_files()), start=2):
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
        given.append(medical_expenses(line_43))
    if line_49 is not None:
        given.append(other_dependants_medical_expenses(line_49))
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-SK"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(saskatchewan_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_53_is_line_51_times_10_point_5_percent(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _expected(salary) == D(expected)
    assert _line(_sheet(tmp_path, salary), IDENTIFIER) == D(expected)


def test_line_53_follows_line_51_with_medical_inputs(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "5000.00", "100.00")

    # Line 50 at a 70,000 salary with line 43 of 5,000.00 and line 49 of 100.00 is 3,019.95
    # (line 47 is 2,080.05, line 48 is 2,919.95); line 51 is 23,860.23 + 3,019.95 = 26,880.18;
    # times 0.105 is 2,822.4189, rounded half-up to 2,822.42.
    assert _line_50("70000", "5000.00", "100.00") == D("3019.95")
    assert _line_51("70000", "3019.95") == D("26880.18")
    assert _expected("70000", "3019.95") == D("2822.42")
    assert _line(sheet, IDENTIFIER) == D("2822.42")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_apply_rate_step_like_manitoba_line_53() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "53",
        "unit": "ca/cad",
        "params": {"rate": "ca-sk/credit_rate"},
        "consumes": {"base": LINE_51},
        "produces": {"output": IDENTIFIER},
    }


def test_line_53_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert kind is sk_catalog.SK428_CREDITS_AT_RATE_LINE_53
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
