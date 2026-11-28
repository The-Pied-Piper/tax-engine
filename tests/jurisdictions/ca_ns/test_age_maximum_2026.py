"""The 2026 `ca-ns/age_maximum` dataset, Worksheet NS428 (5003-d-25e.txt), Line 1 "Maximum amount
5,734.00": the 2025 printed figure indexed by 1.016 and rounded to the nearest dollar
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
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_packages,
    nova_scotia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    nova_scotia_packages().roots(),
    nova_scotia_parameter_parsers(),
)
FAMILY = "ca-ns/age_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-d/5003-d-25e.txt"
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: the 2025 figure (5,734) indexed by Nova Scotia's index rate 1.016 in "
    "T4127 (Jan 2026) (5,734 x 1.016 = 5,825.74), rounded to the nearest dollar, "
    "halves up; T4127 (Jan and Jul 2026) does not print this figure and the 2026 form"
    " is not yet published, so it is unconfirmed. Risks: no CRA text in the repo says Nova "
    "Scotia indexes this amount; the indexing is inferred from Nova Scotia's other amounts, "
    "which it indexes by 1.016 for 2026 (T4127 Table 8.2), after this amount was held at "
    "4,141 from 2016 to 2024 and raised to 5,734 in 2025. The income threshold (30,828) is "
    "held unchanged, as it was in every year from 2016 to 2025; if Nova Scotia indexes it "
    "for 2026, the reduction start "
    "and the zero point both shift."
)
YEAR = 2026


def test_2026_age_maximum_is_5826_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("5826.00"))


def test_2026_age_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT, T4127)


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-ns")]
    lines = (root / "parameters" / "age_maximum" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_age_maximum_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("5734.00"))
    assert data.sources == (CRA_FORM_TEXT,)
