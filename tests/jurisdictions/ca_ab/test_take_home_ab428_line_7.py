"""AB428 (2025) line 7, the tax at the start of the column for lines 2 to 8, real engine.

Form text (Form AB428, CRA 5009-c-25e.txt, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-c/5009-c-25e.txt,
read 2026-11-12): "Column 1: Line 1 is $60,000 or less / ... Line 7: 0.00", "Column 2: Line 1 is
more than $60,000 but not more than $151,234 / ... Line 7: 4,800.00", "Column 3: Line 1 is more
than $151,234 but not more than $181,481 / ... Line 7: 13,923.40". Line 7 is the printed tax at the
start of the column that line 1 falls in, used as printed. Above 181,481 the table
(`ca-ab/brackets_lines_2_to_8`) does not apply (lines 9 to 15 do), so line 7 is blank.

Line 7 is one `core/bracket_column_tax_at_start` step over line 1 with that schedule, output
`ca-ab/ab428_bracket_tax_at_start_line_7`, in the part `ab428_line_7.yaml`. Line 1 is not this
ticket's: its part, `ab428_credits_line_1.yaml`, is composed as it is.

The real parts composed: the Alberta salary, the real Schedule 8, the T1 taxable-income parts,
line 1 and `ab428_line_7.yaml`. The form declaration is test-local, exporting lines 1 and 7.

Figures, computed here from the engine's T1 taxable income (line 26000): salary 20,000 gives line 1
of 19,835.00, 70,000 gives 69,335.00 and 200,000 gives 198,926.00. Above the CPP and EI maxima the
T1 deduction is a constant 1,074.00, so a salary of 182,555.00 gives line 1 of exactly 181,481.00,
and 152,308.00 gives 151,234.00. Below them the deduction is the enhanced CPP, 1% of salary over
3,500 to the cent, so a salary of 60,570.71 gives exactly 60,000.00.
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
import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BracketOutsideRangeLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import AB428_BRACKET_TAX_AT_START_LINE_7
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-AB")
FORM = "ca-ab/ab428_credits"
LINE_1 = "ca-ab/ab428_taxable_income_line_1"
LINE_7 = "ca-ab/ab428_bracket_tax_at_start_line_7"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = ALBERTA_PARTS / "ab428_line_7.yaml"
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
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The AB428 declaration, test-local: lines 1 and 7 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_7}
    """)
LINE_1_PART = ALBERTA_PARTS / "ab428_credits_line_1.yaml"


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield "salary.yaml", (ALBERTA_PARTS / "salary.yaml").read_text(encoding="utf-8")
    for found in sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml")):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            inputs_without_form(found)
            if name.endswith("_inputs.yaml")
            else found.read_text("utf-8"),
        )
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
    yield LINE_PART.name, LINE_PART.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = alberta_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(
    ("salary", "line_1"),
    [
        ("20000", "19835.00"),
        ("70000", "69335.00"),
        ("200000", "198926.00"),
        ("60570.71", "60000.00"),
        ("60570.72", "60000.01"),
        ("152308.00", "151234.00"),
        ("152308.01", "151234.01"),
        ("182555.00", "181481.00"),
        ("182555.01", "181481.01"),
    ],
)
def test_the_salaries_give_the_line_1_figures_the_line_7_cases_rest_on(
    tmp_path: Path, salary: str, line_1: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_1)).value == D(line_1)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 is 19,835.00, not over 60,000: column 1.
        ("20000", "0.00"),
        # Line 1 is 69,335.00, over 60,000 and not over 151,234: column 2.
        ("70000", "4800.00"),
        # Line 1 of exactly 60,000.00 is still column 1; a cent more is column 2.
        ("60570.71", "0.00"),
        ("60570.72", "4800.00"),
        # Line 1 of exactly 151,234.00 is still column 2; a cent more is column 3.
        ("152308.00", "4800.00"),
        ("152308.01", "13923.40"),
        # Line 1 of exactly 181,481.00 is the last figure in column 3.
        ("182555.00", "13923.40"),
    ],
)
def test_line_7_is_the_printed_tax_at_the_start_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_7)).value == D(expected)


@pytest.mark.parametrize("salary", ["200000", "182555.01"])
def test_line_7_is_blank_when_line_1_is_above_181481(tmp_path: Path, salary: str) -> None:
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
        "params": {"schedule": "ca-ab/brackets_lines_2_to_8"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_7},
    }


def test_line_7_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = alberta_kinds().kind(LINE_7)

    assert kind is AB428_BRACKET_TAX_AT_START_LINE_7
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
