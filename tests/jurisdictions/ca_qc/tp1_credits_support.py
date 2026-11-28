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

from tax_engine.application.models.calculation_request import TaxCalculationRequest
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
# TP-1 lines 350, 358, 359 and 361 are a split part of the same printed form (TP-752.PC-V line 48
# reads 359 and 361, and line 391 reads TP-752.PC-V, so they cannot sit in the form that line 391
# is in): the form `ca-qc/tp1_credits_lines_350_to_361` exports 359 and 361 to the other two.
PART_A_FORM = "ca-qc/tp1_credits_lines_350_to_361"
PART_A_DECLARATION = "tp1_credits_lines_350_to_361.yaml"
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
LINE_377_PARTS = (
    PART_A_DECLARATION,
    *LINE_359_PARTS,
    "tp1_credits_line_361.yaml",
    "tp1_credits_line_377.yaml",
)
LINE_377_1_PARTS = (*LINE_377_PARTS, "tp1_credits_line_377_1.yaml")
LINE_388_PARTS = ("tp1_credits_line_388_inputs.yaml", "tp1_credits_line_388.yaml")
LINE_389_PARTS = (*LINE_388_PARTS, "tp1_credits_line_389.yaml")
LINE_397_PARTS = ("tp1_credits_line_397_1_input.yaml", "tp1_credits_line_397.yaml")
# TP-752.PC-V (its line 48 reads lines 359 and 361 of the split part above, line 47 reads Work
# Chart 401 line 8, line 36 reads TP-1 line 275, line 10 reads Work Chart 201 line 6 and the age
# flag of the T1 birth year form) and TP-1 line 391 that reads its line 50.
WORK_CHART_401_PARTS = (
    "work_chart_401.yaml",
    "work_chart_401_line_1.yaml",
    "work_chart_401_line_3.yaml",
    "work_chart_401_line_4.yaml",
    "work_chart_401_line_5.yaml",
    "work_chart_401_line_6.yaml",
    "work_chart_401_line_7.yaml",
    "work_chart_401_line_8.yaml",
)
TP752_PC_LINE_PARTS = (
    "tp752_pc_line_10.yaml",
    "tp752_pc_line_11_input.yaml",
    "tp752_pc_line_13_input.yaml",
    "tp752_pc_line_12.yaml",
    "tp752_pc_line_14.yaml",
    "tp752_pc_line_15.yaml",
    "tp752_pc_line_16.yaml",
    "tp752_pc_line_35.yaml",
    "tp752_pc_line_36.yaml",
    "tp752_pc_line_37.yaml",
    "tp752_pc_line_38.yaml",
    "tp752_pc_line_39.yaml",
    "tp752_pc_line_40.yaml",
    "tp752_pc_line_47.yaml",
    "tp752_pc_line_48.yaml",
    "tp752_pc_line_49.yaml",
    "tp752_pc_line_50.yaml",
)
TP752_PC_PARTS = ("tp752_pc.yaml", *TP752_PC_LINE_PARTS, *WORK_CHART_401_PARTS)
LINE_391_PARTS = (
    PART_A_DECLARATION,
    *LINE_359_PARTS,
    "tp1_credits_line_361.yaml",
    *TP752_PC_PARTS,
    "tp1_credits_line_391.yaml",
)
LINE_399_PARTS = (
    *LINE_377_1_PARTS,
    *TP752_PC_PARTS,
    "tp1_credits_line_391.yaml",
    *LINE_389_PARTS,
    *LINE_397_PARTS,
    "tp1_credits_line_399_inputs.yaml",
    "tp1_credits_line_399.yaml",
)


def credits_form(*exports: str, name: str = FORM) -> str:
    """A test form declaration of the credits form (or of its split part `name`) exporting
    `exports`."""
    lines = "".join(f"    - {export}\n" for export in exports)
    return f"form:\n  name: {name}\n  required: true\n  exports:\n{lines}capabilities: []\n"


def credits_sheet(
    take_home_service: TakeHomeService,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: Artifact[Any],
    name: str = FORM,
) -> Worksheet:
    """The credits worksheet (of the split part `name`) over the real `parts` of lines that read no
    other form; every optional input is left out unless in `given`."""
    service = take_home_service(HEADER, credits_form(*exports, name=name), *parts)
    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(given))
    )[name]
    return sheet


def chain_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: Artifact[Any],
    form: str | None = None,
    name: str = FORM,
) -> Worksheet:
    """The credits worksheet (of the split part `name`) for a salary, over the real chain up to
    Schedule B line 34 and the credit `parts` of a test; every optional input is left out unless in
    `given`. The form declaration is a test-local one exporting `exports`, unless `form` is the real
    declaration."""
    (sheet,) = chain_sheets(
        take_home_service, salary, exports, parts, *given, form=form, name=name
    )[name]
    return sheet


def chain_sheets(
    take_home_service: TakeHomeService,
    salary: str,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: Artifact[Any],
    form: str | None = None,
    name: str = FORM,
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of one run of the chain `chain_sheet` describes."""
    starting: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        *given,
    ]
    service = take_home_service(
        CHAIN_HEADER, form or credits_form(*exports, name=name), *CHAIN_PARTS, *parts
    )
    return dict(
        service.compute(TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting)))
    )
