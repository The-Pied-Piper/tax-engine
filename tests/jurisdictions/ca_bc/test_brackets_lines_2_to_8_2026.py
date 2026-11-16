"""2026 `ca-bc/brackets_lines_2_to_8`, taken from T4127 Table 8.1 (British Columbia), July 2026.

The 2026 Form BC428 (CRA 5010-c) text is not yet published, so the dataset cites T4127 and its
header says so. The thresholds are 50,363 / 100,728 / 115,648 / 140,430 / 190,405 / 265,545 (BC's
own 2.2% index) and the rates are 5.60% (up from 5.06%; the July edition only), 7.70%, 10.50%,
12.29% (lines 2 to 8) and 14.70%, 16.80%, 20.50% (lines 9 to 15). This table covers line 1 of
140,430.00 or less. Each `tax_at_start` is derived, not printed: the cumulative tax on the earlier
brackets, rounded half-up to the cent, because the 2026 form's printed constants are not yet
published.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
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
FAMILY = "ca-bc/brackets_lines_2_to_8"
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
LOWERS = ["0", *THRESHOLDS[:3]]
RATES = ["0.056", "0.077", "0.105", "0.1229"]
TAX_AT_START = ["0.00", "2820.33", "6698.43", "8265.03"]
# The first lower bound of lines 9 to 15, where this table ends.
NEXT_LOWER = "140430"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2026, BRACKETS).values


def test_2026_brackets_are_the_three_columns_from_t4127() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.056"), D("0.00")),
        (D("50363.00"), D("0.077"), D("2820.33")),
        (D("100728.00"), D("0.105"), D("6698.43")),
        (D("115648.00"), D("0.1229"), D("8265.03")),
    ]


def test_2026_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2026_brackets_cite_t4127() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).sources == (T4127_URL,)


def test_the_tax_at_each_start_is_recomputed_from_rates_and_thresholds_rounded_half_up() -> None:
    uppers = [*LOWERS[1:], NEXT_LOWER]
    total = D(0)
    expected = []
    for lower, upper, rate in zip(LOWERS, uppers, RATES, strict=True):
        expected.append(total.quantize(CENT, rounding=ROUND_HALF_UP))
        total += D(rate) * (D(upper) - D(lower))
    starts = [b.tax_at_start for b in _schedule().brackets]

    assert starts == expected == [D(x) for x in TAX_AT_START]
    assert all(start is not None and start.as_tuple().exponent == -2 for start in starts)


def test_2026_up_to_is_140430() -> None:
    assert _schedule().up_to == D("140430.00")


def test_the_table_covers_140430_and_not_a_cent_more() -> None:
    schedule = _schedule()

    assert schedule.covers(D("140430.00"))
    assert not schedule.covers(D("140430.01"))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("50362.99", "0.00"),
        ("50363.00", "0.00"),
        ("50363.01", "50363.00"),
        ("100727.99", "50363.00"),
        ("100728.00", "50363.00"),
        ("100728.01", "100728.00"),
        ("115647.99", "100728.00"),
        ("115648.00", "100728.00"),
        ("115648.01", "115648.00"),
        ("140429.99", "115648.00"),
        ("140430.00", "115648.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)


@pytest.mark.parametrize(
    ("amount", "tax"),
    [
        ("0.00", "0.00"),
        ("30000.00", "1680.00"),  # 0.056 x 30,000
        ("50363.00", "2820.328"),  # 0.056 x 50,363: the 2,820.33 start is this, to the cent
        ("70000.00", "4332.379"),  # 2,820.33 + 0.077 x (70,000 - 50,363)
        ("100728.00", "6698.435"),  # 2,820.33 + 0.077 x 50,365
        ("115648.00", "8265.03"),  # 6,698.43 + 0.105 x 14,920
        (
            "140430.00",
            "11310.7378",
        ),  # 8,265.03 + 0.1229 x 24,782: within half a cent of the next start
    ],
)
def test_the_tax_on_an_amount_is_worked_by_hand(amount: str, tax: str) -> None:
    assert _schedule().tax_on(D(amount)) == D(tax)


def test_the_tax_at_the_split_is_within_half_a_cent_of_the_next_tables_tax_at_start() -> None:
    # The starts are rounded half-up to the cent, so the two tables meet to within half a cent.
    high = SOURCE.get("ca-bc/brackets_lines_9_to_15", 2026, BRACKETS).values

    start = high.brackets[0].tax_at_start
    assert start is not None
    assert abs(_schedule().tax_on(D("140430.00")) - start) <= D("0.005")


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    lines = (root / "parameters" / "brackets_lines_2_to_8" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_brackets_are_unchanged() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert schedule.up_to == D("137407.00")
    assert [(b.lower, b.rate, b.tax_at_start) for b in schedule.brackets] == [
        (D("0.00"), D("0.0506"), D("0.00")),
        (D("49279.00"), D("0.077"), D("2493.52")),
        (D("98560.00"), D("0.105"), D("6288.15")),
        (D("113158.00"), D("0.1229"), D("7820.94")),
    ]
