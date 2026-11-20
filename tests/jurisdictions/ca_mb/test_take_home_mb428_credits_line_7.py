"""MB428 (2025) line 7, the tax at the start of the column for lines 2 to 8, from the salary alone.

Form text (Form MB428, CRA 5007-C, read 2026-11-14,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt): "Column 1: Line 1
is $47,000 or less / ... Line 7: 0.00", "Column 2: Line 1 is more than $47,000 but not more than
$100,000 / ... Line 7: 5,076.00", "Column 3: Line 1 is more than $100,000 / ... Line 7: 11,833.50".
Line 7 is the printed tax at the start of the column that line 1 falls in, used as printed. The form
prints one set of three columns and the last has no upper boundary, so line 7 is never blank: the
schedule (`ca-mb/brackets_lines_2_to_8`) has no `up_to`.

Line 7 is one `core/bracket_column_tax_at_start` step over line 1 with that schedule, output
`ca-mb/mb428_bracket_tax_at_start_line_7`, in the part `mb428_credits_line_7.yaml`. The form does
not name line 7, so the step has no title.

The test composes the real Manitoba salary part, the real Schedule 8 and T1 taxable income parts,
the real `mb428_credits_line_1.yaml` and the real `mb428_credits_line_7.yaml`, and types in only the
salary. The form declaration is test-local, exporting lines 1 and 7.

Figures (hand-computed, not a CRA example): taxable income is the salary less the enhanced CPP
deduction, 9,935.00 / 198,926.00 (and 47,000.01 / 100,000.00 at the edges), so line 7 is 0.00 /
11,833.50 / 5,076.00 / 5,076.00. The boundary salaries are derived below: the deduction is 1% of
the earnings over $3,500 to the cent below the $71,300 maximum, and a flat $1,074.00 from $81,200.
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
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BracketColumnFigureLine
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
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = MB_PARTS / "mb428_credits_line_7.yaml"
FORM_NAME = "ca-mb/mb428_credits"
LINE_1 = "ca-mb/mb428_taxable_income_line_1"
LINE_7 = "ca-mb/mb428_bracket_tax_at_start_line_7"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
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
# The MB428 declaration, test-local: lines 1 and 7 are composed, so it exports those.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_1}
        - {LINE_7}
    capabilities: []
    """)

CASES = [
    ("10000", "9935.00", "0.00"),
    ("200000", "198926.00", "11833.50"),
]
# Salaries whose taxable income sits on a column's edge: line 1 is 47,000.00 or less in column 1,
# not more than 100,000.00 in column 2. One cent more is the next column.
EDGES = [
    ("47439.40", "47000.01", "5076.00"),
    ("101074.00", "100000.00", "5076.00"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield MB_PARTS / "mb428_credits_line_1.yaml"
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


def _kind(identifier: str) -> AmountKind:
    kind = manitoba_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("salary", "line_1", "expected"), [*CASES, *EDGES])
def test_line_7_is_the_printed_tax_at_the_start_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_7)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize("salary", ["500000", "5000000"])
def test_line_7_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(_kind(LINE_7))

    assert not artifact.is_blank
    assert artifact.value == D("11833.50")


@pytest.mark.parametrize(("salary", "line_1", "expected"), CASES)
def test_the_trace_names_the_tax_at_start_of_the_bracket_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    line = BracketColumnFigureLine(
        output=_kind(LINE_7),
        base=_kind(LINE_1),
        base_amount=D(line_1),
        name="tax at start",
        figure=D(expected),
    )

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith(f"falls in a bracket with {D(expected):.2f} of tax on the income below it.")
    )


def test_the_part_is_one_untitled_bracket_column_tax_at_start_step_over_line_1() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_tax_at_start",
        "reference": "7",
        "unit": "ca/cad",
        "params": {"schedule": "ca-mb/brackets_lines_2_to_8"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_7},
    }


def test_line_7_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert LINE_7 in kinds.identifiers()
    kind = kinds.kind(LINE_7)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_BRACKET_TAX_AT_START_LINE_7
