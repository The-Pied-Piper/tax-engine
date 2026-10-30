"""The 2025 minimum for personal-use property on Schedule 3 Part 3, checked against CRA's Guide
T4037.

Guide T4037 2025, "Personal-use property" Example, p.24
(https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4037/t4037-25e.pdf): the chart prints
"Proceeds of disposition (whichever is more: selling price or $1,000)" and "Minus: ACB (whichever
is more: cost or $1,000) plus outlays and expenses". The $1,000 is a plain amount (the `amount`
kind), not a credit or a rate. Form 5000-S3 prints no $1,000 line, so the Guide is the only source.
The Guide states no rounding rule for the figure, so the dataset does not round (`rounding: none`).
No .txt of the Guide is published; the quotes are confirmed 2025 from the PDF.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import NO_ROUNDING

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FAMILY = "ca/personal_use_property_minimum"
T4037_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4037/t4037-25e.pdf"


def test_2025_minimum_is_1000() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1000"))
    # The Guide prints a whole-dollar $1,000 with no rounding rule: the amount is used as it is.
    assert data.rounding == NO_ROUNDING


def test_2025_minimum_cites_the_guide_t4037_pdf() -> None:
    # The printed text: "Proceeds of disposition (whichever is more: selling price or $1,000)".
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert T4037_PDF in data.sources
