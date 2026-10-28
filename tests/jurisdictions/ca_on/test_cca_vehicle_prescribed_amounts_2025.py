"""The 2025 dataset `ca/cca_vehicle_prescribed_amounts`, the prescribed amounts of a Class 10.1
passenger vehicle, checked against CRA's guide. The capability `ca/cca_vehicle_proceeds` that
reads it has its own tests; Return CZ (`returns/2025_return_cz.yaml`) works it end to end.

Guide T4002 (Self-employed Business, Professional, Commission, Farming, and Fishing Income, 2025
edition, docs/cra-forms-2025/t4002-25e.pdf, confirmed from the PDF), "Class 10.1 (30%)": "The
capital cost limits of a Class 10.1 passenger vehicle are the following prescribed amounts:
$30,000 for vehicles acquired before 2022, plus the GST/HST or PST; $34,000 for vehicles acquired
in 2022, plus the GST/HST or PST; $36,000 for vehicles acquired in 2023, plus the GST/HST or PST;
$37,000 for vehicles acquired in 2024, plus the GST/HST or PST; $38,000 for vehicles acquired in
2025, plus the GST/HST or PST" and "Under the immediate expensing rules, if you dispose of a
passenger vehicle acquired after April 18, 2021, to a person or partnership with whom you deal at
arm's length, and its cost exceeds the prescribed amount, the proceeds of disposition will be
adjusted based on a factor equal to the prescribed amount as a proportion of the actual cost of the
vehicle." (Guide T4036 prints the same list.) The tax is a dollars-and-cents box, rounded half-up
to the cent, as the guide states no rounding rule, like the vehicle limits of Form T2125 Chart C.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tax_calculator.jurisdictions.ca
import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts, YearAmountsRow
from tests.jurisdictions.ca_on.end_to_end.support import D

SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FAMILY = "ca/cca_vehicle_prescribed_amounts"


def test_2025_the_prescribed_amounts_are_the_five_printed_in_the_guide() -> None:
    data = SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS)

    assert data.values == YearAmounts(
        (
            YearAmountsRow(2025, {"prescribed_amount": D("38000")}),
            YearAmountsRow(2024, {"prescribed_amount": D("37000")}),
            YearAmountsRow(2023, {"prescribed_amount": D("36000")}),
            YearAmountsRow(2022, {"prescribed_amount": D("34000")}),
            YearAmountsRow(None, {"prescribed_amount": D("30000")}),
        )
    )


def test_2025_the_prescribed_amounts_round_half_up_to_the_cent() -> None:
    assert SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).rounding == CENT


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2030, "38000"),
        (2026, "38000"),
        (2025, "38000"),
        (2024, "37000"),
        (2023, "36000"),
        (2022, "34000"),
        (2021, "30000"),
        (2020, "30000"),
        (0, "30000"),
    ],
)
def test_2025_the_prescribed_amount_for_the_year_the_vehicle_was_acquired(
    year: int, expected: str
) -> None:
    row = SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).values.row_for(year)

    assert row is not None
    assert row.amount("prescribed_amount") == D(expected)


def test_2025_the_dataset_cites_the_guide() -> None:
    sources = SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).sources

    assert sources
    assert all(source.startswith("https://") for source in sources)
    assert any(source.endswith(("t4002-25e.pdf", "t4036-25e.pdf")) for source in sources)


def test_2025_the_dataset_file_quotes_the_guide() -> None:
    path = (
        Path(tax_calculator.jurisdictions.ca.__file__).parent
        / "parameters"
        / FAMILY.removeprefix("ca/")
    )
    text = (path / "2025.yaml").read_text()

    assert "Class 10.1 (30%)" in text
    assert "family: ca/cca_vehicle_prescribed_amounts" in text
    assert "kind: year_amounts" in text
