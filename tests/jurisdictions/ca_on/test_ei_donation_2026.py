"""The 2026 EI maximum insurable earnings and donation high-income threshold, from T4127.

CRA T4127, 122nd Edition (effective January 1, 2026): Table 8.7 "Employment Insurance 2026 rates
and amounts", row "Canada except QC", maximum annual insurable earnings $68,900.00 (Schedule 13
line 5); Table 8.1, the federal 5th bracket threshold $258,482 (Schedule 9, same relation as the
2025 figure 253,414). Both are PRINTED, and the files are provisional until the 2026 form text
is published; the second line of each states the derivation.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
EI_MAXIMUM = "ca/ei_maximum_insurable_earnings"
DONATION_THRESHOLD = "ca/donation_high_income_threshold"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_PREFIX = "# Derivation:"
FIGURES = [(EI_MAXIMUM, "68900.00"), (DONATION_THRESHOLD, "258482.00")]


@pytest.mark.parametrize(("family", "amount"), FIGURES)
def test_2026_figure_is_the_printed_amount(family: str, amount: str) -> None:
    data = SOURCE.get(family, 2026, CREDIT)

    assert data.values == Credit(amount=D(amount))
    assert data.tax_year == 2026


@pytest.mark.parametrize(("family", "amount"), FIGURES)
def test_2026_figure_rounds_half_up_to_the_cent(family: str, amount: str) -> None:
    assert SOURCE.get(family, 2026, CREDIT).rounding == CENT


@pytest.mark.parametrize(("family", "amount"), FIGURES)
def test_2026_figure_cites_t4127(family: str, amount: str) -> None:
    assert T4127 in SOURCE.get(family, 2026, CREDIT).sources


@pytest.mark.parametrize(("family", "amount"), FIGURES)
def test_2026_file_starts_with_the_provisional_line_then_a_derivation_line(
    family: str, amount: str
) -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (root / "parameters" / family.split("/")[1] / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith(DERIVATION_PREFIX)
    assert "T4127" in lines[1]
