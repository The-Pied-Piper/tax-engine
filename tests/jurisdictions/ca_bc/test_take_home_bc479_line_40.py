"""BC479 (2025) line 40, the income threshold.

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

import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_bc.catalog as bc_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
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
    outputs: []
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
    for number, part in enumerate(dict.fromkeys(_part_files()), start=2):
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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Any]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(TaxCalculationRequest(CODE, 2025, tuple(given)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return sheet.get(_kind(identifier)).value


def _step(part_name: str, index: int = 0) -> dict[str, Any]:
    part = yaml.safe_load((BC_PARTS / part_name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert part["form"] == {"name": FORM}
    return dict(part["capabilities"][index])


def test_line_40_is_the_printed_64764_at_every_salary(tmp_path: Path) -> None:
    for salary in ("17000", "100000"):
        value = _value(_sheet(tmp_path / salary, salary), "ca-bc/bc479_renters_threshold_line_40")
        assert str(value) == "64764.00"


def test_line_40_part_is_a_printed_dataset_figure_claimed_whole() -> None:
    assert _step("bc479_line_40.yaml") == {
        "name": "core/credit_amount",
        "title": "Income threshold",
        "reference": "40",
        "unit": "ca/cad",
        "params": {"amount": "ca-bc/renters_credit_threshold"},
        "produces": {"output": "ca-bc/bc479_renters_threshold_line_40"},
    }
