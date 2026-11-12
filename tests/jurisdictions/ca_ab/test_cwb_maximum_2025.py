"""The 2025 maximum of `ca-ab/cwb_maximum`, checked against Schedule 6
(5009-S6, 2025).

Schedule 6 (2025, Alberta edition) line 21: "If you had an eligible spouse or an eligible
dependant, enter $2,619. If not, enter $1,750." The $1,750 is the figure for a filer with no
eligible spouse or dependant, claimed whole.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/cwb_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-s6/5009-s6-25e.txt"


def test_2025_cwb_maximum_is_1750() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("1750"))


def test_2025_cwb_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_maximum_cites_schedule_6() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
