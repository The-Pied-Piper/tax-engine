"""The 2025 `ca-ns/medical_expense_rate` dataset, Form NS428 (5003-c-25e.txt) line 40: "Applicable
rate 3%"

Rounds half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_packages,
    nova_scotia_parameter_parsers,
)

D = Decimal
# Nova Scotia is not in `registrations.JURISDICTIONS` yet, so the source is built over
# its own packages.
SOURCE = YamlParameterSource(
    nova_scotia_packages().roots(),
    nova_scotia_parameter_parsers(),
)
FAMILY = "ca-ns/medical_expense_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"


def test_2025_medical_expense_rate_is_0_03() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.03"))


def test_2025_medical_expense_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_medical_expense_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
