"""MB479 (2025) line 3, line 1 plus line 2, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC, read 2026-11-14): "Line 3: Line 1 plus line 2". Column 1 (You)
only; column 2 (the spouse) is not built for a single filer. Line 3 is one core/sum over line 1
(net income) and the line 2 input (the UCCB and RDSP repayments), which is optional and blank for a
salary-only filer: the blank line 2 is read as 0 and the step prints its own "left blank, taken as
0" row. The result is signed, because line 1 is.

The test composes the T1 employment income form, the real Schedule 8 parts, the real T1 taxable
income parts, the real line 1 part, the line 2 input part and the line 3 part, and types in only the
salary (and, in some tests, line 2 or the social benefits repayment). The MB479 form declaration is
made up here, exporting only line 3.

The expected figures are computed here, not typed: net income is the salary less the enhanced CPP
deduction, 1% of the pensionable earnings between the $3,500 basic exemption and the $71,300 year's
maximum pensionable earnings, plus 4% of the earnings between $71,300 and $81,200, each rounded
half-up to the cent. They are hand-computed from the printed forms, not a CRA example.
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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME, UCCB_REPAYMENT
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_PART = MB_PARTS / "mb479_line_3.yaml"
FORM_NAME = "ca-mb/mb479"
KIND = "ca-mb/mb479_family_income_before_benefits_line_3"
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb479
      required: true
      exports:
        - ca-mb/mb479_family_income_before_benefits_line_3
    capabilities: []
    """)

CASES = [
    ("10000", "9935.00"),
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
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield MB_PARTS / "mb479_line_1.yaml"
    yield MB_PARTS / "mb479_line_2.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
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
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-MB"), 2025, tuple(artifacts))
    )
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


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_3_is_line_1_when_line_2_is_blank(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, Artifact(EMPLOYMENT_INCOME, D(salary)))

    assert _net_income(D(salary)) == D(expected)
    assert sheet.get(manitoba_kinds().kind(KIND)).value == _net_income(D(salary))
    assert sheet.get(manitoba_kinds().kind(KIND)).value == D(expected)


def test_line_3_adds_line_2_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(UCCB_REPAYMENT, D("500")),
    )

    # The 500 repayment is deducted in the net income (T1 line 23300) and line 2 adds it back, so
    # line 3 is the net income of the salary alone.
    assert sheet.get(manitoba_kinds().kind(KIND)).value == _net_income(D("70000"))
    assert sheet.get(manitoba_kinds().kind(KIND)).value == D("69335.00")


def test_line_3_stays_negative_when_line_1_is_negative(tmp_path: Path) -> None:
    # Line 1 is -5,665.00 (see the line 1 test); line 3 keeps the sign, with line 2 blank and given.
    kinds = manitoba_kinds()
    repayment = Artifact(kinds.kind("ca/social_benefits_repayment"), D("75000"))
    salary = Artifact(EMPLOYMENT_INCOME, D("70000"))

    blank = _sheet(tmp_path / "blank", salary, repayment)
    given = _sheet(tmp_path / "given", salary, repayment, Artifact(UCCB_REPAYMENT, D("500")))

    assert blank.get(kinds.kind(KIND)).value == D("-5665.00")
    # The repayment is deducted in line 1 and added back by line 2, so line 3 stays -5,665.00.
    assert given.get(kinds.kind(KIND)).value == D("-5665.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/sum",
        "reference": "3",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-mb/mb479_net_income_line_1",
                "ca-mb/mb479_uccb_rdsp_repayments_line_2",
            ]
        },
        "produces": {"output": KIND},
    }


def test_line_3_is_a_registered_signed_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert not non_negative(kind)
    assert kind is mb_catalog.MB479_FAMILY_INCOME_BEFORE_BENEFITS_LINE_3


def test_the_docstring_quotes_the_form_text_for_column_1_only() -> None:
    doc = squashed(docstring_of(KIND))

    assert "MB479" in doc
    assert 'line 3 "Line 3: Line 1 plus line 2"' in doc
    assert "column 1" in doc
    assert "column 2" not in doc
