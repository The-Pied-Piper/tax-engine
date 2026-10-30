"""CA-ON 2025 end to end, Return A carrying Form RC381: the form's structured trace 1."""

from __future__ import annotations

from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.trace import (
    RateAppliedLine,
)
from tax_engine.jurisdictions.ca.catalog import (
    CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    RC381_PART_3_LINE_20,
    RC381_PART_3_LINE_40,
    RC381_PART_4_LINE_84,
    RC381_PART_4_LINE_85,
    RC381_PART_4_LINE_86,
    RC381_PART_4_LINE_91,
    RC381_PART_4_LINE_91_FROM_LINE_90,
    RC381_PART_4_LINE_111,
    RC381_PART_4_LINE_112,
    RC381_PART_4_LINE_116,
    RC381_PART_4_LINE_116_LESSER,
    RC381_PART_4_LINE_125,
    T4_QPP_CONTRIBUTIONS_BOX_17,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, rc381_own_trace, run_a


def test_the_trace_records_each_total_as_a_structured_line() -> None:
    # The lines of Form RC381's own steps on Return A's inputs, the return carrying one copy of the
    # form instead of its Schedule 8.
    # Return A's T4 box 26 is its 110000 of employment income.
    result = run_a(schedule_8_copies=0, rc381_copies=1)
    trace = rc381_own_trace(result["ca/rc381"][0])
    rated = {line.output: line for line in trace if isinstance(line, RateAppliedLine)}
    assert rated == {
        # Form RC381 Part 4 line 111 "amount from line 84 × 50% =" (the amount for line 31000),
        # line 112 "Amount from line 85 × 50% =", line 125 "Amount from line 86 × 50% =" and line
        # 116 "A × 83.1933% =": Return A has no earnings subject to contributions to speak of (lines
        # 84, 85 and 86 and the amount lettered A are 0.00), so every product is 0.00.
        RC381_PART_4_LINE_111: RateAppliedLine(
            RC381_PART_4_LINE_111,
            RC381_PART_4_LINE_84,
            D("0.00"),
            Rate(D("0.5")),
            CENT,
            D("0.00"),
        ),
        RC381_PART_4_LINE_112: RateAppliedLine(
            RC381_PART_4_LINE_112,
            RC381_PART_4_LINE_85,
            D("0.00"),
            Rate(D("0.5")),
            CENT,
            D("0.00"),
        ),
        RC381_PART_4_LINE_125: RateAppliedLine(
            RC381_PART_4_LINE_125,
            RC381_PART_4_LINE_86,
            D("0.00"),
            Rate(D("0.5")),
            CENT,
            D("0.00"),
        ),
        RC381_PART_4_LINE_116: RateAppliedLine(
            RC381_PART_4_LINE_116,
            RC381_PART_4_LINE_116_LESSER,
            D("0.00"),
            Rate(D("0.831933")),
            CENT,
            D("0.00"),
        ),
        # Form RC381 Part 4 line 91 "amount from line 90 entered as a positive amount × 50% =":
        # line 90 is 0 for Return A, so the base is 0 and so is the 50%.
        RC381_PART_4_LINE_91: RateAppliedLine(
            RC381_PART_4_LINE_91,
            RC381_PART_4_LINE_91_FROM_LINE_90,
            D("0.00"),
            Rate(D("0.5")),
            CENT,
            D("0.00"),
        ),
        # Form RC381 Part 3 line 40 "amount from line 39 x 84.375%": Return A enters no box 17
        # contributions on line 39, so the base is 0 and so is the 84.375%.
        RC381_PART_3_LINE_40: RateAppliedLine(
            RC381_PART_3_LINE_40,
            T4_QPP_CONTRIBUTIONS_BOX_17,
            D("0"),
            Rate(D("0.84375")),
            CENT,
            D("0.00"),
        ),
        # Form RC381 Part 3 line 20 "amount from line 19 x 83.1933%": line 19 is the T4 box 16 total
        # of 4034.10 that Return A enters, 4034.10 x 0.831933 = 3356.1000..., 3356.10.
        RC381_PART_3_LINE_20: RateAppliedLine(
            RC381_PART_3_LINE_20,
            CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
            D("4034.10"),
            Rate(D("0.831933")),
            CENT,
            D("3356.10"),
        ),
    }
