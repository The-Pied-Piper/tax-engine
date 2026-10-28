"""The 2025 capital cost allowance class rates of Form T777 (capital cost allowance schedule for
employees), in three datasets, one for each list the form's capability reads: Class 8 (Part A,
line 13), Classes 10, 54 and 55 (Part A, line 25) and Class 10.1 (Part B, line 25).

2025 Form T777, the printed rates of Part A (Classes 8, 10, 54 and 55, pages 4 and 5) and of Part B
(Class 10.1, "10.1 30%", page 5). Note (8): "For ZEVs and AIIPs (under proposed changes, acquired
before 2025) that became available for use in 2025, the relevant factors are 1 1/2 (Class 54) and
7/8 (Class 55) and 0 for the remaining AIIPs." Note (9): "Under proposed changes, for ZEVs and RIIPs
acquired after 2024 that became available for use in 2025, the relevant factors are 2 1/3 (Class
54), 1 1/2 (Class 55), and 1/2 (Class 8 and 10)." Note (12): "Recapture and terminal loss rules do
not apply." The half-year rule on sale is the rule of Guides T4036 and T4002 for Class 10.1, as the
shared dataset `ca/cca_class_rates` states it. The columns the form computes round half-up to the
cent, the owner's decision, as the form states no rounding rule.

The factor of Class 10.1 for the RIIPs is not printed in notes (8) and (9): it is not tested here
and is listed as an assumption on the ticket.
"""

from __future__ import annotations

from fractions import Fraction as ExactFraction
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.class_rates import (
    CLASS_RATES,
    ClassRate,
    HalfYearRule,
    HalfYearRuleOnSale,
    RecaptureAndTerminalLoss,
)
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_on.end_to_end.support import D

SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T777_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t777/t777-25e.pdf"
CLASS_8 = "ca/t777_class_8_rates"
VEHICLES = "ca/t777_vehicle_class_rates"
CLASS_10_1 = "ca/t777_part_b_class_rates"
SHARED = "ca/cca_class_rates"

# Printed rates of T777 Part A (Class 8, 10, 54, 55) and Part B (Class 10.1).
CLASS_8_RATES = {"8": "0.20"}
VEHICLE_RATES = {"10": "0.30", "54": "0.30", "55": "0.40"}
PART_B_RATES = {"10.1": "0.30"}

# Notes (8) and (9): the AIIP factors ("0 for the remaining AIIPs") and the RIIP factors ("1/2
# (Class 8 and 10)") of the classes, the vehicle classes of Part A.
VEHICLE_AIIP_FACTORS = {
    "10": ExactFraction(0),
    "54": ExactFraction(3, 2),
    "55": ExactFraction(7, 8),
}
VEHICLE_RIIP_FACTORS = {
    "10": ExactFraction(1, 2),
    "54": ExactFraction(7, 3),
    "55": ExactFraction(3, 2),
}
CLASS_8_AIIP_FACTOR = ExactFraction(0)
CLASS_8_RIIP_FACTOR = ExactFraction(1, 2)


def dataset_class(family: str, number: str) -> ClassRate | None:
    return SOURCE.get(family, 2025, CLASS_RATES).values.for_class(D(number))


def listed(family: str) -> dict[str, str]:
    return {str(entry.class_number): str(entry.rate.value) for entry in classes(family)}


def classes(family: str) -> tuple[ClassRate, ...]:
    return SOURCE.get(family, 2025, CLASS_RATES).values.classes


def as_exact(part: Any) -> ExactFraction:
    return ExactFraction(part.numerator, part.denominator)


# --- the rates ----------------------------------------------------------------------------------


def test_the_class_8_dataset_lists_class_8_only_at_its_printed_rate() -> None:
    assert {number: D(rate) for number, rate in listed(CLASS_8).items()} == {
        number: D(rate) for number, rate in CLASS_8_RATES.items()
    }


def test_the_vehicle_dataset_lists_classes_10_54_and_55_at_their_printed_rates() -> None:
    assert {number: D(rate) for number, rate in listed(VEHICLES).items()} == {
        number: D(rate) for number, rate in VEHICLE_RATES.items()
    }


def test_the_part_b_dataset_lists_class_10_1_only_at_its_printed_rate() -> None:
    assert {number: D(rate) for number, rate in listed(CLASS_10_1).items()} == {
        number: D(rate) for number, rate in PART_B_RATES.items()
    }


@pytest.mark.parametrize(
    ("family", "number"),
    [
        (CLASS_8, "10"),
        (CLASS_8, "54"),
        (VEHICLES, "8"),
        (VEHICLES, "10.1"),
        (CLASS_10_1, "8"),
        (CLASS_10_1, "10"),
        (CLASS_10_1, "54"),
    ],
)
def test_a_class_outside_a_list_is_not_in_its_dataset(family: str, number: str) -> None:
    assert dataset_class(family, number) is None


# --- the factors ----------------------------------------------------------------------------------


def test_the_class_8_factors_are_0_for_aiips_and_one_half_for_riips() -> None:
    entry = dataset_class(CLASS_8, "8")

    assert entry is not None
    assert as_exact(entry.aiip_factor) == CLASS_8_AIIP_FACTOR
    assert as_exact(entry.riip_factor) == CLASS_8_RIIP_FACTOR


@pytest.mark.parametrize("number", sorted(VEHICLE_AIIP_FACTORS))
def test_the_vehicle_aiip_factors_are_those_of_note_8(number: str) -> None:
    entry = dataset_class(VEHICLES, number)

    assert entry is not None
    assert as_exact(entry.aiip_factor) == VEHICLE_AIIP_FACTORS[number]


@pytest.mark.parametrize("number", sorted(VEHICLE_RIIP_FACTORS))
def test_the_vehicle_riip_factors_are_those_of_note_9(number: str) -> None:
    entry = dataset_class(VEHICLES, number)

    assert entry is not None
    assert as_exact(entry.riip_factor) == VEHICLE_RIIP_FACTORS[number]


def test_the_class_10_1_aiip_factor_is_0_as_note_8_says_for_the_remaining_aiips() -> None:
    entry = dataset_class(CLASS_10_1, "10.1")

    assert entry is not None
    assert as_exact(entry.aiip_factor) == ExactFraction(0)


# --- the half-year rules and the recapture -------------------------------------------------------


def test_the_part_a_datasets_have_no_half_year_rule_on_sale() -> None:
    for family in (CLASS_8, VEHICLES):
        for entry in classes(family):
            assert entry.half_year_rule_on_sale is HalfYearRuleOnSale.DOES_NOT_APPLY, entry


def test_class_10_1_has_the_half_year_rule_on_sale_and_no_recapture_or_terminal_loss() -> None:
    entry = dataset_class(CLASS_10_1, "10.1")

    assert entry is not None
    assert entry.half_year_rule is HalfYearRule.APPLIES
    assert entry.half_year_rule_on_sale is HalfYearRuleOnSale.APPLIES
    assert entry.recapture_and_terminal_loss is RecaptureAndTerminalLoss.EXCLUDED


# --- the dataset as a whole -------------------------------------------------------------------


@pytest.mark.parametrize("family", [CLASS_8, VEHICLES, CLASS_10_1])
def test_each_dataset_rounds_half_up_to_the_cent_and_has_a_365_day_year(family: str) -> None:
    data = SOURCE.get(family, 2025, CLASS_RATES)

    assert data.rounding == CENT
    assert data.values.full_year_days == 365


@pytest.mark.parametrize("family", [CLASS_8, VEHICLES, CLASS_10_1])
def test_each_dataset_cites_the_2025_form_t777(family: str) -> None:
    assert T777_TEXT in SOURCE.get(family, 2025, CLASS_RATES).sources


def test_the_vehicle_classes_match_the_shared_t2125_dataset_row_for_row() -> None:
    # The same classes, rates and factors as `ca/cca_class_rates`, which Form T2125 Area A reads:
    # a Class 54 or 55 row of the two forms gives the same CCA.
    for number in ("10", "54", "55"):
        ours = dataset_class(VEHICLES, number)
        shared = dataset_class(SHARED, number)

        assert ours is not None and shared is not None, number
        assert ours.rate.value == shared.rate.value, number
        assert as_exact(ours.aiip_factor) == as_exact(shared.aiip_factor), number
        assert as_exact(ours.riip_factor) == as_exact(shared.riip_factor), number
