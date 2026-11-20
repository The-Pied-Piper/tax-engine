"""The 2025 `ca-qc/solidarity_living_alone_amount` dataset, checked against Table C.9 of fiche
110201.

Quebec Ministry of Finance, Dépenses fiscales 2025, fiche 110201, Table C.9, column
"Juillet 2026 à juin 2027": "Composantes relatives à la TVQ: montant pour personne vivant seule
172". The fiche is a web page, so the figure is a listed check until a printed source is found.
The amount is printed, so the dataset holds it as printed, claimed whole: the `credit` kind.
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
FAMILY = "ca-qc/solidarity_living_alone_amount"
SOURCE_PAGE = (
    "https://www.revenuquebec.ca/en/citizens/tax-credits/solidarity-tax-credit/"
    "calculation-of-the-credit/"
)


def test_2025_solidarity_living_alone_amount_is_172() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("172"))


def test_2025_solidarity_living_alone_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_solidarity_living_alone_amount_cites_its_source_page() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (SOURCE_PAGE,)
