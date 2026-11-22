"""The Quebec return benefits: the figures of the 5005-R and TP-1 forms that are benefits, each
exported by its form so a caller can list them.

5005-R (2025) page 8: "Line 171 and line 48200: Add lines 155, 156, and 159 to 170. Total credits".
Of those, the benefits are line 159 (net EI overpayment), line 160 (refundable medical expense
supplement) and line 161 (Canada workers benefit); line 155 (tax already withheld) and line 156 (the
refundable Quebec abatement, a reduction of federal tax) are not. TP-1.D-V (2025-12) page 5 line
456: "Tax credits respecting the work premium. Complete Schedule P." The solidarity tax credit is
the return's own output (`ca-qc/solidarity_credit`) and needs no export.

The engine runs over the real Quebec 2025 manifest with the gross salary the only input. The figures
are hand-computed from the printed lines, not a CRA or Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from functools import cache
from typing import Any

import pytest
import yaml

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    CWB_LINE_161,
    NET_EI_OVERPAYMENT_LINE_159,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160,
    REFUNDABLE_QUEBEC_ABATEMENT_LINE_156,
    SOLIDARITY_CREDIT,
    TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS

D = Decimal
QUEBEC = JurisdictionCode("CA-QC")
SALARIES = ("20000", "70000")
SUPPLEMENT_TYPED = "250.00"


@cache
def _sheets(salary: str, supplement: str | None) -> dict[str, Worksheet]:
    """The one sheet of each form the engine computes for a salary."""
    given = (
        []
        if supplement is None
        else [Artifact(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160, D(supplement))]
    )
    worksheets = build_tax_computation().compute(
        QUEBEC, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)), *given
    )
    return {form: sheets[0] for form, sheets in worksheets.items()}


def _declaration(part: str) -> dict[str, Any]:
    declaration = yaml.safe_load((QUEBEC_PARTS / part).read_text(encoding="utf-8"))
    assert isinstance(declaration, dict)
    return declaration


def test_the_real_t1_form_declaration_exports_the_benefit_lines_159_to_161() -> None:
    declaration = _declaration("t1_tax_and_credits.yaml")

    assert declaration["form"]["name"] == "ca-qc/t1_tax_and_credits"
    assert declaration["form"]["exports"] == [
        "ca-qc/credit_amounts_line_85",
        "ca-qc/credits_line_100",
        "ca-qc/non_refundable_tax_credits_line_122",
        "ca-qc/basic_federal_tax_line_130",
        "ca-qc/federal_tax_line_138",
        "ca-qc/total_payable_line_151",
        "ca-qc/refundable_quebec_abatement_line_156",
        "ca-qc/net_ei_overpayment_line_159",
        "ca-qc/refundable_medical_expense_supplement_line_160",
        "ca-qc/cwb_line_161",
        "ca-qc/refund_or_balance_owing_line_172",
    ]


LINE_456_FIGURES = {"20000": "584.02", "70000": "0.00"}


@pytest.mark.parametrize(("salary", "expected"), list(LINE_456_FIGURES.items()))
def test_tp1_line_456(salary: str, expected: str) -> None:
    sheet = _sheets(salary, None)["ca-qc/tp1_totals"]

    assert sheet.get(TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456).value == D(expected)


CWB_FIGURES = {"20000": "2679.07", "70000": "0.00"}


@pytest.mark.parametrize(("salary", "expected"), list(CWB_FIGURES.items()))
def test_5005_r_line_161(salary: str, expected: str) -> None:
    sheet = _sheets(salary, None)["ca-qc/t1_tax_and_credits"]

    assert sheet.get(CWB_LINE_161).value == D(expected)


@pytest.mark.parametrize("salary", SALARIES)
def test_a_salary_only_line_159_is_zero(salary: str) -> None:
    sheet = _sheets(salary, None)["ca-qc/t1_tax_and_credits"]

    assert sheet.get(NET_EI_OVERPAYMENT_LINE_159).value == D("0.00")


def test_a_salary_only_line_160_is_blank() -> None:
    sheet = _sheets("20000", None)["ca-qc/t1_tax_and_credits"]

    assert sheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160).is_blank


def test_a_typed_line_160_is_read_back() -> None:
    sheet = _sheets("20000", SUPPLEMENT_TYPED)["ca-qc/t1_tax_and_credits"]

    assert sheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160).value == D(SUPPLEMENT_TYPED)


def test_line_156_is_the_printed_abatement_and_is_not_a_benefit() -> None:
    sheet = _sheets("20000", None)["ca-qc/t1_tax_and_credits"]

    assert sheet.get(REFUNDABLE_QUEBEC_ABATEMENT_LINE_156).value == D("23.52")


SOLIDARITY_FIGURES = {"20000": "363.00", "70000": "0.00"}


@pytest.mark.parametrize(("salary", "expected"), list(SOLIDARITY_FIGURES.items()))
def test_the_solidarity_credit_is_the_returns_own_output(salary: str, expected: str) -> None:
    sheet = _sheets(salary, None)["ca-qc/return"]

    assert sheet.get(SOLIDARITY_CREDIT).value == D(expected)
