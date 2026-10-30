"""Parsers for the kind-specific part of YAML parameter datasets.

Each parser handles one parameter kind: the keys it adds to a dataset file and
how to turn them into that kind's values. Parsers register themselves with
`@parameter_parser` when their module is imported, and YamlParameterSource looks them up by kind
in a ParameterParserRegistry. This package imports every parser module, so importing it fills the
shared registry; adding a kind means adding a parser and importing it here.
"""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers import (
    amount,
    amount_by_count,
    brackets,
    claim_reduction,
    class_rates,
    conditions,
    contribution_tier,
    credit,
    factor,
    fraction,
    parser,
    rate,
    rate_table,
    registry,
    rounding_only,
    surcharge_tiers,
    taper,
    threshold_rate,
    year_amounts,
)
from tax_engine.adapters.outbound.parameter_parsers.parser import ParameterParser

__all__ = [
    "ParameterParser",
    "amount",
    "amount_by_count",
    "brackets",
    "claim_reduction",
    "class_rates",
    "conditions",
    "contribution_tier",
    "credit",
    "factor",
    "fraction",
    "parser",
    "rate",
    "rate_table",
    "registry",
    "rounding_only",
    "surcharge_tiers",
    "taper",
    "threshold_rate",
    "year_amounts",
]
