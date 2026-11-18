"""The 2025 amount of `ca-sk/political_contribution_credit_maximum`, checked against Form SK428
(5008-C, 2025).

Form SK428, line 73: "Line 73: Saskatchewan political contribution tax credit (use Worksheet
SK428) (maximum $650)". The maximum is printed, so the dataset holds it as printed, claimed whole:
the `credit` kind, as `ca-sk/pension_income_amount_maximum` is.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_sk.support import saskatchewan_packages, saskatchewan_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(saskatchewan_packages().roots(), saskatchewan_parameter_parsers())
FAMILY = "ca-sk/political_contribution_credit_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt"


def test_2025_political_contribution_credit_maximum_is_650() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("650"))


def test_2025_political_contribution_credit_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_political_contribution_credit_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
