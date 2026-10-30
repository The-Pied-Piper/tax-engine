"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.dependants`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.dependants import (
    CaregiverClaimLine,
    DisabilityTransferLine,
    OtherDependantMedicalLine,
)


@english_renderer
class CaregiverClaimRenderer:
    """English text for CaregiverClaimLine."""

    line_class = CaregiverClaimLine

    def render(self, line: CaregiverClaimLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        base = line.base
        net_income = line.net_income
        maximum = line.maximum
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: dependant {position}: {EnglishFigures.money(base.value)} less net "
            f"income {EnglishFigures.money(net_income)}, at most "
            f"{EnglishFigures.money(maximum.value)} = "
            f"{EnglishFigures.money(result)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class OtherDependantMedicalRenderer:
    """English text for OtherDependantMedicalLine."""

    line_class = OtherDependantMedicalLine

    def render(self, line: OtherDependantMedicalLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        expenses = line.expenses
        net_income = line.net_income
        reduction = line.reduction
        rule = line.rounding
        result = line.result
        at_most = (
            ""
            if reduction.maximum is None
            else f", at most {EnglishFigures.money(reduction.maximum)}"
        )
        return (
            f"{output.label}: dependant {position}: expenses {EnglishFigures.money(expenses)} "
            f"less the lesser of {EnglishFigures.percent(reduction.rate.value)}% of net income "
            f"{EnglishFigures.money(net_income)} and {EnglishFigures.money(reduction.ceiling)} = "
            f"{EnglishFigures.money(result)}{at_most} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class DisabilityTransferRenderer:
    """English text for DisabilityTransferLine."""

    line_class = DisabilityTransferLine

    def render(self, line: DisabilityTransferLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        base = line.base
        supplement = line.supplement
        threshold = line.threshold
        maximum = line.maximum
        under_18 = line.under_18
        care_expenses = line.care_expenses
        line_5 = line.line_5
        line_6 = line.line_6
        line_7 = line.line_7
        line_8 = line.line_8
        credit_amounts = line.credit_amounts
        taxable_income = line.taxable_income
        line_12 = line.line_12
        rule = line.rounding
        result = line.result
        steps = []
        if under_18:
            steps.append(
                f"care expenses {EnglishFigures.money(care_expenses)} less threshold "
                f"{EnglishFigures.money(threshold.value)} = {EnglishFigures.money(line_5)}"
            )
            steps.append(
                f"supplement {EnglishFigures.money(supplement.value)} less "
                f"{EnglishFigures.money(line_5)} "
                f"= {EnglishFigures.money(line_6)}"
            )
        steps.append(
            f"base {EnglishFigures.money(base.value)} + {EnglishFigures.money(line_7)}, at most "
            f"{EnglishFigures.money(maximum.value)} = {EnglishFigures.money(line_8)}"
        )
        steps.append(
            f"{EnglishFigures.money(line_8)} + credit amounts "
            f"{EnglishFigures.money(credit_amounts)} less "
            f"taxable income {EnglishFigures.money(taxable_income)} = "
            f"{EnglishFigures.money(line_12)}"
        )
        steps.append(
            f"the lesser of {EnglishFigures.money(line_8)} and {EnglishFigures.money(line_12)} = "
            f"{EnglishFigures.money(result)} ({EnglishFigures.rounding(rule)})"
        )
        age = "under 18" if under_18 else "18 or older"
        return f"{output.label}: dependant {position}: {age}: {'; '.join(steps)}"
