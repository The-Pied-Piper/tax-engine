"""BC479 (2025) line 45, the British Columbia credits, from the salary alone with the page 2 credit
inputs and the line 44 input given or left out.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14, as recorded on the ticket): "Line 45: Line 36
plus line 44 Enter this amount on line 47900 of your return. British Columbia credits = ^". Line 45
is one core/sum step (`bc479_line_45.yaml`), rounded through `ca-bc/cent_rounding`, over line 35
(`ca-bc/bc479_page_2_total_line_35`; line 36 is a page carry of it, with no step of its own) and the
line 44 input, producing `ca-bc/bc479_british_columbia_credits_line_45`, a non-negative kind,
reference "45", titled as printed. Line 44 is optional and a salary-only caller leaves it blank, so
the step carries the blank rule that reads it as 0 and prints its own "left blank, taken as 0" row.

The test composes the real salary part, the real Schedule 8 and T1 taxable income parts, the real
line 1 to line 44 parts and the new line 45 part, and types in the salary and, in some tests, the
inputs. The form declaration is made up here, exporting only line 45. Figures are hand-computed from
the printed forms (not a CRA example): line 35 is 37.70 at 17,000 and 0.00 above, so line 45 is
37.70 at 17,000 and 0.00 above with line 44 blank.
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

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc479"
LINE_15 = "ca-bc/bc479_page_1_total_line_15"
LINE_35 = "ca-bc/bc479_page_2_total_line_35"
LINE_45 = "ca-bc/bc479_british_columbia_credits_line_45"
RENTER = bc_catalog.BC479_RENTERS_CREDIT_LINE_44
VENTURE = bc_catalog.BC479_VENTURE_CAPITAL_CREDIT_LINE_25
TRAINING = bc_catalog.BC479_TRAINING_CREDITS_LINE_34
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc479_line_45.yaml"
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
        - {LINE_45}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
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
    yield BC_PARTS / "bc479_line_25_input.yaml"
    yield BC_PARTS / "bc479_line_26_input.yaml"
    yield BC_PARTS / "bc479_line_30_input.yaml"
    yield BC_PARTS / "bc479_line_34_input.yaml"
    yield BC_PARTS / "bc479_line_35.yaml"
    yield BC_PARTS / "bc479_line_44_input.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        text = part.read_text(encoding="utf-8")
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


# salary, line 45 (line 35 plus a blank line 44 read as 0).
CASES = [
    ("17000", "37.70"),
    ("20000", "0.00"),
]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_45_is_line_35_with_line_44_blank_for_a_single_filer(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_45 = _sheet(tmp_path, salary).get(_kind(LINE_45)).value

    assert line_45 == D(expected)
    assert str(line_45) == expected
    assert not line_45.is_signed()


def test_line_45_adds_line_44_to_line_35(tmp_path: Path) -> None:
    # 17,000 gives line 35 of 37.70; the renter's credit of 400.00 is added.
    sheet = _sheet(tmp_path, "17000", Artifact(RENTER, D("400.00")))

    assert sheet.get(_kind(LINE_35)).value == D("37.70")
    assert sheet.get(_kind(LINE_45)).value == D("437.70")


def test_line_45_adds_line_44_to_a_line_35_with_inputs(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(TRAINING, D("5.00")), Artifact(RENTER, D("1.25")))

    assert sheet.get(_kind(LINE_45)).value == D("6.25")


def test_line_45_is_a_computed_zero_when_both_parts_are_zero(tmp_path: Path) -> None:
    line_45 = _sheet(tmp_path, "70000").get(_kind(LINE_45))

    assert not line_45.is_blank
    assert str(line_45.value) == "0.00"


def test_a_given_line_44_prints_no_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(RENTER, D("5.00")))

    blanked = {each.kind for each in sheet.trace if isinstance(each, BlankFallbackLine)}
    assert RENTER not in blanked
    assert VENTURE in blanked


def test_the_step_traces_one_sum_line_over_line_35_and_line_44(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(RENTER, D("2.50")))
    kinds = british_columbia_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(LINE_45)]
    assert line.parts == ((kinds.kind(LINE_35), D("37.70")), (RENTER, D("2.50")))
    assert line.total == D("40.20")
    assert line.rounding.apply(D("0.005")) == D("0.01")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_has_one_titled_sum_step_with_a_blank_rule_for_line_44() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": "British Columbia credits",
        "reference": "45",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_35, RENTER.identifier]},
        "blank": {RENTER.identifier: "0"},
        "produces": {"output": LINE_45},
    }


def test_line_45_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_45 in kinds.identifiers()
    kind = kinds.kind(LINE_45)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC479_BRITISH_COLUMBIA_CREDITS_LINE_45"]
