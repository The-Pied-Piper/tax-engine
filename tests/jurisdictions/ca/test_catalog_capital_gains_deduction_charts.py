"""Registered and money kinds of the federal catalog family `capital_gains_deduction_charts`.

Form T657 Charts 2016 to 2023 (Part 1 and Part 2 each) and Chart 2024, Period 1 and Period 2
(confirmed from the PDF; the form lines are in
`tests/jurisdictions/ca_on/test_t657_2025.py`).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    CHART_2016_AMOUNT_B,
    CHART_2016_PART_1_AMOUNT_A,
    CHART_2016_PART_1_AMOUNT_C,
    CHART_2016_PART_1_AMOUNT_F,
    CHART_2016_PART_1_AMOUNT_G,
    CHART_2016_PART_1_AMOUNT_H,
    CHART_2016_PART_1_AMOUNTS_D_AND_E,
    CHART_2016_PART_2_AMOUNT_A,
    CHART_2016_PART_2_AMOUNT_C,
    CHART_2016_PART_2_AMOUNT_E,
    CHART_2016_PART_2_APPLIES,
    CHART_2017_AMOUNT_D,
    CHART_2017_PART_1_AMOUNT_A,
    CHART_2017_PART_1_AMOUNT_C,
    CHART_2017_PART_1_AMOUNT_E,
    CHART_2017_PART_1_AMOUNT_H,
    CHART_2017_PART_1_AMOUNT_I,
    CHART_2017_PART_1_AMOUNT_K,
    CHART_2017_PART_1_AMOUNT_L,
    CHART_2017_PART_1_AMOUNTS_F_AND_G,
    CHART_2017_PART_2_AMOUNT_A,
    CHART_2017_PART_2_AMOUNT_C,
    CHART_2017_PART_2_AMOUNT_E,
    CHART_2017_PART_2_APPLIES,
    CHART_2018_AMOUNT_D,
    CHART_2018_PART_1_AMOUNT_A,
    CHART_2018_PART_1_AMOUNT_C,
    CHART_2018_PART_1_AMOUNT_E,
    CHART_2018_PART_1_AMOUNT_H,
    CHART_2018_PART_1_AMOUNT_I,
    CHART_2018_PART_1_AMOUNT_K,
    CHART_2018_PART_1_AMOUNT_L,
    CHART_2018_PART_1_AMOUNTS_F_AND_G,
    CHART_2018_PART_2_AMOUNT_A,
    CHART_2018_PART_2_AMOUNT_C,
    CHART_2018_PART_2_AMOUNT_E,
    CHART_2018_PART_2_APPLIES,
    CHART_2019_AMOUNT_D,
    CHART_2019_PART_1_AMOUNT_A,
    CHART_2019_PART_1_AMOUNT_C,
    CHART_2019_PART_1_AMOUNT_E,
    CHART_2019_PART_1_AMOUNT_H,
    CHART_2019_PART_1_AMOUNT_I,
    CHART_2019_PART_1_AMOUNT_K,
    CHART_2019_PART_1_AMOUNT_L,
    CHART_2019_PART_1_AMOUNTS_F_AND_G,
    CHART_2019_PART_2_AMOUNT_A,
    CHART_2019_PART_2_AMOUNT_C,
    CHART_2019_PART_2_AMOUNT_E,
    CHART_2019_PART_2_APPLIES,
    CHART_2020_AMOUNT_D,
    CHART_2020_PART_1_AMOUNT_A,
    CHART_2020_PART_1_AMOUNT_C,
    CHART_2020_PART_1_AMOUNT_E,
    CHART_2020_PART_1_AMOUNT_H,
    CHART_2020_PART_1_AMOUNT_I,
    CHART_2020_PART_1_AMOUNT_K,
    CHART_2020_PART_1_AMOUNT_L,
    CHART_2020_PART_1_AMOUNTS_F_AND_G,
    CHART_2020_PART_2_AMOUNT_A,
    CHART_2020_PART_2_AMOUNT_C,
    CHART_2020_PART_2_AMOUNT_E,
    CHART_2020_PART_2_APPLIES,
    CHART_2021_AMOUNT_D,
    CHART_2021_PART_1_AMOUNT_A,
    CHART_2021_PART_1_AMOUNT_C,
    CHART_2021_PART_1_AMOUNT_E,
    CHART_2021_PART_1_AMOUNT_H,
    CHART_2021_PART_1_AMOUNT_I,
    CHART_2021_PART_1_AMOUNT_J,
    CHART_2021_PART_1_AMOUNT_K,
    CHART_2021_PART_1_AMOUNT_M,
    CHART_2021_PART_1_AMOUNT_N,
    CHART_2021_PART_1_AMOUNTS_F_AND_G,
    CHART_2021_PART_2_AMOUNT_A,
    CHART_2021_PART_2_AMOUNT_C,
    CHART_2021_PART_2_AMOUNT_E,
    CHART_2021_PART_2_APPLIES,
    CHART_2022_AMOUNT_D,
    CHART_2022_PART_1_AMOUNT_A,
    CHART_2022_PART_1_AMOUNT_C,
    CHART_2022_PART_1_AMOUNT_E,
    CHART_2022_PART_1_AMOUNT_H,
    CHART_2022_PART_1_AMOUNT_I,
    CHART_2022_PART_1_AMOUNT_J,
    CHART_2022_PART_1_AMOUNT_K,
    CHART_2022_PART_1_AMOUNT_M,
    CHART_2022_PART_1_AMOUNT_N,
    CHART_2022_PART_1_AMOUNTS_F_AND_G,
    CHART_2022_PART_2_AMOUNT_A,
    CHART_2022_PART_2_AMOUNT_C,
    CHART_2022_PART_2_AMOUNT_E,
    CHART_2022_PART_2_APPLIES,
    CHART_2023_AMOUNT_D,
    CHART_2023_PART_1_AMOUNT_A,
    CHART_2023_PART_1_AMOUNT_C,
    CHART_2023_PART_1_AMOUNT_E,
    CHART_2023_PART_1_AMOUNT_H,
    CHART_2023_PART_1_AMOUNT_I,
    CHART_2023_PART_1_AMOUNT_J,
    CHART_2023_PART_1_AMOUNT_K,
    CHART_2023_PART_1_AMOUNT_M,
    CHART_2023_PART_1_AMOUNT_N,
    CHART_2023_PART_1_AMOUNTS_F_AND_G,
    CHART_2023_PART_2_AMOUNT_A,
    CHART_2023_PART_2_AMOUNT_C,
    CHART_2023_PART_2_AMOUNT_E,
    CHART_2023_PART_2_APPLIES,
    CHART_2024_PERIOD_1_AMOUNT_A,
    CHART_2024_PERIOD_1_AMOUNT_C,
    CHART_2024_PERIOD_1_AMOUNT_E,
    CHART_2024_PERIOD_1_AMOUNT_I,
    CHART_2024_PERIOD_1_AMOUNT_K,
    CHART_2024_PERIOD_1_AMOUNT_L,
    CHART_2024_PERIOD_1_AMOUNT_N,
    CHART_2024_PERIOD_1_AMOUNT_O,
    CHART_2024_PERIOD_1_AMOUNTS_F_TO_H,
    CHART_2024_PERIOD_2_AMOUNT_A,
    CHART_2024_PERIOD_2_AMOUNT_C,
    CHART_2024_PERIOD_2_AMOUNT_E,
    CHART_2024_PERIOD_2_AMOUNT_I,
    CHART_2024_PERIOD_2_AMOUNT_K,
    CHART_2024_PERIOD_2_AMOUNT_L,
    CHART_2024_PERIOD_2_AMOUNT_N,
    CHART_2024_PERIOD_2_AMOUNT_O,
    CHART_2024_PERIOD_2_AMOUNTS_F_TO_H,
    T657_CHART_2016_AMOUNT_B_INSTEAD,
    T657_CHART_2016_AMOUNT_D,
    T657_CHART_2016_AMOUNT_E,
    T657_CHART_2016_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2016_USES_D_INSTEAD,
    T657_CHART_2016_USES_D_INSTEAD_CHECKED,
    T657_CHART_2017_AMOUNT_D_INSTEAD,
    T657_CHART_2017_AMOUNT_F,
    T657_CHART_2017_AMOUNT_G,
    T657_CHART_2017_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2017_USES_D_INSTEAD,
    T657_CHART_2017_USES_D_INSTEAD_CHECKED,
    T657_CHART_2018_AMOUNT_D_INSTEAD,
    T657_CHART_2018_AMOUNT_F,
    T657_CHART_2018_AMOUNT_G,
    T657_CHART_2018_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2018_USES_D_INSTEAD,
    T657_CHART_2018_USES_D_INSTEAD_CHECKED,
    T657_CHART_2019_AMOUNT_D_INSTEAD,
    T657_CHART_2019_AMOUNT_F,
    T657_CHART_2019_AMOUNT_G,
    T657_CHART_2019_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2019_USES_D_INSTEAD,
    T657_CHART_2019_USES_D_INSTEAD_CHECKED,
    T657_CHART_2020_AMOUNT_D_INSTEAD,
    T657_CHART_2020_AMOUNT_F,
    T657_CHART_2020_AMOUNT_G,
    T657_CHART_2020_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2020_USES_D_INSTEAD,
    T657_CHART_2020_USES_D_INSTEAD_CHECKED,
    T657_CHART_2021_AMOUNT_D_INSTEAD,
    T657_CHART_2021_AMOUNT_F,
    T657_CHART_2021_AMOUNT_G,
    T657_CHART_2021_AMOUNT_I,
    T657_CHART_2021_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2021_PART_2_AMOUNT_G,
    T657_CHART_2021_USES_D_INSTEAD,
    T657_CHART_2021_USES_D_INSTEAD_CHECKED,
    T657_CHART_2022_AMOUNT_D_INSTEAD,
    T657_CHART_2022_AMOUNT_F,
    T657_CHART_2022_AMOUNT_G,
    T657_CHART_2022_AMOUNT_I,
    T657_CHART_2022_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2022_PART_2_AMOUNT_G,
    T657_CHART_2022_USES_D_INSTEAD,
    T657_CHART_2022_USES_D_INSTEAD_CHECKED,
    T657_CHART_2023_AMOUNT_D_INSTEAD,
    T657_CHART_2023_AMOUNT_F,
    T657_CHART_2023_AMOUNT_G,
    T657_CHART_2023_AMOUNT_I,
    T657_CHART_2023_CLAIMS_ADDITIONAL_DEDUCTION,
    T657_CHART_2023_PART_2_AMOUNT_G,
    T657_CHART_2023_USES_D_INSTEAD,
    T657_CHART_2023_USES_D_INSTEAD_CHECKED,
    T657_CHART_2024_PERIOD_1_AMOUNT_F,
    T657_CHART_2024_PERIOD_1_AMOUNT_G,
    T657_CHART_2024_PERIOD_1_AMOUNT_H,
    T657_CHART_2024_PERIOD_1_AMOUNT_J,
    T657_CHART_2024_PERIOD_2_AMOUNT_F,
    T657_CHART_2024_PERIOD_2_AMOUNT_G,
    T657_CHART_2024_PERIOD_2_AMOUNT_H,
    T657_CHART_2024_PERIOD_2_AMOUNT_J,
)
from tests.kinds import non_negative


def test_the_form_t657_chart_2024_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    # Form T657 Chart 2024, Period 1 and Period 2: the starting amounts (B for Period 1, F, G, H and
    # J of each period) and the computed amounts A to O of each period.
    for identifier, kind in (
        ("ca/t657_chart_2024_period_1_amount_f", T657_CHART_2024_PERIOD_1_AMOUNT_F),
        ("ca/t657_chart_2024_period_1_amount_g", T657_CHART_2024_PERIOD_1_AMOUNT_G),
        ("ca/t657_chart_2024_period_1_amount_h", T657_CHART_2024_PERIOD_1_AMOUNT_H),
        ("ca/t657_chart_2024_period_1_amount_j", T657_CHART_2024_PERIOD_1_AMOUNT_J),
        ("ca/t657_chart_2024_period_2_amount_f", T657_CHART_2024_PERIOD_2_AMOUNT_F),
        ("ca/t657_chart_2024_period_2_amount_g", T657_CHART_2024_PERIOD_2_AMOUNT_G),
        ("ca/t657_chart_2024_period_2_amount_h", T657_CHART_2024_PERIOD_2_AMOUNT_H),
        ("ca/t657_chart_2024_period_2_amount_j", T657_CHART_2024_PERIOD_2_AMOUNT_J),
        ("ca/chart_2024_period_1_amount_a", CHART_2024_PERIOD_1_AMOUNT_A),
        ("ca/chart_2024_period_1_amount_c", CHART_2024_PERIOD_1_AMOUNT_C),
        ("ca/chart_2024_period_1_amount_e", CHART_2024_PERIOD_1_AMOUNT_E),
        ("ca/chart_2024_period_1_amounts_f_to_h", CHART_2024_PERIOD_1_AMOUNTS_F_TO_H),
        ("ca/chart_2024_period_1_amount_i", CHART_2024_PERIOD_1_AMOUNT_I),
        ("ca/chart_2024_period_1_amount_k", CHART_2024_PERIOD_1_AMOUNT_K),
        ("ca/chart_2024_period_1_amount_l", CHART_2024_PERIOD_1_AMOUNT_L),
        ("ca/chart_2024_period_1_amount_n", CHART_2024_PERIOD_1_AMOUNT_N),
        ("ca/chart_2024_period_1_amount_o", CHART_2024_PERIOD_1_AMOUNT_O),
        ("ca/chart_2024_period_2_amount_a", CHART_2024_PERIOD_2_AMOUNT_A),
        ("ca/chart_2024_period_2_amount_c", CHART_2024_PERIOD_2_AMOUNT_C),
        ("ca/chart_2024_period_2_amount_e", CHART_2024_PERIOD_2_AMOUNT_E),
        ("ca/chart_2024_period_2_amounts_f_to_h", CHART_2024_PERIOD_2_AMOUNTS_F_TO_H),
        ("ca/chart_2024_period_2_amount_i", CHART_2024_PERIOD_2_AMOUNT_I),
        ("ca/chart_2024_period_2_amount_k", CHART_2024_PERIOD_2_AMOUNT_K),
        ("ca/chart_2024_period_2_amount_l", CHART_2024_PERIOD_2_AMOUNT_L),
        ("ca/chart_2024_period_2_amount_n", CHART_2024_PERIOD_2_AMOUNT_N),
        ("ca/chart_2024_period_2_amount_o", CHART_2024_PERIOD_2_AMOUNT_O),
    ):
        assert registry.get(identifier) is kind, identifier


def test_the_form_t657_chart_2024_amounts_are_money_non_negative_except_the_signed_lines() -> None:
    # Amounts F and G (T2017 lines 6 and 12) are signed, as the ticket's design sets, and so are
    # amounts C, K, L, N and O (the form prints no floor on C or K); every other starting amount and
    # every computed amount is non-negative.
    signed = (
        T657_CHART_2024_PERIOD_1_AMOUNT_F,
        T657_CHART_2024_PERIOD_1_AMOUNT_G,
        T657_CHART_2024_PERIOD_2_AMOUNT_F,
        T657_CHART_2024_PERIOD_2_AMOUNT_G,
        CHART_2024_PERIOD_1_AMOUNT_C,
        CHART_2024_PERIOD_1_AMOUNT_K,
        CHART_2024_PERIOD_1_AMOUNT_L,
        CHART_2024_PERIOD_1_AMOUNT_N,
        CHART_2024_PERIOD_1_AMOUNT_O,
        CHART_2024_PERIOD_2_AMOUNT_C,
        CHART_2024_PERIOD_2_AMOUNT_K,
        CHART_2024_PERIOD_2_AMOUNT_L,
        CHART_2024_PERIOD_2_AMOUNT_N,
        CHART_2024_PERIOD_2_AMOUNT_O,
    )
    for kind in signed:
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is False, kind.identifier
    for kind in (
        T657_CHART_2024_PERIOD_1_AMOUNT_H,
        T657_CHART_2024_PERIOD_1_AMOUNT_J,
        T657_CHART_2024_PERIOD_2_AMOUNT_H,
        T657_CHART_2024_PERIOD_2_AMOUNT_J,
        CHART_2024_PERIOD_1_AMOUNT_A,
        CHART_2024_PERIOD_1_AMOUNT_E,
        CHART_2024_PERIOD_1_AMOUNTS_F_TO_H,
        CHART_2024_PERIOD_1_AMOUNT_I,
        CHART_2024_PERIOD_2_AMOUNT_A,
        CHART_2024_PERIOD_2_AMOUNT_E,
        CHART_2024_PERIOD_2_AMOUNTS_F_TO_H,
        CHART_2024_PERIOD_2_AMOUNT_I,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier


def test_the_form_t657_chart_2021_to_2023_amounts_are_money_counts_and_signed_lines() -> None:
    # Amounts F and G of Part 1 (T2017 lines 6 and 12) and Part 2's G (box 30, QFFP only) are
    # signed,
    # as the Chart 2024 amounts F and G are; the other starting amounts and every computed amount
    # are
    # non-negative money; the counts (the uses-D and claims answers, and each gate) are whole
    # numbers.
    signed = (
        T657_CHART_2021_AMOUNT_F,
        T657_CHART_2021_AMOUNT_G,
        T657_CHART_2021_PART_2_AMOUNT_G,
        T657_CHART_2022_AMOUNT_F,
        T657_CHART_2022_AMOUNT_G,
        T657_CHART_2022_PART_2_AMOUNT_G,
        T657_CHART_2023_AMOUNT_F,
        T657_CHART_2023_AMOUNT_G,
        T657_CHART_2023_PART_2_AMOUNT_G,
        CHART_2021_PART_1_AMOUNT_C,
        CHART_2021_PART_2_AMOUNT_C,
        CHART_2022_PART_1_AMOUNT_C,
        CHART_2022_PART_2_AMOUNT_C,
        CHART_2023_PART_1_AMOUNT_C,
        CHART_2023_PART_2_AMOUNT_C,
    )
    for kind in signed:
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is False, kind.identifier
    for kind in (
        T657_CHART_2021_AMOUNT_D_INSTEAD,
        T657_CHART_2021_AMOUNT_I,
        T657_CHART_2022_AMOUNT_D_INSTEAD,
        T657_CHART_2022_AMOUNT_I,
        T657_CHART_2023_AMOUNT_D_INSTEAD,
        T657_CHART_2023_AMOUNT_I,
        CHART_2021_PART_1_AMOUNT_A,
        CHART_2021_AMOUNT_D,
        CHART_2021_PART_1_AMOUNT_E,
        CHART_2021_PART_1_AMOUNTS_F_AND_G,
        CHART_2021_PART_1_AMOUNT_H,
        CHART_2021_PART_1_AMOUNT_I,
        CHART_2021_PART_1_AMOUNT_J,
        CHART_2021_PART_1_AMOUNT_K,
        CHART_2021_PART_1_AMOUNT_M,
        CHART_2021_PART_1_AMOUNT_N,
        CHART_2021_PART_2_AMOUNT_A,
        CHART_2021_PART_2_AMOUNT_E,
        CHART_2022_PART_1_AMOUNT_A,
        CHART_2022_AMOUNT_D,
        CHART_2022_PART_1_AMOUNT_E,
        CHART_2022_PART_1_AMOUNTS_F_AND_G,
        CHART_2022_PART_1_AMOUNT_H,
        CHART_2022_PART_1_AMOUNT_I,
        CHART_2022_PART_1_AMOUNT_J,
        CHART_2022_PART_1_AMOUNT_K,
        CHART_2022_PART_1_AMOUNT_M,
        CHART_2022_PART_1_AMOUNT_N,
        CHART_2022_PART_2_AMOUNT_A,
        CHART_2022_PART_2_AMOUNT_E,
        CHART_2023_PART_1_AMOUNT_A,
        CHART_2023_AMOUNT_D,
        CHART_2023_PART_1_AMOUNT_E,
        CHART_2023_PART_1_AMOUNTS_F_AND_G,
        CHART_2023_PART_1_AMOUNT_H,
        CHART_2023_PART_1_AMOUNT_I,
        CHART_2023_PART_1_AMOUNT_J,
        CHART_2023_PART_1_AMOUNT_K,
        CHART_2023_PART_1_AMOUNT_M,
        CHART_2023_PART_1_AMOUNT_N,
        CHART_2023_PART_2_AMOUNT_A,
        CHART_2023_PART_2_AMOUNT_E,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
    for count_kind in (
        T657_CHART_2021_USES_D_INSTEAD,
        T657_CHART_2021_CLAIMS_ADDITIONAL_DEDUCTION,
        T657_CHART_2022_USES_D_INSTEAD,
        T657_CHART_2022_CLAIMS_ADDITIONAL_DEDUCTION,
        T657_CHART_2023_USES_D_INSTEAD,
        T657_CHART_2023_CLAIMS_ADDITIONAL_DEDUCTION,
        CHART_2021_PART_2_APPLIES,
        CHART_2022_PART_2_APPLIES,
        CHART_2023_PART_2_APPLIES,
    ):
        assert count_kind.value_type is int, count_kind.identifier
        assert non_negative(count_kind) is True, count_kind.identifier


def test_the_chart_2024_period_1_amount_b_is_no_longer_a_caller_input(
    registry: ArtifactRegistry,
) -> None:
    # Chart 2024 Period 1's amount B is the total Chart 2023 carries forward, not an input.
    assert "ca/t657_chart_2024_period_1_amount_b" not in registry.identifiers()


def test_the_form_t657_chart_2016_to_2020_amounts_are_money_counts_and_signed_lines() -> None:
    # Amounts D and E of Chart 2016 Part 1 and amounts F and G of Charts 2017 to 2020 (the T2017
    # lines, signed).
    for kind in (
        T657_CHART_2016_AMOUNT_D,
        T657_CHART_2016_AMOUNT_E,
        T657_CHART_2017_AMOUNT_F,
        T657_CHART_2017_AMOUNT_G,
        T657_CHART_2018_AMOUNT_F,
        T657_CHART_2018_AMOUNT_G,
        T657_CHART_2019_AMOUNT_F,
        T657_CHART_2019_AMOUNT_G,
        T657_CHART_2020_AMOUNT_F,
        T657_CHART_2020_AMOUNT_G,
        CHART_2016_PART_2_AMOUNT_C,
        CHART_2017_PART_1_AMOUNT_C,
        CHART_2017_PART_2_AMOUNT_C,
        CHART_2018_PART_1_AMOUNT_C,
        CHART_2018_PART_2_AMOUNT_C,
        CHART_2019_PART_1_AMOUNT_C,
        CHART_2019_PART_2_AMOUNT_C,
        CHART_2020_PART_1_AMOUNT_C,
        CHART_2020_PART_2_AMOUNT_C,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is False, kind.identifier
    for kind in (
        CHART_2016_PART_1_AMOUNT_A,
        CHART_2016_PART_1_AMOUNT_C,
        CHART_2016_AMOUNT_B,
        CHART_2016_PART_1_AMOUNTS_D_AND_E,
        CHART_2016_PART_1_AMOUNT_F,
        CHART_2016_PART_1_AMOUNT_G,
        CHART_2016_PART_1_AMOUNT_H,
        CHART_2017_PART_1_AMOUNT_A,
        CHART_2017_AMOUNT_D,
        CHART_2017_PART_1_AMOUNT_E,
        CHART_2017_PART_1_AMOUNTS_F_AND_G,
        CHART_2017_PART_1_AMOUNT_H,
        CHART_2017_PART_1_AMOUNT_I,
        CHART_2017_PART_1_AMOUNT_K,
        CHART_2017_PART_1_AMOUNT_L,
        CHART_2018_PART_1_AMOUNT_A,
        CHART_2018_AMOUNT_D,
        CHART_2018_PART_1_AMOUNT_E,
        CHART_2018_PART_1_AMOUNTS_F_AND_G,
        CHART_2018_PART_1_AMOUNT_H,
        CHART_2018_PART_1_AMOUNT_I,
        CHART_2018_PART_1_AMOUNT_K,
        CHART_2018_PART_1_AMOUNT_L,
        CHART_2019_PART_1_AMOUNT_A,
        CHART_2019_AMOUNT_D,
        CHART_2019_PART_1_AMOUNT_E,
        CHART_2019_PART_1_AMOUNTS_F_AND_G,
        CHART_2019_PART_1_AMOUNT_H,
        CHART_2019_PART_1_AMOUNT_I,
        CHART_2019_PART_1_AMOUNT_K,
        CHART_2019_PART_1_AMOUNT_L,
        CHART_2020_PART_1_AMOUNT_A,
        CHART_2020_AMOUNT_D,
        CHART_2020_PART_1_AMOUNT_E,
        CHART_2020_PART_1_AMOUNTS_F_AND_G,
        CHART_2020_PART_1_AMOUNT_H,
        CHART_2020_PART_1_AMOUNT_I,
        CHART_2020_PART_1_AMOUNT_K,
        CHART_2020_PART_1_AMOUNT_L,
        CHART_2016_PART_2_AMOUNT_A,
        CHART_2016_PART_2_AMOUNT_E,
        CHART_2017_PART_2_AMOUNT_A,
        CHART_2017_PART_2_AMOUNT_E,
        CHART_2018_PART_2_AMOUNT_A,
        CHART_2018_PART_2_AMOUNT_E,
        CHART_2019_PART_2_AMOUNT_A,
        CHART_2019_PART_2_AMOUNT_E,
        CHART_2020_PART_2_AMOUNT_A,
        CHART_2020_PART_2_AMOUNT_E,
        T657_CHART_2016_AMOUNT_B_INSTEAD,
        T657_CHART_2017_AMOUNT_D_INSTEAD,
        T657_CHART_2018_AMOUNT_D_INSTEAD,
        T657_CHART_2019_AMOUNT_D_INSTEAD,
        T657_CHART_2020_AMOUNT_D_INSTEAD,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
    for count_kind in (
        T657_CHART_2016_USES_D_INSTEAD,
        T657_CHART_2016_CLAIMS_ADDITIONAL_DEDUCTION,
        CHART_2016_PART_2_APPLIES,
        T657_CHART_2017_USES_D_INSTEAD,
        T657_CHART_2017_CLAIMS_ADDITIONAL_DEDUCTION,
        CHART_2017_PART_2_APPLIES,
        T657_CHART_2018_USES_D_INSTEAD,
        T657_CHART_2018_CLAIMS_ADDITIONAL_DEDUCTION,
        CHART_2018_PART_2_APPLIES,
        T657_CHART_2019_USES_D_INSTEAD,
        T657_CHART_2019_CLAIMS_ADDITIONAL_DEDUCTION,
        CHART_2019_PART_2_APPLIES,
        T657_CHART_2020_USES_D_INSTEAD,
        T657_CHART_2020_CLAIMS_ADDITIONAL_DEDUCTION,
        CHART_2020_PART_2_APPLIES,
    ):
        assert count_kind.value_type is int, count_kind.identifier
        assert non_negative(count_kind) is True, count_kind.identifier


def test_the_chart_2021_amount_b_is_no_longer_a_caller_input(
    registry: ArtifactRegistry,
) -> None:
    # Chart 2021 Part 1's amount B is the total Chart 2020 carries forward, not an input.
    assert "ca/t657_chart_2021_amount_b" not in registry.identifiers()


YES_OR_NO_CHECKED = (
    (T657_CHART_2016_USES_D_INSTEAD, T657_CHART_2016_USES_D_INSTEAD_CHECKED),
    (T657_CHART_2017_USES_D_INSTEAD, T657_CHART_2017_USES_D_INSTEAD_CHECKED),
    (T657_CHART_2018_USES_D_INSTEAD, T657_CHART_2018_USES_D_INSTEAD_CHECKED),
    (T657_CHART_2019_USES_D_INSTEAD, T657_CHART_2019_USES_D_INSTEAD_CHECKED),
    (T657_CHART_2020_USES_D_INSTEAD, T657_CHART_2020_USES_D_INSTEAD_CHECKED),
    (T657_CHART_2021_USES_D_INSTEAD, T657_CHART_2021_USES_D_INSTEAD_CHECKED),
    (T657_CHART_2022_USES_D_INSTEAD, T657_CHART_2022_USES_D_INSTEAD_CHECKED),
    (T657_CHART_2023_USES_D_INSTEAD, T657_CHART_2023_USES_D_INSTEAD_CHECKED),
)


@pytest.mark.parametrize(("raw", "checked"), YES_OR_NO_CHECKED, ids=lambda kind: kind.identifier)
def test_each_yes_or_no_checked_kind_is_a_non_negative_count_named_after_its_input(
    raw: ArtifactKind[int], checked: ArtifactKind[int], registry: ArtifactRegistry
) -> None:
    # `ca/yes_or_no_count` checks the caller's 0 or 1 before the steps that read it; a count of 2 or
    # more is refused, not capped.
    assert checked.identifier == f"{raw.identifier}_checked"
    assert registry.get(checked.identifier) is checked
    assert checked.value_type is int
    assert non_negative(checked) is True
