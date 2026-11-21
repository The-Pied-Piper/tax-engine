"""MB479 (2025) line 81, the Manitoba credits, from the salary alone with lines 79 and 80 given or
left out.

Form text (Form MB479, CRA 5007-tc-25e.txt): "Line 81: Add lines 78 to 80. Enter this amount on line
47900 of your return. Manitoba credits = ^". Line 81 is one core/sum step (`mb479_line_81.yaml`),
rounded through `ca-mb/cent_rounding`, over line 78 (`ca-mb/mb479_credits_line_78`), line 79 (the
teaching expense tax credit, a computed line that is never blank) and the line 80 input (the rental
housing construction incentive tax credit, optional), producing
`ca-mb/mb479_manitoba_credits_line_81`, a non-negative kind, reference "81",
titled "Manitoba credits" as printed. Only the line 80 input can be blank, so the step carries one
blank rule reading it as 0 and prints its own "left blank, taken as 0" row. The form exports line
81 and supplies it as `ca/provincial_credits.amount` (`mb479.yaml`, already in place).

The test composes the real Manitoba salary part, the real Schedule 8 and T1 taxable income parts,
the real MB479 parts of lines 1 to 80 and the new `mb479_line_81.yaml`, and types in the salary
and, in some tests, the line 79 teaching supplies expenses and the line 80 credit. The form
declaration is made up here, exporting only lines 78 to 81. Figures are hand-computed from the
printed forms (not a CRA example): line 78 is 95.65 / 0.00 / 0.00 / 0.00, so line 81 is the same
with lines 79 and 80 blank.
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
from tax_engine.domain.trace import BlankFallbackLine, SumLine
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
LINE_PART = MB_PARTS / "mb479_line_81.yaml"
FORM_NAME = "ca-mb/mb479"
IDENTIFIER = "ca-mb/mb479_manitoba_credits_line_81"
LINE_78 = "ca-mb/mb479_credits_line_78"
LINE_79_INPUT = "ca-mb/mb479_teaching_supplies_expenses_line_79"
LINE_79 = "ca-mb/mb479_teaching_expense_credit_line_79"
LINE_80 = "ca-mb/mb479_rental_housing_construction_incentive_tax_credit_line_80"

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
    "t1_uccb_rdsp.yaml",
    "t1_uccb_rdsp_line_11700_inputs.yaml",
    "t1_uccb_rdsp_line_12500_inputs.yaml",
    "t1_uccb_rdsp_line_21300_inputs.yaml",
    "t1_uccb_rdsp_line_23200_inputs.yaml",
    "t1_uccb_rdsp_line_11700.yaml",
    "t1_uccb_rdsp_line_12500.yaml",
    "t1_uccb_rdsp_line_21300.yaml",
    "t1_uccb_rdsp_line_23200.yaml",
)
MB479_PARTS = (
    "mb479_line_1.yaml",
    "mb479_line_2.yaml",
    "mb479_line_3.yaml",
    "mb479_line_4.yaml",
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
    "mb479_line_57.yaml",
    "mb479_line_59_input.yaml",
    "mb479_line_60.yaml",
    "mb479_line_61_input.yaml",
    "mb479_line_61.yaml",
    "mb479_line_62.yaml",
    "mb479_line_63_input.yaml",
    "mb479_line_64.yaml",
    "mb479_line_65_input.yaml",
    "mb479_line_66.yaml",
    "mb479_line_67_input.yaml",
    "mb479_line_68_input.yaml",
    "mb479_line_68.yaml",
    "mb479_line_69.yaml",
    "mb479_line_70.yaml",
    "mb479_line_71_input.yaml",
    "mb479_line_72.yaml",
    "mb479_line_73_input.yaml",
    "mb479_line_73.yaml",
    "mb479_line_74.yaml",
    "mb479_line_75_input.yaml",
    "mb479_line_75.yaml",
    "mb479_line_76.yaml",
    "mb479_line_77_input.yaml",
    "mb479_line_77.yaml",
    "mb479_line_78.yaml",
    "mb479_line_79_input.yaml",
    "mb479_line_79.yaml",
    "mb479_line_80_input.yaml",
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
        - ca-mb/mb479_credits_line_78
        - ca-mb/mb479_teaching_expense_credit_line_79
        - ca-mb/mb479_manitoba_credits_line_81
    capabilities: []
    """)

# salary, line 81: lines 78 to 80 with lines 79 and 80 blank (line 79 computes 0.00, line 80 is
# read as 0).
CASES = [
    ("10000", "95.65"),
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


def _sheet(
    tmp_path: Path, salary: str, line_79: str | None = None, line_80: str | None = None
) -> Worksheet:
    kinds = manitoba_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_79 is not None:
        given.append(Artifact(kinds.kind(LINE_79_INPUT), D(line_79)))
    if line_80 is not None:
        given.append(Artifact(kinds.kind(LINE_80), D(line_80)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


def _blank_rows(sheet: Worksheet) -> list[str]:
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)
    return [row for row in rows if row.lower().startswith("left blank, taken as ca$0")]


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    assert all(isinstance(step, dict) for step in steps)
    return steps


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_81_is_line_78_when_lines_79_and_80_are_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    value = _line(sheet, IDENTIFIER)

    assert value == _line(sheet, LINE_78) == D(expected)
    assert str(value) == expected
    assert _line(sheet, LINE_79) == D("0.00")
    assert sheet.get(manitoba_kinds().kind(LINE_80)).is_blank


@pytest.mark.parametrize(
    ("salary", "line_79", "line_80", "expected"),
    [
        ("10000", "1000", "500.00", "745.65"),
        ("10000", "200.50", "10.00", "135.73"),
    ],
)
def test_line_81_adds_lines_78_to_80(
    tmp_path: Path, salary: str, line_79: str | None, line_80: str | None, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_79=line_79, line_80=line_80)
    value = _line(sheet, IDENTIFIER)
    given_80 = D(line_80) if line_80 is not None else D(0)

    assert value == _line(sheet, LINE_78) + _line(sheet, LINE_79) + given_80 == D(expected)
    assert str(value) == expected


def test_line_81_is_a_computed_zero_when_every_part_is_zero(tmp_path: Path) -> None:
    line_81 = _sheet(tmp_path, "70000").get(manitoba_kinds().kind(IDENTIFIER))

    assert not line_81.is_blank
    assert str(line_81.value) == "0.00"


def test_only_the_line_80_input_is_blank_taken_as_0_on_this_step(tmp_path: Path) -> None:
    kinds = manitoba_kinds()
    sheet = _sheet(tmp_path, "10000")

    blanked = [t.kind for t in sheet.trace if isinstance(t, BlankFallbackLine)]
    assert blanked.count(kinds.kind(LINE_80)) == 1
    assert kinds.kind(LINE_79) not in blanked
    assert kinds.kind(LINE_78) not in blanked


def test_the_sheet_prints_the_title_and_the_reference_of_line_81(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "10000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) == "Manitoba credits"
    assert sheet.reference(label) == "81"
    (step,) = _steps()
    assert step["title"] == "Manitoba credits"
    assert step["reference"] == "81"


def test_the_step_traces_one_sum_line_over_lines_78_to_80(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "10000", line_79="1000", line_80="500.00")
    kinds = manitoba_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line.parts == (
        (kinds.kind(LINE_78), D("95.65")),
        (kinds.kind(LINE_79), D("150.00")),
        (kinds.kind(LINE_80), D("500.00")),
    )
    assert line.total == D("745.65")
    assert line.rounding.apply(D("0.005")) == D("0.01")


def test_the_trace_prints_the_left_blank_row_of_line_81_when_line_80_is_blank(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "10000")
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert _blank_rows(sheet)
    (row,) = [
        r
        for r in rows
        if r.startswith("Line 78 (")
        and " plus line 79 (" in r
        and " plus line 80 (" in r
        and "(CA$95.65)" in r
        and "(CA$0.00)" in r
    ]
    assert "95.65" in row.split(" gives ")[1]


def test_the_part_is_one_titled_sum_step_over_lines_78_to_80() -> None:
    (step,) = _steps()

    assert list(step) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "title": "Manitoba credits",
        "reference": "81",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_78, LINE_79, LINE_80]},
        "blank": {LINE_80: "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB479_MANITOBA_CREDITS_LINE_81
    assert isinstance(kind, AmountKind)
    assert kind.identifier == IDENTIFIER
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_the_form_exports_line_81_and_supplies_it_as_the_provincial_credits() -> None:
    part = yaml.safe_load((MB_PARTS / "mb479.yaml").read_text(encoding="utf-8"))

    assert part["form"]["exports"] == [IDENTIFIER]
    assert part["form"]["supplies"] == {"ca/provincial_credits.amount": IDENTIFIER}
