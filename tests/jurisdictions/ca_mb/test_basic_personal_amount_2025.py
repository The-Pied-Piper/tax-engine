"""The 2025 amount of `ca-mb/basic_personal_amount`, checked against Worksheet MB428
(5007-D, 2025).

Worksheet MB428, section "Line 58040 - Basic personal amount", line 1: "Base amount
15,780.00". The amount is printed, so the dataset holds it as printed, claimed whole: the `credit`
kind, as `ca-ab/supplemental_credit_base` is.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

D = Decimal
# Manitoba is not in `registrations.JURISDICTIONS` yet, so the source is built over its own
# packages.
SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/basic_personal_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-d/5007-d-25e.txt"


def test_2025_basic_personal_amount_is_15780() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("15780"))


def test_2025_basic_personal_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_basic_personal_amount_cites_the_worksheet() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
