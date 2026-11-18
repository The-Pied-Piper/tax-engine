"""MB428 (2025) line 36, add lines 33 to 35, from the salary alone, real parts.

Form text (Form MB428, Manitoba Tax, CRA 5007-c-25e.txt, read 2026-11-17): "Line 36: Add lines 33
to 35. = ^". Lines 34 (the disability amount for self) and 35 (the disability amount transferred
from a dependant) are not built, so line 36 is one core/sum over line 33 alone, as Alberta's line
39 reads its line 36.

The test composes the real Manitoba salary part, the real Schedule 8, T2204 and T1 taxable income
parts, the real parts of Worksheet MB428 lines 1 to 9, the real parts of lines 9, 18, 19, 21, 28,
29 and 33, the line 31 input part and the new `mb428_credits_line_36.yaml`, and types in only the
salary (and, in one test, the pension income amount). The header and the form declarations are made
up here, exporting only line 36, because the shared scaffold owns them. The figures are
hand-computed from the printed forms (not a CRA example): line 36 equals line 33, which is line 29
(line 18 of 15,780.00 at every salary here, plus line 28 of 485.75 / 1,144.75 / 4,369.23 /
4,433.58) plus the pension income amount of 0.
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
LINE_PART = MB_PARTS / "mb428_credits_line_36.yaml"
IDENTIFIER = "ca-mb/mb428_credits_subtotal_line_36"
LINE_33 = "ca-mb/mb428_credits_subtotal_line_33"
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

FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_credits_subtotal_line_36
    capabilities: []
    """)

# salary, line 36: line 33 (line 29 plus line 31 of 0, left out), lines 34 and 35 not being built.
CASES = [
    ("10000", "16265.75"),
    ("20000", "16924.75"),
    ("70000", "20149.23"),
    ("200000", "20213.58"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in WORKSHEET_PARTS:
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
    (folder / "02_credits_form.yaml").write_text(FORM, encoding="utf-8")
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


def _line_36(tmp_path: Path, salary: str, pension: str | None = None) -> Decimal:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if pension is not None:
        given.append(Artifact(mb_catalog.MB428_PENSION_INCOME_AMOUNT, D(pension)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return D(sheet.get(manitoba_kinds().kind(IDENTIFIER)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_36_is_line_33_alone_as_lines_34_and_35_are_not_built(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _line_36(tmp_path, salary) == D(expected)


def test_line_36_carries_a_given_pension_income_amount_through_line_33(tmp_path: Path) -> None:
    # Line 33 at a 70,000 salary is 20,149.23; line 31 of 1,000.00 makes 21,149.23 in line 36.
    assert _line_36(tmp_path, "70000", "1000.00") == D("21149.23")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_like_alberta_line_39() -> None:
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
        "reference": "36",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_33]},
        "produces": {"output": IDENTIFIER},
    }


def test_line_36_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB428_CREDITS_SUBTOTAL_LINE_36
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
