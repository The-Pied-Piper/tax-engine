"""Shared helpers of the TP-1 tax line tests (TP-1.D-V, 2025-12, page 4, lines 401 to 413).

Line 401 reads Work Chart 401 (line 8), which reads line 299 of the TP-1 net income form; line 406
reads line 399 of the credits form, which reads Schedule B. The tests run the real parts of those
chains on the salary (the TP-1 slip figures that Schedule U reads are plain starting inputs, as in
the net income tests) and the tax parts under test. The salary is $20,000, $70,000 and $200,000.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2,
    TP1_PENSIONABLE_SALARY_LINE_98_1,
    TP1_QPIP_PREMIUM_LINE_97,
    TP1_QPP_CONTRIBUTION_LINE_98,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import NET_INCOME_PARTS
from tests.jurisdictions.ca_qc.tp1_credits_support import (
    LINE_399_PARTS,
    SCHEDULE_B_PARTS,
)
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER,
    UPSTREAM_98,
    UPSTREAM_98_1,
    UPSTREAM_98_2,
    UPSTREAM_PARTS,
)
from tests.jurisdictions.ca_qc.work_chart_401_support import D

FORM = "ca-qc/tp1_tax"
# The real chart declaration (it exports line 8) and its parts, over the net income chain.
CHART_PARTS = (
    "work_chart_401.yaml",
    "work_chart_401_line_1.yaml",
    "work_chart_401_line_3.yaml",
    "work_chart_401_line_4.yaml",
    "work_chart_401_line_5.yaml",
    "work_chart_401_line_6.yaml",
    "work_chart_401_line_7.yaml",
    "work_chart_401_line_8.yaml",
)
# Every part line 401 needs besides its own, and every part line 406 needs besides its own (the
# real credits declaration exports line 399); a form cannot hold an output nothing reads, so a
# test takes the chain of the lines it reads.
LINE_401_CHAIN = (*UPSTREAM_PARTS, *NET_INCOME_PARTS, *CHART_PARTS)
LINE_406_CHAIN = (
    *UPSTREAM_PARTS,
    *NET_INCOME_PARTS,
    *SCHEDULE_B_PARTS,
    "tp1_credits.yaml",
    *LINE_399_PARTS,
)


def tax_form(*exports: str) -> str:
    """A test form declaration of the tax form exporting `exports`."""
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM}\n  required: true\n  exports:\n{lines}capabilities: []\n"


def tax_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: Artifact[Any],
    form: str | None = None,
) -> Worksheet:
    """The tax worksheet for a salary, over the real `parts` of the chains it reads and of the
    lines under test; every optional input is left out unless in `given`. The form declaration is
    a test-local one exporting `exports`, unless `form` is the real declaration."""
    starting: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(TP1_QPP_CONTRIBUTION_LINE_98, D(UPSTREAM_98[salary])),
        Artifact(TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2, D(UPSTREAM_98_2[salary])),
        Artifact(TP1_PENSIONABLE_SALARY_LINE_98_1, D(UPSTREAM_98_1[salary])),
        Artifact(TP1_QPIP_PREMIUM_LINE_97, D("0")),
        *given,
    ]
    service = take_home_service(HEADER, form or tax_form(*exports), *parts)
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)[FORM]
    return sheet
