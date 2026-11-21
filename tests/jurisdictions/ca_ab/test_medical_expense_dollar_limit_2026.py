"""The 2026 `ca-ab/medical_expense_dollar_limit` dataset, provisional.

Pins the 2026 figure, rounding, sources, tax year and the header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import (
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)

D = Decimal
SOURCE = YamlParameterSource(
    alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
)
FAMILY = "ca-ab/medical_expense_dollar_limit"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-c/5009-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: assumes the amount is indexed by the 2% factor that moves the 2026 basic "
    "personal amount (22,323 x 1.02 = 22,769.46, printed as 22,769); 2,884 x 1.02 = 2,941.68, "
    "rounded to the nearest dollar, a half going up, to 2,942. Unconfirmed: no source states "
    "Alberta's 2026 medical expenses dollar limit."
)


def test_2026_medical_expense_dollar_limit_value() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(D("2942"))


def test_2026_medical_expense_dollar_limit_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_medical_expense_dollar_limit_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.sources == SOURCES


def test_2026_medical_expense_dollar_limit_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    lines = (
        (root / "parameters" / "medical_expense_dollar_limit" / "2026.yaml")
        .read_text()
        .splitlines()
    )

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_medical_expense_dollar_limit_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("2884"))
