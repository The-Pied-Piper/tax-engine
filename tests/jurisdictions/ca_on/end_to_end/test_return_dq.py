"""CA-ON 2025 end to end: return dq (other employment income in the employment amount and LIFT)."""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CANADA_EMPLOYMENT_AMOUNT,
    CANADA_EMPLOYMENT_AMOUNT_INCOME,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting


def return_dq(employment: str = "500", other: str = "2000") -> Worksheet:
    """Return DQ's inputs as in `returns/2025_return_dq.yaml`, over the two employment keywords.

    The filer has employment income of 500 and other employment income of 2,000 (chosen figures),
    and nothing else.
    """
    base = starting(employment, (), "0", "0", "0", "0", "0", other_employment_income=other)
    return service().compute(CA_ON, 2025, *base)["ca-on/return"][0]


def test_the_canada_employment_amount_is_capped_on_line_1_plus_line_2() -> None:
    # T1 line 92 (line 31260) "Enter whichever is less: $1,471 or line 1 plus line 2.": 500 plus
    # 2,000 is 2,500, above the cap of 1,471, so the amount is 1,471.
    worksheet = return_dq()

    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT_INCOME).value == D("2500")
    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("1471.00")


def test_the_lift_credit_before_maximum_is_5_05_percent_of_line_1_plus_line_2() -> None:
    # Schedule ON428-A line 3 "Line 1 plus line 2": 500 plus 2,000 is 2,500. Line 5 "Line 3
    # multiplied by the percentage from line 4 (maximum $875)": 2,500 at 5.05% is 126.25, under
    # the maximum of 875.
    worksheet = return_dq()

    assert worksheet.get(ontario.LIFT_EMPLOYMENT_INCOME).value == D("2500")
    assert worksheet.get(ontario.LIFT_CREDIT_BEFORE_MAXIMUM).value == D("126.25")
    assert worksheet.get(ontario.LIFT_MAXIMUM_CREDIT).value == D("126.25")


def test_the_lift_credit_for_a_single_individual_is_the_whole_credit_with_no_reduction() -> None:
    # Line 17 "Line 15 minus line 16 (if negative, enter "0")": 2,500 less 32,500, not below zero,
    # so line 19 is 0 and line 20 "Line 14 minus line 19" is 126.25.
    worksheet = return_dq()

    assert worksheet.get(ontario.LIFT_REDUCTION).value == D("0")
    assert worksheet.get(ontario.LIFT_CREDIT_SINGLE).value == D("126.25")


def test_the_traces_read_the_sums_and_the_cap_and_the_rate() -> None:
    rendered = EnglishTraceRenderer().render_all(return_dq().trace)

    assert (
        "canada_employment_amount_income: employment_income 500 + "
        "other_employment_income 2000 = 2500"
    ) in rendered
    assert (
        "canada_employment_amount: lesser of canada_employment_amount_income 2500 and 1471 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "lift_employment_income: employment_income 500 + other_employment_income 2000 = 2500"
    ) in rendered
    assert (
        "lift_credit_before_maximum: 5.05% of lift_employment_income 2500 (half-up to 0.01)"
    ) in rendered


def test_500_and_300_gives_a_canada_employment_amount_of_800() -> None:
    # T1 line 92: 500 plus 300 is 800, under the cap of 1,471, so the amount is 800.
    worksheet = return_dq(other="300")

    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT_INCOME).value == D("800")
    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("800")


def test_other_employment_income_alone_is_a_canada_employment_amount_and_a_lift_base() -> None:
    # T1 line 92: 0 plus 2,000 is 2,000, above the cap, so 1,471. ON428-A line 3: 0 plus 2,000 is
    # 2,000 and line 5 is 2,000 at 5.05%, 101.
    worksheet = return_dq(employment="0", other="2000")

    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("1471.00")
    assert worksheet.get(ontario.LIFT_EMPLOYMENT_INCOME).value == D("2000")
    assert worksheet.get(ontario.LIFT_CREDIT_BEFORE_MAXIMUM).value == D("101.00")
