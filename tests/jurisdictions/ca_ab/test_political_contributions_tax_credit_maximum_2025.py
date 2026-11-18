"""The 2025 `ca-ab/political_contributions_tax_credit_maximum` dataset, AB428 line 72's maximum.

Form text (Form AB428, CRA 5009-c-25e.txt line 238): "Line 72: Alberta political contributions tax
credit (use Worksheet AB428) (maximum $1,000)". The maximum is a figure of the form, not an
input, so
it is a `credit` dataset claimed whole, like the pension income amount maximum. It rounds half-up to
the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/political_contributions_tax_credit_maximum"


def test_2025_amount_is_1000() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=Decimal("1000"))


def test_2025_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_cites_the_ab428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-c/5009-c-25e.txt"
        in data.sources
    )


def test_2025_amount_is_for_tax_year_2025() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.tax_year == 2025
