"""The 2025 `ca-qc/solidarity_reduction_rate_one_component` dataset, checked against fiche 110201.

Quebec Ministry of Finance, Dépenses fiscales 2025, fiche 110201 (credit
reduction text): the reduction rate is 3% when only one of the three
components is received.
The fiche is a web page, so the figure is a listed check until a printed source is found. The
printed 3% is a rate of 0.03. The reduction is a dollars-and-cents figure, so it rounds
half-up to the cent, the project's choice, as the forms state no rounding rule.
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
FAMILY = "ca-qc/solidarity_reduction_rate_one_component"
SOURCE_PAGE = (
    "https://www.revenuquebec.ca/en/citizens/tax-credits/solidarity-tax-credit/"
    "calculation-of-the-credit/"
)


def test_2025_solidarity_reduction_rate_one_component_is_0_03() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.03"))


def test_2025_solidarity_reduction_rate_one_component_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_solidarity_reduction_rate_one_component_cites_its_source_page() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (SOURCE_PAGE,)
