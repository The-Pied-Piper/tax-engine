"""The rounding rule of the Form T1032 ratios, `ca/t1032_rounding`, for the lines of Form T1032 that
divide one amount by another and multiply the quotient (lines 18, 29 and 36).

Form T1032 E (25) states no rounding rule for these lines. Each is a dollars-and-cents box, so the
product rounds half-up to the cent, once, the owner's decision, the repo convention, as the
`rounding_only` dataset of Form T1206 does.

Form T1032 is at https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
ROUNDING = "ca/t1032_rounding"
T1032_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT
    assert data.sources == (T1032_TXT,)
