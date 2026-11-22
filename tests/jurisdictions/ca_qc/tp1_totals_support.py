"""Shared helpers of the TP-1 totals line tests (TP-1.D-V, 2025-12, page 5, lines 432 to 479).

Lines 432, 446, 447 and 456 read four other forms: the tax form (line 432), Schedule F (line 82),
Schedule K (line 98) and Schedule P (line 90). The tests run the real parts of those forms and of
the forms they read (the TP-1 net income lines, Schedule U, Schedule B, the credits lines and the
two work charts), on the salary, with the TP-1 slip figures that Schedule U reads as plain starting
inputs, as the other TP-1 tests do. Every optional input is left out unless a test gives it. The
salary is $20,000, $70,000 and $200,000.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_part_c_support import PART_A, PART_C
from tests.jurisdictions.ca_qc.schedule_k_part_d_support import PART_B, PART_D
from tests.jurisdictions.ca_qc.tp1_net_income_support import HEADER, slip_artifacts
from tests.jurisdictions.ca_qc.tp1_tax_support import LINE_413_CHAIN, LINE_414_PARTS

D = Decimal
FORM = "ca-qc/tp1_totals"
# The real tax form (it exports line 432) and its parts: lines 401 to 432, over their own chain.
TAX_PARTS = (
    *LINE_413_CHAIN,
    "tp1_tax.yaml",
    "tp1_tax_line_401.yaml",
    "tp1_tax_line_406.yaml",
    "tp1_tax_line_413.yaml",
    *LINE_414_PARTS,
    "tp1_tax_line_425_inputs.yaml",
    "tp1_tax_line_425.yaml",
    "tp1_tax_line_430.yaml",
    "tp1_tax_line_431_input.yaml",
    "tp1_tax_line_432.yaml",
)
# The real Schedule F form (it exports line 82) and its parts: Part A lines 10 to 70, Part B lines
# 77 to 82.
SCHEDULE_F_PARTS = (
    "tp1_schedule_f.yaml",
    "tp1_schedule_f_line_10_input.yaml",
    "tp1_schedule_f_line_10.yaml",
    "tp1_schedule_f_line_12.yaml",
    "tp1_schedule_f_line_14.yaml",
    "tp1_schedule_f_line_16.yaml",
    "tp1_schedule_f_line_18.yaml",
    "tp1_schedule_f_line_34_inputs.yaml",
    "tp1_schedule_f_line_25_inputs.yaml",
    "tp1_schedule_f_line_25.yaml",
    "tp1_schedule_f_line_34.yaml",
    "tp1_schedule_f_line_36.yaml",
    "tp1_schedule_f_line_68_inputs.yaml",
    "tp1_schedule_f_line_68.yaml",
    "tp1_schedule_f_line_70.yaml",
    "tp1_schedule_f_line_77.yaml",
    "tp1_schedule_f_line_78.yaml",
    "tp1_schedule_f_column_rate.yaml",
    "tp1_schedule_f_line_80.yaml",
    "tp1_schedule_f_line_81.yaml",
    "tp1_schedule_f_line_82.yaml",
)
# The real Schedule K form (it exports line 98) and its parts: Parts A, B, C and D.
SCHEDULE_K_PARTS = ("tp1_schedule_k.yaml", *PART_A, *PART_B, *PART_C, *PART_D)
# The real Schedule P form (it exports line 90) and its parts.
SCHEDULE_P_PARTS = (
    "schedule_p.yaml",
    "schedule_p_line_10.yaml",
    "schedule_p_line_14_inputs.yaml",
    "schedule_p_line_12.yaml",
    "schedule_p_line_13.yaml",
    "schedule_p_line_15.yaml",
    "schedule_p_line_18.yaml",
    "schedule_p_line_22_inputs.yaml",
    "schedule_p_line_29.yaml",
    "schedule_p_line_52.yaml",
    "schedule_p_line_56.yaml",
    "schedule_p_line_57_inputs.yaml",
    "schedule_p_line_58_inputs.yaml",
    "schedule_p_line_59.yaml",
    "schedule_p_line_60.yaml",
    "schedule_p_line_66.yaml",
    "schedule_p_line_68.yaml",
    "schedule_p_line_70.yaml",
    "schedule_p_line_72.yaml",
    "schedule_p_line_76.yaml",
    "schedule_p_line_80.yaml",
    "schedule_p_line_82.yaml",
    "schedule_p_line_83.yaml",
    "schedule_p_line_84.yaml",
    "schedule_p_line_90.yaml",
)
# Every part the chain over lines 432, 446, 447 and 456 needs besides the totals parts under test;
# a part shared by two forms is listed once.
CHAIN_PARTS = tuple(
    dict.fromkeys((*TAX_PARTS, *SCHEDULE_F_PARTS, *SCHEDULE_K_PARTS, *SCHEDULE_P_PARTS))
)


def totals_form(*exports: str) -> str:
    """A test form declaration of the totals form exporting `exports`."""
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM}\n  required: true\n  exports:\n{lines}capabilities: []\n"


def real_totals_form() -> str:
    """The real totals form declaration (it exports lines 478 and 479)."""
    return (QUEBEC_PARTS / "tp1_totals.yaml").read_text(encoding="utf-8")


def totals_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    form: str,
    parts: tuple[str, ...],
    *given: Artifact[Any],
) -> Worksheet:
    """The totals worksheet for a salary, over the real chain and the totals `parts` of a test;
    every optional input is left out unless in `given`. `form` is the form declaration."""
    starting = [*slip_artifacts(salary), *given]
    service = take_home_service(HEADER, form, *CHAIN_PARTS, *parts)
    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )[FORM]
    return sheet


# The totals parts in form order. A test takes the parts up to the line it checks (a form cannot
# hold an output nothing reads, so a test exports the lines it builds).
LINE_432_PARTS = ("tp1_totals_line_432.yaml",)
LINE_446_PARTS = ("tp1_totals_line_446.yaml",)
LINE_447_PARTS = ("tp1_totals_line_447.yaml",)
LINE_450_PARTS = (
    *LINE_432_PARTS,
    *LINE_446_PARTS,
    *LINE_447_PARTS,
    "tp1_totals_line_450_inputs.yaml",
    "tp1_totals_line_450.yaml",
)
LINE_456_PARTS = ("tp1_totals_line_456.yaml",)
LINE_457_PARTS = ("tp1_totals_line_457_inputs.yaml", "tp1_totals_line_457.yaml")
LINE_465_PARTS = (
    *LINE_456_PARTS,
    *LINE_457_PARTS,
    "tp1_totals_line_465_inputs.yaml",
    "tp1_totals_line_465.yaml",
)
LINE_468_PARTS = (*LINE_465_PARTS, "tp1_totals_line_466_input.yaml", "tp1_totals_line_468.yaml")
LINE_470_PARTS = (*LINE_450_PARTS, *LINE_468_PARTS, "tp1_totals_line_470.yaml")
ZERO_PARTS = ("tp1_totals_zero_line_474_475.yaml",)
LINE_475_PARTS = (*LINE_470_PARTS, *ZERO_PARTS, "tp1_totals_line_475.yaml")
LINE_474_PARTS = (*LINE_470_PARTS, *ZERO_PARTS, "tp1_totals_line_474.yaml")
LINE_478_PARTS = (*LINE_474_PARTS, "tp1_totals_line_476_input.yaml", "tp1_totals_line_478.yaml")
LINE_479_PARTS = (*LINE_475_PARTS, "tp1_totals_line_477_input.yaml", "tp1_totals_line_479.yaml")
# Every totals part: lines 478 and 479 together, which the real form declaration exports.
ALL_PARTS = tuple(dict.fromkeys((*LINE_478_PARTS, *LINE_479_PARTS)))

# The printed lines for each salary, by the default answers: line 432 (the tax after credits), line
# 446, line 447 (not covered by a group plan), line 450, line 456, line 465, line 468, line 470 and
# lines 474, 475, 478 and 479. Hand-computed from the printed lines, not an official example.
SALARIES = ("20000", "70000", "200000")
EXPECTED = {
    "20000": {
        "432": "8.96",
        "446": "0.00",
        "447": "0.00",
        "450": "8.96",
        "456": "584.02",
        "465": "584.02",
        "468": "584.02",
        "470": "-575.06",
        "474": "575.06",
        "475": "0.00",
        "478": "575.06",
        "479": "0.00",
    },
    "70000": {
        "432": "7641.16",
        "446": "0.00",
        "447": "755.00",
        "450": "8396.16",
        "456": "0.00",
        "465": "0.00",
        "468": "0.00",
        "470": "8396.16",
        "474": "0.00",
        "475": "8396.16",
        "478": "0.00",
        "479": "8396.16",
    },
    "200000": {
        "432": "38002.53",
        "446": "0.00",
        "447": "755.00",
        "450": "38757.53",
        "456": "0.00",
        "465": "0.00",
        "468": "0.00",
        "470": "38757.53",
        "474": "0.00",
        "475": "38757.53",
        "478": "0.00",
        "479": "38757.53",
    },
}
