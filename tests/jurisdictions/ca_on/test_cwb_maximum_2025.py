"""The 2025 maximum benefit of the basic Canada workers benefit, checked against Schedule 6 line 21.

Schedule 6 (2025) line 21: "If you had an eligible spouse or an eligible dependant, enter $2,813. If
not, enter $1,633." The $1,633 is the printed figure for a filer with no eligible spouse and no
eligible dependant, claimed whole through core/credit_amount. A dollars-and-cents figure, so it
rounds half-up to the cent, which changes nothing.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
MAXIMUM_FAMILY = "ca/cwb_maximum"
SCHEDULE_6_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_the_maximum_is_1633_claimed_whole() -> None:
    data = SOURCE.get(MAXIMUM_FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("1633.00"))


def test_2025_the_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(MAXIMUM_FAMILY, 2025, CREDIT)

    assert data.rounding == CENT


def test_2025_the_maximum_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(MAXIMUM_FAMILY, 2025, CREDIT)

    assert SCHEDULE_6_TEXT in data.sources
