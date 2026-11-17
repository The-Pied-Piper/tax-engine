"""The 2026 `ca-ab/pension_income_amount_maximum` dataset, provisional until AB428 2026 appears.

The 2026 Form AB428 (CRA 5009-c) text is not yet published, so the figure is derived: the 2025
maximum of 1,719 (AB428 line 34, "maximum $1,719") x 1.02, Alberta's 2026 indexation factor as used
by the 2026 basic personal amount, is 1,753.38, rounded down to whole dollars as 1,753. It is a
`credit` dataset rounded half-up to the cent like 2025.
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
FAMILY = "ca-ab/pension_income_amount_maximum"
PROVISIONAL_PREFIX = "# Provisional:"
DERIVATION_PREFIX = "# Derivation:"


def test_2026_amount_is_1753() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("1753"))


def test_2026_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_amount_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    path = root / "parameters" / "pension_income_amount_maximum" / "2026.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()

    assert lines[0].startswith(PROVISIONAL_PREFIX)
    assert lines[1].startswith(DERIVATION_PREFIX)
    assert "1.02" in lines[1]
    assert "1,753" in lines[1]


def test_2025_amount_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("1719"))


def test_the_2026_amount_is_the_2025_amount_indexed_by_two_percent_rounded_down() -> None:
    indexed = D("1719") * D("1.02")

    assert indexed == D("1753.38")
    assert indexed.to_integral_value(rounding="ROUND_DOWN") == D("1753")
