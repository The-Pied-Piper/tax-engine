"""MB479 (2025) line 1, net income, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC, read 2026-11-14): "Line 1: Net income from line 23600 of the
return (or the amount you would have entered if the instructions on line 23600 said "if negative,
show in brackets")". Column 1 (You) only; column 2 (the spouse) is not built for a single filer.
Line 1 is a calculation: its one step is a core/record_total over the T1 export that gives the
net income before its floor (`ca/t1_taxable_income.net_income_signed`). The result is signed,
because the form shows a negative net income in brackets.

The test composes the real Manitoba salary part, the real Schedule 8 parts, the real T1 taxable
income parts and the real line part (`mb479_line_1.yaml`), and types in only the salary (and, for
the negative case, the social benefits repayment). The MB479 form declaration is made up here,
exporting only line 1, because the real declaration exports other lines.

The expected figures are computed here, not typed: net income is the salary less the enhanced CPP
deduction, 1% of the pensionable earnings between the $3,500 basic exemption and the $71,300 year's
maximum pensionable earnings, plus 4% of the earnings between $71,300 and $81,200, each rounded
half-up to the cent. They are hand-computed from the printed forms, not a CRA example.
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
LINE_PART = MB_PARTS / "mb479_line_1.yaml"
FORM_NAME = "ca-mb/mb479"
KIND = "ca-mb/mb479_net_income_line_1"
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
        - ca-mb/mb479_net_income_line_1
    capabilities: []
    """)

CASES = [
    ("10000", "9935.00"),
    ("200000", "198926.00"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
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


def _sheet(tmp_path: Path, *artifacts: Artifact[Any]) -> Worksheet:
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *artifacts)
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


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_1_is_the_t1_net_income(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, Artifact(EMPLOYMENT_INCOME, D(salary)))

    assert _net_income(D(salary)) == D(expected)
    assert sheet.get(manitoba_kinds().kind(KIND)).value == _net_income(D(salary))


def test_line_1_stays_negative_when_net_income_is_negative(tmp_path: Path) -> None:
    # The repayment of 75,000 is more than the 69,335.00 left after the CPP deduction, so net
    # income is -5,665.00. Line 1 keeps it as it is ("show in brackets"), where the floored line
    # 23600 would read 0.
    kinds = manitoba_kinds()
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(kinds.kind("ca/social_benefits_repayment"), D("75000")),
    )

    assert sheet.get(kinds.kind(KIND)).value == _net_income(D("70000")) - D("75000")
    assert sheet.get(kinds.kind(KIND)).value == D("-5665.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_record_total_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["title"] == "Net income from line 23600 of the return"
    assert step["reference"] == "1"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"records": "ca/t1_taxable_income.net_income_signed"}
    assert step["produces"] == {"output": KIND}


def test_line_1_is_a_registered_signed_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert not non_negative(kind)
    assert kind is mb_catalog.MB479_NET_INCOME_LINE_1
