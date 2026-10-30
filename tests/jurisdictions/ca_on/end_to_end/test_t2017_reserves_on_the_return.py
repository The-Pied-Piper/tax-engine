"""CA-ON 2025 end to end: the Form T2017 reserves as the return reads them.

The summary form `ca/t2017` exports line 13 and line 31 (Part 1). The return reads line 31 as
Schedule 3 line 19200, the one record total of its export, which is added to the capital gains
before reserves (line 21, `ca/capital_gain`); Form T657 Step 1 line 2 reads line 13 the same way. A
reserve claimed on a row is refused above its maximum through the return as through the form alone.

The figures are chosen: one row (or the 2024 line 30 figure) on each of the T2017 lines that reach
the return, with no other figures on the return.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.errors import InputAboveBoundError, UnknownRegistrationError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ANNUAL_GAINS_LINE_2,
    ANNUAL_GAINS_LINE_3,
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    SCHEDULE_3_LINE_19200,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, service

# A line 27 row (the four-year kind): gain 10,000, payable 5,000 of proceeds 10,000, the year of
# disposition, so the maximum is the lesser of 5,000 and 80% of 10,000, which is 5,000.
LINE_27_ROW: dict[str, Any] = {
    "capital_gain": "10000",
    "payable": "5000",
    "proceeds": "10000",
    "years": 0,
    "claimed": "750",
    "previous": "0",
}


def return_with(
    *,
    amounts: Mapping[int, str] | None = None,
    rows: Mapping[int, tuple[Mapping[str, Any], ...]] | None = None,
) -> Worksheet:
    """The return with the Form T2017 figures given and every other input blank."""
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t2017_amounts=dict(amounts or {}),
        t2017_rows=dict(rows or {}),
    )


def test_a_2024_reserve_on_line_30_is_brought_into_income_on_schedule_3_line_19200() -> None:
    # Line 30 "Amount of 2024 reserve for dispositions before November 13, 1981" is 9,000 and no
    # disposition has a reserve: line 31 is 9,000, the capital gain is 9,000, and half is taxable.
    worksheet = return_with(amounts={30: "9000"})

    assert worksheet.get(SCHEDULE_3_LINE_19200).value == D("9000.00")
    assert worksheet.get(CAPITAL_GAIN).value == D("9000.00")
    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("4500.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("4500.00")


def test_a_line_27_claim_reduces_the_capital_gain_on_schedule_3_line_19200() -> None:
    # The claim of 750 is a deduction from income: line 28 is (750), line 31 is (750), so the
    # capital gain is (750), half of it (375) is not taxable, and the taxable gains are 0.
    worksheet = return_with(rows={27: (LINE_27_ROW,)})

    assert worksheet.get(SCHEDULE_3_LINE_19200).value == D("-750.00")
    assert worksheet.get(CAPITAL_GAIN).value == D("-750.00")
    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("-375.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0.00")


def test_a_line_2_reserve_is_line_13_of_the_summary_and_flows_to_t657_step_1_line_3() -> None:
    # A nine-year line 2 row of a 200,000 gain, in the year of disposition (90% is 180,000), claims
    # 100,000: line 13 is (100,000), so Step 1 line 2 is (100,000) and line 3 is (100,000). Line 16
    # of 100,000 brings line 19 and line 31 back to 0, so Schedule 3 line 19200 is 0.
    worksheet = return_with(
        amounts={16: "100000"},
        rows={
            2: (
                {
                    "capital_gain": "200000",
                    "payable": "200000",
                    "proceeds": "200000",
                    "years": 0,
                    "claimed": "100000",
                    "previous": "0",
                    "nine_year": 1,
                },
            )
        },
    )

    assert worksheet.get(ANNUAL_GAINS_LINE_2).value == D("-100000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_3).value == D("-100000.00")
    assert worksheet.get(SCHEDULE_3_LINE_19200).value == D("0.00")


def test_a_claim_above_the_maximum_is_refused_through_the_return_not_capped() -> None:
    # The maximum of the line 27 row is 5,000; a claim of 5,000.01 is refused by the row form, and
    # the return, which runs it, refuses too.
    with pytest.raises(InputAboveBoundError):
        return_with(rows={27: ({**LINE_27_ROW, "claimed": "5000.01"},)})


def test_the_typed_reserve_and_t657_inputs_are_no_longer_registered() -> None:
    # The return's typed inputs are retired: their figures come from the summary form's exports.
    service()  # registers the catalogs

    for identifier in ("ca/capital_gains_reserves", "ca/t657_t2017_line_13"):
        with pytest.raises(UnknownRegistrationError):
            ArtifactRegistry.shared().get(identifier)
