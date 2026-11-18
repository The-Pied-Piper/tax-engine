"""The 2025 `ca-nl/eligible_dependant_amount_maximum` dataset, checked against Form NL428 (5001-C,
2025).

Form NL428 (CRA 5001-c-25e.txt): "Line 23 and line 58160: Line 21 minus line 22 (if negative, enter
"0") (maximum $9,043) =". The maximum is a plain cap, not a credit: the `amount` kind, in `ca/cad`.
The figure is a dollars-and-cents figure, so it rounds half-up to the cent, the project's choice,
as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
# Newfoundland and Labrador is not in `registrations.JURISDICTIONS` yet, so the source is built over
# its own packages.
SOURCE = YamlParameterSource(
    newfoundland_packages().roots(),
    newfoundland_parameter_parsers(),
    newfoundland_units(),
)
FAMILY = "ca-nl/eligible_dependant_amount_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt"


def test_2025_eligible_dependant_amount_maximum_is_9043() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("9043"))
    assert data.unit == newfoundland_units().unit("ca/cad")


def test_2025_eligible_dependant_amount_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_eligible_dependant_amount_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (CRA_FORM_TEXT,)
