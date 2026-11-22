"""The 2026 `ca-ab/dividend_tax_credit_worksheet_rate_line_2` dataset, carried forward from 2025.

Worksheet 5009-D (2025) line 2: "... multiplied by 8.12% =". Provisional: the 2026 form is not
published, so the 2025 printed figure, rounding and source are carried forward and the file says so.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)
FAMILY = "ca-ab/dividend_tax_credit_worksheet_rate_line_2"


def test_2026_rate_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, RATE)
    original = SOURCE.get(FAMILY, 2025, RATE)

    assert carried.values == Rate(D("0.0812"))
    assert carried.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert carried.values == original.values
    assert carried.sources == original.sources


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-ab")]
    lines = (
        (root / "parameters" / "dividend_tax_credit_worksheet_rate_line_2" / "2026.yaml")
        .read_text()
        .splitlines()
    )

    assert lines[0] == (
        "# Provisional: taken from the 2025 form text named in sources; to be confirmed against "
        "the 2026 form text when CRA publishes it."
    )
    assert lines[1] == (
        "# Derivation: carried forward unchanged from the 2025 file; the 2026 form is not yet "
        "published."
    )
