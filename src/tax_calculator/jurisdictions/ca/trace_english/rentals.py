"""English text for the trace lines of `tax_calculator.jurisdictions.ca.trace.rentals`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english.figures import EnglishFigures
from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.jurisdictions.ca.trace.rentals import (
    RentalAdditionLine,
    ShortTermRentalNonCompliantCcaByClassLine,
    ShortTermRentalNonCompliantCcaLine,
    ShortTermRentalNonCompliantLine,
)


@english_renderer
class RentalAdditionRenderer:
    """English text for RentalAdditionLine."""

    line_class = RentalAdditionLine

    def render(self, line: RentalAdditionLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: addition {line.position}: class "
            f"{EnglishFigures.money(line.class_number)} cost "
            f"{EnglishFigures.money(line.total_cost)} "
            f"less personal portion {EnglishFigures.money(line.personal_portion)} = "
            f"{EnglishFigures.money(line.result)}"
        )


@english_renderer
class ShortTermRentalNonCompliantRenderer:
    """English text for ShortTermRentalNonCompliantLine."""

    line_class = ShortTermRentalNonCompliantLine

    def render(self, line: ShortTermRentalNonCompliantLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        related_expenses = line.related_expenses
        non_compliant_days = line.non_compliant_days
        days = line.days
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: row {position}: expenses {EnglishFigures.money(related_expenses)} "
            f"for {non_compliant_days} non-compliant days of {days} short-term days = "
            f"{EnglishFigures.money(result)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class ShortTermRentalNonCompliantCcaRenderer:
    """English text for ShortTermRentalNonCompliantCcaLine."""

    line_class = ShortTermRentalNonCompliantCcaLine

    def render(self, line: ShortTermRentalNonCompliantCcaLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        class_number = line.class_number
        related_cca = line.related_cca
        non_compliant_days = line.non_compliant_days
        days = line.days
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: row {position}: class {EnglishFigures.money(class_number)} CCA "
            f"{EnglishFigures.money(related_cca)} for {non_compliant_days} non-compliant days of "
            f"{days} short-term days = {EnglishFigures.money(result)} "
            f"({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class ShortTermRentalNonCompliantCcaByClassRenderer:
    """English text for ShortTermRentalNonCompliantCcaByClassLine."""

    line_class = ShortTermRentalNonCompliantCcaByClassLine

    def render(self, line: ShortTermRentalNonCompliantCcaByClassLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        class_number = line.class_number
        amounts = " + ".join(EnglishFigures.money(amount) for amount in line.amounts)
        result = line.result
        return (
            f"{output.label}: item {position} class {EnglishFigures.money(class_number)}: "
            f"column 7 {amounts} = {EnglishFigures.money(result)}"
        )
