"""The 2025 figure of `ca-qc/cwb_base_amount`, checked against Schedule 6 (5005-S6, 2025, Quebec edition).

CRA 5005-S6 (2025), page 4 or 5, "Line 17: If you had an eligible spouse or you had both an eligible spouse and an eligible dependant, enter $3,600. If not, enter $2,400."
The filer takes the "If not" branch, so the dataset holds the printed $2,400 for a filer with no eligible spouse and no eligible dependant, claimed whole.
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
FAMILY = "ca-qc/cwb_base_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s6/5005-s6-25e.txt"


def test_2025_cwb_base_amount_is_2400() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("2400"))


def test_2025_cwb_base_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cwb_base_amount_cites_schedule_6() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
