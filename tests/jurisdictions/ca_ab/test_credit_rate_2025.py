"""The 2025 rate of `ca-ab/credit_rate`, checked against Form AB428 (2025), line 53.

Form AB428 (5009-c-25e.txt), line 53: "Alberta non-refundable tax credit rate 8%". The printed
percentage is a rate of 0.08, read by line 54 (and by Worksheet AB428 line 4); both are
dollars-and-cents lines, so the product rounds half-up to the cent. Worksheet AB428
(5009-d-25e.txt), line 4, prints the same "Alberta non-refundable tax credit rate 8%" and reads the
same figure, so the dataset cites both form texts, Form AB428 first.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/credit_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-c/5009-c-25e.txt"
CRA_WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-d/5009-d-25e.txt"


def test_2025_credit_rate_is_8_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.08"))


def test_2025_credit_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_credit_rate_cites_the_form_ab428_and_worksheet_ab428_texts() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT, CRA_WORKSHEET_TEXT)
