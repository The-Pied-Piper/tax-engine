"""The 2026 `ca-on/donations_credit_rate_line_48` dataset, Form ON428 line 48:
"... multiplied by 11.16% ="

The figure is a dollars-and-cents figure, so it rounds half-up to the cent, the project's choice,
as the form states no rounding rule.

Provisional: the 2026 Form ON428 is not published, so the 2025 printed figure is carried forward.
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


def test_2026_donations_credit_rate_line_48_is_0_1116() -> None:
    data = SOURCE.get("ca-on/donations_credit_rate_line_48", 2026, RATE)

    assert data.values == Rate(D("0.1116"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_donations_credit_rate_line_48_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    lines = (
        (root / "parameters" / "donations_credit_rate_line_48" / "2026.yaml")
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
