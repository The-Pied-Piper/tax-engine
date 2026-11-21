"""The 2026 `ca-mb/donations_credit_rate_line_54` dataset, from Form MB428 (5007-c-25e.txt) line 54:
"Line 54: Amount from line 13 of your
federal Schedule 9 multiplied by 10.8% ="

The figure rounds half-up to the cent, the project's choice, as the form states no rounding rule.

Provisional: the 2026 Form MB428 is not published, so the 2025 printed figure is carried forward.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/donations_credit_rate_line_54"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt"


def test_2026_donations_credit_rate_line_54_value_and_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.108"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = manitoba_packages().roots()[Namespace("ca-mb")]
    lines = (
        (root / "parameters" / "donations_credit_rate_line_54" / "2026.yaml")
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


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, RATE)
    original = SOURCE.get(FAMILY, 2025, RATE)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
    assert carried.sources == original.sources
