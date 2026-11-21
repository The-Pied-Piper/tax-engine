"""BC479 (2025) line 44, the renter's tax credit with the line 37 gate.

Form text (Form BC479, CRA 5010-TC, read 2026-11-21 from the repo's cra-docs copy): see the printed
renter's tax credit section, lines 37 to 44. Figures are hand-computed from the printed form (not a
CRA example). Line 6 is the salary less the CPP and CPP2 deductions of the T1 chain.
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
from tax_engine.domain.trace import ChosenByCountLine
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
LINE_44 = "ca-bc/bc479_renters_credit_line_44"
LINE_BEFORE = "ca-bc/bc479_renters_credit_before_months_check"
LINE_41 = "ca-bc/bc479_renters_income_over_threshold_line_41"
LINE_43 = "ca-bc/bc479_renters_reduction_line_43"
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc479"
LINE_6 = "ca-bc/bc479_adjusted_family_net_income_line_6"
LINE_45 = "ca-bc/bc479_british_columbia_credits_line_45"
RENTER = bc_catalog.BC479_RENTERS_CREDIT_LINE_44
MONTHS = bc_catalog.BC479_RENTERS_MONTHS_LINE_37
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PARTS = [
    BC_PARTS / "bc479_line_37_input.yaml",
    BC_PARTS / "bc479_line_38.yaml",
    BC_PARTS / "bc479_line_40.yaml",
    BC_PARTS / "bc479_line_41.yaml",
    BC_PARTS / "bc479_line_43.yaml",
    BC_PARTS / "bc479_line_44.yaml",
]
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
        - {LINE_44}
        - {LINE_6}
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
    yield from LINE_PARTS


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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Any]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(CODE, 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return sheet.get(_kind(identifier)).value


# salary, line 6 (the salary less the CPP and CPP2 deductions of the T1 chain), line 44 with rent
# paid for 12 months: well below the 64,764 threshold, 0.99 above it, in the phase-out, one dollar
# short of 84,764 (line 41 of 19,999.00 gives 399.98), exactly at 84,764 (a 400.00 reduction, so
# 0.00), and above it (the reduction exceeds 400.00, so line 44 is floored at 0.00).
CASES = [
    ("17000", "16865.00", "400.00"),
    ("65000", "64385.00", "400.00"),
    ("65383.83", "64764.99", "399.98"),
    ("70000", "69335.00", "308.58"),
    ("85500", "84426.00", "6.76"),
    ("85837", "84763.00", "0.02"),
    ("85838", "84764.00", "0.00"),
    ("100000", "98926.00", "0.00"),
]


@pytest.mark.parametrize(("salary", "line_6", "expected"), CASES)
def test_line_44_with_rent_paid_follows_the_printed_lines(
    tmp_path: Path, salary: str, line_6: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, Artifact(MONTHS, 12))

    assert _value(sheet, LINE_6) == D(line_6)
    line_44 = _value(sheet, LINE_44)
    assert line_44 == D(expected)
    assert str(line_44) == expected
    assert not line_44.is_signed()


@pytest.mark.parametrize("salary", ["17000", "70000", "100000"])
def test_a_salary_only_caller_has_line_44_of_zero(tmp_path: Path, salary: str) -> None:
    line_44 = _sheet(tmp_path, salary).get(_kind(LINE_44))

    assert not line_44.is_blank
    assert str(line_44.value) == "0.00"


@pytest.mark.parametrize("months", [0, 1, 12])
def test_line_44_is_the_credit_for_one_month_or_more_and_zero_for_none(
    tmp_path: Path, months: int
) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(MONTHS, months))

    assert str(_value(sheet, LINE_44)) == ("400.00" if months else "0.00")


def test_the_subtraction_is_still_shown_when_the_gate_gives_zero(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert _value(sheet, LINE_BEFORE) == D("308.58")
    assert _value(sheet, LINE_44) == D("0.00")


def test_the_gate_is_traced_with_the_months_and_the_chosen_amount(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(MONTHS, 12))

    (line,) = (
        each
        for each in sheet.trace
        if isinstance(each, ChosenByCountLine) and each.output is _kind(LINE_44)
    )
    assert line.count == 12
    assert line.chosen_kind is _kind(LINE_BEFORE)
    assert line.chosen_value == D("400.00")


def _step(part_name: str, index: int = 0) -> dict[str, Any]:
    part = yaml.safe_load((BC_PARTS / part_name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert part["form"] == {"name": FORM}
    return dict(part["capabilities"][index])


def test_line_44_part_has_the_subtraction_then_the_gate_with_the_reference_on_the_gate() -> None:
    assert _step("bc479_line_44.yaml", 0) == {
        "name": "core/subtract_not_below_zero",
        "title": "Renter's tax credit before the months check",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {
            "amount": "ca-bc/bc479_renters_maximum_line_38",
            "less": LINE_43,
        },
        "produces": {"output": LINE_BEFORE},
    }
    assert _step("bc479_line_44.yaml", 2) == {
        "name": "core/choose_by_count",
        "title": "British Columbia renter's tax credit",
        "reference": "44",
        "unit": "ca/cad",
        "consumes": {
            "count": MONTHS.identifier,
            "when_none": "ca-bc/bc479_renters_zero",
            "when_any": LINE_BEFORE,
        },
        "blank": {"count": "0"},
        "produces": {"output": LINE_44},
    }


def test_the_new_kinds_are_registered_with_the_right_types() -> None:
    kinds = british_columbia_kinds()

    for identifier in (LINE_44, LINE_BEFORE, LINE_41, LINE_43):
        kind = kinds.kind(identifier)
        assert isinstance(kind, AmountKind)
        assert kind.value_type is Decimal
        assert non_negative(kind)
