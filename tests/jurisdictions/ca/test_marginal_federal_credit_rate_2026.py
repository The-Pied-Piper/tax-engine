"""The 2026 `ca/marginal_federal_credit_rate` dataset: T1 line 114 "Federal non-refundable tax
credit rate 14%", applied to the CPP base and EI contributions (T1 lines 30800 and 31200).
It holds the printed rate and rounds nothing."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE
from tax_engine.domain.parameters.rounding import NO_ROUNDING

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/marginal_federal_credit_rate"
YEAR = 2026


def test_2026_marginal_federal_credit_rate_holds_the_printed_rate_and_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, YEAR, RATE)

    assert data.kind is RATE
    assert data.family == FAMILY
    assert data.tax_year == YEAR
    assert data.values.value == D("0.14")
    assert data.rounding == NO_ROUNDING
    assert data.rounding.apply(D("0.123456789")) == D("0.123456789")
    assert data.sources
