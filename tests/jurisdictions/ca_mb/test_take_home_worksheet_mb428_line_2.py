"""Worksheet MB428 (2025) line 2, the amount from line 23600 of the return, from the salary alone.

Form text (Worksheet MB428, CRA 5007-D): "Line 2: Amount from line 23600 of your return". The form
names no label for the line, so the step has no title. Line 23600 is read as the T1 form exports it,
floored, `ca/t1_taxable_income.net_income`, which reaches this form only as a record list: line 2 is
a core/record_total over it, as BC428 line 74 is. The kind is non-negative.

The test composes the real Manitoba salary part, the real federal parts the T1 taxable income form
needs (Schedule 8 for line 23300, and the T1 lines 15000, 23300, 23400, 23600, 23600 signed and
26000 with their inputs) and the real `worksheet_mb428_line_2.yaml`, and types in only the salary.
The Worksheet MB428 form declaration is made up here, exporting only line 2, because the real
declaration exports another line. The service is built over the Manitoba package list of
`support.py`.

The expected figures are computed here, not typed: net income is the salary less the enhanced CPP
deduction, 1% of the pensionable earnings between the $3,500 basic exemption and the $71,300 year's
maximum pensionable earnings, plus the second additional CPP contribution, 4% of the earnings
between $71,300 and $81,200, each rounded half-up to the cent.
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
PART = MB_PARTS / "worksheet_mb428_line_2.yaml"
IDENTIFIER = "ca-mb/worksheet_mb428_line_2"
FORM_NAME = "ca-mb/worksheet_mb428"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 2.
FEDERAL_PARTS = (
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
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_line_2
    capabilities: []
    """)


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
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
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


def _line_2(tmp_path: Path, salary: str) -> Decimal:
    return D(_sheet(tmp_path, salary).get(manitoba_kinds().kind(IDENTIFIER)).value)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("10000", "9935.00"),
        ("20000", "19835.00"),
        ("70000", "69335.00"),
        ("200000", "198926.00"),
    ],
)
def test_line_2_is_the_t1_net_income(tmp_path: Path, salary: str, expected: str) -> None:
    assert _net_income(D(salary)) == D(expected)
    assert _line_2(tmp_path, salary) == _net_income(D(salary))


def test_the_part_is_one_untitled_record_total_step_over_the_t1_net_income() -> None:
    assert _step() == {
        "name": "core/record_total",
        "reference": "2",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.net_income"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_step_keys_are_in_order_and_there_is_no_title() -> None:
    assert list(_step()) == ["name", "reference", "unit", "consumes", "produces"]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.WORKSHEET_MB428_LINE_2
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_the_kind_rejects_a_negative_amount() -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(manitoba_kinds().kind(IDENTIFIER), D("-0.01"))


def test_the_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(IDENTIFIER))

    assert "Worksheet MB428" in doc
    assert 'line 2 "Line 2: Amount from line 23600 of your return"' in doc


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_no_left_blank_row_is_printed_for_line_2(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, salary)

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert rows
    assert not any("left blank, taken as" in row.lower() for row in rows)
