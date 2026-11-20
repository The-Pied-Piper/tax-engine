"""Shared helpers of the Schedule B line tests (TP-1.D.B-V, 2025-12, lines 10 to 34).

Schedule B reads line 275 of the TP-1 net income form, which reads three other forms (see
`tp1_net_income_support.py`). The tests run the real parts of the whole chain on the salary, so
line 275 is the figure the chain gives (the TP-1 slip figures that Schedule U reads are plain
starting inputs, as in its own tests); only the Schedule B part files under test change from one
test module to the next. The salary is $20,000, $70,000 and $200,000, whose line 275 is 18,635.00,
67,915.00 and 197,506.00.
"""

from __future__ import annotations

from decimal import Decimal
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
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER,
    UPSTREAM_98,
    UPSTREAM_98_1,
    UPSTREAM_98_2,
    UPSTREAM_PARTS,
)

D = Decimal
FORM = "ca-qc/schedule_b"
# The real net income form declaration (it exports lines 275 and 299) and its line parts.
NET_INCOME_PARTS = (
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
# Line 275 at each salary, as the TP-1 net income chain gives it.
LINE_275 = {"20000": "18635.00", "70000": "67915.00", "200000": "197506.00"}


def schedule_b_form(*exports: str) -> str:
    """A Schedule B form declaration that exports only the lines a test builds."""
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM}\n  required: true\n  exports:\n{lines}"


def schedule_b_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: Artifact[Any],
    form: str | None = None,
) -> Worksheet:
    """The Schedule B worksheet for a salary, over the real chain up to line 275 and the Schedule B
    `parts` of a test; every optional input is left out unless in `given`. The form declaration is a
    test-local one exporting `exports`, unless `form` is the real declaration."""
    starting: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(TP1_QPP_CONTRIBUTION_LINE_98, D(UPSTREAM_98[salary])),
        Artifact(TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2, D(UPSTREAM_98_2[salary])),
        Artifact(TP1_PENSIONABLE_SALARY_LINE_98_1, D(UPSTREAM_98_1[salary])),
        Artifact(TP1_QPIP_PREMIUM_LINE_97, D("0")),
        *given,
    ]
    service = take_home_service(
        HEADER, form or schedule_b_form(*exports), *UPSTREAM_PARTS, *NET_INCOME_PARTS, *parts
    )
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)[FORM]
    return sheet


# The Schedule B parts from line 10 to line 18 (the family income chain), and with line 20; a form
# cannot hold an output nothing reads, so a test takes the parts up to the line it exports.
LINE_18_PARTS = (
    "schedule_b_line_10.yaml",
    "schedule_b_line_12_input.yaml",
    "schedule_b_line_14.yaml",
    "schedule_b_line_16.yaml",
    "schedule_b_line_18.yaml",
)
LINE_20_PARTS = (
    *LINE_18_PARTS,
    "schedule_b_line_20_input.yaml",
    "schedule_b_line_20.yaml",
)
LINE_31_PARTS = (*LINE_20_PARTS, "schedule_b_line_30.yaml", "schedule_b_line_31.yaml")
