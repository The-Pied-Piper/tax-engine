"""Shared set-up of the 5005-R line 78 tests: the real Step 3 chain, the real form declarations
and the real Schedule 8 and Schedule 6 imports, so line 23600 is read from the salary through the
real lines. The header is made up."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import real_import

D = Decimal
T1_FORM = "ca-qc/t1_taxable_income"
TAX_FORM = "ca-qc/t1_tax_and_credits"
STEP_3_PARTS = (
    "t1_employment_income_line_10400_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_21.yaml",
    "t1_taxable_income_line_27_inputs.yaml",
    "t1_taxable_income_line_27.yaml",
    "t1_taxable_income_line_28.yaml",
    "t1_taxable_income_line_32_inputs.yaml",
    "t1_taxable_income_line_32.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_22215.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23500_inputs.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
)
# The PPIP premium form, which 5005-R line 91 reads, and the credit lines of 5005-R Step 5 Part B
# (the form declaration exports line 85 and line 100, so every producer is composed).
PPIP_PARTS = (
    "ppip_premium.yaml",
    "ppip_premium_inputs.yaml",
    "ppip_premium_line_91.yaml",
)
LINE_85_INPUT_PARTS = (
    "t1_tax_and_credits_line_30100_inputs.yaml",
    "t1_tax_and_credits_line_30300_inputs.yaml",
    "t1_tax_and_credits_line_30400_inputs.yaml",
    "t1_tax_and_credits_line_30425_inputs.yaml",
    "t1_tax_and_credits_line_30450_inputs.yaml",
    "t1_tax_and_credits_line_30500_inputs.yaml",
)
LINE_100_INPUT_PARTS = (
    "t1_tax_and_credits_line_31000_inputs.yaml",
    "t1_tax_and_credits_line_31217_inputs.yaml",
    "t1_tax_and_credits_line_31210_inputs.yaml",
    "t1_tax_and_credits_line_31215_inputs.yaml",
    "t1_tax_and_credits_line_31220_inputs.yaml",
    "t1_tax_and_credits_line_31240_inputs.yaml",
    "t1_tax_and_credits_line_31270_inputs.yaml",
    "t1_tax_and_credits_line_31285_inputs.yaml",
    "t1_tax_and_credits_line_31300_inputs.yaml",
)
# The parts of lines 101 to 122, in form line order (5005-R Step 5 Part B, from the pension income
# amount to the total federal non-refundable tax credits).
LINES_101_TO_122_PARTS: tuple[str, ...] = (
    "t1_tax_and_credits_line_31400_inputs.yaml",
    "t1_tax_and_credits_line_102.yaml",
    "t1_tax_and_credits_line_31600_inputs.yaml",
    "t1_tax_and_credits_line_31800_inputs.yaml",
    "t1_tax_and_credits_line_105.yaml",
    "t1_tax_and_credits_line_31900_inputs.yaml",
    "t1_tax_and_credits_line_32300_inputs.yaml",
    "t1_tax_and_credits_line_32400_inputs.yaml",
    "t1_tax_and_credits_line_32600_inputs.yaml",
    "t1_tax_and_credits_line_110.yaml",
    "t1_tax_and_credits_line_112.yaml",
    "t1_tax_and_credits_line_113.yaml",
    "t1_tax_and_credits_line_33099_inputs.yaml",
    "t1_tax_and_credits_line_114.yaml",
    "t1_tax_and_credits_line_33199_inputs.yaml",
    "t1_tax_and_credits_line_33200.yaml",
    "t1_tax_and_credits_line_33500.yaml",
    "t1_tax_and_credits_line_33800.yaml",
    "t1_tax_and_credits_line_34900_inputs.yaml",
    "t1_tax_and_credits_line_34990_inputs.yaml",
    "t1_tax_and_credits_line_35000.yaml",
)
CREDIT_PARTS = (
    *LINE_85_INPUT_PARTS,
    "t1_tax_and_credits_line_85.yaml",
    "t1_tax_and_credits_line_30800.yaml",
    "t1_tax_and_credits_line_31200.yaml",
    "t1_tax_and_credits_line_31205.yaml",
    "t1_tax_and_credits_line_31260.yaml",
    *LINE_100_INPUT_PARTS,
    "t1_tax_and_credits_line_100.yaml",
    *LINES_101_TO_122_PARTS,
)
# Part A of Step 5 as printed: lines 71 to 77, then Part C and Step 6 (lines 123 to
# 172, in form line order).
PART_A_PARTS: tuple[str, ...] = (
    "t1_tax_and_credits_line_71.yaml",
    "t1_tax_and_credits_line_72.yaml",
    "t1_tax_and_credits_line_73.yaml",
    "t1_tax_and_credits_line_74.yaml",
    "t1_tax_and_credits_line_75.yaml",
    "t1_tax_and_credits_line_76.yaml",
    "t1_tax_and_credits_line_77.yaml",
)
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
    "t1_tax_and_credits_line_41600_inputs.yaml",
    "t1_tax_and_credits_line_41600.yaml",
    "t1_tax_and_credits_line_41700.yaml",
    "t1_tax_and_credits_line_41500_inputs.yaml",
    "t1_tax_and_credits_line_41800_inputs.yaml",
    "t1_tax_and_credits_line_42000.yaml",
    "t1_tax_and_credits_line_42120_inputs.yaml",
    "t1_tax_and_credits_line_42200.yaml",
    "t1_tax_and_credits_line_42800_inputs.yaml",
    "t1_tax_and_credits_line_43500.yaml",
    "t1_tax_and_credits_line_43850_inputs.yaml",
    "t1_tax_and_credits_line_43850.yaml",
    "t1_tax_and_credits_line_44000.yaml",
    "t1_tax_and_credits_line_45000.yaml",
    "t1_tax_and_credits_line_45100.yaml",
    "t1_tax_and_credits_line_45200_inputs.yaml",
    "t1_tax_and_credits_line_45300.yaml",
    "t1_tax_and_credits_line_45350_inputs.yaml",
    "t1_tax_and_credits_line_45355_inputs.yaml",
    "t1_tax_and_credits_line_45400_inputs.yaml",
    "t1_tax_and_credits_line_45600_inputs.yaml",
    "t1_tax_and_credits_line_45700_inputs.yaml",
    "t1_tax_and_credits_line_46900_inputs.yaml",
    "t1_tax_and_credits_line_46900.yaml",
    "t1_tax_and_credits_line_47555_inputs.yaml",
    "t1_tax_and_credits_line_47556_inputs.yaml",
    "t1_tax_and_credits_line_47600_inputs.yaml",
    "t1_tax_and_credits_line_48200.yaml",
    "t1_tax_and_credits_line_172.yaml",
)
STEP_4_PARTS = (
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_26000.yaml",
)
PARTS = (
    *PPIP_PARTS,
    "t1_taxable_income.yaml",
    *STEP_3_PARTS,
    *STEP_4_PARTS,
    "t1_tax_and_credits_line_30000_line_3.yaml",
    "t1_tax_and_credits_line_30000.yaml",
    *CREDIT_PARTS,
    *PART_A_PARTS,
    *PART_C_PARTS,
)
HEADER = (
    dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    imports:
    """)
    + real_import("ca/schedule_8")
    + real_import("ca/schedule_6")
    + real_import("ca/t2204")
)
# The real tax and credits declaration is the form; the real T1 declaration is the first part.
FORM = (QUEBEC_PARTS / "t1_tax_and_credits.yaml").read_text(encoding="utf-8")


def sheets(
    take_home_service: TakeHomeService, salary: str, *given: tuple[AmountKind, str]
) -> tuple[Worksheet, Worksheet]:
    """The T1 taxable-income sheet and the tax and credits sheet for `salary`, with the optional
    figures in `given` (a kind and its figure) typed in."""
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        *(Artifact(kind, D(figure)) for kind, figure in given),
    )
    (t1,) = worksheets[T1_FORM]
    (sheet,) = worksheets[TAX_FORM]
    return t1, sheet
