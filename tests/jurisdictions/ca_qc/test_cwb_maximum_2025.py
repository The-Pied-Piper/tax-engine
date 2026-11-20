"""The 2025 figure of `ca-qc/cwb_maximum`, checked against Schedule 6 (5005-S6, 2025, Quebec
edition).

CRA 5005-S6 (2025), page 4 or 5, "Line 21: If you did not have an eligible spouse or an eligible
dependant, enter $3,812.06. If you had an eligible spouse but did not have an eligible dependant,
enter $5,943.38. ..." The filer takes the "If not" branch, so the dataset holds the printed
$3,812.06 for a filer with no eligible spouse and no eligible dependant, claimed whole.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/cwb_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s6/5005-s6-25e.txt"


def test_2025_cwb_maximum_is_3812_06() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("3812.06"))


def test_2025_cwb_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_maximum_cites_schedule_6() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
