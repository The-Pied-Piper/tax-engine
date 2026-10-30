"""The 2025 amount of `ca/tuition_transfer_maximum_per_student`, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 104 and line 32400 "Tuition amount transferred from a child or
grandchild", and the T1 guide (form 5000-G, 2025): "The maximum amount each student can transfer to
you is $5,000 minus the amount that they used to reduce their own tax payable." The $5,000 is a
per-unit amount, times the number of students the transfer comes from (a count).

The dataset holds one amount, rounded half-up to the cent; it is a plain amount (the `amount`
kind), not a claimed credit.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
PER_STUDENT_MAXIMUM = "ca/tuition_transfer_maximum_per_student"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5000-g/5000-g-25e.txt"


def test_2025_transfer_maximum_per_student_is_5000() -> None:
    data = SOURCE.get(PER_STUDENT_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("5000.00"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
