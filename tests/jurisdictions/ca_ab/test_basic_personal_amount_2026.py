"""The 2026 `ca-ab/basic_personal_amount` dataset: the Alberta basic personal amount.

The figure is taken from T4127 Table 8.2 (Alberta, January 2026), because the 2026 Form AB428
(CRA 5009-c) text is not yet published; the dataset header says so. The amount is not income-tested,
so it is a `credit` dataset, rounded half-up to the cent like 2025. It is the 2025 amount of 22,323
indexed by 2%: 22,323 x 1.02 = 22,769.46, which T4127 prints as 22,769.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/basic_personal_amount"
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)


def test_2026_amount_is_22769() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("22769"))


def test_2026_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_amount_cites_t4127_only() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (T4127_URL,)


def test_2026_amount_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    lines = (root / "parameters" / "basic_personal_amount" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation:")


def test_2025_amount_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("22323"))


def test_the_2026_amount_is_the_2025_amount_indexed_by_two_percent() -> None:
    indexed = D("22323") * D("1.02")

    assert indexed == D("22769.46")
    assert indexed.to_integral_value(rounding="ROUND_DOWN") == D("22769")
    assert abs(indexed - D("22769")) < D("1")
