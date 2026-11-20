"""Revenu Quebec TP-1 (2025) line 101, "Employment income, RL-1 slip, box A", as the Quebec
take-home manifest wires it: the salary the caller gives, read as it is.

Line 101 is an input of the form, and the take-home caller's one input is the salary (the part
`salary.yaml`), so line 101 is a copy of that input and has no step. The form part
`tp1_income.yaml` names the form and exports the salary as line 101.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025" / "tp1_income.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)


def test_the_form_part_names_the_form_and_has_no_steps() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"]["name"] == "ca-qc/tp1_income"
    assert part["form"]["title"] == "Income Tax Return"
    assert part["capabilities"] == []


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_the_salary_is_line_101_unchanged(take_home_service: TakeHomeService, salary: str) -> None:
    form = dedent("""\
        form:
          name: ca-qc/tp1_income
          required: true
          exports:
            - ca/employment_income
        """)
    (sheet,) = take_home_service(HEADER, form, "salary.yaml").compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )["ca-qc/tp1_income"]

    assert sheet.get(EMPLOYMENT_INCOME).value == D(salary)
