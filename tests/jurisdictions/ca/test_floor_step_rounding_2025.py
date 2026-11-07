"""The 2025 rounding datasets of the federal floor steps (`core/subtract_not_below_zero`), one per
form line: Schedule 8 lines 4, 5 and 7, T2204 lines 7, 8 and 13, and T1 taxable income lines 23600
and 26000.

A floor step ("if negative, enter 0") takes the difference of two lines and rounds it by its own
dataset's rule, so each line prints to the cent. Each dataset is a `rounding_only` dataset that
carries nothing but its rule, half-up to the cent, the rule of the dollars-and-cents boxes.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILIES = (
    "ca/schedule_8_line_4_rounding",
    "ca/schedule_8_line_5_rounding",
    "ca/schedule_8_line_7_rounding",
    "ca/t2204_line_7_rounding",
    "ca/t2204_line_8_rounding",
    "ca/t2204_line_13_rounding",
    "ca/t1_taxable_income_line_23600_rounding",
    "ca/t1_taxable_income_line_26000_rounding",
)


@pytest.mark.parametrize("family", FAMILIES)
def test_2025_floor_step_rounding_is_half_up_to_the_cent(family: str) -> None:
    data = SOURCE.get(family, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)
