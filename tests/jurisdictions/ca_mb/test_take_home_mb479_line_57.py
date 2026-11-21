"""MB479 (2025) line 57, line 55 multiplied by line 56, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC): "Line 57: If you entered a number on line 56, multiply line 55
by line 56. Otherwise, enter the amount from line 55." Line 57 prints no label, so its step has no
title. It is one core/multiply of line 55 by the line 56 input. The line 56 input reads 1 when left
blank, so line 57 takes line 55 and the step needs no blank rule; line 55 is always produced.

The test composes the real Manitoba salary part, the real Schedule 8 parts, the real T1 taxable
income parts, the real MB479 parts of lines 1 to 7, 17, 18, 19 and 53, the real
`mb479_line_55.yaml`, the real line 56 input part and the new `mb479_line_57.yaml`, and types in
only
the salary (and, in two tests, line 56). The MB479 form declaration is made up here, exporting only
lines 55 and 57. The figures are line 55 as its own test pins it (95.65 / 0.00 / 0.00 / 0.00),
times 2 or 0 when line 56 is entered. They are hand-computed from the printed forms, not a CRA
example.
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
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
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
LINE_PART = MB_PARTS / "mb479_line_57.yaml"
FORM_NAME = "ca-mb/mb479"
IDENTIFIER = "ca-mb/mb479_credits_line_57"
LINE_55 = "ca-mb/mb479_credits_line_55"
LINE_56 = "ca-mb/mb479_eia_mspd_number_line_56"
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")
MB479_PARTS = (
    "mb479_line_1.yaml",
    "mb479_line_2_input.yaml",
    "mb479_line_3.yaml",
    "mb479_line_4_input.yaml",
    "mb479_line_5.yaml",
    "mb479_line_5_column_2_input.yaml",
    "mb479_line_6.yaml",
    "mb479_line_7.yaml",
    "mb479_line_17_inputs.yaml",
    "mb479_line_17.yaml",
    "mb479_line_18.yaml",
    "mb479_line_19.yaml",
    "mb479_line_53_input.yaml",
    "mb479_line_55.yaml",
    "mb479_line_56_input.yaml",
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
        - ca-mb/mb479_credits_line_55
        - ca-mb/mb479_credits_line_57
    capabilities: []
    """)

# salary, line 57: line 55 as its own test pins it, times line 56, blank and read as 1.
CASES = [
    ("10000", "95.65"),
    ("200000", "0.00"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in MB479_PARTS:
        yield MB_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
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


def _sheet(tmp_path: Path, salary: str, line_56: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_56 is not None:
        given.append(Artifact(mb_catalog.MB479_EIA_MSPD_NUMBER_LINE_56, D(line_56)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_57_is_line_55_when_line_56_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line(sheet, IDENTIFIER) == _line(sheet, LINE_55) == D(expected)


def test_line_57_multiplies_line_55_by_an_entered_line_56(tmp_path: Path) -> None:
    # Line 55 at a 10,000 salary is 95.65; times 2 is 191.30.
    sheet = _sheet(tmp_path, "10000", "2")

    assert _line(sheet, IDENTIFIER) == D("191.30")


def test_line_57_is_zero_when_line_56_is_entered_as_zero(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "10000", "0")

    assert _line(sheet, IDENTIFIER) == D("0.00")


def test_the_step_renders_as_a_product_line_with_no_left_blank_row_of_its_own(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "10000")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    product_rows = [row for row in rows if "multiplied by" in row and "gives" in row]
    assert product_rows
    assert not any("left blank" in row.lower() for row in product_rows)
    # The step has no blank rule, so no blank row names line 56 or the line 57 amount.
    assert not any("mb479_eia_mspd_number" in row.lower() for row in rows)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_multiply_step_over_lines_55_and_56() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert "blank" not in step
    assert step == {
        "name": "core/multiply",
        "reference": "57",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"multiplicand": LINE_55, "multiplier": LINE_56},
        "produces": {"output": IDENTIFIER},
    }


def test_line_57_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB479_CREDITS_LINE_57
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
