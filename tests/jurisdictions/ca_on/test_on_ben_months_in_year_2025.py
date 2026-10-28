"""The 2025 months in the year of Form ON-BEN Part B, checked against CRA's form.

Form ON-BEN (form 5006-TG, 2025) Part B column 3 "Number of months resident in 2025": the months of
one row may be at most the 12 months of a year. The form does not print the 12; the
dataset is a constant claimed whole (the `credit` kind), as the northern residents' days in the
year is.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
ON_BEN_MONTHS_IN_YEAR = "ca-on/on_ben_months_in_year"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-tg/5006-tg-25e.txt"


def test_2025_on_ben_months_in_year_is_12() -> None:
    data = SOURCE.get(ON_BEN_MONTHS_IN_YEAR, 2025, CREDIT)

    assert data.values == Credit(amount=D("12"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
