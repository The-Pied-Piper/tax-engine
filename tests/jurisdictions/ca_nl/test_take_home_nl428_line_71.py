"""NL428 (2025) line 71, the Form T691 amount times 60%, from the real parts, real engine.

Form text (Form NL428, CRA 5001-C, confirmed 2026-11-18): "Line 71: Amount from line 14 of Part 7 of
Form T691 multiplied by 60% =". The input is the Form T691 amount, which its own part declares as
optional, read as 0 when left out. Line 71 is one calculation: 60% of the amount, a printed rate
held in the `ca-nl/minimum_tax_rate` dataset, rounded half-up to the cent. A salary-only caller
leaves the amount out, so line 71 is 0.00 at every salary: 0.00 / 0.00 / 0.00 at 20,000 / 70,000 /
200,000.

The input part and the line 71 part are loaded under a test-local header and form declaration,
over the Newfoundland and Labrador package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
CODE = JurisdictionCode("CA-NL")
FORM_NAME = "ca-nl/nl428"
AMOUNT = "ca-nl/nl428_t691_amount_line_71"
LINE_71 = "ca-nl/nl428_additional_tax_minimum_tax_line_71"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART = NL_PARTS / "nl428_line_71.yaml"

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        unit: ca/cad
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_71}
    capabilities: []
    """)


def _sheet(tmp_path: Path, salary: str, amount: str | None) -> Any:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, name in enumerate(["nl428_line_71_input.yaml", PART.name], start=2):
        text = (NL_PARTS / name).read_text(encoding="utf-8")
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
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
        given.append(Artifact(newfoundland_kinds().kind(AMOUNT), D(amount)))
    (sheet,) = service.compute(CODE, 2025, *given)[FORM_NAME]
    return sheet


def _line_71(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(newfoundland_kinds().kind(LINE_71)).value
    assert isinstance(value, Decimal)
    return value


def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path) -> None:
    # The amount is left out, read as 0 by the step's blank rule, so line 71 is 0.00.
    value = _line_71(tmp_path, "70000", None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # A Form T691 amount of 1000.00: 60% of 1000.00 is 600.00.
        ("1000.00", "600.00"),
        # 333.33 x 60% = 199.998, rounded half-up to 200.00.
        ("333.33", "200.00"),
    ],
)
def test_line_71_is_60_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_71(tmp_path, "70000", amount)

    assert value == D(expected)
    assert str(value) == expected


def test_the_part_is_one_apply_rate_step_over_the_line_71_amount() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["capabilities"] == [
        {
            "name": "core/apply_rate",
            "title": "Newfoundland and Labrador additional tax for minimum tax purposes",
            "reference": "71",
            "unit": "ca/cad",
            "params": {"rate": "ca-nl/minimum_tax_rate"},
            "consumes": {"base": AMOUNT},
            "blank": {"base": "0"},
            "produces": {"output": LINE_71},
        }
    ]
    assert list(part["capabilities"][0]) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
