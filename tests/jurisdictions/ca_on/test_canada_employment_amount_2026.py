"""The 2026 Canada employment amount cap, taken from T4127 (122nd edition, January 2026).

T4127 Table 8.2 "Other rates and amounts for 2026", row Federal: CEA 1,501; formula K4 =
0.14 x $1,501. A plain amount (the `amount` kind) as in 2025, rounded half-up to the cent. The
dataset is provisional until the 2026 T1 (5000-R) is published.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.core.capabilities.capped_amount import CappedAmount

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)
FAMILY = "ca/canada_employment_amount"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"

# Made up for this test and not registered: the income the cap applies to, and its capped amount.
INCOME = AmountKind("ex/income")
CAPPED = AmountKind("ex/capped")


def test_2026_cap_is_1501() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(D("1501"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_cap_cites_t4127() -> None:
    assert SOURCE.get(FAMILY, 2026, AMOUNT).sources == (T4127_URL,)


def test_2026_cap_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (
        (root / "parameters" / "canada_employment_amount" / "2026.yaml").read_text().splitlines()
    )

    assert lines[0] == PROVISIONAL_HEADER


def test_2025_cap_is_unchanged() -> None:
    assert SOURCE.get(FAMILY, 2025, AMOUNT).values == Amount(D("1471"))


@pytest.mark.parametrize(
    ("income", "capped"),
    [
        # A $70,000 salary: well above the cap.
        ("70000", "1501"),
        # At the cap, and a cent above it.
        ("1501", "1501"),
        ("1501.01", "1501"),
        # Below the cap the income itself is the lesser.
        ("1000.50", "1000.50"),
        ("0", "0"),
    ],
)
def test_caps_employment_income(income: str, capped: str) -> None:
    capability = CappedAmount(SOURCE.get(FAMILY, 2026, AMOUNT), INCOME, CAPPED)

    result = capability.compute((Artifact(INCOME, D(income)),))

    assert result.outputs == (Artifact(CAPPED, D(capped)),)
