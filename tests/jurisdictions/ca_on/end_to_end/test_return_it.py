"""CA-ON 2025 end to end: return it (returns/2025_return_it.yaml).

Return IT has the machine of CRA's Guide T4037 depreciable property example (p.20: cost $10,000,
UCC $6,000) sold in each of situations A ($4,000), B ($8,000) and C ($12,000), each a real estate
row (Schedule 3 line 5) answered "depreciable property" 1, a fourth row of ordinary property sold
for $9,500 (cost $10,000, answered 0) and a share row (proceeds $20,000, cost $10,000). The Guide
says "A loss from the sale of depreciable property is not considered to be a capital loss"
(p.19, confirmed 2026-10-25 from the PDF; no .txt published), so rows A and B count 0, row C counts
its gain of 2,000 and the ordinary loss of 500 still offsets: line 5 is 1,500, not the -6,500 the
rows give without the answer. The terminal loss and recapture side of the same example (T776 or
T2125 capital cost allowance) is covered by existing worked returns and is not repeated here.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    CAPITAL_GAINS_AFTER_DEFERRAL,
    CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION,
    CAPITAL_GAINS_BEFORE_RESERVES,
    CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES,
    INCLUDED_CAPITAL_GAIN,
    REAL_ESTATE_GAIN_OR_LOSS,
    SHARE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, RealEstateDisposition, run

# Schedule 3 Part 3 line 5 rows (proceeds, adjusted cost base, outlays, depreciable property).
SITUATION_A: RealEstateDisposition = ("4000", "10000", "0", 1)
SITUATION_B: RealEstateDisposition = ("8000", "10000", "0", 1)
SITUATION_C: RealEstateDisposition = ("12000", "10000", "0", 1)
ORDINARY_PROPERTY: RealEstateDisposition = ("9500", "10000", "0", 0)
ALL_ROWS = (SITUATION_A, SITUATION_B, SITUATION_C, ORDINARY_PROPERTY)
SHARES = ("20000", "10000", "0")


def return_it(real_estate: tuple[RealEstateDisposition, ...] = ALL_ROWS) -> Worksheet:
    """The worksheet of Return IT's Ontario return, as in `returns/2025_return_it.yaml`: the four
    real estate rows and the share row, and no other income."""
    return run("0", (SHARES,), "0", "0", "0", "0", "0", real_estate_dispositions=real_estate)[
        "ca-on/return"
    ][0]


def test_return_it_line_5_counts_0_0_2000_and_minus_500_for_1500() -> None:
    # A: 4,000 - 10,000 = -6,000, a loss on depreciable property counting 0. B: 8,000 - 10,000 =
    # -2,000, counting 0. C: 12,000 - 10,000 = 2,000. Ordinary property: 9,500 - 10,000 = -500,
    # still offsetting. Line 5 = 0 + 0 + 2,000 - 500 = 1,500.
    assert return_it().get(REAL_ESTATE_GAIN_OR_LOSS).value == D("1500")


def test_return_it_with_every_row_answered_0_line_5_would_be_minus_6500() -> None:
    # The same four rows all answered 0: -6,000 - 2,000 + 2,000 - 500 = -6,500.
    unflagged = tuple((p, c, o, 0) for p, c, o, _ in ALL_ROWS)

    assert return_it(unflagged).get(REAL_ESTATE_GAIN_OR_LOSS).value == D("-6500")


def test_return_it_situation_a_alone_has_no_capital_gain_or_loss() -> None:
    # Guide T4037 p.20 A: terminal loss $2,000, no capital gain (and no capital loss either).
    assert return_it((SITUATION_A,)).get(REAL_ESTATE_GAIN_OR_LOSS).value == D("0")


def test_return_it_situation_b_alone_has_no_capital_gain_or_loss() -> None:
    # Guide T4037 p.20 B: recapture $2,000, no capital gain.
    assert return_it((SITUATION_B,)).get(REAL_ESTATE_GAIN_OR_LOSS).value == D("0")


def test_return_it_situation_c_alone_has_a_capital_gain_of_2000() -> None:
    # Guide T4037 p.20 C: recapture $4,000 and capital gain $2,000.
    assert return_it((SITUATION_C,)).get(REAL_ESTATE_GAIN_OR_LOSS).value == D("2000")


def test_return_it_share_line_3_is_10000() -> None:
    # Share row: 20,000 - 10,000 - 0.
    assert return_it().get(SHARE_GAIN_OR_LOSS).value == D("10000")


def test_return_it_line_11_is_carried_through_schedule_3_to_line_21() -> None:
    # Line 11 = 10,000 + 1,500 = 11,500; line 14, 17, 19 and 21 are the same (no deferral, slips,
    # business investment loss reduction or reserves).
    worksheet = return_it()

    assert worksheet.get(CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES).value == D("11500")
    assert worksheet.get(CAPITAL_GAINS_AFTER_DEFERRAL).value == D("11500")
    assert worksheet.get(CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION).value == D("11500")
    assert worksheet.get(CAPITAL_GAINS_BEFORE_RESERVES).value == D("11500")
    assert worksheet.get(CAPITAL_GAIN).value == D("11500")


def test_return_it_taxable_capital_gain_is_half_of_11500_at_5750() -> None:
    # Line 24 = 11,500 x 50% = 5,750.00, so T1 line 12700 is 5,750.00. Without the answer it
    # would be (10,000 - 6,500) x 50% = 1,750.00.
    worksheet = return_it()

    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("5750.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("5750.00")


def test_return_it_trace_says_a_loss_on_depreciable_property_counts_0() -> None:
    rendered = EnglishTraceRenderer().render_all(return_it().trace)

    assert (
        "real_estate_gain_or_loss: disposition 1: gain -6000 = proceeds 4000 less adjusted cost "
        "base 10000 less outlays 0; depreciable property: a loss counts 0 -> 0"
    ) in rendered
    assert (
        "real_estate_gain_or_loss: disposition 4: gain -500 = proceeds 9500 less adjusted cost "
        "base 10000 less outlays 0"
    ) in rendered
