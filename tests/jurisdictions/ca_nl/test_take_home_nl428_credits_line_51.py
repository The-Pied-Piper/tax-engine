"""NL428 (2025) lines 49 and 51, net income and net income times 3%, from the salary, real parts.

Form text (Form NL428, CRA 5001-C, confirmed 2026-11-18): "Line 49: Amount from line 23600 of your
return", "Line 50: Applicable rate 3%" and "Line 51: Line 49 multiplied by the percentage from
line 50 =". Line 49 is read as the T1 form exports it, floored, `ca/t1_taxable_income.net_income`,
which reaches this form only as a record list, so it is a core/record_total over it, as line 1 is.
Line 50 is the printed 3%, the `ca-nl/medical_expense_rate` dataset, and has no step. Line 51 is a
core/apply_rate step that applies it to line 49, rounded half-up to the cent by the dataset's rule.
The form prints no label for either line, so neither step has a title.

The test composes the real Schedule 8 parts, the real T1 taxable income parts and the real line
part (`nl428_credits_line_51.yaml`), and types in only the salary. The header, the salary input and
the form declaration are made up here, the form exporting the two lines.

The expected figures are computed here, not typed: net income is the salary less the enhanced CPP
deduction, 1% of the pensionable earnings between the $3,500 basic exemption and the $71,300 year's
maximum pensionable earnings, plus the second additional CPP contribution, 4% of the earnings
between $71,300 and $81,200, each rounded half-up to the cent; line 51 is 3% of it, half-up to the
cent. The hand figures are asserted too (not a CRA example).
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
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.catalog as nl_catalog
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
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CENT = D("0.01")
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = NL_PARTS / "nl428_credits_line_51.yaml"
FORM_NAME = "ca-nl/nl428_credits"
LINE_49 = "ca-nl/nl428_net_income_line_49"
KIND = "ca-nl/nl428_medical_expenses_rate_amount_line_51"
# The real federal parts the T1 taxable-income form needs, beside the salary and lines 49 and 51.
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
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_net_income_line_49
        - ca-nl/nl428_medical_expenses_rate_amount_line_51
    capabilities: []
    """)

CASES = [
    ("10000", "9935.00", "298.05"),
    ("20000", "19835.00", "595.05"),
    ("70000", "69335.00", "2080.05"),
    ("200000", "198926.00", "5967.78"),
]


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in the catalog."""
    path = Path(nl_catalog.__file__)
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
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-NL"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


@pytest.mark.parametrize(("salary", "net_income", "expected"), CASES)
def test_line_51_is_net_income_times_3_percent(
    tmp_path: Path, salary: str, net_income: str, expected: str
) -> None:
    assert _net_income(D(salary)) == D(net_income)
    assert _cent(D(net_income) * D("0.03")) == D(expected)

    sheet = _sheet(tmp_path, salary)

    assert _value(sheet, LINE_49) == D(net_income)
    assert _value(sheet, KIND) == D(expected)


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def test_the_part_is_an_untitled_record_total_then_an_untitled_apply_rate_step() -> None:
    assert _steps() == [
        {
            "name": "core/record_total",
            "reference": "49",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_taxable_income.net_income"},
            "produces": {"output": LINE_49},
        },
        {
            "name": "core/apply_rate",
            "reference": "51",
            "unit": "ca/cad",
            "params": {"rate": "ca-nl/medical_expense_rate"},
            "consumes": {"base": LINE_49},
            "produces": {"output": KIND},
        },
    ]


def test_the_step_keys_are_in_order_and_there_is_no_title() -> None:
    first, second = _steps()

    assert list(first) == ["name", "reference", "unit", "consumes", "produces"]
    assert list(second) == ["name", "reference", "unit", "params", "consumes", "produces"]


@pytest.mark.parametrize(
    ("identifier", "declared"),
    [
        (LINE_49, nl_catalog.NL428_NET_INCOME_LINE_49),
        (KIND, nl_catalog.NL428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_51),
    ],
)
def test_each_kind_is_a_registered_non_negative_decimal_amount(
    identifier: str, declared: AmountKind
) -> None:
    kinds = newfoundland_kinds()

    assert identifier in kinds.identifiers()
    kind = kinds.kind(identifier)
    assert kind is declared
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))


def test_the_docstrings_quote_the_form_text() -> None:
    assert 'line 49 "Amount from line 23600 of your return"' in squashed(docstring_of(LINE_49))
    doc = squashed(docstring_of(KIND))

    assert 'line 51 "Line 49 multiplied by the percentage from line 50"' in doc


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_no_left_blank_row_is_printed_for_lines_49_and_51(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, salary)

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert rows
    assert not any("left blank, taken as" in row.lower() for row in rows)
