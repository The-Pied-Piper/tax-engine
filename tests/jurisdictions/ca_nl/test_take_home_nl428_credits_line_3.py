"""NL428 (2025) line 3, the lower bound of the column for lines 2 to 8, real engine.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 3: 0.00" in column 1, "Line 3: 44,192.00"
in column 2, "Line 3: 88,382.00" in column 3 and "Line 3: 157,792.00" in column 4, under "Column 1:
Line 1 is $44,192 or less", "Column 2: Line 1 is more than $44,192 but not more than $88,382",
"Column 3: Line 1 is more than $88,382 but not more than $157,792" and "Column 4: Line 1 is more
than $157,792 but not more than $220,910". Line 3 is the printed lower bound of the column that
line 1 falls in. Above 220,910 the table (`ca-nl/brackets_lines_2_to_8`, whose bounds are the
printed ones) does not apply (lines 9 to 15 do), so line 3 is blank.

Line 3 is one `core/bracket_column_lower_bound` step over line 1 with that schedule, output
`ca-nl/nl428_bracket_lower_bound_line_3`, in the part `nl428_credits_line_3.yaml`. Line 1 is not
this ticket's: its part, `nl428_credits_line_1.yaml`, is composed as it is.

The real parts composed: the real Schedule 8, the T1 taxable-income parts, line 1 and
`nl428_credits_line_3.yaml`. The header, the salary input and the form declaration are test-local
(Newfoundland and Labrador has no salary part), the form exporting lines 1 and 3.

Figures, computed from the engine's T1 taxable income (line 26000): salary 70,000 gives line 1 of
69,335.00. Below the CPP and EI maxima the deduction is the enhanced CPP, 1% of salary over 3,500 to
the cent, so a salary of 44,603.03 gives exactly 44,192.00. The other column bounds are checked in
`test_brackets_lines_2_to_8_2025.py`. Hand figures, not a CRA example.
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
import tax_engine.jurisdictions.ca_nl
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
from tax_engine.jurisdictions.ca_nl.catalog import NL428_BRACKET_LOWER_BOUND_LINE_3
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
CODE = JurisdictionCode("CA-NL")
FORM = "ca-nl/nl428_credits"
LINE_1 = "ca-nl/nl428_taxable_income_line_1"
LINE_3 = "ca-nl/nl428_bracket_lower_bound_line_3"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = NL_PARTS / "nl428_credits_line_3.yaml"
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_10100.yaml",
    "t1_taxable_income_line_10400.yaml",
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
# The NL428 declaration, test-local: lines 1 and 3 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
    """)
LINE_1_PART = NL_PARTS / "nl428_credits_line_1.yaml"


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
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
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = newfoundland_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 is 69,335.00, over 44,192 and not over 88,382: column 2.
        ("70000", "44192.00"),
        # Line 1 of exactly 44,192.00 is still column 1.
        ("44603.03", "0.00"),
        # Line 1 is 88,382.01, over 88,382 and not over 157,792: column 3.
        ("89456.01", "88382.00"),
        # Line 1 is 198,926.00, over 157,792 and not over 220,910: column 4.
        ("200000", "157792.00"),
    ],
)
def test_line_3_is_the_lower_bound_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_3)).value == D(expected)


@pytest.mark.parametrize("salary", ["300000", "221984.01"])
def test_line_3_is_blank_when_line_1_is_above_220910(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_3)).is_blank


def test_the_blank_says_why_in_the_trace(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "300000")
    line = BracketOutsideRangeLine(_kind(LINE_3), _kind(LINE_1), D("298926.00"))

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith("(298926.00) is outside the range of the bracket table, so it is left blank.")
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
        "params": {"schedule": "ca-nl/brackets_lines_2_to_8"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_3},
    }


def test_line_3_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(LINE_3)

    assert kind is NL428_BRACKET_LOWER_BOUND_LINE_3
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
