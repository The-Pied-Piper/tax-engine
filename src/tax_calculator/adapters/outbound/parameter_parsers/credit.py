"""Parses `credit` datasets: an amount into a Credit. The rate is its own `rate` dataset."""

from __future__ import annotations

from tax_calculator.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_calculator.adapters.outbound.yaml_support import YamlNode
from tax_calculator.domain.parameters.credit import CREDIT, Credit


@parameter_parser
class CreditParser:
    """Parser for `credit` datasets: the credit amount a rate turns into tax relief."""

    kind = CREDIT
    body_keys = frozenset({"amount"})

    def parse(self, document: YamlNode) -> Credit:
        """Build a Credit from the dataset's `amount` (a quoted decimal)."""
        return Credit(amount=document.field("amount").parse_decimal())
