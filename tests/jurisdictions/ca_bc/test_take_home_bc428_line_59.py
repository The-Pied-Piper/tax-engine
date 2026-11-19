"""BC428 (2025) line 59, the qualifying gifts also claimed on line 57 multiplied by 25%, from the
salary alone with the gifts input given or left out.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 59 and line 58980: Amount of qualifying
gifts also claimed on line 57 multiplied by 25% = ^". Line 59 is a dollars-and-cents line, and 25%
is a printed rate, so it is the `ca-bc/farmers_food_donation_rate` dataset figure. Line 59 is one
core/apply_rate step over the gifts input (`ca-bc/bc428_qualifying_gifts_line_59`), rounded half-up
to the cent by the dataset's own rule. The gifts input is an optional input a salary-only caller
leaves out, read as blank and then as 0 by the step's own blank rule, which prints its own "left
blank, taken as 0" row.

The test composes the real salary part, the line 59 input part and the new `bc428_line_59.yaml`,
and types in the salary and, in some tests, the gifts. The form declaration is made up here,
exporting only line 59. The figures are hand-computed from the printed form (not a CRA example):
the gifts times 0.25, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankFallbackLine, RateAppliedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_FARMERS_FOOD_DONATION_CREDIT_LINE_59,
    BC428_QUALIFYING_GIFTS_LINE_59,
)
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc428_line_59.yaml"
GIFTS = "ca-bc/bc428_qualifying_gifts_line_59"
IDENTIFIER = "ca-bc/bc428_farmers_food_donation_credit_line_59"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_farmers_food_donation_credit_line_59
    capabilities: []
    """)

# gifts given, line 59 (the gifts times 25%, rounded half-up to the cent)
CASES = [
    ("100.00", "25.00"),
    ("0.02", "0.01"),
]


def _part_files() -> list[Path]:
    return [
        BC_PARTS / "salary.yaml",
        BC_PARTS / "bc428_line_59_input.yaml",
        LINE_PART,
    ]


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{found.name}").write_text(
            found.read_text(encoding="utf-8"), encoding="utf-8"
        )
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


def _sheet(tmp_path: Path, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D("70000")), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-BC"), 2025, *given)
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet


@pytest.mark.parametrize(("gifts", "expected"), CASES)
def test_line_59_is_the_gifts_times_25_percent(tmp_path: Path, gifts: str, expected: str) -> None:
    sheet = _sheet(tmp_path, Artifact(BC428_QUALIFYING_GIFTS_LINE_59, D(gifts)))

    assert sheet.get(BC428_FARMERS_FOOD_DONATION_CREDIT_LINE_59).value == D(expected)


def test_line_59_is_zero_when_no_gifts_are_given(tmp_path: Path) -> None:
    assert _sheet(tmp_path).get(BC428_FARMERS_FOOD_DONATION_CREDIT_LINE_59).value == D("0")


def test_a_blank_gifts_line_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path)

    (blank,) = [
        each
        for each in sheet.trace
        if isinstance(each, BlankFallbackLine) and each.kind is BC428_QUALIFYING_GIFTS_LINE_59
    ]
    assert blank.fallback == 0
    rows = EnglishTraceRenderer().render_all(sheet.trace)
    assert any("Left blank, taken as 0" in row for row in rows)


def test_the_product_is_traced_with_its_base_and_the_rate(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, Artifact(BC428_QUALIFYING_GIFTS_LINE_59, D("100.00")))

    (line,) = (
        each
        for each in sheet.trace
        if isinstance(each, RateAppliedLine)
        and each.output is BC428_FARMERS_FOOD_DONATION_CREDIT_LINE_59
    )
    assert line.base_amount == D("100.00")
    assert line.rate == Rate(D("0.25"))
    assert line.result == D("25.00")


def _part() -> dict[str, object]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_apply_rate_step_over_the_gifts_input() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    capabilities = part["capabilities"]
    assert isinstance(capabilities, list)
    (step,) = capabilities
    assert isinstance(step, dict)
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/apply_rate",
        "reference": "59",
        "unit": "ca/cad",
        "params": {"rate": "ca-bc/farmers_food_donation_rate"},
        "consumes": {"base": GIFTS},
        "blank": {"base": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_59_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert kind is BC428_FARMERS_FOOD_DONATION_CREDIT_LINE_59
    assert isinstance(kind, AmountKind)
    assert kind.identifier == IDENTIFIER
    assert kind.value_type is Decimal
    assert non_negative(kind)
