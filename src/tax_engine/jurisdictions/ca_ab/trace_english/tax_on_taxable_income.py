"""English text for the trace lines of `tax_engine.jurisdictions.ca_ab.trace.tax_on_taxable_income`:
one renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca_ab.trace.tax_on_taxable_income import TaxOnTaxableIncomeLine


@english_renderer
class TaxOnTaxableIncomeRenderer:
    """English text for TaxOnTaxableIncomeLine."""

    line_class = TaxOnTaxableIncomeLine

    def render(self, line: TaxOnTaxableIncomeLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        used = names.figure(line.used, line.used_amount)
        return (
            f"{used}, with {names.of(line.left_blank)} left blank, gives "
            f"{names.shown(line.output.label, line.used_amount)}"
        )
