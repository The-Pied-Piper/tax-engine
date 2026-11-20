"""Shared set-up of the 5005-R Step 5 Part C tests (lines 123 to 138): the real Steps 3 and 4 chain,
the real credit lines of Part B, the real Part A lines 71 to 77 and the real Part C parts up to the
line under test, so every figure is read from the salary through the real lines. The form
declaration is test-local: its one export is the line under test. The header is made up."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.basic_personal_amount_support import HEADER, PARTS, TAX_FORM
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
# Part A of Step 5 as printed: lines 71 to 77.
PART_A_PARTS = tuple(f"t1_tax_and_credits_line_{line}.yaml" for line in range(71, 78))
# The parts of Part C, in form line order (the optional lines first read by the line after them).
PART_C_PARTS: tuple[str, ...] = (
    "t1_tax_and_credits_line_40424_inputs.yaml",
    "t1_tax_and_credits_line_40400.yaml",
    "t1_tax_and_credits_line_40425_inputs.yaml",
    "t1_tax_and_credits_line_40427_inputs.yaml",
    "t1_tax_and_credits_line_129.yaml",
    "t1_tax_and_credits_line_42900.yaml",
    "t1_tax_and_credits_line_131_inputs.yaml",
    "t1_tax_and_credits_line_132.yaml",
    "t1_tax_and_credits_line_40500_inputs.yaml",
    "t1_tax_and_credits_line_134.yaml",
    "t1_tax_and_credits_line_135_inputs.yaml",
    "t1_tax_and_credits_line_136.yaml",
    "t1_tax_and_credits_line_137_inputs.yaml",
    "t1_tax_and_credits_line_40600.yaml",
)
LINE_122 = "ca-qc/non_refundable_tax_credits_line_122"
# The identifier each step part produces.
STEP_EXPORTS: dict[str, str] = {
    "t1_tax_and_credits_line_40400.yaml": "ca-qc/federal_tax_with_split_income_line_125",
    "t1_tax_and_credits_line_129.yaml": "ca-qc/federal_credits_and_carryovers_line_129",
    "t1_tax_and_credits_line_42900.yaml": "ca-qc/basic_federal_tax_line_130",
    "t1_tax_and_credits_line_132.yaml": "ca-qc/federal_tax_with_surtax_line_132",
    "t1_tax_and_credits_line_134.yaml": "ca-qc/federal_tax_less_foreign_tax_credit_line_134",
    "t1_tax_and_credits_line_136.yaml": "ca-qc/federal_tax_with_itc_recapture_line_136",
    "t1_tax_and_credits_line_40600.yaml": "ca-qc/federal_tax_line_138",
}


def form(exports: tuple[str, ...]) -> str:
    """The tax and credits declaration, test-local: it exports line 122 and every Part C step up to
    the line under test, so no composed step is left an orphan."""
    listed = "".join(f"            - {name}\n" for name in exports)
    return dedent(f"""\
        form:
          name: {TAX_FORM}
          required: true
          exports:
{listed}        capabilities: []
        """)


def sheets(
    take_home_service: TakeHomeService,
    salary: str,
    last: str,
    *given: tuple[AmountKind, str],
) -> Worksheet:
    """The tax and credits sheet for `salary`, with the Part C parts up to `last` composed and the
    optional figures in `given` typed in."""
    upto = PART_C_PARTS.index(last) + 1
    exports = (
        LINE_122,
        *(STEP_EXPORTS[part] for part in PART_C_PARTS[:upto] if part in STEP_EXPORTS),
    )
    parts = (*PARTS, *PART_A_PARTS, *PART_C_PARTS[:upto])
    worksheets = take_home_service(HEADER, form(exports), *parts).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        *(Artifact(kind, D(figure)) for kind, figure in given),
    )
    (sheet,) = worksheets[TAX_FORM]
    return sheet
