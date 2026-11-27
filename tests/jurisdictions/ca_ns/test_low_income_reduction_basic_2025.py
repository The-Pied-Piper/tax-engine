"""The 2025 `ca-ns/low_income_reduction_basic` dataset, against Form NS428 (5003-C, 2025).

Form NS428: line 71: "Basic reduction Claim $300". The printed figure is taken as printed, so the
dataset holds it whole, the `credit` kind.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ns.ns428_credits_support import parameter_source

D = Decimal
FAMILY = "ca-ns/low_income_reduction_basic"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"


def test_2025_low_income_reduction_basic_is_300() -> None:
    assert parameter_source().get(FAMILY, 2025, CREDIT).values == Credit(amount=D("300"))


def test_2025_low_income_reduction_basic_rounds_half_up_to_the_cent() -> None:
    data = parameter_source().get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_low_income_reduction_basic_cites_the_form() -> None:
    assert parameter_source().get(FAMILY, 2025, CREDIT).sources == (CRA_FORM_TEXT,)
