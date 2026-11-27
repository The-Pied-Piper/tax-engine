"""The 2025 `ca-ns/age_tax_credit_income_limit` dataset, Form NS428
(5003-c-25e.txt), Line 98 "taxable income is less than $24,000": the printed figure,
claimed whole (the `credit` kind). Rounds half-up to the cent, the project's choice, as the form
states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_packages,
    nova_scotia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    nova_scotia_packages().roots(),
    nova_scotia_parameter_parsers(),
)
FAMILY = "ca-ns/age_tax_credit_income_limit"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"
YEAR = 2025


def test_2025_age_tax_credit_income_limit_is_24000() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("24000"))


def test_2025_age_tax_credit_income_limit_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_age_tax_credit_income_limit_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
