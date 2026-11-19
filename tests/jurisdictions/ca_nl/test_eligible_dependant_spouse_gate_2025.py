"""The 2025 `ca-nl/eligible_dependant_spouse_gate` dataset: a two-band switch giving the most NL428
line 23 may be, the printed maximum 9,043 where line 20 is 0.00 and 0 where it is at least one cent
(Form NL428, CRA 5001-C 2025: "Line 23 and line 58160: Line 21 minus line 22 (if negative, enter
"0") (maximum $9,043)"). Guide 5000-G, line 30400: "If you did not claim an amount on line 30300 of
your return, you may be able to claim this amount for one dependant"; NL Income Tax Act, 2000,
s. 9(1)(b) gives the eligible dependant amount only to an individual who does not claim the spouse
amount.

Only the 9,043 is a printed form figure; the rows are a switch. A base of 0.00 gives 9,043 and a
base of 0.01 or more gives 0; a base exactly at the second row's `over` (0.005) is in the lower
band.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.parameters.credit import CREDIT
from tax_engine.jurisdictions.core.capabilities.amount_by_band import AmountFromBand
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/eligible_dependant_spouse_gate"
YEAR = 2025

# Made up for this test and not registered: the amount claimed, and the most.
CLAIMED = AmountKind("ex/claimed")
MOST = AmountKind("ex/most")


def _most(base: str) -> Decimal:
    capability = AmountFromBand(SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND), CLAIMED, MOST)

    (output,) = capability.compute((Artifact(CLAIMED, D(base)),)).outputs

    assert output.kind is MOST
    assert isinstance(output.value, Decimal)
    return output.value


def test_the_gate_is_the_amount_by_band_kind() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == YEAR


def test_the_gate_has_two_bands_the_first_from_0_and_the_second_above_half_a_cent() -> None:
    bands = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.bands

    assert len(bands) == 2
    assert bands[0].over == 0
    assert bands[0].amount == 9043
    assert bands[1].over == D("0.005")
    assert bands[1].amount == 0


@pytest.mark.parametrize(
    ("base", "expected"),
    [("0", "9043"), ("0.00", "9043"), ("0.005", "9043"), ("0.01", "0"), ("9043.00", "0")],
)
def test_the_gate_gives_9043_at_nothing_claimed_and_0_from_one_cent(
    base: str, expected: str
) -> None:
    assert _most(base) == D(expected)


def test_the_gate_names_the_form_and_the_act_as_its_sources() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-g/5000-g-25e.txt",
        "https://assembly.nl.ca/legislation/sr/statutes/i01-1.htm",
    )


def test_the_gate_band_for_0_is_not_the_band_for_one_cent() -> None:
    values = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).values

    assert values.band_for(D("0.00")) is values.bands[0]
    assert values.band_for(D("0.005")) is values.bands[0]
    assert values.band_for(D("0.01")) is values.bands[1]


def test_the_gate_maximum_is_the_eligible_dependant_maximum() -> None:
    maximum = SOURCE.get("ca-nl/eligible_dependant_amount_maximum", 2025, CREDIT).values.amount

    assert SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).values.bands[0].amount == maximum
