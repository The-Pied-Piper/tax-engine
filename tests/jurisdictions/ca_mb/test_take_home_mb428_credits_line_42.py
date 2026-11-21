"""MB428 (2025) line 42, add lines 36 to 41, from the salary alone, real parts.

Form text (Form MB428, Manitoba Tax, CRA 5007-c-25e.txt, read 2026-11-17): "Line 42: Add lines 36
to 41. = ^". Lines 37 to 40 are blank optional inputs for a salary-only filer and are skipped, so
line 42 is one core/sum over line 36 and line 41, as Alberta's line 43 skips lines 40 and 42.

The test composes the real Manitoba salary part, the real Schedule 8, T2204 and T1 taxable income
parts, the real parts of Worksheet MB428 lines 1 to 9, the real parts of lines 9, 18, 19, 21, 28,
29, 33 and 36, the line 31 input part, the real parts of Schedule MB428-A lines 1 to 12 and of
line 41, and the new `mb428_credits_line_42.yaml`, and types in only the salary (and, in one test,
the pension income amount). The header and the form declarations are made up here, exporting only
line 42 (and the Schedule MB428-A line 12 that line 41 reads), because the shared scaffold owns
them. The figures are hand-computed from the printed forms (not a CRA example): line 36 is line 33
(16,265.75 / 16,924.75 / 20,149.23 / 20,213.58), line 41 is the family tax benefit (1,170.85 /
279.85 / 0.00 / 0.00), and line 42 is their sum.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
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
LINE_PART = MB_PARTS / "mb428_credits_line_42.yaml"
IDENTIFIER = "ca-mb/mb428_credits_subtotal_line_42"
LINE_36 = "ca-mb/mb428_credits_subtotal_line_36"
LINE_41 = "ca-mb/mb428_family_tax_benefit_line_41"
FORM_NAME = "ca-mb/mb428_credits"
CREDIT_PARTS = (
    "mb428_credits_line_9.yaml",
    "mb428_credits_line_19.yaml",
    "mb428_credits_line_21.yaml",
    "mb428_credits_line_28.yaml",
    "mb428_credits_line_18.yaml",
    "mb428_credits_line_29.yaml",
    "mb428_credits_line_31_input.yaml",
    "mb428_credits_line_31.yaml",
    "mb428_credits_line_33.yaml",
    "mb428_credits_line_36.yaml",
    "mb428_credits_line_41.yaml",
)
SCHEDULE_PARTS = (
    "mb428_a_line_1.yaml",
    "mb428_a_line_10.yaml",
    "mb428_a_line_11.yaml",
    "mb428_a_line_11_product.yaml",
    "mb428_a_line_12.yaml",
)
WORKSHEET_PARTS = (
    "worksheet_mb428_line_1.yaml",
    "worksheet_mb428_line_2.yaml",
    "worksheet_mb428_line_3.yaml",
    "worksheet_mb428_line_4.yaml",
    "worksheet_mb428_line_5.yaml",
    "worksheet_mb428_line_6.yaml",
    "worksheet_mb428_line_7.yaml",
    "worksheet_mb428_line_8.yaml",
    "worksheet_mb428_line_9.yaml",
)
# The real federal parts the T1 taxable-income form needs, beside the salary and the worksheet.
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_basic_personal_amount_line_1
        - ca-mb/worksheet_mb428_line_2
        - ca-mb/worksheet_mb428_basic_personal_amount_line_3
        - ca-mb/worksheet_mb428_line_4
        - ca-mb/worksheet_mb428_basic_personal_amount_line_5
        - ca-mb/worksheet_mb428_line_6
        - ca-mb/worksheet_mb428_basic_personal_amount_line_7
        - ca-mb/worksheet_mb428_line_8
        - ca-mb/worksheet_mb428_basic_personal_amount_line_9
    capabilities: []
    """)

SCHEDULE_FORM = dedent("""\
    form:
      name: ca-mb/mb428_a
      required: true
      exports:
        - ca-mb/mb428_a_family_tax_benefit_line_12
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_credits_subtotal_line_42
    capabilities: []
    """)

# salary, line 42: line 36 plus line 41, lines 37 to 40 being blank optional inputs.
CASES = [
    ("10000", "17436.60"),
    ("200000", "20213.58"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in WORKSHEET_PARTS:
        yield MB_PARTS / name
    for name in SCHEDULE_PARTS:
        yield MB_PARTS / name
    for name in CREDIT_PARTS:
        yield MB_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, form declarations and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(WORKSHEET_FORM, encoding="utf-8")
    (folder / "02_schedule_form.yaml").write_text(SCHEDULE_FORM, encoding="utf-8")
    (folder / "03_credits_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=4):
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


def _line_42(tmp_path: Path, salary: str, pension: str | None = None) -> Decimal:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if pension is not None:
        given.append(Artifact(mb_catalog.MB428_PENSION_INCOME_AMOUNT, D(pension)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return D(sheet.get(manitoba_kinds().kind(IDENTIFIER)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_42_is_line_36_plus_line_41(tmp_path: Path, salary: str, expected: str) -> None:
    assert _line_42(tmp_path, salary) == D(expected)


def test_line_42_carries_a_given_pension_income_amount_through_line_36(tmp_path: Path) -> None:
    # Line 36 at a 70,000 salary is 20,149.23 and line 41 is 0.00; line 31 of 1,000.00 makes
    # 21,149.23 in line 36 and so in line 42.
    assert _line_42(tmp_path, "70000", "1000.00") == D("21149.23")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_like_alberta_line_43() -> None:
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
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "reference": "42",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_36, LINE_41]},
        "produces": {"output": IDENTIFIER},
    }


def test_line_42_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB428_CREDITS_SUBTOTAL_LINE_42
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
