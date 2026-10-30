"""CA-ON 2025 end to end: return mr (Guide T4037 "Restricted farm loss", the RFL balance).

Guide T4037 (2025), p.34: "The amount of RFLs that you can apply cannot be more than the property
taxes and interest on money you borrowed to buy the farmland that were included in the calculation
of the RFLs for each year." and "Also, you have to reduce your RFL balance by these amounts." The
unapplied RFL of 20,000 from 2000 holds 10,000 of property taxes and interest (5,000 and 5,000), the
pool that may be applied. Each farmland row applies at most its own part (checked by the list's
capability), and the total applied over the real estate, qualified farm or fishing property and
foreclosure lists is refused above the pool, not capped.

The worked return `returns/2025_return_mr.yaml` (checked by `test_worked_returns.py`) pins the
figures; this module tests the sum across the lists and the refusal.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    OTHER_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
    QFFP_RESTRICTED_FARM_LOSS_APPLIED,
    REAL_ESTATE_GAIN_OR_LOSS,
    REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED,
    RESTRICTED_FARM_LOSS_APPLIED_CHECKED,
    RESTRICTED_FARM_LOSS_APPLIED_TOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    FarmlandDisposition,
    QffpFarmlandDisposition,
    run,
)

# Real estate: proceeds 200000, ACB 160000 (the Guide's line B), outlays 0, not depreciable
# property, 10000 of property taxes and interest in the restricted farm loss, 5000 of property
# taxes (line C) and 5000 of interest (line D) added to the cost base.
REAL_ESTATE: FarmlandDisposition = ("200000", "160000", "0", 0, "10000", "5000", "5000")
# Qualified farm or fishing property: proceeds 50000, ACB 30000, 10000 applied (5000 and 5000), a
# gain of 20000 before the farm loss, so the applied amount is at most the gain.
QFFP: QffpFarmlandDisposition = ("50000", "30000", "0", "10000", "5000", "5000")
# The same row as a sale of 30000 with an ACB of 30000: no gain and no farm loss applied.
QFFP_NOTHING_APPLIED: QffpFarmlandDisposition = ("30000", "30000", "0", "0", "0", "0")


def run_mr(
    *,
    real_estate: tuple[FarmlandDisposition, ...] = (),
    qffp: tuple[QffpFarmlandDisposition, ...] = (),
    foreclosures: tuple[QffpFarmlandDisposition, ...] = (),
    other_foreclosures: tuple[QffpFarmlandDisposition, ...] = (),
    pool: str = "10000",
) -> dict[str, tuple[Worksheet, ...]]:
    return run(
        employment_income="0",
        share_dispositions=(),
        unused_rrsp_contributions="0",
        rrsp_contributions="0",
        rrsp_deduction_limit="0",
        rrsp_amount_deducted="0",
        union_dues="0",
        real_estate_dispositions=real_estate,
        qffp_dispositions=qffp,
        qffp_foreclosure_dispositions=foreclosures,
        other_foreclosure_dispositions=other_foreclosures,
        unapplied_restricted_farm_loss_taxes_and_interest=pool,
    )


# The refusal names the total over every list and the pool, both as the engine prints them.
ABOVE_THE_POOL = (
    r"ca/restricted_farm_loss_applied_total 20000 is above "
    r"ca/unapplied_restricted_farm_loss_taxes_and_interest 10000"
)


def test_the_real_estate_and_qffp_applications_are_summed_against_the_pool() -> None:
    # Each row passes alone (10000 against its own part of 10000); together they apply 20000.
    with pytest.raises(InputAboveBoundError, match=ABOVE_THE_POOL):
        run_mr(real_estate=(REAL_ESTATE,), qffp=(QFFP,))


def test_the_real_estate_and_foreclosure_applications_are_summed_against_the_pool() -> None:
    with pytest.raises(InputAboveBoundError, match=ABOVE_THE_POOL):
        run_mr(real_estate=(REAL_ESTATE,), foreclosures=(QFFP,))


def test_each_list_alone_applies_the_whole_pool_and_is_accepted() -> None:
    real_estate_only = run_mr(real_estate=(REAL_ESTATE,))["ca-on/return"][0]
    qffp_only = run_mr(qffp=(QFFP,))["ca-on/return"][0]

    assert real_estate_only.get(RESTRICTED_FARM_LOSS_APPLIED_CHECKED).value == D("10000")
    assert qffp_only.get(RESTRICTED_FARM_LOSS_APPLIED_CHECKED).value == D("10000")


def test_applying_exactly_the_pool_across_the_lists_is_accepted() -> None:
    worksheet = run_mr(real_estate=(REAL_ESTATE,), qffp=(QFFP_NOTHING_APPLIED,))["ca-on/return"][0]

    assert worksheet.get(REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED).value == D("10000")
    assert worksheet.get(QFFP_RESTRICTED_FARM_LOSS_APPLIED).value == D("0")
    assert worksheet.get(RESTRICTED_FARM_LOSS_APPLIED_TOTAL).value == D("10000")
    assert worksheet.get(RESTRICTED_FARM_LOSS_APPLIED_CHECKED).value == D("10000")


def test_applying_less_than_the_pool_is_accepted_as_claimed() -> None:
    # 5000 applied (2500 and 2500) of the 10000 pool: the gain is 200000 - 160000 - 5000 = 35000.
    row: FarmlandDisposition = ("200000", "160000", "0", 0, "5000", "2500", "2500")
    worksheet = run_mr(real_estate=(row,))["ca-on/return"][0]

    assert worksheet.get(REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED).value == D("5000")
    assert worksheet.get(RESTRICTED_FARM_LOSS_APPLIED_TOTAL).value == D("5000")
    assert worksheet.get(RESTRICTED_FARM_LOSS_APPLIED_CHECKED).value == D("5000")
    assert worksheet.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("35000")


def test_a_pool_of_zero_refuses_any_application() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/restricted_farm_loss_applied_total 10000 is above "
        r"ca/unapplied_restricted_farm_loss_taxes_and_interest 0",
    ):
        run_mr(real_estate=(REAL_ESTATE,), pool="0")


def test_a_sale_with_no_gain_and_no_farm_loss_adds_nothing_to_the_total() -> None:
    worksheet = run_mr(real_estate=(REAL_ESTATE,), qffp=(QFFP_NOTHING_APPLIED,))["ca-on/return"][0]

    assert worksheet.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("30000")
    assert worksheet.get(QFFP_RESTRICTED_FARM_LOSS_APPLIED).value == D("0")


def test_the_real_estate_and_other_foreclosure_applications_are_summed_against_the_pool() -> None:
    with pytest.raises(InputAboveBoundError, match=ABOVE_THE_POOL):
        run_mr(real_estate=(REAL_ESTATE,), other_foreclosures=(QFFP,))


def test_the_other_foreclosure_list_alone_applies_the_whole_pool_and_is_accepted() -> None:
    worksheet = run_mr(other_foreclosures=(QFFP,))["ca-on/return"][0]

    assert worksheet.get(OTHER_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED).value == D("10000")
    assert worksheet.get(RESTRICTED_FARM_LOSS_APPLIED_CHECKED).value == D("10000")
