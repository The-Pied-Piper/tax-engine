"""CA-ON 2025 end to end: return jt."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITH_DEPENDANT,
    CWB_FAMILY_NET_INCOME_LINE_12,
    CWB_FAMILY_NET_INCOME_LINE_13,
    CWB_FAMILY_WORKING_INCOME,
    CWB_LINE_28_BY_SPOUSE,
    CWB_REDUCTION_WITH_DEPENDANT,
    CWB_SECONDARY_EARNER_EXEMPTION,
    CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM,
    CWB_SECONDARY_EARNER_SPOUSES,
    CWB_SECONDARY_EARNER_YOURS,
    CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12,
    CWB_SPOUSE_WORKING_INCOME,
    CWB_WORKING_INCOME_LESS_SPOUSE,
    NET_INCOME,
    WORKING_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, service, spouse_inputs, starting

CA_ON = JurisdictionCode("CA-ON")


def return_jt(**overrides: Any) -> Worksheet:
    """Return JT's inputs (`returns/2025_return_jt.yaml`): a filer and an eligible spouse.

    The filer's income is other employment income of 20000.00 (line 10400), with no T4 employment,
    so no CPP or EI premium; the spouse's working income and net income are both 12000.00.
    `overrides` replace any keyword of `starting`.
    """
    given: dict[str, Any] = {
        "other_employment_income": "20000",
        "spouse_net_income": "12000",
        "spouse_net_income_before_adjustments": "12000",
        "spouse_or_common_law_partner_on_december_31": 1,
    }
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        **{**spouse_inputs("12000", overrides), **given, **overrides},
    )
    return service().compute(CA_ON, 2025, *artifacts)["ca-on/return"][0]


def test_return_jt_net_income_is_the_other_employment_income_of_20000() -> None:
    # Other employment income (line 10400) of 20000.00 is the whole of total income (line 15000),
    # with no deduction (no T4 employment, so no CPP or EI premium): net income is 20000.00.
    worksheet = return_jt()

    assert worksheet.get(NET_INCOME).value == D("20000.00")


def test_return_jt_schedule_6_column_1_and_2_working_income() -> None:
    # Column 1 line 5: the other employment income, 20000.00, with no scholarships or
    # self-employment income. Column 2 line 5: the spouse's employment income, 12000.00.
    # Line 6: 20000.00 + 12000.00 = 32000.00, the family working income.
    worksheet = return_jt()

    assert worksheet.get(WORKING_INCOME).value == D("20000.00")
    assert worksheet.get(CWB_SPOUSE_WORKING_INCOME).value == D("12000.00")
    assert worksheet.get(CWB_FAMILY_WORKING_INCOME).value == D("32000.00")


def test_return_jt_line_14_takes_the_spouse_column_as_the_filers_income_is_not_less() -> None:
    # Line 12: column 1 is 20000.00 (net income, nothing to take off); column 2 is the spouse's
    # 12000.00. Line 13 is 32000.00. The filer's working income (20000.00) is equal to or more
    # than the spouse's (12000.00), so line 14 is the less of the spouse's column 2 figures,
    # 12000.00 and 12000.00, which is 12000.00: under the $16,386 maximum, so not capped.
    # Line 15 is 32000.00 - 12000.00 = 20000.00.
    worksheet = return_jt()

    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_12).value == D("20000.00")
    assert worksheet.get(CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12).value == D("12000.00")
    assert worksheet.get(CWB_FAMILY_NET_INCOME_LINE_13).value == D("32000.00")
    assert worksheet.get(CWB_WORKING_INCOME_LESS_SPOUSE).value == D("8000.00")
    assert worksheet.get(CWB_SECONDARY_EARNER_YOURS).value == D("20000.00")
    assert worksheet.get(CWB_SECONDARY_EARNER_SPOUSES).value == D("12000.00")
    assert worksheet.get(CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM).value == D("12000.00")
    assert worksheet.get(CWB_SECONDARY_EARNER_EXEMPTION).value == D("12000.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("20000.00")


def test_return_jt_canada_workers_benefit_is_the_maximum_of_2813_with_an_eligible_spouse() -> None:
    # Line 16 is 32000.00; line 18 is 29000.00; line 20 is 27% of it, 7830.00, so line 22 is the
    # lesser of 7830.00 and line 21's $2,813 (an eligible spouse), 2813.00. Line 23 is 20000.00,
    # below the $30,639 of line 24, so line 25 is 0 and line 28 is 2813.00 - 0 = 2813.00: the
    # Canada workers benefit, which is the figure of line 45300.
    worksheet = return_jt()

    assert worksheet.get(CWB_LINE_28_BY_SPOUSE).value == D("2813.00")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITH_DEPENDANT).value == D("2813.00")
    assert worksheet.get(CWB_REDUCTION_WITH_DEPENDANT).value == D("0.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITH_DEPENDANT).value == D("2813.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("2813.00")
