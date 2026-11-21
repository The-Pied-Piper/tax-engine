"""The 2025 `ca-ab/medical_expense_dollar_limit` dataset, checked against Form AB428 (5009-c, 2025).

Form AB428 (CRA 5009-c-25e.txt): "Line 48: Enter whichever is less: $2,884 or the amount from line
47.". The dollar limit is a plain cap, not a credit: the `amount` kind, in `ca/cad`. The figure is a
dollars-and-cents figure, so it rounds half-up to the cent, the project's choice, as the form states
no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import (
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(
    alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
)
FAMILY = "ca-ab/medical_expense_dollar_limit"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-c/5009-c-25e.txt"


def test_2025_medical_expense_dollar_limit_is_2884() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("2884"))
    assert data.unit == alberta_units().unit("ca/cad")


def test_2025_medical_expense_dollar_limit_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_medical_expense_dollar_limit_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (CRA_FORM_TEXT,)
