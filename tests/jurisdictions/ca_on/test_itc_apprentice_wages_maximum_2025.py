"""The 2025 cap on an apprentice's eligible salary and wages for the apprenticeship job creation
tax credit, checked against CRA's Form T2038(IND).

2025 Form T2038(IND), Part B, Table 1 "Calculation of total Apprenticeship job creation tax credit",
column 3 "The lesser of eligible salary and wages** payable in the year or $20,000.": each
apprentice's row takes the lesser of their eligible salary and wages and $20,000, and the total of
column 3 is multiplied by 0.10 (Part B amount D, not this dataset). The $20,000 is a plain amount
(the `amount` kind), not a credit. Column 3 is a dollars-and-cents box, so each row's lesser is
rounded half-up to the cent, the rule of the dataset.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
FAMILY = "ca/itc_apprentice_wages_maximum"
T2038_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2038-ind/t2038-ind-25e.pdf"


def test_2025_maximum_is_20000() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("20000"))
    # T2038(IND) Part B Table 1 column 3, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_cites_the_t2038_ind_form() -> None:
    # The form text is "The lesser of eligible salary and wages payable in the year or $20,000."
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert T2038_PDF in data.sources
