"""BC428 (2025) line 67, add lines 64 to 66, from the real parts, real engine.

Form text (Form BC428, CRA 5010-C): "Line 67: Add lines 64 to 66. = ^". One core/sum step, rounded
half-up to the cent by `ca-bc/cent_rounding`, over line 64 (a copy of line 60, so the step consumes
`ca-bc/bc428_non_refundable_credits_line_60` and has no step of its own), line 65 (the British
Columbia dividend tax credit, computed from its
worksheet) and line 66 (the minimum tax carryover, the 34.9%
result). The form prints no title for the line beyond its label, so the step is untitled. Line 65
is always computed (a salary-only filer's worksheet gives 0.00), so the step has no blank rule; line
60 is always computed and line 66 defaults to 0 (its input is read as 0, not blank), so they need
none. The form prints no floor on line 67, but every addend is
non-negative, so the kind is non-negative.

The test composes the T1 employment income form, the Schedule 8 and T2204 parts, the real
BC428 parts up to line 60, the line 65 input part, the line 66 input and calculation parts, and the
new `bc428_line_67.yaml`, and types in only the salary, plus line 65 and the line 66 amount where a
case needs them. The header and the form declaration (BC428, exporting line 67) are made up here,
because the shared scaffold owns them. The salary figures are the line 60 test's: with lines 65 and
66 blank, line 67 is line 60.
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
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.credits_against_federal_tax import MINIMUM_TAX_CARRYOVER
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_MINIMUM_TAX_CARRYOVER_LINE_66,
    BC428_NON_REFUNDABLE_CREDITS_LINE_60,
    BC428_TOTAL_LINE_67,
)
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
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc428_line_67.yaml"
LINE_60 = "ca-bc/bc428_non_refundable_credits_line_60"
LINE_65 = "ca-bc/bc428_dividend_tax_credit_line_65"
LINE_66 = "ca-bc/bc428_minimum_tax_carryover_line_66"
IDENTIFIER = "ca-bc/bc428_total_line_67"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_total_line_67
    capabilities: []
    """)

# salary, line 67 with lines 65 and 66 blank (so line 67 is line 60, the line 60 test's figures).
CASES = [
    ("17000", "702.28"),
    ("200000", "878.70"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield from form_parts("t1_lines_copied_by_provinces")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield BC_PARTS / "bc428_line_16.yaml"
    yield BC_PARTS / "bc428_line_25.yaml"
    yield BC_PARTS / "bc428_line_27.yaml"
    yield BC_PARTS / "bc428_line_29.yaml"
    yield BC_PARTS / "bc428_line_33.yaml"
    yield BC_PARTS / "bc428_line_35.yaml"
    yield BC_PARTS / "bc428_line_36_input.yaml"
    yield BC_PARTS / "bc428_line_36.yaml"
    yield BC_PARTS / "bc428_line_37.yaml"
    yield BC_PARTS / "bc428_line_40.yaml"
    yield BC_PARTS / "bc428_line_45.yaml"
    yield BC_PARTS / "bc428_line_46.yaml"
    yield BC_PARTS / "bc428_line_47.yaml"
    yield BC_PARTS / "bc428_line_49.yaml"
    yield BC_PARTS / "bc428_line_50.yaml"
    yield BC_PARTS / "bc428_line_51.yaml"
    yield BC_PARTS / "bc428_line_52_input.yaml"
    yield BC_PARTS / "bc428_line_53.yaml"
    yield BC_PARTS / "bc428_line_54.yaml"
    yield BC_PARTS / "bc428_line_56.yaml"
    yield BC_PARTS / "bc428_line_57_input.yaml"
    yield BC_PARTS / "bc428_line_58.yaml"
    yield BC_PARTS / "bc428_line_59_input.yaml"
    yield BC_PARTS / "bc428_line_59.yaml"
    yield BC_PARTS / "bc428_line_60.yaml"
    yield BC_PARTS / "bc428_line_65.yaml"
    yield BC_PARTS / "bc428_line_66.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
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
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-BC"), 2025, *given)
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_67_is_line_60_when_lines_65_and_66_are_empty(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(BC428_TOTAL_LINE_67).value == D(expected)
    assert sheet.get(BC428_NON_REFUNDABLE_CREDITS_LINE_60).value == D(expected)
    assert sheet.get(BC428_MINIMUM_TAX_CARRYOVER_LINE_66).value == D("0")


def _dividends() -> list[Artifact[Decimal]]:
    kinds = british_columbia_kinds()
    return [
        Artifact(kinds.kind("ca/taxable_dividends"), D("1000")),
        Artifact(kinds.kind("ca/taxable_dividends_other_than_eligible"), D("400")),
    ]


@pytest.mark.parametrize(
    ("dividends", "carryover", "expected"),
    [
        # Line 65 is 7.84 plus 72.00, 79.84 (400 at 1.96%, 600 at 12%): 875.44 plus 79.84.
        (True, False, "955.28"),
        # Line 66 is 34.9% of 1,000.00, 349.00, so line 67 is 875.44 plus 349.00.
        (False, True, "1224.44"),
        # Both: 875.44 plus 79.84 plus 349.00.
        (True, True, "1304.28"),
    ],
)
def test_line_67_adds_lines_65_and_66_when_they_are_given(
    tmp_path: Path, dividends: bool, carryover: bool, expected: str
) -> None:
    extra = _dividends() if dividends else []
    if carryover:
        extra.append(Artifact(MINIMUM_TAX_CARRYOVER, D("1000")))

    sheet = _sheet(tmp_path, "70000", *extra)

    assert sheet.get(BC428_TOTAL_LINE_67).value == D(expected)


def test_line_66_is_34_9_percent_of_the_amount_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(MINIMUM_TAX_CARRYOVER, D("1000")))

    assert sheet.get(BC428_MINIMUM_TAX_CARRYOVER_LINE_66).value == D("349.00")


def test_the_trace_has_a_row_for_line_67(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)

    assert any("875.44" in row and "gives" in row for row in rows)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "67",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {"parts": [LINE_60, LINE_65, LINE_66]},
        "produces": {"output": IDENTIFIER},
    }


def test_line_67_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert kind is BC428_TOTAL_LINE_67
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
