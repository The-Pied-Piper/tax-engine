"""MB479 (2025) line 18, line 6 multiplied by 1%, from the salary alone, real parts.

Form text (form MB479, CRA 5007-TC): "Line 18: Amount from line 6 above multiplied by 1% =". The 1%
is a printed rate, so it is the `ca-mb/personal_tax_credit_reduction_rate` dataset figure and has
no step of its own; the line is one core/apply_rate step over line 6 (family income), rounded
half-up to the cent by the dataset's own rule, as MB428-A line 11 is over its net income box. The
form prints no sentence for line 6 itself, so none is quoted, and it names no label for line 18, so
the step has no title.

The test composes the real Manitoba salary part, the real Schedule 8 parts, the real T1 taxable
income parts, the real line 1, line 2 input, line 3, line 4 input, line 5, line 5 column 2 input and
line 6 parts and the new line 18 part, and types in only the salary (and, in some tests, the column
2 figure). The MB479 form declaration is made up here, exporting only line 18.

The expected figures are computed here, not typed: line 6 is the salary less the enhanced CPP
deduction (plus column 2 when given), times 0.01, half-up to the cent. They are hand-computed from
the printed forms, not a CRA example.
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
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = MB_PARTS / "mb479_line_18.yaml"
FORM_NAME = "ca-mb/mb479"
KIND = "ca-mb/mb479_reduction_line_18"
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
        - ca-mb/mb479_reduction_line_18
    capabilities: []
    """)

# salary, line 6 (as the line 6 test pins), line 18
CASES = [
    ("10000", "9935.00", "99.35"),
    ("200000", "198926.00", "1989.26"),
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


def _line_18(tmp_path: Path, *artifacts: Artifact[Any]) -> Decimal:
    return D(_sheet(tmp_path, *artifacts).get(manitoba_kinds().kind(KIND)).value)


@pytest.mark.parametrize(("salary", "line_6", "expected"), CASES)
def test_line_18_is_line_6_times_1_percent(
    tmp_path: Path, salary: str, line_6: str, expected: str
) -> None:
    assert _net_income(D(salary)) == D(line_6)
    assert _cent(D(line_6) * D("0.01")) == D(expected)
    assert _line_18(tmp_path, Artifact(EMPLOYMENT_INCOME, D(salary))) == D(expected)


def test_line_18_takes_line_6_with_column_2_when_it_is_given(tmp_path: Path) -> None:
    line_18 = _line_18(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(MB479_FAMILY_INCOME_COLUMN_2_LINE_5, D("500")),
    )

    assert line_18 == _cent((_net_income(D("70000")) + D("500")) * D("0.01"))
    assert line_18 == D("698.35")


def test_line_18_rounds_half_up_to_the_cent(tmp_path: Path) -> None:
    # Line 6 is 69,335.50, so the exact product is 693.3550: the third decimal is a 5, rounded up.
    line_18 = _line_18(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(MB479_FAMILY_INCOME_COLUMN_2_LINE_5, D("0.50")),
    )

    assert (_net_income(D("70000")) + D("0.50")) * D("0.01") == D("693.3550")
    assert line_18 == D("693.36")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_untitled_apply_rate_step_over_line_6() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/apply_rate",
        "reference": "18",
        "unit": "ca/cad",
        "params": {"rate": "ca-mb/personal_tax_credit_reduction_rate"},
        "consumes": {"base": "ca-mb/mb479_family_income_line_6"},
        "produces": {"output": KIND},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert kind is mb_catalog.MB479_REDUCTION_LINE_18
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_the_docstring_names_the_form_and_both_lines_and_quotes_the_multiplication() -> None:
    doc = squashed(docstring_of(KIND))

    assert "MB479" in doc
    assert "line 18" in doc
    assert "line 6" in doc
    assert "multiplied by 1%" in doc
    assert "Add the amounts" not in doc
