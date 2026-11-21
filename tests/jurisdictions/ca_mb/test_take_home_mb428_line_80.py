"""MB428 (2025) line 80, line 78 minus line 79 (not below 0), from the salary alone, real parts.

Form text (Form MB428, CRA 5007-c): "Line 80: Line 78 minus line 79 (if negative, enter "0") = ^".
The form prints no title for the line, so the step is untitled. Line 80 is one
core/subtract_not_below_zero step over line 78 (`ca-mb/mb428_tax_line_78`) and line 79
(`ca-mb/mb428_employee_share_purchase_tax_credit_line_79`, the optional input of
`mb428_line_79_input.yaml`), rounded by `ca-mb/cent_rounding`. A salary-only caller has no employee
share purchase tax credit, so line 79 is left blank, and the step has a blank rule reading it as 0
and prints its own "left blank, taken as 0" row, as the line 78 step does for its line 77.

The test composes the real parts that lead to line 78 (the line 78 test's parts, including
`mb428_line_78.yaml`), the line 79 input part `mb428_line_79_input.yaml` and the new
`mb428_line_80.yaml`, and types in only the salary (and, in some tests, the line 79 input amount).
The header and the form declarations are made up here: the credits form exports lines 1, 3 to 8 and
57, and `ca-mb/mb428` exports only line 80. The figures are line 78 (the line 78 test, equal to
line 76) with line 79 left blank and read as 0, hand-computed from the printed forms, not a CRA
example: 0.00 / 5,747.59 (and 284.08 at 20,000, the floor case).
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
from tests.manifest_support import inputs_without_form

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_PART = MB_PARTS / "mb428_line_80.yaml"
LINE_79_INPUT_PART = MB_PARTS / "mb428_line_79_input.yaml"
LINE_78_PART = MB_PARTS / "mb428_line_78.yaml"
LINE_77_PART = MB_PARTS / "mb428_line_77.yaml"
LINE_77_INPUT_PART = MB_PARTS / "mb428_line_77_input.yaml"
LINE_76_PART = MB_PARTS / "mb428_line_76.yaml"
LINE_75_INPUT_PART = MB_PARTS / "mb428_line_75_input.yaml"
LINE_74_PART = MB_PARTS / "mb428_line_74.yaml"
LINE_73_INPUT_PART = MB_PARTS / "mb428_line_73_input.yaml"
LINE_72_PART = MB_PARTS / "mb428_line_72.yaml"
LINE_71_INPUT_PART = MB_PARTS / "mb428_line_71_input.yaml"
LINE_70_PART = MB_PARTS / "mb428_line_70.yaml"
LINE_69_INPUT_PART = MB_PARTS / "mb428_line_69_input.yaml"
LINE_67_PART = MB_PARTS / "mb428_line_67.yaml"
LINE_66_INPUT_PART = MB_PARTS / "mb428_line_66_input.yaml"
LINE_66_PART = MB_PARTS / "mb428_line_66.yaml"
LINE_65_PART = MB_PARTS / "mb428_line_65.yaml"
LINE_64_PART = MB_PARTS / "mb428_line_64.yaml"
LINE_60_PART = MB_PARTS / "mb428_line_60.yaml"
LINE_59_PART = MB_PARTS / "mb428_line_59_input.yaml"
LINE_58_PART = MB_PARTS / "mb428_line_58.yaml"
LINE_61_PART = MB_PARTS / "mb428_line_61.yaml"
LINE_62_PART = MB_PARTS / "mb428_line_62_input.yaml"
LINE_63_INPUT_PART = MB_PARTS / "mb428_credits_line_63_input.yaml"
LINE_63_PART = MB_PARTS / "mb428_line_63.yaml"
LINE_57_PART = MB_PARTS / "mb428_credits_line_57.yaml"
LINE_53_PART = MB_PARTS / "mb428_credits_line_53.yaml"
LINE_56_PARTS = tuple(
    MB_PARTS / name
    for name in (
        "mb428_credits_line_54_inputs.yaml",
        "mb428_credits_line_54.yaml",
        "mb428_credits_line_55_inputs.yaml",
        "mb428_credits_line_55.yaml",
        "mb428_credits_line_56.yaml",
    )
)
FORM_NAME = "ca-mb/mb428"
CREDITS_FORM_NAME = "ca-mb/mb428_credits"
LINE_57 = "ca-mb/mb428_non_refundable_credits_line_57"
LINE_78 = "ca-mb/mb428_tax_line_78"
LINE_79 = "ca-mb/mb428_employee_share_purchase_tax_credit_line_79"
IDENTIFIER = "ca-mb/mb428_tax_line_80"
CREDIT_PARTS = (
    *(f"mb428_credits_line_{n}.yaml" for n in (1, 3, 4, 5, 6, 7, 8)),
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
    "worksheet_mb428_other_dependants.yaml",
    "worksheet_mb428_other_dependants_line_3.yaml",
    "worksheet_mb428_other_dependants_total.yaml",
    "mb428_credits_line_49.yaml",
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
# The MB428 credits declaration, test-local: lines 1 to 57 are composed, so it exports lines 1, 3 to
# 8 (line 58 reads line 8) and 57.
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
        - {LINE_57}
    capabilities: []
    """)
# The MB428 declaration, test-local: lines 58 to 80 are composed, so it exports only line 80.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 80 with line 79 left out, so line 79 is blank and read as 0 and line 80 equals line
# 78. Line 78 is 0.00 / 5,747.59 (line 76 less a blank line 77).
CASES = [
    ("10000", "0.00"),
    ("70000", "5747.59"),
]
# salary, line 79 entry, line 78, line 80: line 78 minus line 79, not below 0.
CASES_WITH_LINE_79 = [
    # 5747.59 - 300.005 = 5447.585 rounds half-up to 5447.59.
    ("70000", "300.005", "5747.59", "5447.59"),
    # Line 79 above line 78 (284.08 at 20,000): the floor.
    ("20000", "300.00", "284.08", "0.00"),
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
    yield LINE_53_PART
    yield from LINE_56_PARTS
    yield LINE_57_PART
    yield LINE_58_PART
    yield LINE_59_PART
    yield LINE_60_PART
    yield LINE_61_PART
    yield LINE_62_PART
    yield LINE_63_INPUT_PART
    yield LINE_63_PART
    yield LINE_64_PART
    yield LINE_65_PART
    yield LINE_66_INPUT_PART
    yield LINE_66_PART
    yield LINE_67_PART
    yield LINE_69_INPUT_PART
    yield LINE_70_PART
    yield LINE_71_INPUT_PART
    yield LINE_72_PART
    yield LINE_73_INPUT_PART
    yield LINE_74_PART
    yield LINE_75_INPUT_PART
    yield LINE_76_PART
    yield LINE_77_INPUT_PART
    yield LINE_77_PART
    yield LINE_78_PART
    yield LINE_79_INPUT_PART
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, form declarations and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(WORKSHEET_FORM, encoding="utf-8")
    (folder / "02_schedule_form.yaml").write_text(SCHEDULE_FORM, encoding="utf-8")
    (folder / "03_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "04_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=5):
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


def _sheet(tmp_path: Path, salary: str, line_79: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_79 is not None:
        given.append(
            Artifact(mb_catalog.MB428_EMPLOYEE_SHARE_PURCHASE_TAX_CREDIT_LINE_79, D(line_79))
        )
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_80_is_line_78_when_line_79_is_left_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 78 is recomputed from the real parts, and line 79 is blank, read as 0.
    assert _line(sheet, LINE_78) == D(expected)
    assert sheet.get(manitoba_kinds().kind(LINE_79)).is_blank
    assert _line(sheet, IDENTIFIER) == D(expected)
    assert str(_line(sheet, IDENTIFIER)) == expected


@pytest.mark.parametrize(("salary", "line_79", "line_78", "expected"), CASES_WITH_LINE_79)
def test_line_80_is_line_78_minus_line_79_not_below_zero_when_line_79_is_given(
    tmp_path: Path, salary: str, line_79: str, line_78: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_79)

    assert _line(sheet, LINE_78) == D(line_78)
    # Line 79 is an input: the entry is taken as given.
    assert _line(sheet, LINE_79) == D(line_79)
    line_80 = _line(sheet, IDENTIFIER)
    assert line_80 == D(expected)
    assert str(line_80) == expected
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert not line_80.is_signed()


def test_the_sheet_prints_no_title_and_the_reference_of_line_80(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "80"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_a_blank_rule_on_line_79() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "80",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"amount": LINE_78, "less": LINE_79},
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step


def test_line_80_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(mb_catalog)["MB428_TAX_LINE_80"]
