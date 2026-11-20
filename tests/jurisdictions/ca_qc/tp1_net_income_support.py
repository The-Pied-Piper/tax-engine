"""Shared helpers of the TP-1 net income line tests (lines 201 to 275).

The net income lines read three other forms: line 199 from the TP-1 income form, line 201 from Work
Chart 201 and line 248 from Schedule U. The tests run the real parts of those forms on the salary,
so the figures are the ones the chain gives, the TP-1 slip figures (lines 97 to 98.2) included;
only the part files of the net income lines under test change from one test module to the next.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import WORK_CHART_201_PARTS

D = Decimal

# The TP-1 income parts (lines 97 to 199): the slip figures that Schedule U reads come from them.
TP1_INCOME_PARTS = (
    "salary.yaml",
    "tp1_income.yaml",
    "tp1_income_line_199_input.yaml",
    "tp1_income_line_199.yaml",
    "tp1_income_line_97_input.yaml",
    "tp1_income_line_97.yaml",
    "tp1_income_line_98_input.yaml",
    "tp1_income_line_98.yaml",
    "tp1_income_line_98_1_input.yaml",
    "tp1_income_line_98_1.yaml",
    "tp1_income_line_98_2_input.yaml",
    "tp1_income_line_98_2.yaml",
)

# The TP-1 income parts and the Schedule U parts, which read the slip figures.
UPSTREAM_PARTS = (
    *TP1_INCOME_PARTS,
    *WORK_CHART_201_PARTS,
    "tp1_schedule_u.yaml",
    "tp1_schedule_u_line_10.yaml",
    "tp1_schedule_u_line_11.yaml",
    "tp1_schedule_u_line_12_base.yaml",
    "tp1_schedule_u_line_12.yaml",
    "tp1_schedule_u_line_13.yaml",
    "tp1_schedule_u_line_14.yaml",
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_14_3.yaml",
    "tp1_schedule_u_line_14_4.yaml",
    "tp1_schedule_u_line_15.yaml",
    "tp1_schedule_u_line_16.yaml",
    "tp1_schedule_u_line_17_2.yaml",
    "tp1_schedule_u_line_17.yaml",
    "tp1_schedule_u_line_17_3.yaml",
    "tp1_schedule_u_line_17_4.yaml",
    "tp1_schedule_u_line_17_5.yaml",
    "tp1_schedule_u_line_18_5.yaml",
    "tp1_schedule_u_line_18_7.yaml",
    "tp1_schedule_u_line_18_8.yaml",
    "tp1_schedule_u_line_19.yaml",
    "tp1_schedule_u_line_20.yaml",
    "tp1_schedule_u_line_21.yaml",
    "tp1_schedule_u_line_22.yaml",
    "tp1_schedule_u_line_23.yaml",
)


HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)


def slip_artifacts(salary: str) -> list[Artifact[Any]]:
    """The starting inputs of the chain: the salary (the TP-1 slip figures come from its steps)."""
    return [Artifact(EMPLOYMENT_INCOME, D(salary))]


def form_part(*exports: str) -> str:
    """A test form declaration of the net income form exporting `exports`."""
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: ca-qc/tp1_net_income\n  required: true\n  exports:\n{lines}"


def net_income_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: tuple[AmountKind, str],
) -> Worksheet:
    """The net income worksheet for a salary, over the upstream parts and the net income `parts`;
    every optional input is left out unless in `given`."""
    starting = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    ]
    starting.extend(Artifact(kind, D(value)) for kind, value in given)
    service = take_home_service(HEADER, form_part(*exports), *UPSTREAM_PARTS, *parts)
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca-qc/tp1_net_income"]
    return sheet
