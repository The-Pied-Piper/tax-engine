"""2026 `ca-bc/brackets_lines_9_to_15`, taken from T4127 Table 8.1 (British Columbia), July 2026.

The 2026 Form BC428 (CRA 5010-c) text is not yet published, so the dataset cites T4127 and its
header says so. This table covers line 1 above 140,430.00 (the 2025 split was 137,407.00): its
first bracket starts where lines 2 to 8 end, so every amount falls in exactly one of the two tables.
The rates are 14.7%, 16.8% and 20.5%; each `tax_at_start` is derived, not printed, and is recomputed
here from the rates and thresholds, continuing the cumulative tax of lines 2 to 8, rounded half-up
to the cent.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import AmountOutsideBracketRangeError
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

D = Decimal
CENT = D("0.01")
# British Columbia is not in `registrations.JURISDICTIONS` yet; the source uses its own packages.
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/brackets_lines_9_to_15"
LOW_FAMILY = "ca-bc/brackets_lines_2_to_8"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jul 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds are T4127 Table 8.1 (BC indexes at its own 2.2%, not the federal "
    "factor) and the rates are as printed there, the first rate rising from 5.06% to 5.60% for "
    "2026 on (the July edition only; the January edition still shows 5.06%). tax_at_start is "
    "derived, not printed: the cumulative tax on the earlier brackets at those rates, rounded "
    "half-up to the cent (reproduces the 2025 printed constants)."
)
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-07-26e.pdf"

# T4127 Table 8.1 (British Columbia) as printed, in bracket order across both line sets.
THRESHOLDS = ["50363", "100728", "115648", "140430", "190405", "265545"]
LOWERS = THRESHOLDS[3:]
RATES = ["0.147", "0.168", "0.205"]
TAX_AT_START = ["11310.74", "18657.07", "31280.59"]
# Cumulative tax at 140,430 from lines 2 to 8, unrounded: four columns up to the split.
TAX_AT_SPLIT = (
    D("0.056") * D("50363")
    + D("0.077") * D("50365")
    + D("0.105") * D("14920")
    + D("0.1229") * D("24782")
)


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2026, BRACKETS).values


def test_2026_brackets_are_the_three_columns_from_t4127() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("140430.00"), D("0.147"), D("11310.74")),
        (D("190405.00"), D("0.168"), D("18657.07")),
        (D("265545.00"), D("0.205"), D("31280.59")),
    ]


def test_2026_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2026_brackets_cite_t4127() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).sources == (T4127_URL,)


def test_the_table_has_no_upper_end() -> None:
    assert _schedule().up_to is None


def test_the_tax_at_each_start_is_recomputed_from_rates_and_thresholds_rounded_half_up() -> None:
    uppers = [*LOWERS[1:], None]
    total = TAX_AT_SPLIT
    expected = []
    for lower, upper, rate in zip(LOWERS, uppers, RATES, strict=True):
        expected.append(total.quantize(CENT, rounding=ROUND_HALF_UP))
        if upper is not None:
            total += D(rate) * (D(upper) - D(lower))
    starts = [b.tax_at_start for b in _schedule().brackets]

    assert starts == expected == [D(x) for x in TAX_AT_START]
    assert all(start is not None and start.as_tuple().exponent == -2 for start in starts)


def test_the_low_tables_up_to_is_this_tables_first_from() -> None:
    low = SOURCE.get(LOW_FAMILY, 2026, BRACKETS).values

    assert low.up_to == _schedule().brackets[0].lower == D("140430.00")


@pytest.mark.parametrize("amount", ["0", "50363.00", "115648.00", "140429.99", "140430.00"])
def test_a_base_at_or_below_140430_is_outside_the_range(amount: str) -> None:
    schedule = _schedule()

    assert not schedule.covers(D(amount))
    with pytest.raises(AmountOutsideBracketRangeError):
        schedule.column_for(D(amount))


@pytest.mark.parametrize("amount", ["140430.01", "190405.00", "265545.00", "500000"])
def test_a_base_above_140430_is_in_the_range(amount: str) -> None:
    assert _schedule().covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("140430.01", "140430.00"),
        ("190404.99", "140430.00"),
        ("190405.00", "140430.00"),
        ("190405.01", "190405.00"),
        ("265544.99", "190405.00"),
        ("265545.00", "190405.00"),
        ("265545.01", "265545.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)


@pytest.mark.parametrize(
    ("amount", "tax"),
    [
        ("140430.01", "11310.74147"),  # 11,310.74 + 0.147 x 0.01 (the rounded start, then the rate)
        ("160000.00", "14176.97"),  # 11,310.74 + 0.147 x (160,000 - 140,430)
        ("200000.00", "20269.03"),  # 18,657.07 + 0.168 x (200,000 - 190,405)
        ("250000.00", "28669.03"),  # 18,657.07 + 0.168 x (250,000 - 190,405)
        ("265545.00", "31280.59"),  # 18,657.07 + 0.168 x 75,140: the 31,280.59 start, to the cent
        ("300000.00", "38343.865"),  # 31,280.59 + 0.205 x (300,000 - 265,545)
    ],
)
def test_the_tax_on_an_amount_is_worked_by_hand(amount: str, tax: str) -> None:
    assert _schedule().tax_on(D(amount)) == D(tax)


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    lines = (root / "parameters" / "brackets_lines_9_to_15" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_brackets_are_unchanged() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert schedule.brackets[0].lower == D("137407.00")
    assert [b.tax_at_start for b in schedule.brackets] == [
        D("10801.15"),
        D("17989.30"),
        D("30341.16"),
    ]
