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
T1_FORM = "ca-qc/t1_tax_and_credits"
TP1_TOTALS_FORM = "ca-qc/tp1_totals"
SUPPLEMENT_TYPED = "250.00"


@cache
def _sheets(salary: str, supplement: str | None) -> dict[str, Worksheet]:
    given = (
        []
        if supplement is None
        else [Artifact(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160, D(supplement))]
    )
    worksheets = build_tax_computation().compute(
        QUEBEC, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)), *given
    )
    sheets = {form: forms[0] for form, forms in worksheets.items()}
    return sheets


def _exports(part: str) -> list[str]:
    declaration = yaml.safe_load((QUEBEC_PARTS / part).read_text(encoding="utf-8"))
    exports = declaration["form"]["exports"]
    assert isinstance(exports, list)
    return exports


def test_the_t1_form_exports_the_benefit_lines_159_to_161() -> None:
    exports = _exports("t1_tax_and_credits.yaml")

    assert "ca-qc/net_ei_overpayment_line_159" in exports
    assert "ca-qc/refundable_medical_expense_supplement_line_160" in exports
    assert "ca-qc/cwb_line_161" in exports


def test_the_totals_form_exports_the_work_premium_of_line_456() -> None:
    assert "ca-qc/tp1_work_premium_tax_credits_line_456" in _exports("tp1_totals.yaml")


def test_the_withheld_tax_of_line_155_is_not_exported() -> None:
    exports = _exports("t1_tax_and_credits.yaml")

    assert not any(name.endswith("line_155") for name in exports)


@pytest.mark.parametrize(
    ("salary", "work_premium", "cwb"),
    [("20000", "584.02", "2679.07"), ("70000", "0.00", "0.00")],
)
def test_a_salary_only_filer_has_the_work_premium_and_the_cwb(
    salary: str, work_premium: str, cwb: str
) -> None:
    sheets = _sheets(salary, None)

    assert sheets[TP1_TOTALS_FORM].get(TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456).value == D(
        work_premium
    )
    assert sheets[T1_FORM].get(CWB_LINE_161).value == D(cwb)


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_a_salary_only_filer_has_no_net_ei_overpayment(salary: str) -> None:
    sheet = _sheets(salary, None)[T1_FORM]

    assert sheet.get(NET_EI_OVERPAYMENT_LINE_159).value == D("0.00")


def test_a_salary_only_filer_leaves_the_medical_supplement_blank() -> None:
    sheet = _sheets("20000", None)[T1_FORM]

    assert sheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160).is_blank


def test_a_typed_medical_supplement_is_read_back() -> None:
    sheet = _sheets("20000", SUPPLEMENT_TYPED)[T1_FORM]

    assert sheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160).value == D(SUPPLEMENT_TYPED)


def test_the_abatement_of_line_156_is_the_printed_figure() -> None:
    # Line 156 is a reduction of federal tax, not a benefit, so it is not exported as one.
    sheet = _sheets("20000", None)[T1_FORM]

    assert sheet.get(REFUNDABLE_QUEBEC_ABATEMENT_LINE_156).value == D("23.52")


@pytest.mark.parametrize(("salary", "expected"), [("20000", "363.00"), ("70000", "0.00")])
def test_the_solidarity_credit_is_the_returns_own_output(salary: str, expected: str) -> None:
    sheet = _sheets(salary, None)["ca-qc/return"]

    assert sheet.get(SOLIDARITY_CREDIT).value == D(expected)
