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

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER,
    UPSTREAM_PARTS,
)

D = Decimal
FORM = "ca-qc/schedule_b"
# The real net income form declaration (it exports lines 275 and 299) and its line parts.
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
    parts = (T1_BIRTH_YEAR_DECLARATION, *parts) if "schedule_b_line_22.yaml" in parts else parts
    starting: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        *given,
    ]
    service = take_home_service(
        HEADER, form or schedule_b_form(*exports), *UPSTREAM_PARTS, *NET_INCOME_PARTS, *parts
    )
    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )[FORM]
    return sheet


# The Schedule B parts from line 10 to line 18 (the family income chain), and with line 20; a form
# cannot hold an output nothing reads, so a test takes the parts up to the line it exports.
LINE_18_PARTS = (
    "schedule_b_line_10.yaml",
    "schedule_b_line_16.yaml",
    "schedule_b_line_18.yaml",
)
LINE_20_PARTS = (
    *LINE_18_PARTS,
    "schedule_b_line_20_input.yaml",
    "schedule_b_line_20.yaml",
)
# The year of birth is the 5005-R's input, which Schedule B line 22 reads through the T1's export.
# The real T1 declaration exports lines a Schedule B test does not build, so a test declares a T1
# that exports the year alone, with the real input part (a part with a line break is written as is).
T1_BIRTH_YEAR_DECLARATION = (
    "form:\n  name: ca-qc/t1_tax_and_credits\n  required: true\n  exports:\n    - ca/birth_year\n"
)
LINE_22_PARTS = (
    "t1_tax_and_credits_birth_year_inputs.yaml",
    "schedule_b_line_22.yaml",
)
LINE_31_PARTS = (
    *LINE_20_PARTS,
    *LINE_22_PARTS,
    "schedule_b_line_30.yaml",
    "schedule_b_line_31.yaml",
)
