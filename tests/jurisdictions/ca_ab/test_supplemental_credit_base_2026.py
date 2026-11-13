"""The 2026 `ca-ab/supplemental_credit_base` dataset: the Alberta supplemental credit base amount.

The figure is taken from T4127 (Alberta, January 2026), because the 2026 Worksheet AB428
(CRA 5009-d) is not yet published; the dataset header says so. The amount is not income-tested,
so it is a `credit` dataset, rounded half-up to the cent like 2025. It is the 2025 amount of 4,800
indexed by 2%: 4,800 x 1.02 = 4,896.00, which T4127 prints as 4,896.
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
FAMILY = "ca-ab/supplemental_credit_base"
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in T4127 (4,896), which agrees with the 2025 amount of "
    "4,800 indexed by 2% (4,800 x 1.02 = 4,896.00); no rounding applied here."
)


def test_2026_amount_is_4896() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("4896"))


def test_2026_amount_is_a_plain_credit_not_income_tested() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert isinstance(data.values, Credit)
    assert data.kind == CREDIT


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
    lines = (
        (root / "parameters" / "supplemental_credit_base" / "2026.yaml").read_text().splitlines()
    )

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_amount_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("4800"))


def test_the_2026_amount_is_the_2025_amount_indexed_by_two_percent_exactly() -> None:
    assert D("4800") * D("1.02") == D("4896.00")
