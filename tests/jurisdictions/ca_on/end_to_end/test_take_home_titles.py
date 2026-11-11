"""The take-home manifest names its forms and figures for a reader: $70,000 in Ontario, 2025."""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import DefaultedInputLine
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
    assert on428.title("on428_pension_income_amount") == "Pension income amount"
    assert on428.reference("on428_pension_income_amount") == "27"
    assert on428.title("on428_medical_expenses_line_43") == "Medical expenses"
    assert on428.reference("on428_medical_expenses_line_43") == "43"
    assert on428.title("on428_donations_credit_line_49") == "Donations and gifts"
    assert on428.reference("on428_donations_credit_line_49") == "49"
    assert on428.title("on428_tax_on_split_income_line_54") == "Ontario tax on split income"
    assert on428.reference("on428_tax_on_split_income_line_54") == "54"
    assert on428.title("on428_dividend_tax_credit_line_57") == "Ontario dividend tax credit"
    assert on428.reference("on428_dividend_tax_credit_line_57") == "57"
    assert on428.title("on428_minimum_tax_carryover_line_60") == "Ontario minimum tax carryover"
    assert on428.reference("on428_minimum_tax_carryover_line_60") == "60"
    assert (
        on428.title("on428_additional_tax_for_minimum_tax_line_72")
        == "Ontario additional tax for minimum tax purposes"
    )
    assert on428.reference("on428_additional_tax_for_minimum_tax_line_72") == "72"
    assert (
        on428.title("on428_provincial_foreign_tax_credit_line_82")
        == "Provincial foreign tax credit"
    )
    assert on428.reference("on428_provincial_foreign_tax_credit_line_82") == "82"
    assert on428.title("on428_qualifying_food_donations_line_87") is None
    assert on428.reference("on428_qualifying_food_donations_line_87") == "87"
    assert on428.title("no_such_label") is None
    assert on428.reference("on428_surtax_total_line_68") == "68"
    assert on428.reference("on428_taxable_income_line_1") == "1"
    assert on428.reference("on428_taxable_income_line_89") == "1"
    assert on428.reference("no_such_label") is None


def test_schedule_8_line_a_is_traced_as_the_months_default_with_its_printed_reference() -> None:
    sheets = build_tax_computation().compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, Decimal("70000"))
    )

    (schedule_8,) = sheets["ca/schedule_8"]
    (months,) = [
        line
        for line in schedule_8.trace
        if isinstance(line, DefaultedInputLine) and line.label == "cpp_months"
    ]

    assert months.amount == 12
    assert (
        EnglishTraceRenderer().render(months) == "No value given, so the form's default gives 12."
    )
    assert schedule_8.reference("cpp_months") == "A"
