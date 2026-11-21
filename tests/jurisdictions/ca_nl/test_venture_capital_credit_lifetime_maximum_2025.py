"""The 2025 `ca-nl/venture_capital_credit_lifetime_maximum` dataset, Form NL428 line 82 guide
(5001-pc-25e.txt): "The lifetime maximum you can claim is $75,000."

The maximum is printed, so the dataset holds it as printed, claimed whole: the `credit` kind.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/venture_capital_credit_lifetime_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-pc/5001-pc-25e.txt"


def test_2025_venture_capital_credit_lifetime_maximum_is_75000() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("75000"))


def test_2025_venture_capital_credit_lifetime_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_venture_capital_credit_lifetime_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
