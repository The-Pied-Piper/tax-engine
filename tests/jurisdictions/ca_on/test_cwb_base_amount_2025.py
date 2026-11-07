"""The 2025 amount of `ca/cwb_base_amount`, checked against Schedule 6 (5000-S6, 2025).

Schedule 6 (2025) line 17: "Base amount 3,000.00". The amount is printed, so the dataset holds it
as printed: one amount, rounded half-up to the cent. It is claimed whole, so it is the `credit`
kind, as `ca/home_buyers_maximum` is.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
CWB_BASE_AMOUNT = "ca/cwb_base_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"


def test_2025_cwb_base_amount_is_3000() -> None:
    data = SOURCE.get(CWB_BASE_AMOUNT, 2025, CREDIT)

    assert data.values == Credit(amount=D("3000"))


def test_2025_cwb_base_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(CWB_BASE_AMOUNT, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_base_amount_cites_schedule_6() -> None:
    data = SOURCE.get(CWB_BASE_AMOUNT, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
