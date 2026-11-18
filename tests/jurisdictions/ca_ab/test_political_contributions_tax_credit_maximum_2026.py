"""The 2026 `ca-ab/political_contributions_tax_credit_maximum` dataset, provisional.

The 2026 Form AB428 (CRA 5009-c) text is not yet published, so the figure is carried forward: the
2025 maximum of 1,000 (AB428 line 72, "maximum $1,000") unchanged. It is a printed statutory
maximum, not a credit amount, and Alberta indexes only its credit amounts, so it has not moved. It
is a `credit` dataset rounded half-up to the cent like 2025.
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
FAMILY = "ca-ab/political_contributions_tax_credit_maximum"
PROVISIONAL_LINE = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_PREFIX = "# Derivation:"


def test_2026_amount_is_1000() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("1000"))


def test_2026_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_amount_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    path = root / "parameters" / "political_contributions_tax_credit_maximum" / "2026.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()

    assert lines[0] == PROVISIONAL_LINE
    assert lines[1].startswith(DERIVATION_PREFIX)
    assert "1,000" in lines[1]
    assert "index" in lines[1]


def test_2025_amount_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("1000"))
