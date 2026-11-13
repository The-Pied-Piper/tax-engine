"""2026 `ca-ab/brackets_lines_9_to_15`, taken from T4127 Table 8.1 (Alberta), January 2026.

The 2026 Form AB428 (CRA 5009-c) text is not yet published, so the dataset cites T4127 and its
header says so. This table covers line 1 above 185,111.00 (the 2025 split was 181,481.00): its
first bracket starts where lines 2 to 8 end, so every amount falls in exactly one of the two tables.
The rates are 13%, 14% and 15%; each `tax_at_start` is carried unrounded and is also recomputed
exactly here from the rates and thresholds, continuing the cumulative tax of lines 2 to 8.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import AmountOutsideBracketRangeError
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/brackets_lines_9_to_15"
LOW_FAMILY = "ca-ab/brackets_lines_2_to_8"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds and rates as printed in T4127 Table 8.1; tax_at_start calculated "
    "as the cumulative tax on the earlier brackets, rounded half-up to the cent (reproduces the "
    "2025 printed constants)."
)
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"

# T4127 Table 8.1 (Alberta) as printed, in bracket order across both line sets.
THRESHOLDS = ["61200", "154259", "185111", "246813", "370220"]
LOWERS = THRESHOLDS[2:]
RATES = ["0.13", "0.14", "0.15"]
TAX_AT_START = ["17904.14", "25925.40", "43202.38"]
# Cumulative tax at 185,111 from lines 2 to 8: 0.08 x 61,200 + 0.10 x 93,059 + 0.12 x 30,852.
TAX_AT_SPLIT = D("0.08") * D("61200") + D("0.10") * D("93059") + D("0.12") * D("30852")


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2026, BRACKETS).values


def test_2026_brackets_are_the_three_columns_from_t4127() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("185111.00"), D("0.13"), D("17904.14")),
        (D("246813.00"), D("0.14"), D("25925.40")),
        (D("370220.00"), D("0.15"), D("43202.38")),
    ]


def test_2026_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2026_brackets_cite_t4127() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).sources == (T4127_URL,)


def test_the_table_has_no_upper_end() -> None:
    assert _schedule().up_to is None


def test_the_tax_at_each_start_is_recomputed_exactly_from_rates_and_thresholds() -> None:
    uppers = [*LOWERS[1:], None]
    total = TAX_AT_SPLIT
    expected = []
    for lower, upper, rate in zip(LOWERS, uppers, RATES, strict=True):
        expected.append(total)
        if upper is not None:
            total += D(rate) * (D(upper) - D(lower))
    starts = [b.tax_at_start for b in _schedule().brackets]

    assert starts == expected == [D(x) for x in TAX_AT_START]
    assert all(start is not None and start.as_tuple().exponent == -2 for start in starts)


def test_the_low_tables_up_to_is_this_tables_first_from() -> None:
    low = SOURCE.get(LOW_FAMILY, 2026, BRACKETS).values

    assert low.up_to == _schedule().brackets[0].lower == D("185111.00")


@pytest.mark.parametrize("amount", ["0", "61200.00", "154259.00", "185110.99", "185111.00"])
def test_a_base_at_or_below_185111_is_outside_the_range(amount: str) -> None:
    schedule = _schedule()

    assert not schedule.covers(D(amount))
    with pytest.raises(AmountOutsideBracketRangeError):
        schedule.column_for(D(amount))


@pytest.mark.parametrize("amount", ["185111.01", "246813.00", "370220.00", "500000"])
def test_a_base_above_185111_is_in_the_range(amount: str) -> None:
    assert _schedule().covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("185111.01", "185111.00"),
        ("246812.99", "185111.00"),
        ("246813.00", "185111.00"),
        ("246813.01", "246813.00"),
        ("370219.99", "246813.00"),
        ("370220.00", "246813.00"),
        ("370220.01", "370220.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)


@pytest.mark.parametrize(
    ("amount", "tax"),
    [
        ("200000.00", "19839.71"),  # 17,904.14 + 0.13 x (200,000 - 185,111)
        ("246813.00", "25925.40"),  # 17,904.14 + 0.13 x 61,702: continuous at the threshold
        ("300000.00", "33371.58"),  # 25,925.40 + 0.14 x (300,000 - 246,813)
        ("370220.00", "43202.38"),  # 25,925.40 + 0.14 x 123,407
        ("400000.00", "47669.38"),  # 43,202.38 + 0.15 x (400,000 - 370,220)
    ],
)
def test_the_tax_on_an_amount_is_worked_by_hand(amount: str, tax: str) -> None:
    assert _schedule().tax_on(D(amount)) == D(tax)


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    lines = (root / "parameters" / "brackets_lines_9_to_15" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_brackets_are_unchanged() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert schedule.brackets[0].lower == D("181481.00")
    assert [b.tax_at_start for b in schedule.brackets] == [
        D("17553.04"),
        D("25417.13"),
        D("42355.31"),
    ]
