"""MB428 (2025) line 41, family tax benefit, read from Schedule MB428-A, real parts.

Form text (Form MB428, CRA 5007-C, read 2026-11-17): "Line 41 and line 61470: Family tax benefit
(attach Schedule MB428-A) ^". Schedule MB428-A (CRA 5007-A) line 12 says "Enter this amount on line
61470 of your Form MB428", so the one step is a core/record_total over the Schedule MB428-A export
that gives line 12 (another form reads an export only as a record list), as line 9 reads the
Worksheet MB428 export.

The test composes the real Manitoba salary part, the real Schedule 8 and T1 taxable income parts,
the real parts of Schedule MB428-A lines 1 to 12 (`mb428_a_line_1.yaml`,
`mb428_a_line_10.yaml`, `mb428_a_line_11.yaml`, `mb428_a_line_11_product.yaml`,
`mb428_a_line_12.yaml`) and the real line part (`mb428_credits_line_41.yaml`), and types in only
the salary. The header and the two form declarations are made up here, exporting the lines read,
because the shared scaffold owns them. The figures are hand-computed from the printed forms (not a
CRA example): net income is the salary less the enhanced CPP deduction, 1% of (salary - 3,500);
line 11 is 9% of it; line 12 is 2,065.00 less line 11, not below 0.
- $10,000: net income 9,935.00, line 11 = 894.15, line 12 = 1,170.85.
- $70,000: net income 69,335.00, line 11 = 6,240.15, above 2,065.00, so 0.00.
- $23,140 and $23,141 sit either side of the cut-off: 0.08 and 0.00.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
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
from tax_engine.domain.trace import RecordTotalLine
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
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = MB_PARTS / "mb428_credits_line_41.yaml"
FORM_NAME = "ca-mb/mb428_credits"
KIND = "ca-mb/mb428_family_tax_benefit_line_41"
SCHEDULE_KIND = "ca-mb/mb428_a_family_tax_benefit_line_12"
SCHEDULE_PARTS = (
    "mb428_a_line_1.yaml",
    "mb428_a_line_10.yaml",
    "mb428_a_line_11.yaml",
    "mb428_a_line_11_product.yaml",
    "mb428_a_line_12.yaml",
)
# The real federal parts the T1 taxable-income form needs, beside the salary and the schedule.
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
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
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
      name: ca-mb/mb428_a
      required: true
      exports:
        - ca-mb/mb428_a_family_tax_benefit_line_12
    capabilities: []
    """)
CREDITS_FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_family_tax_benefit_line_41
    capabilities: []
    """)

CASES = [
    ("10000", "1170.85"),
    ("70000", "0.00"),
    ("23140", "0.08"),
    ("23141", "0.00"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in SCHEDULE_PARTS:
        yield MB_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=3):
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


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _line_11(salary: Decimal) -> Decimal:
    """Schedule MB428-A line 11: 9% of net income, rounded half-up to the cent."""
    return _cent(_net_income(salary) * D("0.09"))


def _schedule_amount(salary: Decimal) -> Decimal:
    """Schedule MB428-A line 12: 2,065.00 less line 11, never below 0."""
    return max(D("2065.00") - _line_11(salary), D(0)).quantize(CENT)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_41_is_the_schedule_mb428_a_family_tax_benefit(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _schedule_amount(D(salary)) == D(expected)
    sheet = _sheet(tmp_path, salary)
    line_41 = D(sheet.get(manitoba_kinds().kind(KIND)).value)

    assert line_41 == _schedule_amount(D(salary))
    assert line_41 == D(expected)
    assert str(line_41) == expected
    assert not sheet.get(manitoba_kinds().kind(KIND)).is_blank


def test_the_net_income_and_line_11_at_the_salaries_are_recomputed() -> None:
    assert _net_income(D("10000")) == D("9935.00")
    assert _line_11(D("10000")) == D("894.15")
    assert _line_11(D("23140")) == D("2064.92")
    assert _line_11(D("23141")) == D("2065.01")


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_trace_totals_the_one_schedule_record(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kind = manitoba_kinds().kind(KIND)

    (line,) = [t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output == kind]
    assert line.amounts == (D(expected),)
    assert line.total == D(expected)


def _line() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_declares_exactly_one_capability() -> None:
    part = _line()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    assert len(part["capabilities"]) == 1


def test_the_one_step_is_a_titled_record_total_over_the_schedule_export() -> None:
    (step,) = _line()["capabilities"]

    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step == {
        "name": "core/record_total",
        "title": "Family tax benefit",
        "reference": "41",
        "unit": "ca/cad",
        "consumes": {"records": "ca-mb/mb428_a.mb428_a_family_tax_benefit_line_12"},
        "produces": {"output": KIND},
    }
    assert step["unit"] == "ca/cad"


def test_line_41_is_a_registered_non_negative_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_FAMILY_TAX_BENEFIT_LINE_41
