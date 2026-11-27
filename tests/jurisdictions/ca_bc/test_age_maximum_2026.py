"""The 2026 `ca-bc/age_maximum` dataset, Worksheet BC428
(5010-d-25e.txt), Line 1 "Maximum amount 5,799.00" on the 2025 form:
that figure indexed by 1.022 to 5,927.00 (provisional),
claimed whole (the `credit` kind). Rounds half-up to the cent, the project's choice, as the form
states no rounding rule.
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
FAMILY = "ca-bc/age_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-d/5010-d-25e.txt"
YEAR = 2026
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: the 2025 figure 5,799 indexed by BC's 2026 index rate 1.022 "
    "(T4127 Table 8.2; BC's basic personal amount moved 12,932 to 13,216 by the "
    "same factor): 5,799 x 1.022 = 5,926.58, rounded to the nearest dollar, halves "
    "up, 5,927. T4127 does not print this figure and the 2026 form is not yet "
    "published, so it is unconfirmed."
)


def test_2026_age_maximum_is_5927_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("5927.00"))


def test_2026_age_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2026_age_maximum_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    lines = (root / "parameters" / "age_maximum" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_age_maximum_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("5799.00"))


def test_the_2026_age_maximum_is_the_2025_figure_indexed_by_one_point_zero_two_two() -> None:
    indexed = D("5799") * D("1.022")

    assert indexed.quantize(D("1"), rounding="ROUND_HALF_UP") == D("5927")
