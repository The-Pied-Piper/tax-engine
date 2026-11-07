"""The 2025 `ca/cent_rounding` dataset: the one rule shared by the federal floor steps
(`core/subtract_not_below_zero`), Schedule 8 lines 4, 5 and 7, Schedule 6 line 18, T2204 lines 7,
8 and 13, and T1 taxable income lines 23600 and 26000. It carries nothing but its rule, half-up to
the cent, the rule of the dollars-and-cents boxes. It cites the Schedule 8, Schedule 6, T2204 and
T1 text."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/cent_rounding"


def test_2025_cent_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_cent_rounding_cites_the_schedule_8_schedule_6_t2204_and_t1_text() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2204/t2204-25e.pdf",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-r/5006-r-25e.txt",
    )
