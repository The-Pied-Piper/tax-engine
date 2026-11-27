"""BC428 (2025) line 3, the lower bound of the column for lines 2 to 8, from the salary alone.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Column 1: Line 1 is $49,279 or less / Line 3:
0.00", "Column 2: Line 1 is more than $49,279 but not more than $98,560 / Line 3: 49,279.00",
"Column 3: Line 1 is more than $98,560 but not more than $113,158 / Line 3: 98,560.00", "Column 4:
Line 1 is more than $113,158 but not more than $137,407 / Line 3: 113,158.00". Above 137,407 the
table (`ca-bc/brackets_lines_2_to_8`) does not apply (lines 9 to 15 do), so line 3 is blank.

Line 3 is one `core/bracket_column_lower_bound` step over line 1 with that schedule, output
`ca-bc/bc428_bracket_lower_bound_line_3`, in the part `bc428_line_3.yaml`.

Line 1 is the real `bc428_line_1.yaml` (#903). The real parts composed: the British Columbia salary,
Schedule 8, the T1 taxable-income parts, `bc428_line_1.yaml` and `bc428_line_3.yaml`. The form
declaration is test-local, exporting lines 1 and 3. The service is built over the package list of
`support.py`.

Figures (ticket, hand-computed): taxable income is the salary less the CPP enhanced and
second-ceiling amounts, 69,335.00 / 198,926.00, so line 3 is
49,279.00 for $70,000 and blank for $200,000.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BracketOutsideRangeLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC428_BRACKET_LOWER_BOUND_LINE_3
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_3 = "ca-bc/bc428_bracket_lower_bound_line_3"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc428_line_3.yaml"
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 1 and 3 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    for found in form_parts("schedule_8"):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            found.read_text("utf-8"),
        )
    yield "bc428_line_1.yaml", (BC_PARTS / "bc428_line_1.yaml").read_text(encoding="utf-8")
    yield LINE_PART.name, LINE_PART.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(dict.fromkeys(_part_files()), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(CODE, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 is 69,335.00, over 49,279 and not over 98,560: column 2.
        ("70000", "49279.00"),
        # Line 1 on the first column's upper edge stays in that column.
        ("49741.41", "0.00"),
    ],
)
def test_line_3_is_the_lower_bound_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_3)).value == D(expected)


@pytest.mark.parametrize("salary", ["200000", "138482"])
def test_line_3_is_blank_when_line_1_is_above_137407(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_3)).is_blank


def test_the_blank_says_why_in_the_trace(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")
    line = BracketOutsideRangeLine(_kind(LINE_3), _kind(LINE_1), D("198926.00"))

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith("(198926.00) is outside the range of the bracket table, so it is left blank.")
    )


def test_the_part_is_one_bracket_column_lower_bound_step_over_line_1() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_lower_bound",
        "reference": "3",
        "unit": "ca/cad",
        "params": {"schedule": "ca-bc/brackets_lines_2_to_8"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_3},
    }


def test_line_3_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_3)

    assert kind is BC428_BRACKET_LOWER_BOUND_LINE_3
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
