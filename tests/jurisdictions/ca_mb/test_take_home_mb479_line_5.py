"""MB479 (2025) line 5, line 3 minus line 4 (not below 0), from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC, read 2026-11-14): "Line 5: Line 3 minus line 4 (if negative,
enter "0")" and "Column 1 You =". Column 1 (You) only; column 2 (the spouse) is not built for a
single filer. Line 5 is one core/subtract_not_below_zero step over line 3 (`amount`) and the line 4
input (`less`, the UCCB and RDSP income), which is optional and blank for a salary-only filer: the
blank line 4 is read as 0 and the step prints its own "left blank, taken as 0" row. The result is
floored at 0, so the kind `ca-mb/mb479_family_income_column_1_line_5` is non-negative. The form
names no label for the line, so the step has no title.

The test composes the real Manitoba salary part, the real Schedule 8 parts, the real T1 taxable
income parts, the real line 1 and line 3 parts, the line 2 and line 4 input parts and the line 5
part, and types in only the salary (and, in some tests, line 4). The MB479 form declaration is made
up here, exporting only line 5.

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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME, UCCB_INCOME
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
LINE_PART = MB_PARTS / "mb479_line_5.yaml"
FORM_NAME = "ca-mb/mb479"
LINE_3 = "ca-mb/mb479_family_income_before_benefits_line_3"
LINE_4 = "ca-mb/mb479_uccb_rdsp_income_line_4"
KIND = "ca-mb/mb479_family_income_column_1_line_5"
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
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200.yaml",
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
        - ca-mb/mb479_family_income_column_1_line_5
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
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield MB_PARTS / "mb479_line_1.yaml"
    yield MB_PARTS / "mb479_line_2.yaml"
    yield MB_PARTS / "mb479_line_3.yaml"
    yield MB_PARTS / "mb479_line_4.yaml"
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


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_5_is_line_3_when_line_4_is_blank(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, Artifact(EMPLOYMENT_INCOME, D(salary)))

    assert _net_income(D(salary)) == D(expected)
    assert sheet.get(manitoba_kinds().kind(KIND)).value == _net_income(D(salary))
    assert sheet.get(manitoba_kinds().kind(KIND)).value == D(expected)


def test_line_5_subtracts_line_4_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(UCCB_INCOME, D("500")),
    )

    assert sheet.get(manitoba_kinds().kind(KIND)).value == _net_income(D("70000")) - D("500")
    assert sheet.get(manitoba_kinds().kind(KIND)).value == D("68835.00")


def test_line_5_is_the_floor_when_line_4_exceeds_line_3(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("10000")),
        Artifact(UCCB_INCOME, D("10000")),
    )

    line_5 = sheet.get(manitoba_kinds().kind(KIND)).value
    assert D("10000") > _net_income(D("10000"))
    assert line_5 == D("0.00")
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert str(line_5) == "0.00"
    assert not line_5.is_signed()


def test_line_5_is_the_floor_when_line_4_equals_line_3(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("10000")),
        Artifact(UCCB_INCOME, D("9935.00")),
    )

    assert sheet.get(manitoba_kinds().kind(KIND)).value == D("0.00")


def test_a_given_line_4_prints_no_left_blank_row_for_it(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(UCCB_INCOME, D("500")),
    )

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert any("not below 0" in row for row in rows)
    blank_rows = [row for row in rows if "left blank, taken as 0" in row.lower()]
    assert not blank_rows  # lines 2 and 4 are sums of the T1 lines, never blank on this sheet


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_subtract_not_below_zero_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "5",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"amount": LINE_3, "less": LINE_4},
        "produces": {"output": KIND},
    }


def test_line_5_is_a_registered_non_negative_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB479_FAMILY_INCOME_COLUMN_1_LINE_5
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))


def test_the_docstring_quotes_the_form_text_for_column_1_only() -> None:
    doc = squashed(docstring_of(KIND))

    assert "MB479" in doc
    assert 'line 5 "Line 3 minus line 4 (if negative, enter "0")"' in doc
    assert "column 1" in doc
    assert "column 2" not in doc
