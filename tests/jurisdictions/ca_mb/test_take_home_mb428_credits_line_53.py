"""MB428 (2025) line 53, line 51 multiplied by the line 52 rate of 10.8%, from the salary alone.

Form text (Form MB428, CRA 5007-c): "Line 52: Manitoba non-refundable tax credits rate 10.8%" and
"Line 53 and line 58840: Line 51 multiplied by the percentage from line 52 = ^". Line 52 is a
printed rate, so it is the `ca-mb/credit_rate` dataset figure and has no step of its own; line 53
is one core/apply_rate step over line 51, rounded half-up to the cent by the dataset's own rule, as
Alberta's line 54 is over line 52. Line 53 prints no name, so the step has no title.

The test composes the T1 employment income form, the real Schedule 8, T2204 and T1 taxable income
parts, the real parts of Worksheet MB428 lines 1 to 9, the real parts of Schedule MB428-A lines 1 to
12, the real parts of MB428 lines 9, 18, 19, 21, 28, 29, 33, 36, 41, 42 and 51, the line 31 and line
50 input parts, and the new `mb428_credits_line_53.yaml`, and types in only the salary (and, in one
test, line 50). The header and the form declarations are made up here, exporting only line 53. The
figures are line 51 as the engine produces it (17,436.60 / 17,204.60 / 20,149.23 / 20,213.58) times
10.8%, half-up to the cent.
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

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_PART = MB_PARTS / "mb428_credits_line_53.yaml"
IDENTIFIER = "ca-mb/mb428_credits_at_rate_line_53"
LINE_51 = "ca-mb/mb428_credits_total_line_51"
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
    "mb428_credits_line_42.yaml",
    "mb428_credits_line_43_inputs.yaml",
    "mb428_credits_line_44.yaml",
    "mb428_credits_line_46.yaml",
    "mb428_credits_line_47.yaml",
    "mb428_credits_line_48.yaml",
    "mb428_credits_line_49_inputs.yaml",
    "mb428_credits_line_50.yaml",
    "mb428_credits_line_51.yaml",
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
        - ca-mb/mb428_credits_at_rate_line_53
    capabilities: []
    """)

# salary, line 53: line 51 as the engine produces it, times 10.8%, half-up to the cent. Line 51 is
# 17,436.60 / 17,204.60 / 20,149.23 / 20,213.58 (line 50 blank, read as 0): 1,883.1528, 1,858.0968,
# 2,176.11684 and 2,183.06664, rounded to 1,883.15 / 1,858.10 / 2,176.12 / 2,183.07.
CASES = [
    ("10000", "1883.15"),
    ("200000", "2183.07"),
]


def _part_files() -> Iterator[Path]:
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
            part.read_text(encoding="utf-8"),
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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_53_is_line_51_times_10_point_8_percent(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _line(_sheet(tmp_path, salary), IDENTIFIER) == D(expected)


def test_line_53_follows_line_51_when_line_49_is_given(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(mb_catalog.MB428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49, D("1000.00")),
    )

    # Line 51 at a 70,000 salary is 21,149.23 with line 50 of 1,000.00; times 0.108 is 2,284.11684,
    # rounded half-up to 2,284.12.
    assert _line(sheet, IDENTIFIER) == D("2284.12")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_apply_rate_step_like_alberta_line_54() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "53",
        "unit": "ca/cad",
        "params": {"rate": "ca-mb/credit_rate"},
        "consumes": {"base": LINE_51},
        "produces": {"output": IDENTIFIER},
    }


def test_line_53_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB428_CREDITS_AT_RATE_LINE_53
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
