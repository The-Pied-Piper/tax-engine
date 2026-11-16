"""The 2026 `ca-bc/basic_personal_amount` dataset: the British Columbia basic personal amount.

The figure is taken from T4127 Table 8.2 (British Columbia, July 2026), because the 2026 Form BC428
(CRA 5010-c) text is not yet published; the dataset header says so. The amount is not income-tested,
so it is a `credit` dataset, rounded half-up to the cent like 2025. It is the 2025 amount of 12,932
indexed by BC's own 2.2%: 12,932 x 1.022 = 13,216.50, which T4127 prints as 13,216.
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

D = Decimal
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/basic_personal_amount"
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-jul-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jul 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in T4127 Table 8.2, British Columbia row (13,216); no "
    "rounding applied here."
)


def test_2026_amount_is_13216() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("13216"))


def test_2026_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_amount_cites_the_july_t4127_only() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (T4127_URL,)


def test_2026_amount_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    lines = (root / "parameters" / "basic_personal_amount" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_amount_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("12932"))


def test_the_2026_amount_is_the_2025_amount_indexed_by_two_point_two_percent() -> None:
    indexed = D("12932") * D("1.022")

    assert indexed == D("13216.504")
    assert indexed.to_integral_value(rounding="ROUND_DOWN") == D("13216")
    assert abs(indexed - D("13216")) < D("1")
