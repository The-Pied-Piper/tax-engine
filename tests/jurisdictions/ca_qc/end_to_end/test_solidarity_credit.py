"""The Quebec solidarity tax credit (2025 return, payment period July 2026 to June 2027), as one
chain: the optional answers, the maximum before reduction, the family income (TP-1 line 275) and
the reduction rule, ending in the yearly amount the form exports.

Source: Quebec Ministry of Finance, fiche 110201, Table C.9, and Schedule D (TP-1.D.D-V
(2025-12)). The fiche is a web page, so its figures are a listed check. The chain runs the real
parts of the solidarity form and of the forms it reads: the net income lines of TP-1 (as in the net
income chain tests, with the TP-1 slip figures as plain starting inputs). The salary is $20,000,
$70,000 and $200,000, whose line 275 is 18,635.00, 67,915.00 and 197,506.00. The expected figures
are hand-computed from the printed figures, not an official example: the credit is the maximum
less the reduction (6% of the income over 43,195, or 3% when no housing component is received),
and never less than the QST component less the 3% reduction.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    SOLIDARITY_CREDIT_AFTER_REDUCTION,
    SOLIDARITY_FAMILY_INCOME,
    SOLIDARITY_MAXIMUM_BEFORE_REDUCTION,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_maximum_support import (
    ALONE,
    ANSWERS_PART,
    FORM,
    OCCUPANTS,
    TENANT,
)
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER,
    UPSTREAM_PARTS,
)

D = Decimal
PARTS = (
    *UPSTREAM_PARTS,
    "tp1_net_income.yaml",
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_input.yaml",
    "tp1_net_income_line_254.yaml",
    "tp1_net_income_line_256.yaml",
    "tp1_net_income_line_260_input.yaml",
    "tp1_net_income_line_275.yaml",
    "tp1_net_income_line_276_input.yaml",
    "tp1_net_income_line_278_input.yaml",
    "tp1_net_income_line_279.yaml",
    "tp1_net_income_line_298_input.yaml",
    "tp1_net_income_line_299.yaml",
    "solidarity_credit_amounts.yaml",
    ANSWERS_PART,
    "solidarity_credit_maximum.yaml",
    "solidarity_credit_family_income.yaml",
    "solidarity_credit_reduction.yaml",
)
# The real form declaration: it exports the printed amounts and the credit after the reduction.
FORM_PART = (QUEBEC_PARTS / "solidarity_credit.yaml").read_text(encoding="utf-8")
INCOME = {"20000": "18635.00", "70000": "67915.00", "200000": "197506.00"}


def sheet(
    take_home_service: TakeHomeService,
    salary: str,
    alone: int | None = None,
    tenant: int | None = None,
    occupants: int | None = None,
) -> Worksheet:
    """The solidarity credit sheet for a salary and the optional answers (a left-out answer takes
    its default)."""
    given: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    ]
    for name, answer in ((ALONE, alone), (TENANT, tenant), (OCCUPANTS, occupants)):
        if answer is not None:
            given.append(Artifact(quebec_kinds().kind(name), answer))
    service = take_home_service(HEADER, FORM_PART, *PARTS)
    (worksheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *given)[FORM]
    return worksheet


@pytest.mark.parametrize(
    ("salary", "maximum", "credit"),
    [
        ("20000", "363.00", "363.00"),
        ("70000", "363.00", "0.00"),
        ("200000", "363.00", "0.00"),
    ],
)
def test_the_default_answers_are_the_qst_component_alone(
    take_home_service: TakeHomeService, salary: str, maximum: str, credit: str
) -> None:
    worksheet = sheet(take_home_service, salary)

    assert str(worksheet.get(SOLIDARITY_FAMILY_INCOME).value) == INCOME[salary]
    assert str(worksheet.get(SOLIDARITY_MAXIMUM_BEFORE_REDUCTION).value) == maximum
    assert str(worksheet.get(SOLIDARITY_CREDIT_AFTER_REDUCTION).value) == credit


@pytest.mark.parametrize(
    ("salary", "maximum", "credit"),
    [
        ("20000", "1281.00", "1281.00"),
        ("70000", "1281.00", "0.00"),
        ("200000", "1281.00", "0.00"),
    ],
)
def test_alone_and_a_tenant_receive_the_three_components(
    take_home_service: TakeHomeService, salary: str, maximum: str, credit: str
) -> None:
    worksheet = sheet(take_home_service, salary, alone=1, tenant=1)

    assert str(worksheet.get(SOLIDARITY_MAXIMUM_BEFORE_REDUCTION).value) == maximum
    assert str(worksheet.get(SOLIDARITY_CREDIT_AFTER_REDUCTION).value) == credit


@pytest.mark.parametrize(
    ("answers", "maximum", "credit"),
    [
        # Alone but not a tenant: 363 + 172 and no housing component.
        ({"alone": 1, "tenant": 0}, "535.00", "535.00"),
        # A tenant but not alone: 363 + 746.
        ({"alone": 0, "tenant": 1}, "1109.00", "1109.00"),
        # A tenant sharing the dwelling with two others: 363 + 906 / 3.
        ({"tenant": 1, "occupants": 3}, "665.00", "665.00"),
        # A tenant sharing the dwelling with three others: 363 + 906 / 4.
        ({"alone": 0, "tenant": 1, "occupants": 4}, "589.50", "589.50"),
    ],
)
def test_the_answers_move_the_maximum_and_the_credit_at_a_low_income(
    take_home_service: TakeHomeService, answers: dict[str, int], maximum: str, credit: str
) -> None:
    worksheet = sheet(take_home_service, "20000", **answers)

    assert str(worksheet.get(SOLIDARITY_MAXIMUM_BEFORE_REDUCTION).value) == maximum
    assert str(worksheet.get(SOLIDARITY_CREDIT_AFTER_REDUCTION).value) == credit
