"""The 2025 `ca-ns/low_income_reduction_maximum` dataset, checked against Form NS428 (5003-C, 2025).

Form NS428: line 74: "Add lines 71 to 73. (maximum $600)". The printed maximum is a plain cap, not a
credit: the `amount` kind, in `ca/cad`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ns.ns428_credits_support import parameter_source

D = Decimal
FAMILY = "ca-ns/low_income_reduction_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"


def test_2025_low_income_reduction_maximum_is_600() -> None:
    assert parameter_source().get(FAMILY, 2025, AMOUNT).values == Amount(D("600"))


def test_2025_low_income_reduction_maximum_rounds_half_up_to_the_cent() -> None:
    data = parameter_source().get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_low_income_reduction_maximum_cites_the_form() -> None:
    assert parameter_source().get(FAMILY, 2025, AMOUNT).sources == (CRA_FORM_TEXT,)
