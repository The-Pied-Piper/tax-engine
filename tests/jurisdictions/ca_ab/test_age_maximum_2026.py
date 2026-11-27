"""The 2026 `ca-ab/age_maximum` dataset, Worksheet AB428 (5009-d-25e.txt), Line 1 "Maximum amount
6,221.00" (2025 text) indexed by Alberta's 2026 factor 1.02 (6,345.42, nearest dollar, halves up:
6,345.00), provisional, claimed whole (the `credit` kind). Rounds half-up to the cent, the
project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/age_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-d/5009-d-25e.txt"
YEAR = 2026
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 2025 amount 6,221 x 1.02 (Alberta's 2026 indexation factor, as for its 2026 "
    "basic personal amount) = 6,345.42, rounded to the nearest dollar, halves up, = 6,345."
)


def _file_text() -> str:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    return (root / "parameters" / "age_maximum" / "2026.yaml").read_text()


def test_2026_age_maximum_is_6345_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("6345.00"))


def test_2026_age_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_age_maximum_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("6221.00"))


def test_the_2026_figure_is_the_2025_amount_times_1_02_to_the_nearest_dollar() -> None:
    indexed = D("6221") * D("1.02")

    assert indexed == D("6345.42")
    assert indexed.quantize(D("1"), rounding=ROUND_HALF_UP) == D("6345")
