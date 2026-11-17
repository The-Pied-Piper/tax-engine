"""MB428 (2025) line 1, taxable income, from the salary alone, real parts.

Form text (Form MB428, CRA 5007-C, read 2026-11-14): "Line 1: Enter your taxable income from line
26000 of your return." Line 1 is a calculation, not an input: its one step is a core/record_total
over the T1 export that gives taxable income (`ca/t1_taxable_income.taxable_income`), as Alberta's
line 1 is (`ab428_credits_line_1.yaml`). The form prints no label for the line, so the step has no
title. Line 2 in each column is a copy of line 1 and has no step.

The test composes the real Manitoba salary part, the real Schedule 8 parts, the real T1 taxable
income parts and the real line part (`mb428_credits_line_1.yaml`), and types in only the salary.
The form declaration is made up here, exporting the line read, because the real form part exports
only the lines already built.

The expected figures are computed here, not typed: taxable income (equal to net income) is the
salary less the enhanced CPP deduction, 1% of the pensionable earnings between the $3,500 basic
exemption and the $71,300 year's maximum pensionable earnings, plus the second additional CPP
contribution, 4% of the earnings between $71,300 and $81,200, each rounded half-up to the cent.
The four hand figures are asserted too (not a CRA example).
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
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
LINE_PART = MB_PARTS / "mb428_credits_line_1.yaml"
FORM_NAME = "ca-mb/mb428_credits"
KIND = "ca-mb/mb428_taxable_income_line_1"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
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
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_taxable_income_line_1
    capabilities: []
    """)

CASES = [
    ("10000", "9935.00"),
    ("20000", "19835.00"),
    ("70000", "69335.00"),
    ("200000", "198926.00"),
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


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line_1(tmp_path: Path, salary: str) -> Decimal:
    return D(_sheet(tmp_path, salary).get(manitoba_kinds().kind(KIND)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _taxable_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_1_is_the_t1_taxable_income(tmp_path: Path, salary: str, expected: str) -> None:
    assert _taxable_income(D(salary)) == D(expected)
    line_1 = _line_1(tmp_path, salary)

    assert line_1 == _taxable_income(D(salary))
    assert line_1 == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_record_total_step_over_the_t1_taxable_income() -> None:
    assert _step() == {
        "name": "core/record_total",
        "reference": "1",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.taxable_income"},
        "produces": {"output": KIND},
    }


def test_the_step_keys_are_in_order_and_there_is_no_title() -> None:
    assert list(_step()) == ["name", "reference", "unit", "consumes", "produces"]


def test_line_1_is_a_registered_non_negative_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_TAXABLE_INCOME_LINE_1


def test_the_kind_rejects_a_negative_amount() -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(manitoba_kinds().kind(KIND), D("-0.01"))


def test_the_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(KIND))

    assert "Form MB428" in doc
    assert 'Line 1 "Enter your taxable income from line 26000 of your return"' in doc


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_no_left_blank_row_is_printed_for_line_1(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, salary)

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert rows
    assert not any("left blank, taken as" in row.lower() for row in rows)
