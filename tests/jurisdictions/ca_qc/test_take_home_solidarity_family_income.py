"""The solidarity credit's family income: TP-1 line 275, "Net income".

Source: Revenu Quebec "Calculation of the Credit" (a web page) and Schedule D. The credit for July
2026 to June 2027 is reduced from the net income of the 2025 return. Line 275 is the export of the
TP-1 net income form, which another form reads as a record list, so the step is `core/record_total`
over `ca-qc/tp1_net_income.tp1_net_income_line_275`. The tests run the real net income lines on the
salary: line 275 is 18,635.00 / 67,915.00 / 197,506.00 at a salary of 20,000 / 70,000 / 200,000
(hand-computed from the printed lines, not an official example).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    SOLIDARITY_FAMILY_INCOME,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_maximum_support import FORM
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER,
    UPSTREAM_PARTS,
)
from tests.kinds import non_negative

D = Decimal
PART = "solidarity_credit_family_income.yaml"
IDENTIFIER = "ca-qc/solidarity_family_income"
NET_INCOME_PARTS = (
    "tp1_net_income.yaml",
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_inputs.yaml",
    "tp1_net_income_line_254.yaml",
    "tp1_net_income_line_256.yaml",
    "tp1_net_income_line_260_input.yaml",
    "tp1_net_income_line_275.yaml",
    "tp1_net_income_line_276_input.yaml",
    "tp1_net_income_line_278_input.yaml",
    "tp1_net_income_line_279.yaml",
    "tp1_net_income_line_298_inputs.yaml",
    "tp1_net_income_line_298.yaml",
    "tp1_net_income_line_299.yaml",
)
FORM_PART = f"form:\n  name: {FORM}\n  required: true\n  exports:\n    - {IDENTIFIER}\n"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_family_income_is_line_275(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    service = take_home_service(HEADER, FORM_PART, *UPSTREAM_PARTS, *NET_INCOME_PARTS, PART)
    starting: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    ]

    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )[FORM]

    assert str(sheet.get(SOLIDARITY_FAMILY_INCOME).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_the_step_totals_line_275() -> None:
    part = _part()

    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/tp1_net_income.tp1_net_income_line_275"},
        "produces": {"output": IDENTIFIER},
    }
    assert "reference" not in step
    assert "title" not in step


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SOLIDARITY_FAMILY_INCOME
    assert isinstance(SOLIDARITY_FAMILY_INCOME, AmountKind)
    assert non_negative(SOLIDARITY_FAMILY_INCOME)
