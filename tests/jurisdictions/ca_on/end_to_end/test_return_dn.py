"""CA-ON 2025 end to end: return dn."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CREDITS_AGAINST_FEDERAL_TAX,
    FEDERAL_LOGGING_TAX_CREDIT,
    FEDERAL_TAX,
    FEDERAL_TAX_LESS_CREDITS,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    LOGGING_CREDIT_BASE,
    LOGGING_CREDIT_CAP,
    PROVINCES_LOGGING_TAX_CREDIT,
    TAXABLE_INCOME,
)
from tax_engine.jurisdictions.ca.trace import LoggingTaxCreditLine
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# The two provinces of Return DN, as its inputs give them (`returns/2025_return_dn.yaml`).
FIRST_PROVINCE = {"tax_paid": "300", "net_logging_income": "6000"}
SECOND_PROVINCE = {"tax_paid": "900", "net_logging_income": "3000"}


def return_dn(
    *provinces: dict[str, str], other_income: str = "50000"
) -> dict[str, tuple[Worksheet, ...]]:
    """Return DN's worksheets for the provinces given (both by default), with the other income of
    50,000 (the taxable income of line 26000) unless another is given."""
    given = provinces or (FIRST_PROVINCE, SECOND_PROVINCE)
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income=other_income,
        logging_provinces=given,
    )


def worksheet_dn(*provinces: dict[str, str], other_income: str = "50000") -> Worksheet:
    return return_dn(*provinces, other_income=other_income)["ca-on/return"][0]


def test_the_two_provinces_give_200_and_200_for_a_provinces_total_of_400() -> None:
    worksheet = worksheet_dn()

    assert worksheet.get(PROVINCES_LOGGING_TAX_CREDIT).value == D("400.00")


def test_each_province_is_a_line_of_its_own_by_position() -> None:
    lines: list[Any] = [
        line for line in worksheet_dn().trace if isinstance(line, LoggingTaxCreditLine)
    ]

    assert [line.position for line in lines] == [1, 2]
    assert [line.result for line in lines] == [D("200.00"), D("200.00")]
    # Province 2: 66.6667% of 900 is 600.00 and 6.6667% of 3,000 is 200.00: the income side.
    assert lines[1].tax_share == D("600.00")
    assert lines[1].income_share == D("200.00")


def test_the_cap_is_6_6667_percent_of_the_50000_of_taxable_income() -> None:
    worksheet = worksheet_dn()

    assert worksheet.get(TAXABLE_INCOME).value == D("50000")
    assert worksheet.get(LOGGING_CREDIT_BASE).value == D("50000.00")
    assert worksheet.get(LOGGING_CREDIT_CAP).value == D("3333.35")


def test_line_133_is_the_provinces_total_when_the_cap_is_above_it() -> None:
    assert worksheet_dn().get(FEDERAL_LOGGING_TAX_CREDIT).value == D("400.00")


def test_line_134_is_line_132_less_line_133() -> None:
    worksheet = worksheet_dn()

    assert worksheet.get(FEDERAL_TAX).value == (
        worksheet.get(FEDERAL_TAX_WITH_ITC_RECAPTURE).value - D("400.00")
    )


def test_line_139_reads_line_134_and_not_line_132() -> None:
    worksheet = worksheet_dn()

    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == (
        worksheet.get(FEDERAL_TAX).value - worksheet.get(CREDITS_AGAINST_FEDERAL_TAX).value
    )


def test_the_acceptance_example_of_one_province_gives_line_133_of_200() -> None:
    # Tax paid 300 and net logging income 6,000 in one province, taxable income 50,000: the lesser
    # of 200.00 and 400.00 is 200.00, under the cap of 3,333.35.
    worksheet = worksheet_dn(FIRST_PROVINCE)

    assert worksheet.get(FEDERAL_LOGGING_TAX_CREDIT).value == D("200.00")


def test_the_cap_binds_when_taxable_income_is_5000() -> None:
    # 6.6667% of 5,000 is 333.335, rounded half-up to 333.34: the cap, under the provinces' 400.00.
    worksheet = worksheet_dn(other_income="5000")

    assert worksheet.get(LOGGING_CREDIT_CAP).value == D("333.34")
    assert worksheet.get(PROVINCES_LOGGING_TAX_CREDIT).value == D("400.00")
    assert worksheet.get(FEDERAL_LOGGING_TAX_CREDIT).value == D("333.34")


def test_no_logging_provinces_give_line_133_of_zero() -> None:
    # No province with a logging operation: the list is empty, and line 133 is 0 (the cap is not
    # what limits it, the provinces' total is 0).
    no_provinces = run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="50000",
        logging_provinces=(),
    )["ca-on/return"][0]

    assert no_provinces.get(PROVINCES_LOGGING_TAX_CREDIT).value == D("0")
    assert no_provinces.get(FEDERAL_LOGGING_TAX_CREDIT).value == D("0")
