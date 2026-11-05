"""Parses `claim_reduction` datasets: a rate, a ceiling and an optional maximum."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parser import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.rate import Rate
from tax_engine.jurisdictions.ca.parameter_shapes.claim_reduction import (
    CLAIM_REDUCTION,
    ClaimReduction,
)


@parameter_parser
class ClaimReductionParser:
    """Parser for `claim_reduction` datasets: `rate` and `ceiling`, and `maximum` if stated."""

    kind = CLAIM_REDUCTION
    body_keys = frozenset({"rate", "ceiling"})
    optional_keys = frozenset({"maximum"})

    def parse(self, document: YamlNode) -> ClaimReduction:
        """Build a ClaimReduction from the dataset's quoted decimals `rate`, `ceiling` and,
        when present, `maximum`."""
        maximum = document.optional_field("maximum")
        return ClaimReduction(
            Rate(document.field("rate").parse_decimal()),
            document.field("ceiling").parse_decimal(),
            None if maximum is None else maximum.parse_decimal(),
        )
