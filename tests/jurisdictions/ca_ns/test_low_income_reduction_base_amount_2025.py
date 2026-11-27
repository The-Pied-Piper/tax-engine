"""The 2025 `ca-ns/low_income_reduction_base_amount` dataset, against Form NS428 (5003-C, 2025).

Form NS428: line 80: "Base amount 15,000.00". The printed figure is taken as printed, so the
dataset holds it whole, the `credit` kind.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ns.ns428_credits_support import parameter_source

D = Decimal
FAMILY = "ca-ns/low_income_reduction_base_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"


def test_2025_low_income_reduction_base_amount_is_15000() -> None:
    assert parameter_source().get(FAMILY, 2025, CREDIT).values == Credit(amount=D("15000"))


def test_2025_low_income_reduction_base_amount_rounds_half_up_to_the_cent() -> None:
    data = parameter_source().get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_low_income_reduction_base_amount_cites_the_form() -> None:
    assert parameter_source().get(FAMILY, 2025, CREDIT).sources == (CRA_FORM_TEXT,)
