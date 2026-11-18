"""The 2025 amount of `ca-mb/venture_capital_credit_maximum`, checked against Form MB428
(5007-C, 2025).

Form MB428, line 77: "Line 77 and line 60850: Manitoba small business venture capital tax credit
for individuals (complete Form T1256-1) (maximum $120,000)". The maximum is printed, so the dataset
holds it as printed, claimed whole: the `credit` kind, as `ca-mb/basic_personal_amount` is.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/venture_capital_credit_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt"


def test_2025_venture_capital_credit_maximum_is_120000() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("120000"))


def test_2025_venture_capital_credit_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_venture_capital_credit_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
