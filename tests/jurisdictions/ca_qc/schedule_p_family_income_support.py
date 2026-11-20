"""Shared helper of the Schedule P family income tests (Part C, lines 52 to 54).

Line 52 reads TP-1 line 275 from the TP-1 net income form, which reads TP-1 line 199, Work Chart
201 and Schedule U. The tests run the real parts of those forms on the salary, with the TP-1 slip
figures that Schedule U reads as plain starting inputs, as the TP-1 net income tests do
(`tp1_net_income_support.py`); only the Schedule P `parts` of a test change from one test module to
the next.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER,
    UPSTREAM_PARTS,
)

D = Decimal

NET_INCOME_PARTS = (
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
)


def family_income_worksheet(
    take_home_service: TakeHomeService,
    form: str,
    parts: tuple[str, ...],
    salary: str,
    *given: tuple[ArtifactKind[Any], str],
) -> Worksheet:
    """The Schedule P worksheet of a salary, over the real net income parts and the Schedule P
    `parts` of a test; `given` are the optional answers the test passes."""
    starting = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    ]
    starting.extend(Artifact(kind, kind.value_type(value)) for kind, value in given)
    service = take_home_service(HEADER, form, *NET_INCOME_PARTS, *parts)
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca-qc/schedule_p"]
    return sheet
