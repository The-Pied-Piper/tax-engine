"""BC479 (2025) line 1, net income, from the salary alone, real parts.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14): "Line 1: Net income from line 23600 of the
return (or the amount you would have entered if the instructions on line 23600 said "if negative,
show in brackets")". Column 1 (You) only; column 2 (the spouse) is not built for a single filer.
Line 1 is a calculation: its one step is a core/record_total over the T1 export that gives the
net income before its floor (`ca/t1_taxable_income.net_income_signed`), as Schedule 6 line 7 reads
it (`schedule_6_line_7.yaml`). The result is signed, because the form shows a negative net income
in brackets.

The test composes the real British Columbia salary part, the real Schedule 8 parts, the real T1
taxable income parts and the real line part (`bc479_line_1.yaml`), and types in only the salary
(and, for the negative case, line 23500). The form declaration is made up here, exporting the line
read, because the real form part is owned by another change. The figures are hand-computed from the
printed forms (not a CRA example) and are re-checked by the test.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC479_NET_INCOME_LINE_1
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_INPUT

D = Decimal
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc479_line_1.yaml"
KIND = "ca-bc/bc479_net_income_line_1"
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
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)

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
      name: ca-bc/bc479
      required: true
      exports:
        - ca-bc/bc479_net_income_line_1
    capabilities: []
    """)

CASES = [
    ("17000", "16865.00"),
    ("200000", "198926.00"),
]


def _part_files() -> Iterator[Path]:
    yield T1_LINE_10100_INPUT
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
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
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


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_1_is_the_t1_net_income(tmp_path: Path, salary: str, expected: str) -> None:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-BC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )

    (sheet,) = worksheets["ca-bc/bc479"]
    assert sheet.get(BC479_NET_INCOME_LINE_1).value == D(expected)


def test_line_1_stays_negative_when_net_income_is_negative(tmp_path: Path) -> None:
    # Line 23500 of 75,000 is more than line 23400 of 69,335.00, so net income is -5,665.00. Line 1
    # keeps it as it is ("show in brackets"), where the floored line 23600 would read 0.
    kinds = british_columbia_kinds()
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-BC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(kinds.kind("ca/social_benefits_repayment"), D("75000")),
    )

    (sheet,) = worksheets["ca-bc/bc479"]
    assert sheet.get(BC479_NET_INCOME_LINE_1).value == D("-5665.00")


def _line() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_record_total_step_like_schedule_6_line_7() -> None:
    part = _line()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc479"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["title"] == "Net income from line 23600 of the return"
    assert step["reference"] == "1"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"records": "ca/t1_taxable_income.net_income_signed"}
    assert step["produces"] == {"output": KIND}


def test_line_1_is_a_registered_signed_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert not non_negative(kind)
    assert kind is BC479_NET_INCOME_LINE_1
