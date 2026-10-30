"""Parses `amount_by_count` datasets: quoted counts and quoted decimals into an AmountByCount."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount


@parameter_parser
class AmountByCountParser:
    """Parser for `amount_by_count` datasets: `amounts`, quoted counts to quoted decimals."""

    kind = AMOUNT_BY_COUNT
    body_keys = frozenset({"amounts"})

    def parse(self, document: YamlNode) -> AmountByCount:
        """Build an AmountByCount from the dataset's `amounts`, in file order."""
        amounts = document.field("amounts")
        return AmountByCount(
            tuple(
                (YamlNode(key, node.where).parse_whole_number(), node.parse_decimal())
                for key, node in amounts.fields()
            )
        )
