"""The 2026 `ca-on/age_income_threshold` dataset, Worksheet ON428 (5006-d-25e.txt), Line 3 "Income
threshold 46,330.00": the 2025 printed figure indexed by 1.019 and rounded to the nearest dollar
(provisional), claimed whole (the `credit` kind). Rounds half-up to the cent, the project's
choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/age_income_threshold"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d/5006-d-25e.txt"
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: the 2025 figure (46,330) indexed by Ontario's index rate 1.019 in "
    "T4127 (Jan 2026) (46,330 x 1.019 = 47,210.27), rounded to the nearest dollar, "
    "halves up; T4127 (Jan and Jul 2026) does not print this figure and the 2026 form"
    " is not yet published, so it is unconfirmed."
)
YEAR = 2026


def test_2026_age_income_threshold_is_47210_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("47210.00"))


def test_2026_age_income_threshold_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_income_threshold_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT, T4127)


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    lines = (root / "parameters" / "age_income_threshold" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_age_income_threshold_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("46330.00"))
    assert data.sources == (CRA_FORM_TEXT,)
