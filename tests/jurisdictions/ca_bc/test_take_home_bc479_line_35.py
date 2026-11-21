"""BC479 (2025) line 35, the page 2 total, from the salary alone with the page 2 credit inputs given
or left out.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14, as recorded on the ticket): "Line 35: Add lines
16, 25, 26, 30 and 34. = ^". Line 35 is one core/sum step (`bc479_line_35.yaml`), rounded through
`ca-bc/cent_rounding`, over line 15 (`ca-bc/bc479_page_1_total_line_15`; line 16 is a page carry of
it, with no step of its own), lines 25 and 34 (each computed from its printed lines) and the line 26
and 30 inputs, producing
`ca-bc/bc479_page_2_total_line_35`, a non-negative kind, reference "35", with no title (the form
prints none). The line 26 and 30 inputs are optional and a salary-only caller leaves them blank, so
the step carries the blank rule that reads each as 0 and prints its own "left blank, taken as 0" row
per blank input.

The test composes the real salary part, the real Schedule 8 and T1 taxable income parts, the real
line 1 to line 15 parts, the line 17 to 34 parts and the new line 35 part, and types in the salary
and, in some tests, the inputs. The form declaration is made up here, exporting only line 35.
Figures are hand-computed from the printed forms (not a CRA example): line 15 is 37.70 at 17,000
and 0.00 above (no renovation expenses), so line 35 is 37.70 at 17,000 and 0.00 above with the
inputs blank.
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
import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_bc.catalog as bc_catalog
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
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc479"
LINE_13 = "ca-bc/bc479_sales_tax_credit_line_13"
LINE_15 = "ca-bc/bc479_page_1_total_line_15"
LINE_35 = "ca-bc/bc479_page_2_total_line_35"
VENTURE = bc_catalog.BC479_VENTURE_CAPITAL_CREDIT_LINE_25
VENTURE_GIVEN = bc_catalog.BC479_VENTURE_CAPITAL_CREDIT_LINE_21
MINING = bc_catalog.BC479_MINING_EXPLORATION_CREDIT_LINE_26
CLEAN = bc_catalog.BC479_CLEAN_BUILDINGS_CREDIT_LINE_30
TRAINING = bc_catalog.BC479_TRAINING_CREDITS_LINE_34
TRAINING_GIVEN = bc_catalog.BC479_TRAINING_CREDIT_INDIVIDUALS_LINE_31
EXPENSES = bc_catalog.BC479_HOME_RENOVATION_EXPENSES_LINE_14
BLANK_INPUTS = (MINING, CLEAN)
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc479_line_35.yaml"
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_35}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield _federal(name)
    yield BC_PARTS / "bc479_line_1.yaml"
    yield BC_PARTS / "bc479_line_2.yaml"
    yield BC_PARTS / "bc479_line_3.yaml"
    yield BC_PARTS / "bc479_line_4.yaml"
    yield BC_PARTS / "bc479_line_5.yaml"
    yield BC_PARTS / "bc479_line_6.yaml"
    yield BC_PARTS / "bc479_line_7.yaml"
    yield BC_PARTS / "bc479_line_8.yaml"
    yield BC_PARTS / "bc479_line_9.yaml"
    yield BC_PARTS / "bc479_line_11.yaml"
    yield BC_PARTS / "bc479_line_12.yaml"
    yield BC_PARTS / "bc479_line_13.yaml"
    yield BC_PARTS / "bc479_home_renovation_expenses_maximum.yaml"
    yield BC_PARTS / "bc479_line_14_input.yaml"
    yield BC_PARTS / "bc479_line_14_check.yaml"
    yield BC_PARTS / "bc479_line_14.yaml"
    yield BC_PARTS / "bc479_line_15.yaml"
    yield BC_PARTS / "bc479_line_17_input.yaml"
    yield BC_PARTS / "bc479_line_18_input.yaml"
    yield BC_PARTS / "bc479_line_20.yaml"
    yield BC_PARTS / "bc479_line_21_input.yaml"
    yield BC_PARTS / "bc479_line_23_input.yaml"
    yield BC_PARTS / "bc479_line_25.yaml"
    yield BC_PARTS / "bc479_line_26_input.yaml"
    yield BC_PARTS / "bc479_line_30_input.yaml"
    yield BC_PARTS / "bc479_line_31_input.yaml"
    yield BC_PARTS / "bc479_line_32_input.yaml"
    yield BC_PARTS / "bc479_line_33_input.yaml"
    yield BC_PARTS / "bc479_line_34.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{part.name}").write_text(text, encoding="utf-8")
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(CODE, 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


# salary, line 35 (line 15 plus the four blank inputs read as 0).
CASES = [
    ("17000", "37.70"),
    ("20000", "0.00"),
]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_35_is_line_15_with_the_inputs_blank_for_a_single_filer(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_35 = _sheet(tmp_path, salary).get(_kind(LINE_35)).value

    assert line_35 == D(expected)
    assert str(line_35) == expected
    assert not line_35.is_signed()


def test_line_35_adds_the_inputs_to_line_15(tmp_path: Path) -> None:
    # 17,000 gives line 15 of 37.70; 100.10 + 200.20 + 300.30 + 400.40 = 1,001.00 more.
    sheet = _sheet(
        tmp_path,
        "17000",
        Artifact(VENTURE_GIVEN, D("100.10")),
        Artifact(MINING, D("200.20")),
        Artifact(CLEAN, D("300.30")),
        Artifact(TRAINING_GIVEN, D("400.40")),
    )

    assert sheet.get(_kind(LINE_15)).value == D("37.70")
    assert sheet.get(_kind(LINE_35)).value == D("1038.70")


def test_line_35_includes_the_renovation_credit_through_line_15(tmp_path: Path) -> None:
    # 1,234.56 of expenses gives line 14 of 123.46, so line 15 is 161.16.
    sheet = _sheet(
        tmp_path, "17000", Artifact(EXPENSES, D("1234.56")), Artifact(TRAINING_GIVEN, D("1"))
    )

    assert sheet.get(_kind(LINE_35)).value == D("162.16")


def test_line_35_is_a_computed_zero_when_every_part_is_zero(tmp_path: Path) -> None:
    line_35 = _sheet(tmp_path, "70000").get(_kind(LINE_35))

    assert not line_35.is_blank
    assert line_35.value == D("0.00")
    assert str(line_35.value) == "0.00"


def test_each_blank_input_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    blanks = [each for each in sheet.trace if isinstance(each, BlankFallbackLine)]
    for kind in BLANK_INPUTS:
        (blank,) = [each for each in blanks if each.kind is kind]
        assert blank.fallback == 0
    rows = EnglishTraceRenderer().render_all(sheet.trace)
    assert sum("Left blank, taken as 0" in row for row in rows) >= 2


def test_a_given_input_prints_no_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(TRAINING_GIVEN, D("5.00")))

    blanked = {each.kind for each in sheet.trace if isinstance(each, BlankFallbackLine)}
    assert TRAINING_GIVEN not in blanked
    assert {MINING, CLEAN} <= blanked


def test_the_step_traces_one_sum_line_over_line_15_and_the_four_inputs(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(TRAINING_GIVEN, D("2.50")))
    kinds = british_columbia_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(LINE_35)]
    assert line.parts == (
        (kinds.kind(LINE_15), D("37.70")),
        (VENTURE, D("0.00")),
        (MINING, D("0")),
        (CLEAN, D("0")),
        (TRAINING, D("2.50")),
    )
    assert line.total == D("40.20")
    assert line.rounding.apply(D("0.005")) == D("0.01")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_has_one_untitled_sum_step_with_a_blank_rule_for_lines_26_and_30() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "35",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {
            "parts": [
                LINE_15,
                VENTURE.identifier,
                MINING.identifier,
                CLEAN.identifier,
                TRAINING.identifier,
            ]
        },
        "blank": {k.identifier: "0" for k in BLANK_INPUTS},
        "produces": {"output": LINE_35},
    }


def test_line_35_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_35 in kinds.identifiers()
    kind = kinds.kind(LINE_35)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC479_PAGE_2_TOTAL_LINE_35"]
