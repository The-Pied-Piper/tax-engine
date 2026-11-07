"""Parses `amount_by_band` datasets: a list of rows, each a flat {over, amount} or a sloped
{over, minus, rate, plus}, into AmountByBand."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parser import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.errors import DomainError, InvalidAmountByBandError
from tax_engine.domain.parameters.amount_by_band import (
    AMOUNT_BY_BAND,
    AmountBand,
    AmountByBand,
)
from tax_engine.domain.parameters.rate import Rate

_ROW_KEYS = frozenset({"over"})
_OPTIONAL_ROW_KEYS = frozenset({"amount", "minus", "rate", "plus"})


@parameter_parser
class AmountByBandParser:
    """Parser for `amount_by_band` datasets: the chart's rows, in order."""

    kind = AMOUNT_BY_BAND
    body_keys = frozenset({"rows"})

    def parse(self, document: YamlNode) -> AmountByBand:
        """Build AmountByBand from the dataset's `rows` list of {over, amount} or
        {over, minus, rate, plus}."""
        return AmountByBand(tuple(self._band(entry) for entry in document.field("rows").items()))

    @staticmethod
    def _band(entry: YamlNode) -> AmountBand:
        fields = entry.require_mapping(_ROW_KEYS, optional=_OPTIONAL_ROW_KEYS)
        over = fields.field("over").parse_decimal()
        amount_node = fields.optional_field("amount")
        minus_node = fields.optional_field("minus")
        rate_node = fields.optional_field("rate")
        plus_node = fields.optional_field("plus")
        try:
            return AmountBand(
                over,
                amount=None if amount_node is None else amount_node.parse_decimal(),
                minus=None if minus_node is None else minus_node.parse_decimal(),
                rate=None if rate_node is None else Rate(rate_node.parse_decimal()),
                plus=None if plus_node is None else plus_node.parse_decimal(),
            )
        except DomainError as exc:
            # Name the row: the value objects do not know where in the list they sit.
            raise InvalidAmountByBandError(f"{entry.where}: {exc}") from exc
