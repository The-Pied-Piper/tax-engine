"""2026 `ca-ab/brackets_lines_2_to_8`, taken from T4127 Table 8.1 (Alberta), January 2026.

The 2026 Form AB428 (CRA 5009-c) text is not yet published, so the dataset cites T4127 and its
header says so. The thresholds are 61,200 / 154,259 / 185,111 / 246,813 / 370,220 and the rates are
8%, 10%, 12% (lines 2 to 8) and 13%, 14%, 15% (lines 9 to 15). This table covers line 1 of
185,111.00 or less. Each `tax_at_start` is the cumulative tax on the earlier brackets, calculated exactly from the
rates and thresholds (every value is already exact to the cent, so no rounding is needed) and
carried unrounded, because the 2026 form's printed constants are not yet published.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/brackets_lines_2_to_8"
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
LOWERS = ["0", *THRESHOLDS[:2]]
RATES = ["0.08", "0.10", "0.12"]
TAX_AT_START = ["0.00", "4896.00", "14201.90"]
# The first lower bound of lines 9 to 15, where this table ends.
NEXT_LOWER = "185111"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2026, BRACKETS).values


def test_2026_brackets_are_the_three_columns_from_t4127() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.08"), D("0.00")),
        (D("61200.00"), D("0.10"), D("4896.00")),
        (D("154259.00"), D("0.12"), D("14201.90")),
    ]


def test_2026_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2026_brackets_cite_t4127() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).sources == (T4127_URL,)


def test_the_tax_at_each_start_is_recomputed_exactly_from_rates_and_thresholds() -> None:
    uppers = [*LOWERS[1:], NEXT_LOWER]
    total = D(0)
    expected = []
    for lower, upper, rate in zip(LOWERS, uppers, RATES, strict=True):
        expected.append(total)
        total += D(rate) * (D(upper) - D(lower))
    starts = [b.tax_at_start for b in _schedule().brackets]

    assert starts == expected == [D(x) for x in TAX_AT_START]
    assert all(start is not None and start.as_tuple().exponent == -2 for start in starts)


def test_2026_up_to_is_185111() -> None:
    assert _schedule().up_to == D("185111.00")


def test_the_table_covers_185111_and_not_a_cent_more() -> None:
    schedule = _schedule()

    assert schedule.covers(D("185111.00"))
    assert not schedule.covers(D("185111.01"))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("61199.99", "0.00"),
        ("61200.00", "0.00"),
        ("61200.01", "61200.00"),
        ("154258.99", "61200.00"),
        ("154259.00", "61200.00"),
        ("154259.01", "154259.00"),
        ("185110.99", "154259.00"),
        ("185111.00", "154259.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)


@pytest.mark.parametrize(
    ("amount", "tax"),
    [
        ("0.00", "0.00"),
        ("30000.00", "2400.00"),  # 0.08 x 30,000
        ("61200.00", "4896.00"),  # 0.08 x 61,200: continuous at the first threshold
        ("70000.00", "5776.00"),  # 4,896.00 + 0.10 x (70,000 - 61,200)
        ("154259.00", "14201.90"),  # 4,896.00 + 0.10 x 93,059
        ("160000.00", "14890.82"),  # 14,201.90 + 0.12 x (160,000 - 154,259)
        ("185111.00", "17904.14"),  # 14,201.90 + 0.12 x 30,852: the next table's start
    ],
)
def test_the_tax_on_an_amount_is_worked_by_hand(amount: str, tax: str) -> None:
    assert _schedule().tax_on(D(amount)) == D(tax)


def test_the_tax_at_the_split_equals_the_next_tables_tax_at_start() -> None:
    high = SOURCE.get("ca-ab/brackets_lines_9_to_15", 2026, BRACKETS).values

    assert _schedule().tax_on(D("185111.00")) == high.brackets[0].tax_at_start


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    lines = (root / "parameters" / "brackets_lines_2_to_8" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_brackets_are_unchanged() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert schedule.up_to == D("181481.00")
    assert [(b.lower, b.tax_at_start) for b in schedule.brackets] == [
        (D("0.00"), D("0.00")),
        (D("60000.00"), D("4800.00")),
        (D("151234.00"), D("13923.40")),
    ]
