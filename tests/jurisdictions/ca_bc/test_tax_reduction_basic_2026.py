"""The 2026 `ca-bc/tax_reduction_basic` dataset (provisional): 690 from T4127 (July 2026).

Not the January edition's indexed 575 and not the prorated payroll figure 805."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE
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
FAMILY = "ca-bc/tax_reduction_basic"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-jul-26e.pdf",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jul 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_PREFIX = "# Derivation: "


def _file_lines() -> list[str]:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    return (root / "parameters" / "tax_reduction_basic" / "2026.yaml").read_text().splitlines()


def test_2026_tax_reduction_basic_is_690() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(D("690"))


def test_2026_tax_reduction_basic_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_tax_reduction_basic_cites_its_source() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES
    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file_lines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith(DERIVATION_PREFIX)


def test_2025_tax_reduction_basic_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(D("562"))


def test_the_reduction_ends_at_net_income_44_952() -> None:
    base = SOURCE.get("ca-bc/tax_reduction_base_amount", 2026, CREDIT).values
    rate = SOURCE.get("ca-bc/tax_reduction_rate", 2026, RATE).values
    basic = SOURCE.get(FAMILY, 2026, CREDIT).values

    end = base.amount + basic.amount / rate.value

    assert int(end) == 44952
