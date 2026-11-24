"""The 2026 `ca/take_home_average_rate_rounding` dataset: the rule for the take-home average rate,
total deductions (income tax, CPP, CPP2, EI) over the salary. It carries nothing but its rule, the
exact quotient rounded once, half-up to 0.0001, so a rate such as 0.1598 prints as 15.98%. No form
prints this figure or a precision for it, so the rule is the project's choice."""

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
FAMILY = "ca/take_home_average_rate_rounding"
YEAR = 2026


def test_2026_average_rate_rounding_is_half_up_to_four_places() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.family == FAMILY
    assert data.tax_year == YEAR
    assert data.rounding == RoundTo(D("0.0001"), RoundingMode.HALF_UP)
    assert data.rounding.apply(D("0.15985")) == D("0.1599")
    assert data.rounding.apply(D("0.159849")) == D("0.1598")


def test_2026_average_rate_rounding_names_its_sources() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources
