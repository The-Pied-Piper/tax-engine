"""The solidarity credit QST base amount (fiche 110201, Table C.9, "montant de base 363") as the
Quebec take-home part wires it.

The amount is a printed figure, held in the `ca-qc/solidarity_qst_base_amount` dataset;
`core/credit_amount` produces it as an artifact the reduction rule can read. No input is taken.
The figure is a listed check: the fiche is a web page.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import SOLIDARITY_QST_BASE_AMOUNT
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService

D = Decimal
PART = "solidarity_credit_amounts.yaml"
FORM = "ca-qc/solidarity_credit"

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM_PART = (QUEBEC_PARTS / "solidarity_credit.yaml").read_text(encoding="utf-8")


def test_the_qst_base_amount_is_the_printed_363(take_home_service: TakeHomeService) -> None:
    service = take_home_service(HEADER, FORM_PART, PART)

    (sheet,) = service.compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )[FORM]

    assert sheet.get(SOLIDARITY_QST_BASE_AMOUNT).value == D("363.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_claims_the_dataset_whole() -> None:
    part = _part()

    assert part["form"] == {"name": FORM}
    (step,) = [
        step
        for step in part["capabilities"]
        if step["produces"] == {"output": "ca-qc/solidarity_qst_base_amount"}
    ]
    assert step["name"] == "core/credit_amount"
    assert step["unit"] == "ca/cad"
    assert step["params"] == {"amount": "ca-qc/solidarity_qst_base_amount"}
    assert step["produces"] == {"output": "ca-qc/solidarity_qst_base_amount"}
