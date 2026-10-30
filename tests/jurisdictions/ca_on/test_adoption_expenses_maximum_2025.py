"""The 2025 Ontario adoption expenses maximum, checked against CRA's forms.

Form ON428 (form 5006-C), "Line 23 and line 58330: Adoption expenses": the line 23 box, with no
maximum printed on the form. Form T2203 (2025), note (5) to its Ontario and Manitoba amounts:
"If you were a resident of Ontario, you can claim up to $15,551 of eligible expenses for each
child in the year the adoption is finalized or recognized under Ontario law." Two adoptive parents
can split the amount if the total combined claim for eligible expenses for each child is not more
than the amount before the split.

The dataset holds one amount, the per-child cap, rounded half-up to the cent (a dollars-and-cents
figure on the claim); it is a plain amount (the `amount` kind), not a claimed credit.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
ADOPTION_EXPENSES_MAXIMUM = "ca-on/adoption_expenses_maximum"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"
T2203_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2203/t2203-25e.pdf"


def test_2025_adoption_expenses_maximum_is_15551_for_each_child() -> None:
    data = SOURCE.get(ADOPTION_EXPENSES_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("15551"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_adoption_expenses_maximum_cites_the_form_and_the_t2203_note() -> None:
    assert SOURCE.get(ADOPTION_EXPENSES_MAXIMUM, 2025, AMOUNT).sources == (ON428_TEXT, T2203_PDF)
