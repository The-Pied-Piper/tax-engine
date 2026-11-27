"""The 2025 `ca-ns/labour_sponsored_credit_maximum` dataset, against Form NS428 (5003-C, 2025).

Form NS428: line 90: "(maximum $2,000)". The maximum is printed, so the dataset holds it as
printed, claimed whole: the `credit` kind.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ns.ns428_credits_support import parameter_source

D = Decimal
FAMILY = "ca-ns/labour_sponsored_credit_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"


def test_2025_labour_sponsored_credit_maximum_is_2000() -> None:
    assert parameter_source().get(FAMILY, 2025, CREDIT).values == Credit(amount=D("2000"))


def test_2025_labour_sponsored_credit_maximum_rounds_half_up_to_the_cent() -> None:
    data = parameter_source().get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_labour_sponsored_credit_maximum_cites_the_form() -> None:
    assert parameter_source().get(FAMILY, 2025, CREDIT).sources == (CRA_FORM_TEXT,)
