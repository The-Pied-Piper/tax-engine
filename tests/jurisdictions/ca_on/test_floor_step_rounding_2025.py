"""The 2025 rounding datasets of the Ontario floor steps (`core/subtract_not_below_zero`), one per
form line: ON428 lines 4, 53, 61, 65, 71, 80, 81, 83, 86 and 88, and ON428-A lines 17 and 20.

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
    "ca-on/on428_line_4_rounding",
    "ca-on/on428_line_53_rounding",
    "ca-on/on428_line_61_rounding",
    "ca-on/on428_line_65_rounding",
    "ca-on/on428_line_71_rounding",
    "ca-on/on428_line_80_rounding",
    "ca-on/on428_line_81_rounding",
    "ca-on/on428_line_83_rounding",
    "ca-on/on428_line_86_rounding",
    "ca-on/on428_line_88_rounding",
    "ca-on/on428_a_line_17_rounding",
    "ca-on/on428_a_line_20_rounding",
)


@pytest.mark.parametrize("family", FAMILIES)
def test_2025_floor_step_rounding_is_half_up_to_the_cent(family: str) -> None:
    data = SOURCE.get(family, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)
