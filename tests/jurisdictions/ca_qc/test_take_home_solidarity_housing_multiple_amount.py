"""The solidarity credit housing amount for multiple owners or tenants (fiche 110201, Table C.9,
"montant de base pour frais de logement 906") as the Quebec take-home part wires it.

The amount is a printed figure, held in the `ca-qc/solidarity_housing_multiple_amount` dataset;
`core/credit_amount` produces it as an artifact the reduction rule can read. No input is taken.
The figure is a listed check: the fiche is a web page.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_qc.catalog import SOLIDARITY_HOUSING_MULTIPLE_AMOUNT
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_support import amounts_form_part

D = Decimal
PART = "solidarity_credit_amounts.yaml"
FORM = "ca-qc/solidarity_credit"

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM_PART = amounts_form_part()


def test_the_solidarity_housing_multiple_amount_is_the_printed_906(
    take_home_service: TakeHomeService,
) -> None:
    service = take_home_service(HEADER, FORM_PART, PART)

    (sheet,) = service.compute(TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025))[FORM]

    assert sheet.get(SOLIDARITY_HOUSING_MULTIPLE_AMOUNT).value == D("906.00")


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
        if step["produces"] == {"output": "ca-qc/solidarity_housing_multiple_amount"}
    ]
    assert step["name"] == "core/credit_amount"
    assert step["unit"] == "ca/cad"
    assert step["params"] == {"amount": "ca-qc/solidarity_housing_multiple_amount"}
