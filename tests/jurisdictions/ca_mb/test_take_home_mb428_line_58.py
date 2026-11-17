"""MB428 (2025) line 58, the Manitoba tax on taxable income from line 8, real parts.

Form text (Form MB428, CRA 5007-c): "Line 58: Manitoba tax on taxable income from line 8 ^" (Part C,
Manitoba tax). Line 58 is a copy of line 8, which sits on the other form `ca-mb/mb428_credits`
(lines 1 to 57), so its one step is a `core/record_total` over that form's line 8 export, read as a
record list (another form reads an export only as a record list). There is one table, so there is
no choice between two lines and no blank.

The test composes the real Manitoba salary part, the real Schedule 8, the T1 taxable income parts,
the real parts of lines 1, 3, 4, 5, 6, 7 and 8 of `ca-mb/mb428_credits`, and the new
`mb428_line_58.yaml`, and types in only the salary. The header and the two form declarations are
made up here: the credits form exports lines 1, 3, 4, 5, 6, 7 and 8, and `ca-mb/mb428` exports only
line 58. The figures are line 8 as the engine produces it (hand-computed in the line 8 test, not a
CRA example): 1,072.98 / 2,142.18 / 7,923.71 / 29,046.62.
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
from tax_engine.domain.trace import RecordTotalLine
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
LINE_PART = MB_PARTS / "mb428_line_58.yaml"
CREDITS_PARTS = tuple(f"mb428_credits_line_{n}.yaml" for n in (1, 3, 4, 5, 6, 7, 8))
FORM_NAME = "ca-mb/mb428"
CREDITS_FORM_NAME = "ca-mb/mb428_credits"
LINE_8 = "ca-mb/mb428_tax_on_taxable_income_line_8"
IDENTIFIER = "ca-mb/mb428_manitoba_tax_on_taxable_income_line_58"
TITLE = "Manitoba tax on taxable income from line 8"
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
# The credits form declaration, test-local: lines 1, 3, 4, 5, 6, 7 and 8 are composed.
CREDITS_FORM = dedent(f"""\
    form:
      name: {CREDITS_FORM_NAME}
      required: true
      exports:
        - ca-mb/mb428_taxable_income_line_1
        - ca-mb/mb428_bracket_lower_bound_line_3
        - ca-mb/mb428_taxable_income_over_lower_bound_line_4
        - ca-mb/mb428_bracket_rate_line_5
        - ca-mb/mb428_tax_on_excess_line_6
        - ca-mb/mb428_bracket_tax_at_start_line_7
        - {LINE_8}
    capabilities: []
    """)
# The MB428 declaration, test-local: only line 58 is composed, so it exports only that.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 58: the same as line 8.
CASES = [
    ("10000", "1072.98"),
    ("20000", "2142.18"),
    ("70000", "7923.71"),
    ("200000", "29046.62"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in CREDITS_PARTS:
        yield MB_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, form declarations and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=3):
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


def _sheet(tmp_path: Path, form: str, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[form]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_58_is_line_8_read_across_the_forms(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_8 = _line(_sheet(tmp_path, CREDITS_FORM_NAME, salary), LINE_8)
    line_58 = _line(_sheet(tmp_path / "other", FORM_NAME, salary), IDENTIFIER)

    assert line_8 == line_58 == D(expected)
    assert str(line_58) == expected


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_trace_totals_the_one_line_8_record(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, salary)
    kind = manitoba_kinds().kind(IDENTIFIER)

    (line,) = [t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output == kind]
    assert line.amounts == (D(expected),)
    assert line.total == D(expected)


def test_the_trace_row_prints_line_8_and_the_total_and_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, "70000")
    kind = manitoba_kinds().kind(IDENTIFIER)

    (line,) = [t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output == kind]
    row = EnglishTraceRenderer().render(line, sheet)
    assert row == "Line 8 (CA$7923.71) gives CA$7923.71."
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)
    assert not any("left blank, taken as" in each.lower() for each in rows)


def test_the_sheet_prints_the_title_and_the_reference_of_line_58(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, "70000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) == TITLE
    assert sheet.reference(label) == "58"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_titled_record_total_over_the_credits_form_line_8_export() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step == {
        "name": "core/record_total",
        "title": TITLE,
        "reference": "58",
        "unit": "ca/cad",
        "consumes": {"records": "ca-mb/mb428_credits.mb428_tax_on_taxable_income_line_8"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_58_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_MANITOBA_TAX_ON_TAXABLE_INCOME_LINE_58
