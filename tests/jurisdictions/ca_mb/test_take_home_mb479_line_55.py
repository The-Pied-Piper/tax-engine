"""MB479 (2025) line 55, line 53 plus line 54, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC): "Line 54: Enter your personal tax credit from line 19." and
"Line 55: Line 53 plus line 54 =". Line 54 is a copy of line 19, so it gets no step. Line 55 prints
no label, so its step has no title. Line 55 is one core/sum over the line 53 input and line 19, as
MB428 line 51 is; a blank line 53 is read as 0 and the step prints its own "Left blank, taken as 0"
row. Line 19 is always produced, so it needs no blank row.

The test composes the real Manitoba salary part, the real Schedule 8 parts, the real T1 taxable
income parts, the real MB479 parts of lines 1 to 7, 17, 18 and 19, the line 53 input part and the
new `mb479_line_55.yaml`, and types in only the salary (and, in one test, line 53). The MB479 form
declaration is made up here, exporting only line 55 and the line 19 it reads. The figures are line
19 as its own test pins them (95.65 / 0.00 / 0.00 / 0.00), plus line 53 of 0 when blank. They are
hand-computed from the printed forms, not a CRA example.
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
LINE_PART = MB_PARTS / "mb479_line_55.yaml"
FORM_NAME = "ca-mb/mb479"
IDENTIFIER = "ca-mb/mb479_credits_line_55"
LINE_19 = "ca-mb/mb479_personal_tax_credit_line_19"
LINE_53 = "ca-mb/mb479_homeowner_renter_senior_credits_line_53"
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
        - ca-mb/mb479_personal_tax_credit_line_19
    capabilities: []
    """)

# salary, line 55: line 19 as its own test pins it, plus line 53, blank and read as 0.
CASES = [
    ("10000", "95.65"),
    ("20000", "0.00"),
    ("70000", "0.00"),
    ("200000", "0.00"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
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


def _sheet(tmp_path: Path, salary: str, line_53: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_53 is not None:
        given.append(Artifact(mb_catalog.MB479_HOMEOWNER_RENTER_SENIOR_CREDITS_LINE_53, D(line_53)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_55_is_line_19_when_line_53_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line(sheet, IDENTIFIER) == _line(sheet, LINE_19) == D(expected)


def test_line_55_adds_line_53_when_it_is_given(tmp_path: Path) -> None:
    # Line 19 at a 70,000 salary is 0.00; line 53 of 100.00 makes 100.00.
    sheet = _sheet(tmp_path, "70000", "100.00")

    assert _line(sheet, IDENTIFIER) == D("100.00")


def test_line_55_adds_line_53_to_a_non_zero_line_19(tmp_path: Path) -> None:
    # Line 19 at a 10,000 salary is 95.65; line 53 of 100.00 makes 195.65.
    sheet = _sheet(tmp_path, "10000", "100.00")

    assert _line(sheet, IDENTIFIER) == D("195.65")


def test_a_blank_line_53_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)

    assert any("left blank, taken as 0" in row.lower() for row in rows)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_over_lines_53_and_19() -> None:
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
    assert "title" not in step
    assert step == {
        "name": "core/sum",
        "reference": "55",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_53, LINE_19]},
        "blank": {LINE_53: "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_55_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB479_CREDITS_LINE_55
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
