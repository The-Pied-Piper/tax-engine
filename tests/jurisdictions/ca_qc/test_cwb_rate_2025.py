"""The 2025 figure of `ca-qc/cwb_rate`, checked against Schedule 6 (5005-S6, 2025, Quebec edition).

CRA 5005-S6 (2025), page 4 or 5, "Line 19: If you had an eligible dependant but did not have an eligible spouse, enter 20%. If you had both an eligible spouse and an eligible dependant, enter 23.9%. If not, enter 37.3%."
The filer takes the "If not" branch, so the dataset holds the printed 37.3% for a filer with no eligible spouse and no eligible dependant, held as a rate of 0.373.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/cwb_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s6/5005-s6-25e.txt"


def test_2025_cwb_rate_is_0_373() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.373"))


def test_2025_cwb_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_rate_cites_schedule_6() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
