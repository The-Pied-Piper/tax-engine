"""The 2025 `ca-on/rate_rounding` dataset: the rule of the Ontario return summary's average income
tax rate (`core/divide`, total payable over salary). It carries nothing but its rule, half-up to
0.0001: a rate as a fraction, so 0.1642 prints as 16.42%. The forms print no precision for this
figure, so the precision is the project's choice, recorded in the dataset header like
`ca-on/cent_rounding`. The 2025 dataset serves the 2025 take-home."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/rate_rounding"


def test_2025_rate_rounding_is_half_up_to_ten_thousandths() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.0001"), RoundingMode.HALF_UP)


def test_2025_rate_rounding_names_its_sources() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.tax_year == 2025
    assert data.sources
