"""Shared helpers of the Schedule F line 25 and 34 tests (TP-1.D.F-V, 2025-12, Part A).

The tests run the real parts of the Schedule F chain up to line 36 on a salary: line 10 reads
line 199 of the TP-1 income form, so the income parts come with it. The optional inputs are left
out unless a test gives them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS, UPSTREAM_PARTS

D = Decimal
FORM = "ca-qc/tp1_schedule_f"
# The end of a chain: a form cannot hold a produced line that nothing reads or exports.
LINE_36 = "ca-qc/tp1_schedule_f_income_line_36"
LINE_70 = "ca-qc/tp1_schedule_f_income_subject_line_70"
LINE_25_INPUTS = ("24",)
LINE_34_INPUTS = ("20", "30", "31", "33")
LINE_36_PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_f_line_10_input.yaml",
    "tp1_schedule_f_line_10.yaml",
    "tp1_schedule_f_line_12.yaml",
    "tp1_schedule_f_line_14.yaml",
    "tp1_schedule_f_line_16.yaml",
    "tp1_schedule_f_line_18.yaml",
    "tp1_schedule_f_line_34_inputs.yaml",
    "tp1_schedule_f_line_25_inputs.yaml",
    "tp1_schedule_f_line_25.yaml",
    "tp1_schedule_f_line_22.yaml",
    "tp1_schedule_f_line_23.yaml",
    "tp1_schedule_f_line_26.yaml",
    "tp1_schedule_f_line_28.yaml",
    "tp1_schedule_f_line_29.yaml",
    "tp1_schedule_f_line_34.yaml",
    "tp1_schedule_f_line_36.yaml",
)
# The printed lines that line 68 adds; lines 41, 46, 54, 56 and 58 copy TP-1 lines 246, 245, 225,
# 231 and 234 (given on the TP-1 net income form), the other seven are inputs of Schedule F.
LINE_68_LINES = ("41", "42", "43", "43_1", "44", "45", "46", "54", "56", "58", "60", "62")
LINE_68_TP1_COPIES = ("41", "46", "54", "56", "58")
LINE_68_INPUTS = tuple(line for line in LINE_68_LINES if line not in LINE_68_TP1_COPIES)
# The real TP-1 net income form declaration (it exports lines 275 and 299 and the TP-1 lines the
# Schedule F lines copy) and its line parts, over the Work Chart 201 and Schedule U parts it reads.
NET_INCOME_PARTS = (
    *UPSTREAM_PARTS,
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
LINE_68_COPY_PARTS = tuple(f"tp1_schedule_f_line_{line}.yaml" for line in LINE_68_TP1_COPIES)
LINE_70_PARTS = (
    *LINE_36_PARTS,
    *NET_INCOME_PARTS,
    *LINE_68_COPY_PARTS,
    "tp1_schedule_f_line_68_inputs.yaml",
    "tp1_schedule_f_line_68.yaml",
    "tp1_schedule_f_line_70.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)


def schedule_f(
    take_home_service: TakeHomeService,
    salary: str,
    export: str,
    *given: tuple[AmountKind, str],
    parts: tuple[str, ...] = LINE_36_PARTS,
    end: str = LINE_36,
) -> Worksheet:
    """The Schedule F worksheet for a salary, exporting `export` and the chain's `end`.

    Every optional input is left out unless it is in `given`."""
    exports = dict.fromkeys((export, end))
    form = f"form:\n  name: {FORM}\n  required: true\n  exports:\n"
    form += "".join(f"    - {name}\n" for name in exports)
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    starting.extend(Artifact(kind, D(value)) for kind, value in given)
    (sheet,) = take_home_service(HEADER, form, *parts).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )[FORM]
    return sheet
