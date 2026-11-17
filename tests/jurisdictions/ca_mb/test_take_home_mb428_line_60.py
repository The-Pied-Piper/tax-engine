"""MB428 (2025) line 60, line 58 plus line 59, from the salary alone, real parts.

Form text (Form MB428, CRA 5007-c): "Line 60: Line 58 plus line 59 = ^". The form prints no title
for the line, so the step is untitled. Line 59, "Line 59 and line 61510: Manitoba tax on split
income (complete Form T1206)", is an optional input, blank for a salary-only filer. Line 60 is one
core/sum over line 58 and the line 59 input, as line 51 is over line 42 and line 50; the blank
line 59 is read as 0 and the step prints its own "left blank, taken as 0" row.

The test composes the real Manitoba salary part, the real Schedule 8, the T1 taxable income parts,
the real parts of lines 1, 3, 4, 5, 6, 7 and 8 of `ca-mb/mb428_credits`, the real
`mb428_line_58.yaml` and `mb428_line_59_input.yaml`, and the new `mb428_line_60.yaml`, and types in
only the salary (and, in one test, line 59). The header and the two form declarations are made up
here: the credits form exports lines 1, 3, 4, 5, 6, 7 and 8, and `ca-mb/mb428` exports only line 60.
The figures are line 58 (the same as line 8, hand-computed in the line 8 test, not a CRA example)
plus line 59 of 0 when blank: 1,072.98 / 2,142.18 / 7,923.71 / 29,046.62.
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
LINE_PART = MB_PARTS / "mb428_line_60.yaml"
LINE_58_PART = MB_PARTS / "mb428_line_58.yaml"
LINE_59_PART = MB_PARTS / "mb428_line_59_input.yaml"
CREDITS_PARTS = tuple(f"mb428_credits_line_{n}.yaml" for n in (1, 3, 4, 5, 6, 7, 8))
FORM_NAME = "ca-mb/mb428"
CREDITS_FORM_NAME = "ca-mb/mb428_credits"
LINE_58 = "ca-mb/mb428_manitoba_tax_on_taxable_income_line_58"
LINE_59 = "ca-mb/mb428_tax_on_split_income_line_59"
IDENTIFIER = "ca-mb/mb428_tax_before_credits_line_60"
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
        - ca-mb/mb428_tax_on_taxable_income_line_8
    capabilities: []
    """)
# The MB428 declaration, test-local: lines 58 to 60 are composed, so it exports only line 60.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 60: line 58 (the same as line 8), plus line 59, blank and read as 0.
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
    yield LINE_58_PART
    yield LINE_59_PART
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


def _sheet(tmp_path: Path, salary: str, line_59: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_59 is not None:
        given.append(Artifact(mb_catalog.MB428_TAX_ON_SPLIT_INCOME_LINE_59, D(line_59)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_60_is_line_58_when_line_59_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line(sheet, IDENTIFIER) == _line(sheet, LINE_58) == D(expected)
    assert str(_line(sheet, IDENTIFIER)) == expected


def test_line_60_adds_line_59_when_it_is_given(tmp_path: Path) -> None:
    # Line 58 at a 70,000 salary is 7,923.71; line 59 of 100.00 makes 8,023.71.
    sheet = _sheet(tmp_path, "70000", "100.00")

    assert _line(sheet, IDENTIFIER) == D("8023.71")


def test_a_blank_line_59_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)

    assert any("left blank, taken as 0" in row.lower() for row in rows)


def test_the_sheet_prints_no_title_and_the_reference_of_line_60(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "60"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_over_lines_58_and_59() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "reference": "60",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_58, LINE_59]},
        "blank": {LINE_59: "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_60_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_TAX_BEFORE_CREDITS_LINE_60
