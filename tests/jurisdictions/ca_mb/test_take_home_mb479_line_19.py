"""MB479 (2025) line 19, personal tax credit, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC): "Line 19: Line 17 minus line 18 (if negative, enter "0") Enter
this amount on line 54. Personal tax credit =". The printed label "Personal tax credit" is the step
title, as "Total credits" is line 17's. Line 19 is one core/subtract_not_below_zero step over
line 17 (total credits) less line 18 (the reduction), rounded to the cent, floored at 0. Both
inputs are always produced, so the step needs no blank rows.

The test composes the real Manitoba salary part, the real Schedule 8 parts, the real T1 taxable
income parts, the real line 1, line 2 input, line 3, line 4 input, line 5, line 5 column 2 input,
line 6, line 7, line 17 inputs, line 17 and line 18 parts and the new line 19 part, and types in
only the salary (and, in some tests, the column 2 figure). A salary-only filer leaves every
optional credit blank, so line 17 is the 195.00 basic credit. The MB479 form declaration is made up
here, exporting only line 19.

The expected figures are computed here, not typed: line 6 is the salary less the enhanced CPP
deduction (plus column 2 when given), line 18 is 1% of it half-up to the cent, and line 19 is
max(0, 195.00 - line 18). They are hand-computed from the printed forms, not a CRA example.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_mb.catalog import (
    MB479_FAMILY_INCOME_COLUMN_2_LINE_5,
)
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CENT = D("0.01")
ZERO = D(0)
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = MB_PARTS / "mb479_line_19.yaml"
FORM_NAME = "ca-mb/mb479"
KIND = "ca-mb/mb479_personal_tax_credit_line_19"
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

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb479
      required: true
      exports:
        - ca-mb/mb479_personal_tax_credit_line_19
    capabilities: []
    """)

BASIC_CREDIT = D("195.00")
# salary, line 6 (as the line 6 test pins), line 19
CASES = [
    ("10000", "9935.00", "95.65"),
    ("20000", "19835.00", "0.00"),
]


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in the Manitoba catalog."""
    path = Path(mb_catalog.__file__)
    body = ast.parse(path.read_text(encoding="utf-8")).body
    for statement, following in zip(body, body[1:], strict=False):
        if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
            continue
        constants = [each.value for each in statement.value.args if isinstance(each, ast.Constant)]
        if (
            identifier.rpartition("/")[2] in constants
            and isinstance(following, ast.Expr)
            and isinstance(following.value, ast.Constant)
        ):
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield MB_PARTS / "mb479_line_1.yaml"
    yield MB_PARTS / "mb479_line_2_input.yaml"
    yield MB_PARTS / "mb479_line_3.yaml"
    yield MB_PARTS / "mb479_line_4_input.yaml"
    yield MB_PARTS / "mb479_line_5.yaml"
    yield MB_PARTS / "mb479_line_5_column_2_input.yaml"
    yield MB_PARTS / "mb479_line_6.yaml"
    yield MB_PARTS / "mb479_line_7.yaml"
    yield MB_PARTS / "mb479_line_17_inputs.yaml"
    yield MB_PARTS / "mb479_line_17.yaml"
    yield MB_PARTS / "mb479_line_18.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, *artifacts: Artifact[Any]) -> Worksheet:
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *artifacts)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _line_19(tmp_path: Path, *artifacts: Artifact[Any]) -> Decimal:
    return D(_sheet(tmp_path, *artifacts).get(manitoba_kinds().kind(KIND)).value)


def _expected(salary: Decimal, column_2: Decimal = ZERO) -> Decimal:
    line_18 = _cent((_net_income(salary) + column_2) * D("0.01"))
    return _cent(max(BASIC_CREDIT - line_18, D(0)))


@pytest.mark.parametrize(("salary", "line_6", "expected"), CASES)
def test_line_19_is_line_17_minus_line_18_floored_at_zero(
    tmp_path: Path, salary: str, line_6: str, expected: str
) -> None:
    assert _net_income(D(salary)) == D(line_6)
    assert _expected(D(salary)) == D(expected)
    assert _line_19(tmp_path, Artifact(EMPLOYMENT_INCOME, D(salary))) == D(expected)


def test_line_19_is_floored_at_zero_when_column_2_drives_line_18_above_line_17(
    tmp_path: Path,
) -> None:
    # Line 6 is 2,069,335, so line 18 is 20,693.35, far above the 195.00 of line 17.
    line_19 = _line_19(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(MB479_FAMILY_INCOME_COLUMN_2_LINE_5, D("2000000")),
    )

    assert _expected(D("70000"), D("2000000")) == D(0)
    assert line_19 == D("0.00")
    assert line_19 >= 0


def test_line_19_is_zero_when_line_18_equals_line_17(tmp_path: Path) -> None:
    # Line 6 is 19,500.00, so line 18 is exactly 195.00.
    line_19 = _line_19(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("10000")),
        Artifact(MB479_FAMILY_INCOME_COLUMN_2_LINE_5, D("9565")),
    )

    assert line_19 == D("0.00")


def test_line_19_takes_line_6_with_column_2_when_it_is_given(tmp_path: Path) -> None:
    # Line 6 is 9,935 + 500 = 10,435, line 18 is 104.35.
    line_19 = _line_19(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("10000")),
        Artifact(MB479_FAMILY_INCOME_COLUMN_2_LINE_5, D("500")),
    )

    assert line_19 == _expected(D("10000"), D("500"))
    assert line_19 == D("90.65")


@pytest.mark.parametrize("salary", ["10000", "20000"])
def test_line_19_is_produced_non_negative(tmp_path: Path, salary: str) -> None:
    assert _line_19(tmp_path, Artifact(EMPLOYMENT_INCOME, D(salary))) >= 0


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_titled_subtract_not_below_zero_step_over_lines_17_and_18() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "params", "consumes", "produces"]
    assert "blank" not in step
    assert step == {
        "name": "core/subtract_not_below_zero",
        "title": "Personal tax credit",
        "reference": "19",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {
            "amount": "ca-mb/mb479_total_credits_line_17",
            "less": "ca-mb/mb479_reduction_line_18",
        },
        "produces": {"output": KIND},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert kind is mb_catalog.MB479_PERSONAL_TAX_CREDIT_LINE_19
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_the_docstring_names_the_form_and_the_lines_and_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(KIND))

    assert "MB479" in doc
    assert "line 19" in doc
    assert "line 17" in doc
    assert "line 18" in doc
    assert 'Line 17 minus line 18 (if negative, enter "0")' in doc
