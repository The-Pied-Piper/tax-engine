"""The take-home manifest names its forms and figures for a reader: $70,000 in Ontario, 2025."""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME


def test_the_worksheets_carry_the_titles_the_manifest_gives() -> None:
    sheets = build_tax_computation().compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, Decimal("70000"))
    )

    (on428,) = sheets["ca-on/on428"]
    (schedule_8,) = sheets["ca/schedule_8"]
    (summary,) = sheets["ca-on/return"]

    assert on428.form_title == "Form ON428: Ontario Tax"
    assert schedule_8.form_title == "Schedule 8: Canada Pension Plan Contributions and Overpayment"
    assert summary.form_title == "Return summary"
    assert on428.title("on428_surtax_total_line_68") == "Ontario surtax"
    assert on428.title("on428_tax_on_taxable_income_line_8") == "Ontario tax on taxable income"
    assert on428.title("on428_taxable_income_line_1") is None
    assert on428.title("no_such_label") is None
    assert on428.reference("on428_surtax_total_line_68") == "68"
    assert on428.reference("on428_taxable_income_line_1") == "1"
    assert on428.reference("on428_taxable_income_line_89") == "1"
    assert on428.reference("no_such_label") is None
