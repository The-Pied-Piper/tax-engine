"""The 2026 `ca/marginal_rate_rounding` dataset: the rule for a marginal rate that is a quotient
(the federal basic personal amount's fall per dollar of net income). It carries nothing but its
rule, the quotient rounded once, half-up to 0.0000001. No form prints a precision for it, so the
rule is the project's choice."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/marginal_rate_rounding"
YEAR = 2026


def test_2026_marginal_rate_rounding_is_half_up_to_seven_places() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.family == FAMILY
    assert data.tax_year == YEAR
    assert data.rounding == RoundTo(D("0.0000001"), RoundingMode.HALF_UP)
    assert data.rounding.apply(D("0.15985005")) == D("0.1598501")
    assert data.rounding.apply(D("0.15985004")) == D("0.1598500")


def test_2026_marginal_rate_rounding_names_its_sources() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources
