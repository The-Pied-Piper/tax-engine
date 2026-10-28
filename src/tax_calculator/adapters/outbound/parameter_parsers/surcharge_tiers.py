"""Parses `surcharge_tiers` datasets: a list of {threshold, rate, maximum?} into SurchargeTiers."""

from __future__ import annotations

from tax_calculator.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_calculator.adapters.outbound.yaml_support import YamlNode
from tax_calculator.domain.errors import DomainError, InvalidSurchargeTiersError
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)

_TIER_KEYS = frozenset({"threshold", "rate"})
_OPTIONAL_TIER_KEYS = frozenset({"maximum"})


@parameter_parser
class SurchargeTiersParser:
    """Parser for `surcharge_tiers` datasets: a list of thresholds and rates, each optionally
    with a maximum."""

    kind = SURCHARGE_TIERS
    body_keys = frozenset({"tiers"})

    def parse(self, document: YamlNode) -> SurchargeTiers:
        """Build SurchargeTiers from the dataset's `tiers` list of {threshold, rate, maximum?}."""
        return SurchargeTiers(tuple(self._tier(entry) for entry in document.field("tiers").items()))

    @staticmethod
    def _tier(entry: YamlNode) -> SurchargeTier:
        fields = entry.require_mapping(_TIER_KEYS, optional=_OPTIONAL_TIER_KEYS)
        threshold = fields.field("threshold").parse_decimal()
        rate = fields.field("rate").parse_decimal()
        maximum_node = fields.optional_field("maximum")
        maximum = None if maximum_node is None else maximum_node.parse_decimal()
        try:
            return SurchargeTier(threshold=threshold, rate=Rate(rate), maximum=maximum)
        except DomainError as exc:
            # Name the tier: the value objects do not know where in the list they sit.
            raise InvalidSurchargeTiersError(f"{entry.where}: {exc}") from exc
