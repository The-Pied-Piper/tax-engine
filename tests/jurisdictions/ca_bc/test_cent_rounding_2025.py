"""The 2025 `ca-bc/cent_rounding` dataset: the one rule shared by every British Columbia step
that rounds a dollars-and-cents box of BC428 (5010-C) and BC479 (5010-TC). It carries nothing but
its rule, half-up to the cent. It cites the BC428 and BC479 text."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/cent_rounding"


def test_2025_cent_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_cent_rounding_cites_the_bc428_and_bc479_text() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-c/5010-c-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-tc/5010-tc-25e.txt",
    )
