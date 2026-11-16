"""T1 General 2025 (5006-R, British Columbia) line 47900 "Provincial or territorial credits", from
the salary alone.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14, as recorded on the ticket): "Line 45: Line 36
plus line 44 Enter this amount on line 47900 of your return." The T1 text for line 47900 itself is
to be confirmed. British Columbia's BC479 form supplies its line 45 as
`ca/provincial_credits.amount`, so the T1 part reads it through `core/record_total` into the new
non-negative kind `ca/provincial_credits_line_47900`, and line 47900 is a copy of BC479 line 45.

The test composes the real salary, Schedule 8 and T1 taxable income parts, the real BC479 form and
its line 1 to line 45 parts and the real T1 part under test. The T1 form declaration, exporting line
47900, is made up here. The expected figure is BC479 line 45, read from the sheet the run computes
for that form beside the T1 form.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
T1_FORM = "ca/t1_tax_and_credits"
BC479_FORM = "ca-bc/bc479"
LINE_45 = "ca-bc/bc479_british_columbia_credits_line_45"
LINE_47900 = "ca/provincial_credits_line_47900"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
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
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The T1 tax and credits declaration, test-local: its one export is line 47900, the line under test.
T1_TAX_AND_CREDITS = dedent(f"""\
    form:
      name: {T1_FORM}
      required: true
      exports:
        - {LINE_47900}
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield _federal(name)
    yield from sorted(BC_PARTS.glob("bc479*.yaml"))
    yield _federal("t1_tax_and_credits_line_47900.yaml")


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, the T1 form
    declaration and the real part files."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(T1_TAX_AND_CREDITS, encoding="utf-8")
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


def _worksheets(tmp_path: Path, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))


@pytest.mark.parametrize("salary", ["10000", "17000", "20000", "70000", "200000"])
def test_line_47900_is_bc479_line_45_read_from_the_sheets(tmp_path: Path, salary: str) -> None:
    worksheets = _worksheets(tmp_path, salary)
    kinds = british_columbia_kinds()
    (t1,) = worksheets[T1_FORM]
    (bc479,) = worksheets[BC479_FORM]
    line_45 = bc479.get(kinds.kind(LINE_45))

    line_47900 = t1.get(kinds.kind(LINE_47900))

    assert not line_47900.is_blank
    assert line_47900.value == line_45.value
    assert line_47900.value.as_tuple().exponent == -2


@pytest.mark.parametrize("salary", ["10000", "20000", "70000"])
def test_line_47900_is_not_blank_even_when_bc479_line_45_is_zero(
    tmp_path: Path, salary: str
) -> None:
    (t1,) = _worksheets(tmp_path, salary)[T1_FORM]

    assert not t1.get(british_columbia_kinds().kind(LINE_47900)).is_blank


def test_a_supplied_line_47900_is_not_passed_on_as_blank(tmp_path: Path) -> None:
    (t1,) = _worksheets(tmp_path, "70000")[T1_FORM]

    assert not [line for line in t1.trace if isinstance(line, BlankPassedOnLine)]


def test_the_provincial_credits_line_47900_kind_is_registered_and_non_negative() -> None:
    kind = british_columbia_kinds().kind(LINE_47900)

    assert kind.identifier == LINE_47900
    assert non_negative(kind) is True
