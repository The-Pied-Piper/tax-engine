"""The 2025 reduction threshold of `ca-ab/cwb_reduction_threshold`, checked against Schedule 6
(5009-S6, 2025).

Schedule 6 (2025, Alberta edition) line 24: "If you had an eligible spouse or an eligible
dependant, enter $32,772. If not, enter $26,159." The $26,159 is the figure for a filer with no
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
FAMILY = "ca-ab/cwb_reduction_threshold"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-s6/5009-s6-25e.txt"


def test_2025_cwb_reduction_threshold_is_26159() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("26159"))


def test_2025_cwb_reduction_threshold_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_reduction_threshold_cites_schedule_6() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
