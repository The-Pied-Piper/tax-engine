"""The 2025 dataset `ca/cca_zepv_prescribed_amounts`, the prescribed amounts of a Class 54
zero-emission passenger vehicle, checked against CRA's guide. The capability
`ca/cca_vehicle_proceeds` that reads it has its own tests; Return DH
(`returns/2025_return_dh.yaml`) works it end to end.

Guide T4036 (Rental Income, 2025 edition, docs/cra-forms-2025/t4036-25e.pdf, confirmed from the
PDF), "Class 54 (30%)": "There is a limit of $61,000 (plus federal and provincial sales taxes) on
the capital cost for each zero-emission passenger vehicle in Class 54." and "If a zero-emission
passenger vehicle is disposed of to a person or partnership with whom you deal at arm's length,
and its cost exceeds the prescribed amount ($55,000 for vehicles acquired after March 18, 2019,
and before January 1, 2022; $59,000 for vehicles acquired after December 31, 2021, and before
January 1, 2023; or $61,000 for vehicles acquired after December 31, 2022), the proceeds of
disposition will be adjusted based on a factor equal to the prescribed amount as a proportion of
the actual cost of the vehicle." The amounts are by the year acquired: 2019 to 2021, 2022, and
2023 and later; a vehicle acquired before 2019 is not a Class 54 vehicle, so the table has no row
for it. The tax is a dollars-and-cents box, rounded half-up to the cent, as the guide states no
rounding rule, like the Class 10.1 dataset.
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
FAMILY = "ca/cca_zepv_prescribed_amounts"


def test_2025_the_prescribed_amounts_are_the_three_printed_in_the_guide() -> None:
    data = SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS)

    assert data.values == YearAmounts(
        (
            YearAmountsRow(2023, {"prescribed_amount": D("61000")}),
            YearAmountsRow(2022, {"prescribed_amount": D("59000")}),
            YearAmountsRow(2019, {"prescribed_amount": D("55000")}),
        )
    )


def test_2025_the_prescribed_amounts_round_half_up_to_the_cent() -> None:
    assert SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).rounding == CENT


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2030, "61000"),
        (2026, "61000"),
        (2025, "61000"),
        (2024, "61000"),
        (2023, "61000"),
        (2022, "59000"),
        (2021, "55000"),
        (2020, "55000"),
        (2019, "55000"),
    ],
)
def test_2025_the_prescribed_amount_for_the_year_the_vehicle_was_acquired(
    year: int, expected: str
) -> None:
    row = SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).values.row_for(year)

    assert row is not None
    assert row.amount("prescribed_amount") == D(expected)


@pytest.mark.parametrize("year", [2018, 2000, 0])
def test_2025_a_year_before_2019_has_no_prescribed_amount(year: int) -> None:
    # "vehicles acquired after March 18, 2019": nothing is printed for an earlier year.
    assert SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).values.row_for(year) is None


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

    assert "Class 54 (30%)" in text
    assert "family: ca/cca_zepv_prescribed_amounts" in text
    assert "kind: year_amounts" in text
