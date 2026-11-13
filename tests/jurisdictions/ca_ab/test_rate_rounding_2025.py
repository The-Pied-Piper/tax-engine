"""The 2025 `ca-ab/rate_rounding` dataset: the rule of the Alberta return summary's average income
tax rate (`core/divide`, total payable over salary). It carries nothing but its rule, half-up to
0.0001: a rate as a fraction, so 0.1598 prints as 15.98%. The forms print no precision for this
figure, so the precision is the project's choice, recorded in the dataset header."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/rate_rounding"
YEAR = 2025


def test_the_rate_rounding_is_half_up_to_ten_thousandths() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.0001"), RoundingMode.HALF_UP)
    assert data.tax_year == YEAR


def test_the_rate_rounding_names_its_sources() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources
