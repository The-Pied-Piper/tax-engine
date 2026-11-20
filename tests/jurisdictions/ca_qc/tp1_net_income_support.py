"""Shared helpers of the TP-1 net income line tests (lines 201 to 275).

The net income lines read three other forms: line 199 from the TP-1 income form, line 201 from Work
Chart 201 and line 248 from Schedule U. The tests run the real parts of those forms on the salary,
so the figures are the ones the chain gives (the TP-1 slip figures that Schedule U reads are plain
starting inputs, as in its own tests); only the part files of the net income lines under test
change from one test module to the next.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2,
    TP1_PENSIONABLE_SALARY_LINE_98_1,
    TP1_QPIP_PREMIUM_LINE_97,
    TP1_QPP_CONTRIBUTION_LINE_98,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import WORK_CHART_201_PARTS

D = Decimal

# Only line 199 of the TP-1 income parts: Schedule U reads the TP-1 slip figures (lines 97 to 98.2)
# as plain starting inputs, which the full TP-1 income parts would also produce.
UPSTREAM_PARTS = (
    "salary.yaml",
    "tp1_income.yaml",
    "tp1_income_line_199_input.yaml",
    "tp1_income_line_199.yaml",
    *WORK_CHART_201_PARTS,
    "tp1_schedule_u.yaml",
    "tp1_schedule_u_line_11.yaml",
    "tp1_schedule_u_line_12.yaml",
    "tp1_schedule_u_line_13.yaml",
    "tp1_schedule_u_line_14.yaml",
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_14_3.yaml",
    "tp1_schedule_u_line_14_4.yaml",
    "tp1_schedule_u_line_15.yaml",
    "tp1_schedule_u_line_16.yaml",
    "tp1_schedule_u_line_17_2.yaml",
    "tp1_schedule_u_line_17_3.yaml",
    "tp1_schedule_u_line_17_5.yaml",
    "tp1_schedule_u_line_18_7.yaml",
    "tp1_schedule_u_line_18_8.yaml",
    "tp1_schedule_u_line_19.yaml",
    "tp1_schedule_u_line_20.yaml",
    "tp1_schedule_u_line_21.yaml",
    "tp1_schedule_u_line_22.yaml",
    "tp1_schedule_u_line_23.yaml",
)

# The TP-1 figures that Schedule U reads, as the TP-1 income steps give them for each salary; they
# are plain starting inputs here, as in the Schedule U tests.
UPSTREAM_98 = {"20000": "1056.00", "70000": "4256.00", "200000": "4339.20", "3000": "0"}
UPSTREAM_98_2 = {"20000": "0", "70000": "0", "200000": "396.00", "3000": "0"}
UPSTREAM_98_1 = {"20000": "20000", "70000": "70000", "200000": "81200", "3000": "3000"}

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-qc/tp1_qpp_contribution_line_98
        required: true
      - name: ca-qc/tp1_additional_qpp_contribution_line_98_2
        required: true
      - name: ca-qc/tp1_pensionable_salary_line_98_1
        required: true
      - name: ca-qc/tp1_qpip_premium_line_97
        required: true
    outputs:
      - ca/employment_income
    """)


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
        Artifact(TP1_QPP_CONTRIBUTION_LINE_98, D(UPSTREAM_98[salary])),
        Artifact(TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2, D(UPSTREAM_98_2[salary])),
        Artifact(TP1_PENSIONABLE_SALARY_LINE_98_1, D(UPSTREAM_98_1[salary])),
        Artifact(TP1_QPIP_PREMIUM_LINE_97, D("0")),
    ]
    starting.extend(Artifact(kind, D(value)) for kind, value in given)
    service = take_home_service(HEADER, form_part(*exports), *UPSTREAM_PARTS, *parts)
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca-qc/tp1_net_income"]
    return sheet
