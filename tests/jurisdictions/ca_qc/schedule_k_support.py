"""Shared helpers of the Schedule K Part A line tests (lines 36 to 48).

Schedule K line 36 reads TP-1 line 275 from the TP-1 net income form. The tests run the real parts
of that form and the forms it reads (see `tp1_net_income_support.py`) on the salary, so the figure
is the one the chain gives; only the Schedule K part files under test change from one test module to
the next. Every optional input is left out unless a test gives it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER,
    UPSTREAM_PARTS,
)

D = Decimal
FORM_NAME = "ca-qc/tp1_schedule_k"
NET_INCOME_PARTS = (
    "tp1_net_income.yaml",
    "tp1_net_income_line_275_spouse_input.yaml",
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


def form_part(export: str | tuple[str, ...]) -> str:
    """A test form declaration of Schedule K exporting `export`, one kind or several."""
    exports = (export,) if isinstance(export, str) else export
    lines = "".join(f"    - {kind}\n" for kind in exports)
    return f"form:\n  name: {FORM_NAME}\n  required: true\n  exports:\n{lines}"


def schedule_k_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    export: str | tuple[str, ...],
    parts: tuple[str, ...],
    *given: tuple[AmountKind | CountKind, str],
) -> Worksheet:
    """The Schedule K worksheet for a salary, over the upstream and net income parts and the
    Schedule K `parts`; every optional input is left out unless in `given`."""
    starting: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    ]
    for kind, value in given:
        if isinstance(kind, CountKind):
            starting.append(Artifact(kind, int(value)))
        else:
            starting.append(Artifact(kind, D(value)))
    service = take_home_service(
        HEADER, form_part(export), *UPSTREAM_PARTS, *NET_INCOME_PARTS, *parts
    )
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)[FORM_NAME]
    return sheet
