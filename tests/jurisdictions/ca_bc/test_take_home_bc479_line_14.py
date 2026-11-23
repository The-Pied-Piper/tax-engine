"""BC479 (2025) line 14, the home renovation expenses multiplied by 10%, from the salary alone with
the expenses input given or left out.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14): "Line 14: Enter your home renovation
expenses from line 5 of your Schedule BC(S12). (maximum $10,000) Line 60480 ^ multiplied by 10%
= ^". The printed 10% is a rate, held in the `ca-bc/home_renovation_credit_rate` dataset (0.10),
so line 14 is one `core/apply_rate` step (`bc479_line_14.yaml`) over the checked expenses
(`ca-bc/bc479_home_renovation_expenses_checked`), rounded half-up to the cent by the dataset's own
rule, producing `ca-bc/bc479_home_renovation_credit_line_14`, a non-negative kind, reference "14",
with no title. The expenses input is optional: a salary-only caller leaves it out, and the step's
blank rule reads the checked amount as 0 and prints its own "left blank, taken as 0" row. The
printed $10,000 maximum is checked before the step reads the amount (`bc479_line_14_check.yaml`):
an amount above it is rejected with `InputAboveBoundError`, not multiplied.

The test composes the T1 employment income form, the real maximum and check parts, the real line 14
input part and the new `bc479_line_14.yaml`, and types in the salary and, in some tests, the
expenses. The form declaration is made up here, exporting only line 14. The figures are
hand-computed from the printed form (not a CRA example): the expenses times 0.10, rounded half-up to
the cent."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_bc.catalog as bc_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankFallbackLine, RateAppliedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC479_HOME_RENOVATION_EXPENSES_LINE_14
from tests.federal_forms import form_parts
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
LINE_PART = BC_PARTS / "bc479_line_14.yaml"
MAXIMUM_PART = BC_PARTS / "bc479_home_renovation_expenses_maximum.yaml"
CHECK_PART = BC_PARTS / "bc479_line_14_check.yaml"
EXPENSES = BC479_HOME_RENOVATION_EXPENSES_LINE_14
CHECKED = "ca-bc/bc479_home_renovation_expenses_checked"
IDENTIFIER = "ca-bc/bc479_home_renovation_credit_line_14"
RATE_FAMILY = "ca-bc/home_renovation_credit_rate"
FORM = "ca-bc/bc479"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# expenses given, line 14 (the expenses times 10%, rounded half-up to the cent)
CASES = [
    ("10000.00", "1000.00"),
    ("0.05", "0.01"),
]

SALARIES = ["17000", "200000"]


def _part_files() -> Iterator[Path]:
    yield from form_parts("t1_employment_income")
    yield MAXIMUM_PART
    yield BC_PARTS / "bc479_line_14_input.yaml"
    yield CHECK_PART
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-BC"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("expenses", "expected"), CASES)
def test_line_14_is_the_expenses_times_10_percent(
    tmp_path: Path, expenses: str, expected: str
) -> None:
    line_14 = _sheet(tmp_path, "70000", Artifact(EXPENSES, D(expenses))).get(_kind(IDENTIFIER))

    assert line_14.value == D(expected)
    assert str(line_14.value) == expected


def test_an_amount_above_the_printed_maximum_is_rejected_not_multiplied(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(tmp_path, "70000", Artifact(EXPENSES, D("12000.00")))


@pytest.mark.parametrize("salary", SALARIES)
def test_line_14_is_a_computed_zero_when_no_expenses_are_given(tmp_path: Path, salary: str) -> None:
    line_14 = _sheet(tmp_path, salary).get(_kind(IDENTIFIER))

    assert not line_14.is_blank
    assert line_14.value == D("0.00")
    assert str(line_14.value) == "0.00"


def test_a_blank_expenses_line_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (blank,) = [
        each
        for each in sheet.trace
        if isinstance(each, BlankFallbackLine) and each.kind is _kind(CHECKED)
    ]
    assert blank.fallback == 0
    rows = EnglishTraceRenderer().render_all(sheet.trace)
    assert any("Left blank, taken as 0" in row for row in rows)


def test_the_product_is_traced_with_its_base_and_the_rate(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(EXPENSES, D("10000.00")))

    (line,) = (
        each
        for each in sheet.trace
        if isinstance(each, RateAppliedLine) and each.output is _kind(IDENTIFIER)
    )
    assert line.base == _kind(CHECKED)
    assert line.base_amount == D("10000.00")
    assert line.rate == Rate(D("0.10"))
    assert line.result == D("1000.00")


def _part() -> dict[str, object]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_apply_rate_step_over_the_checked_expenses() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    capabilities = part["capabilities"]
    assert isinstance(capabilities, list)
    (step,) = capabilities
    assert isinstance(step, dict)
    # The printed 10% is the dataset rate, so the step reads it as a parameter and has no step of
    # its own. Line 14 prints no title, so the step has none.
    assert step == {
        "name": "core/apply_rate",
        "reference": "14",
        "unit": "ca/cad",
        "params": {"rate": RATE_FAMILY},
        "consumes": {"base": CHECKED},
        "blank": {"base": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_14_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert kind is vars(bc_catalog)["BC479_HOME_RENOVATION_CREDIT_LINE_14"]
    assert isinstance(kind, AmountKind)
    assert kind.identifier == IDENTIFIER
    assert kind.value_type is Decimal
    assert non_negative(kind)
