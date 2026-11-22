"""Shared helpers of the TP-1 credit line tests (TP-1.D-V, 2025-12, page 4, lines 350 to 399).

Lines 350 to 359 read nothing from another form, so their tests run the real parts of the lines
under test over a test header and a test-local form declaration. Line 361 reads Schedule B (line
34), which reads line 275 of the TP-1 net income form, which reads three other forms (see
`tp1_net_income_support.py` and `schedule_b_support.py`): the tests of line 361 and after run the
real parts of the whole chain on the salary (the TP-1 slip figures that Schedule U reads are plain
starting inputs, as in its own tests), the real Schedule B declaration and the credit parts under
test. The salary is $20,000, $70,000 and $200,000.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import LINE_31_PARTS, NET_INCOME_PARTS
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER as CHAIN_HEADER,
)
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    UPSTREAM_PARTS,
)

D = Decimal
FORM = "ca-qc/tp1_credits"
HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The real Schedule B form declaration (it exports line 34) and its parts up to line 34.
SCHEDULE_B_PARTS = (
    "schedule_b.yaml",
    *LINE_31_PARTS,
    "schedule_b_line_32.yaml",
    "schedule_b_line_33_input.yaml",
    "schedule_b_line_34.yaml",
)
# Every part the chain over line 361 needs besides the credit parts under test.
CHAIN_PARTS = (*UPSTREAM_PARTS, *NET_INCOME_PARTS, *SCHEDULE_B_PARTS)
# The credit parts from line 350 to line 377.1 (a form cannot hold an output nothing reads, so a
# test takes the parts up to the line it exports).
LINE_359_PARTS = (
    "tp1_credits_line_350.yaml",
    "tp1_credits_line_358_input.yaml",
    "tp1_credits_line_359.yaml",
)
LINE_377_PARTS = (*LINE_359_PARTS, "tp1_credits_line_361.yaml", "tp1_credits_line_377.yaml")
LINE_377_1_PARTS = (*LINE_377_PARTS, "tp1_credits_line_377_1.yaml")
LINE_388_PARTS = ("tp1_credits_line_388_inputs.yaml", "tp1_credits_line_388.yaml")
LINE_389_PARTS = (*LINE_388_PARTS, "tp1_credits_line_389.yaml")
LINE_397_PARTS = ("tp1_credits_line_397_1_input.yaml", "tp1_credits_line_397.yaml")
LINE_399_PARTS = (
    *LINE_377_1_PARTS,
    *LINE_389_PARTS,
    *LINE_397_PARTS,
    "tp1_credits_line_399_inputs.yaml",
    "tp1_credits_line_399.yaml",
)


def credits_form(*exports: str) -> str:
    """A test form declaration of the credits form exporting `exports`."""
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM}\n  required: true\n  exports:\n{lines}capabilities: []\n"


def credits_sheet(
    take_home_service: TakeHomeService,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: Artifact[Any],
) -> Worksheet:
    """The credits worksheet over the real `parts` of lines that read no other form; every optional
    input is left out unless in `given`."""
    service = take_home_service(HEADER, credits_form(*exports), *parts)
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *given)[FORM]
    return sheet


def chain_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: Artifact[Any],
    form: str | None = None,
) -> Worksheet:
    """The credits worksheet for a salary, over the real chain up to Schedule B line 34 and the
    credit `parts` of a test; every optional input is left out unless in `given`. The form
    declaration is a test-local one exporting `exports`, unless `form` is the real declaration."""
    starting: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        *given,
    ]
    service = take_home_service(CHAIN_HEADER, form or credits_form(*exports), *CHAIN_PARTS, *parts)
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)[FORM]
    return sheet
