"""CA-ON 2025 end to end: return is (returns/2025_return_is.yaml).

Return IS has three personal-use property rows, the figures of CRA's Guide T4037 example (p.24),
and no other income. Each row's proceeds and adjusted cost base are raised to the Guide's $1,000
minimum where lower, so every figure is worked by hand from the Guide's chart below, not taken
from the engine: the china cabinet gives 0, the boat 150 and the personal computer a loss
counting 0.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    CAPITAL_GAINS_AFTER_DEFERRAL,
    CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION,
    CAPITAL_GAINS_BEFORE_RESERVES,
    CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES,
    INCLUDED_CAPITAL_GAIN,
    PERSONAL_USE_PROPERTY_GAIN,
    PERSONAL_USE_PROPERTY_GAIN_ROWS,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Schedule 3 Part 3 rows (proceeds, adjusted cost base, outlays), Guide T4037 p.24: the china
# cabinet 900, 500, 0; the boat 1,200, 850, 50; the personal computer 1,500, 3,200, 30.
CHINA_CABINET = ("900", "500", "0")
BOAT = ("1200", "850", "50")
PERSONAL_COMPUTER = ("1500", "3200", "30")


def run_is() -> dict[str, tuple[Worksheet, ...]]:
    """Return IS's inputs, as in `returns/2025_return_is.yaml`: the three personal-use rows and no
    other income."""
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        personal_use_property_dispositions=(CHINA_CABINET, BOAT, PERSONAL_COMPUTER),
    )


def return_is() -> Worksheet:
    """The worksheet of Return IS's Ontario return."""
    return run_is()["ca-on/return"][0]


def test_return_is_line_9_is_150_the_boats_gain_with_the_1000_minimum() -> None:
    # China cabinet: 1,000 - 1,000 - 0 = 0. Boat: 1,200 - 1,000 - 50 = 150 (ACB 850 raised to
    # 1,000). Personal computer: 1,500 - 3,200 - 30 = -1,730, a loss counting 0. Line 9 = 150.
    worksheet = return_is()

    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN_ROWS).value == D("150")
    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN).value == D("150")


def test_return_is_line_9_is_carried_through_schedule_3_to_line_21() -> None:
    # Line 11 = 0 + ... + 150 = 150; line 14 = 150 (no deferral); line 17 = 150 (no slips);
    # line 19 = 150 (no business investment loss reduction); line 21 = 150 (no reserves).
    worksheet = return_is()

    assert worksheet.get(CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES).value == D("150")
    assert worksheet.get(CAPITAL_GAINS_AFTER_DEFERRAL).value == D("150")
    assert worksheet.get(CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION).value == D("150")
    assert worksheet.get(CAPITAL_GAINS_BEFORE_RESERVES).value == D("150")
    assert worksheet.get(CAPITAL_GAIN).value == D("150")


def test_return_is_taxable_capital_gain_is_half_of_150_at_75() -> None:
    # Line 24 = 150 x 50% = 75.00, positive, so T1 line 12700 is 75.00.
    worksheet = return_is()

    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("75.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("75.00")


def test_return_is_trace_names_the_boat_row_with_the_minimum_applied() -> None:
    rendered = EnglishTraceRenderer().render_all(return_is().trace)

    assert (
        "personal_use_property_gain_rows: disposition 2: gain 150 = proceeds 1200 (greater of "
        "1200 and minimum 1000) less adjusted cost base 1000 (greater of 850 and minimum 1000) "
        "less outlays 50; gain only 150, not below 0"
    ) in rendered
