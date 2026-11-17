"""The 2026 `ca-bc/political_contribution_tax_credit_maximum` dataset, carried from 2025.

The 2026 Form BC428 (CRA 5010-c) text is not yet published and no source states a change, so the
2026 file repeats the 2025 maximum of 500 (BC428 line 84, "maximum $500") and rounding, cites the
2025 form text, and says so in its header.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/political_contribution_tax_credit_maximum"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_PREFIX = "# Derivation:"


def test_2026_amount_is_the_2025_amount_of_500() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=Decimal("500"))


def test_2026_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2026_amount_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_2026_amount_cites_the_2025_form_text() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-c/5010-c-25e.txt",
    )


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    path = root / "parameters" / "political_contribution_tax_credit_maximum" / "2026.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith(DERIVATION_PREFIX)


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, CREDIT)
    original = SOURCE.get(FAMILY, 2025, CREDIT)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
