"""BC428 (2025) line 7, the tax at the start of the column for lines 2 to 8, real engine.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Column 1: Line 1 is $49,279 or less / ...
Line 7: 0.00", "Column 2: Line 1 is more than $49,279 but not more than $98,560 / ... Line 7:
2,493.52", "Column 3: Line 1 is more than $98,560 but not more than $113,158 / ... Line 7:
6,288.15" and "Column 4: Line 1 is more than $113,158 but not more than $137,407 / ... Line 7:
7,820.94". Line 7 is the printed tax at the start of the column that line 1 falls in, used as
printed. Above 137,407 the table (`ca-bc/brackets_lines_2_to_8`) does not apply, so line 7 is blank.

Line 7 is one `core/bracket_column_tax_at_start` step over line 1 with that schedule, output
`ca-bc/bc428_bracket_tax_at_start_line_7`, in the part `bc428_line_7.yaml`. Line 1 is
`ca-bc/bc428_taxable_income_line_1`, its part `bc428_line_1.yaml`, composed as it is; line 7 reads
it directly, so lines 3 and 4 are not composed.

The real parts composed: the British Columbia salary, Schedule 8, the T1 taxable-income parts, lines
1 and 7. The form declaration is test-local, exporting lines 1 and 7. The service is built over the
package list of `support.py`.

Figures (ticket, hand-computed): taxable income is the salary less the CPP enhanced and
second-ceiling amounts, 16,865.00 / 69,335.00 / 198,926.00, so line 7 is
0.00 for $17,000 (column 1), 2,493.52 for $70,000 (column 2) and blank for
$200,000. The salaries at the column edges are those of the BC428 line 4 test, whose line 1 figures
are checked there.
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
from tax_engine.jurisdictions.ca_bc.catalog import BC428_BRACKET_TAX_AT_START_LINE_7
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
LINE_7 = "ca-bc/bc428_bracket_tax_at_start_line_7"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_1_PART = BC_PARTS / "bc428_line_1.yaml"
LINE_PART = BC_PARTS / "bc428_line_7.yaml"
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
# The BC428 declaration, test-local: lines 1 and 7 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_7}
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
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
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
        # Line 1 is 16,865.00, not over 49,279: column 1.
        ("17000", "0.00"),
        # Line 1 is 69,335.00, over 49,279 and not over 98,560: column 2.
        ("70000", "2493.52"),
    ],
)
def test_line_7_is_the_printed_tax_at_the_start_of_the_column_for_the_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_7)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 of exactly 49,279.00 is still column 1; a cent more is column 2.
        ("49741.41", "0.00"),
        ("49741.42", "2493.52"),
    ],
)
def test_line_7_changes_column_just_above_each_printed_upper_bound(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_7)).value == D(expected)


@pytest.mark.parametrize("salary", ["200000", "138482"])
def test_line_7_is_blank_when_line_1_is_above_137407(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_7)).is_blank


def test_the_blank_says_why_in_the_trace(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")
    line = BracketOutsideRangeLine(_kind(LINE_7), _kind(LINE_1), D("198926.00"))

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith("(198926.00) is outside the range of the bracket table, so it is left blank.")
    )


def test_the_part_is_one_bracket_column_tax_at_start_step_over_line_1() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_tax_at_start",
        "reference": "7",
        "unit": "ca/cad",
        "params": {"schedule": "ca-bc/brackets_lines_2_to_8"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_7},
    }


def test_line_7_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_7)

    assert kind is BC428_BRACKET_TAX_AT_START_LINE_7
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
