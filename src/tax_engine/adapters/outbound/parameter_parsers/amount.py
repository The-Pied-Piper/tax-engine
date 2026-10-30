"""Parses `amount` datasets: one quoted decimal into an Amount, which checks it is not negative."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.amount import AMOUNT, Amount


@parameter_parser
class AmountParser:
    """Parser for `amount` datasets: a single `amount`."""

    kind = AMOUNT
    body_keys = frozenset({"amount"})

    def parse(self, document: YamlNode) -> Amount:
        """Build an Amount from the dataset's `amount` (a quoted decimal)."""
        return Amount(document.field("amount").parse_decimal())
