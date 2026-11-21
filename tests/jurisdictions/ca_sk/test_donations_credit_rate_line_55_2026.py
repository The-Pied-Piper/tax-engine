"""The 2026 `ca-sk/donations_credit_rate_line_55` dataset, Form SK428 (5008-c-25e.txt) line 55:
"Amount from line 14 of your federal Schedule 9 multiplied by 14.5% ="

Rounds half-up to the cent, the project's choice, as the form states no rounding rule.

Provisional: the 2026 Form SK428 is not published, so the 2025 printed figure is
carried forward.
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


def test_2026_donations_credit_rate_line_55_is_0_145() -> None:
    data = SOURCE.get("ca-sk/donations_credit_rate_line_55", 2026, RATE)

    assert data.values == Rate(D("0.145"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_donations_credit_rate_line_55_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-sk")]
    lines = (
        (root / "parameters" / "donations_credit_rate_line_55" / "2026.yaml")
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
