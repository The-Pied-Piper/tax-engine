"""The 2025 principal residence Chart 1 factor, checked against CRA's worksheet.

Form T2091(IND)-WS, Principal Residence Worksheet, Chart 1: "Complete this chart if the amount on
line 7 is more than the amount on line 10." "Multiply line 14 by 1.1." (line 16). The printed
factor is 1.1, a dataset of the `factor` kind; line 16 is a dollars-and-cents box, so the dataset
rounds it half-up to the cent, the owner's decision, as the worksheet states no rounding rule.
The worksheet is published only as its 2023 edition (no 2025 or 2024 version exists), so the
dataset cites that PDF.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.factor import FACTOR, Factor
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FAMILY = "ca/principal_residence_chart_1_factor"
WORKSHEET_PDF = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2091ind-ws/t2091ind-ws-23e.pdf"
)


def test_2025_factor_is_the_printed_1_point_1() -> None:
    data = SOURCE.get(FAMILY, 2025, FACTOR)

    assert data.values == Factor(D("1.1"))


def test_2025_factor_rounds_line_16_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, FACTOR)

    assert data.rounding == CENT


def test_2025_factor_cites_the_worksheet_pdf_only() -> None:
    data = SOURCE.get(FAMILY, 2025, FACTOR)

    assert data.sources == (WORKSHEET_PDF,)
