"""NL428 (2025) line 68, the minimum tax carryover times 60%, from the real parts, real engine.

Form text (Form NL428, CRA 5001-C, confirmed 2026-11-18): "Line 68 and line 61540: Amount from
line 40427 of your return multiplied by 60% =". The input is the amount from line 40427 of the
return (`ca-nl/nl428_minimum_tax_carryover_amount_line_68`), which its own part declares as
optional, read as 0 when left out. Line 68 is one calculation: 60% of the amount, a printed rate
held in the `ca-nl/minimum_tax_rate` dataset, rounded half-up to the cent. A salary-only caller
leaves the amount out, so line 68 is 0.00 at every salary: 0.00 / 0.00 at 20,000 /
200,000.

The inputs part and the line 68 part are loaded under a test-local header and form declaration,
over the Newfoundland and Labrador package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
MINIMUM_TAX_CARRYOVER = "ca/minimum_tax_carryover"
CODE = JurisdictionCode("CA-NL")
FORM_NAME = "ca-nl/nl428"
AMOUNT = "ca-nl/nl428_minimum_tax_carryover_amount_line_68"
LINE_68 = "ca-nl/nl428_minimum_tax_carryover_line_68"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART = NL_PARTS / "nl428_line_68.yaml"

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_68}
    capabilities: []
    """)


def _sheet(tmp_path: Path, salary: str, amount: str | None) -> Any:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    for part in form_parts("t1_employment_income"):
        (folder / f"00_t1_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, name in enumerate([PART.name], start=2):
        text = (NL_PARTS / name).read_text(encoding="utf-8")
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    for number, found in enumerate(form_parts("t1_lines_copied_by_provinces"), start=20):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    service = TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(),
            newfoundland_parameter_parsers(),
            newfoundland_units(),
        ),
        newfoundland_capabilities(),
    )
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if amount is not None:
        given.append(Artifact(newfoundland_kinds().kind(MINIMUM_TAX_CARRYOVER), D(amount)))
    (sheet,) = service.compute(CODE, 2025, *given)[FORM_NAME]
    return sheet


def _line_68(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(newfoundland_kinds().kind(LINE_68)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path, salary: str) -> None:
    # The amount is left out, read as 0 by the step's blank rule, so line 68 is 0.00 throughout.
    value = _line_68(tmp_path, salary, None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # An amount of 1000.00: 60% of 1000.00 is 600.00.
        ("1000.00", "600.00"),
        # 333.33 x 60% = 199.998, rounded half-up to 200.00.
        ("333.33", "200.00"),
    ],
)
def test_line_68_is_60_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_68(tmp_path, "70000", amount)

    assert value == D(expected)
    assert str(value) == expected


def test_the_part_is_one_apply_rate_step_over_the_line_68_amount() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["capabilities"][1:] == [
        {
            "name": "core/apply_rate",
            "title": "Newfoundland and Labrador minimum tax carryover",
            "reference": "68",
            "unit": "ca/cad",
            "params": {"rate": "ca-nl/minimum_tax_rate"},
            "consumes": {"base": AMOUNT},
            "produces": {"output": LINE_68},
        }
    ]
    assert list(part["capabilities"][1]) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "produces",
    ]


def test_the_amount_is_a_record_total_of_the_t1_line_40427_export_with_no_input_of_its_own() -> (
    None
):
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert "inputs" not in part
    assert part["capabilities"][0] == {
        "name": "core/record_total",
        "title": "Amount from line 40427 of your return",
        "reference": "68 box A",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_lines_copied_by_provinces.minimum_tax_carryover_line_40427"},
        "produces": {"output": AMOUNT},
    }
