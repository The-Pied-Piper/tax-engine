"""The 2025 dataset `ca/cca_class_10_1_conditions`, the costs a passenger vehicle must be more than
to belong in Class 10.1, checked against CRA's guide. The capability `ca/cca_vehicle_class_checks`
that reads it has its own tests.

Guide T4044 (Employment Expenses, 2025 edition, docs/cra-forms-2025/t4044-25e.txt), "Class 10.1":
"Include your passenger vehicle in Class 10.1 if it meets one of the following conditions: - You
acquired it after December 31, 2000, and before January 1, 2022, and it cost you more than $30,000
- You acquired it after December 31, 2021, and before January 1, 2023, and it cost you more than
$34,000 - You acquired it after December 31, 2022, and before January 1, 2024, and it cost you more
than $36,000 - You acquired it after December 31, 2023, and before January 1, 2025, and it cost you
more than $37,000 - You acquired it after December 31, 2024, and it cost you more than $38,000. If
your passenger vehicle does not meet any of these conditions, then it belongs in Class 10."
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca
import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts, YearAmountsRow
from tests.jurisdictions.ca_on.end_to_end.support import D

SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FAMILY = "ca/cca_class_10_1_conditions"


def test_2025_the_minimum_costs_are_the_five_printed_in_the_guide() -> None:
    data = SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS)

    assert data.values == YearAmounts(
        (
            YearAmountsRow(2025, {"minimum_cost": D("38000")}),
            YearAmountsRow(2024, {"minimum_cost": D("37000")}),
            YearAmountsRow(2023, {"minimum_cost": D("36000")}),
            YearAmountsRow(2022, {"minimum_cost": D("34000")}),
            YearAmountsRow(2001, {"minimum_cost": D("30000")}),
        )
    )


def test_2025_the_minimum_costs_round_half_up_to_the_cent() -> None:
    assert SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).rounding == CENT


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2026, "38000"),
        (2025, "38000"),
        (2024, "37000"),
        (2023, "36000"),
        (2022, "34000"),
        (2021, "30000"),
        (2001, "30000"),
    ],
)
def test_2025_the_minimum_cost_for_the_year_the_vehicle_was_acquired(
    year: int, expected: str
) -> None:
    row = SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).values.row_for(year)

    assert row is not None
    assert row.amount("minimum_cost") == D(expected)


@pytest.mark.parametrize("year", [2000, 1999, 0])
def test_2025_a_vehicle_acquired_before_2001_meets_none_of_the_conditions(year: int) -> None:
    assert SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).values.row_for(year) is None


def test_2025_the_dataset_cites_the_guide() -> None:
    sources = SOURCE.get(FAMILY, 2025, YEAR_AMOUNTS).sources

    assert sources
    assert all(source.startswith("https://") for source in sources)
    assert any("t4044" in source for source in sources)


def test_2025_the_dataset_file_quotes_the_guide() -> None:
    path = (
        Path(tax_engine.jurisdictions.ca.__file__).parent
        / "parameters"
        / FAMILY.removeprefix("ca/")
    )
    text = (path / "2025.yaml").read_text()

    assert "Include your passenger vehicle in Class 10.1 if it meets one of" in text
    assert "family: ca/cca_class_10_1_conditions" in text
    assert "kind: year_amounts" in text
