"""The 2025 `ca-mb/fertility_treatment_credit_maximum`, checked against Form MB479 (5007-TC).

Form MB479, line 61: the eligible medical expenses for fertility treatments "multiplied by 40%
(maximum $16,000) =". The printed maximum bounds the line's result, as Ontario's LIFT maximum
bounds ON428-A line 5. Line 61 is a dollars-and-cents line, so the capped amount rounds half-up to
the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_mb.support import (
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)

D = Decimal
SOURCE = YamlParameterSource(
    manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
)
FAMILY = "ca-mb/fertility_treatment_credit_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-tc/5007-tc-25e.txt"


def test_2025_fertility_treatment_credit_maximum_is_16000() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("16000"))


def test_2025_fertility_treatment_credit_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_fertility_treatment_credit_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (CRA_FORM_TEXT,)
