"""The 2026 `ca-nl/venture_capital_credit_lifetime_maximum` dataset, provisional.

Pins the 2026 figure, rounding, sources, tax year, and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/venture_capital_credit_lifetime_maximum"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-pc/5001-pc-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 guide text named in sources; to be confirmed against "
    "the 2026 guide text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; the 2026 guide is not yet "
    "published."
)


def test_2026_venture_capital_credit_lifetime_maximum_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("75000"))


def test_2026_venture_capital_credit_lifetime_maximum_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_venture_capital_credit_lifetime_maximum_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_venture_capital_credit_lifetime_maximum_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    lines = (
        (root / "parameters" / "venture_capital_credit_lifetime_maximum" / "2026.yaml")
        .read_text()
        .splitlines()
    )

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_venture_capital_credit_lifetime_maximum_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("75000"))
