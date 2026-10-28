"""CA-ON 2025 end to end: return cw."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError, ValidationError
from tax_calculator.domain.trace import AtMostLine, RecordTotalLine, SumLine
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    IMMEDIATE_EXPENSING_AGREED_LIMIT,
    IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    IMMEDIATE_EXPENSING_TOTAL_CLAIM,
    RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
)
from tax_calculator.jurisdictions.ca.trace import ImmediateExpensingAgreedLimitLine
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return CW: a rental (Form T776), a shop (Form T2125), a farm (Form T2042) and, in some tests, a
# fishing business (Form T2121), each statement writing off one Class 8 property in full at once
# (column 3 = column 4 = column 9, so column 13 is 0 and the claim, column 21, is column 9). Each
# statement has income of its claim plus 100000, so that the claim is never above the income
# before CCA. Area A endnote 5 limits the total of column 9 to the immediate expensing limit,
# $1.5 million when not associated with another EPOP; the Guides T4002 and T4036 say "The
# deduction is limited to $1.5 million per tax year". The forms are silent on several statements;
# the limit is the person's.
LIMIT = "1500000"


def class_8(claim: str) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Area A, Class 8 bought and expensed in full: column 1, 2, 3, 5, 11, 12, the claim, no
    property left, column 4, column 6 and column 9."""
    return ("8", "0", claim, "0", "0", "0", claim, 0, claim, "0", claim)


def with_income(claim: str) -> str:
    """The income before CCA of a source whose claim is `claim`: 100000 more."""
    return str(D(claim) + D("100000"))


def rental(claim: str, **changes: Any) -> dict[str, Any]:
    return {
        "rental_properties": ((1, "0", with_income(claim)),),
        "rental_cca_classes_rows": ((*class_8(claim), "0"),),
        **changes,
    }


def shop(claim: str, **changes: Any) -> dict[str, Any]:
    return {
        "business": {"gross_sales": with_income(claim)},
        "business_cca_classes_rows": (class_8(claim),),
        **changes,
    }


def farm(claim: str, **changes: Any) -> dict[str, Any]:
    return {
        "farm": {"wheat": with_income(claim)},
        "farm_cca_classes_rows": (class_8(claim),),
        **changes,
    }


def fishing(claim: str, **changes: Any) -> dict[str, Any]:
    return {
        "fish": {"fish_products": with_income(claim)},
        "fish_cca_classes_rows": (class_8(claim),),
        **changes,
    }


def associated(prefix: str, percentage: str) -> dict[str, Any]:
    """Area G: associated with one other EPOP (1) under an agreement that was filed (1), the
    percentage assigned to the statement `percentage` and the total of column 3 100."""
    return {
        f"{prefix}_epop_associated": 1,
        f"{prefix}_epop_agreement_filed": 1,
        f"{prefix}_epop_percentage": percentage,
        f"{prefix}_epop_percentage_total": "100",
    }


def run_cw(
    *,
    rentals: tuple[Mapping[str, Any], ...] = (),
    shops: tuple[Mapping[str, Any], ...] = (),
    farms: tuple[Mapping[str, Any], ...] = (),
    fishings: tuple[Mapping[str, Any], ...] = (),
) -> Worksheet:
    """The worksheet of the return of Return CW's kind with the given statements: returns/
    2025_return_cw.yaml has a rental of 600000, a shop of 500000 and a farm of 400000."""
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        rental_statements=rentals,
        business_statements=shops,
        farm_statements=farms,
        fish_statements=fishings,
    )["ca-on/return"][0]


def return_cw() -> Worksheet:
    return run_cw(rentals=(rental("600000"),), shops=(shop("500000"),), farms=(farm("400000"),))


# --- the return passes at the limit ------------------------------------------------------------


def test_a_rental_a_shop_and_a_farm_claiming_exactly_the_limit_pass() -> None:
    # Return CW: 600000 + 500000 + 400000 = 1500000, the limit of every statement.
    worksheet = return_cw()

    assert worksheet.get(IMMEDIATE_EXPENSING_TOTAL_CLAIM).value == D("1500000")
    assert worksheet.get(IMMEDIATE_EXPENSING_AGREED_LIMIT).value == D(LIMIT)


def test_the_totals_are_one_for_each_form_then_the_grand_total() -> None:
    worksheet = return_cw()

    assert worksheet.get(RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL).value == D("600000")
    assert worksheet.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL).value == D("500000")
    assert worksheet.get(FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL).value == D("400000")
    assert worksheet.get(FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL).value == D("0")
    assert worksheet.get(IMMEDIATE_EXPENSING_CLAIMS_TOTAL).value == D("1500000")


def test_the_trace_shows_one_line_for_each_form_total_then_the_grand_total_then_the_check() -> None:
    trace = return_cw().trace
    totals = {
        "ca/rental_immediate_expensing_claims_total": (D("600000"),),
        "ca/business_immediate_expensing_claims_total": (D("500000"),),
        "ca/farm_immediate_expensing_claims_total": (D("400000"),),
        "ca/fish_immediate_expensing_claims_total": (),
    }

    form_lines = [
        line
        for line in trace
        if isinstance(line, RecordTotalLine) and line.output.identifier in totals
    ]
    assert {line.output.identifier: line.amounts for line in form_lines} == totals
    (grand,) = (
        line
        for line in trace
        if isinstance(line, SumLine)
        and line.output.identifier == "ca/immediate_expensing_claims_total"
    )
    (check,) = (
        line
        for line in trace
        if isinstance(line, AtMostLine)
        and line.output.identifier == "ca/immediate_expensing_total_claim"
    )
    assert grand.total == D("1500000")
    assert (check.amount_value, check.bound_value) == (D("1500000"), D(LIMIT))
    assert max(trace.index(line) for line in form_lines) < trace.index(grand) < trace.index(check)


def test_the_trace_names_the_statements_compared_and_the_agreed_limit() -> None:
    trace = return_cw().trace

    (line,) = (line for line in trace if isinstance(line, ImmediateExpensingAgreedLimitLine))
    assert [
        (kind.identifier, position, claim, limit)
        for kind, position, claim, limit in line.statements
    ] == [
        ("ca/t776.rental_immediate_expensing_limit_unprorated", 1, D("600000"), D(LIMIT)),
        ("ca/t2125.business_immediate_expensing_limit_unprorated", 1, D("500000"), D(LIMIT)),
        ("ca/t2042.farm_immediate_expensing_limit_unprorated", 1, D("400000"), D(LIMIT)),
    ]
    assert line.limit == line.amount == D(LIMIT)
    assert EnglishTraceRenderer().render(line).endswith("agreed limit 1500000")


# --- more than the limit is refused --------------------------------------------------------------


def test_a_shop_and_a_farm_that_together_claim_more_than_the_limit_are_refused() -> None:
    # Each is under the limit by itself (1000000 and 800000), together they are 1800000.
    shop_alone = run_cw(shops=(shop("1000000"),))
    farm_alone = run_cw(farms=(farm("800000"),))
    assert shop_alone.get(IMMEDIATE_EXPENSING_TOTAL_CLAIM).value == D("1000000")
    assert farm_alone.get(IMMEDIATE_EXPENSING_TOTAL_CLAIM).value == D("800000")

    with pytest.raises(
        InputAboveBoundError,
        match=(
            r"ca/immediate_expensing_claims_total 1800000(\.0+)? is above "
            r"ca/immediate_expensing_agreed_limit 1500000(\.0+)?"
        ),
    ):
        run_cw(shops=(shop("1000000"),), farms=(farm("800000"),))


def test_a_total_one_cent_above_the_limit_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/immediate_expensing_claims_total 1500000\.01 is above .* 1500000",
    ):
        run_cw(rentals=(rental("600000"),), shops=(shop("500000"),), farms=(farm("400000.01"),))


def test_a_fishing_statement_counts_toward_the_limit() -> None:
    four = (rental("400000"), shop("400000"), farm("400000"), fishing("300000"))
    assert run_cw(rentals=(four[0],), shops=(four[1],), farms=(four[2],), fishings=(four[3],)).get(
        IMMEDIATE_EXPENSING_TOTAL_CLAIM
    ).value == D("1500000")

    with pytest.raises(InputAboveBoundError, match="1500000.01 is above"):
        run_cw(
            rentals=(four[0],),
            shops=(four[1],),
            farms=(four[2],),
            fishings=(fishing("300000.01"),),
        )


def test_several_statements_of_one_form_count_toward_the_limit() -> None:
    assert run_cw(shops=(shop("700000"), shop("800000"))).get(
        IMMEDIATE_EXPENSING_TOTAL_CLAIM
    ).value == D("1500000")

    with pytest.raises(InputAboveBoundError, match="1500000.01 is above"):
        run_cw(shops=(shop("700000"), shop("800000.01")))


def test_the_total_is_checked_against_the_associated_limit_when_every_claim_shares_it() -> None:
    # Associated at 40% (amount iii 600000) on both statements, the agreement being one document:
    # 350000 + 300000 = 650000 is above 600000, though each is under it.
    both = associated("business", "40")
    both_farm = associated("farm", "40")
    run_cw(shops=(shop("350000", **both),))
    run_cw(farms=(farm("300000", **both_farm),))

    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/immediate_expensing_claims_total 650000 is above "
        r"ca/immediate_expensing_agreed_limit 600000",
    ):
        run_cw(shops=(shop("350000", **both),), farms=(farm("300000", **both_farm),))


def test_exactly_one_statement_over_the_limit_still_refuses_at_the_form() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"total of column 9 \(1500000\.01\) is above the immediate expensing limit",
    ):
        run_cw(shops=(shop("1500000.01"),))


# --- statements of fiscal periods of different lengths --------------------------------------------

# 1 August to 31 December 2025: 153 days, entered as the T2125 From and to dates.
SHORT_PERIOD = {"business_fiscal_period_from": 20250801, "business_fiscal_period_to": 20251231}
SHORT_PERIOD_LIMIT = "628767.12"


def test_a_short_period_shop_and_a_full_year_farm_claiming_within_the_limit_pass() -> None:
    # Guide T4002: "The limit is also prorated for tax years shorter than 365 days". The shop's
    # own limit is 1500000 x 153 / 365 = 628767.12 and the farm's is 1500000; the person's limit,
    # compared before the days scaling, is 1500000, and 600000 + 800000 = 1400000 is under it.
    worksheet = run_cw(
        shops=(shop("600000", **SHORT_PERIOD),),
        farms=(farm("800000"),),
    )

    assert worksheet.get(IMMEDIATE_EXPENSING_AGREED_LIMIT).value == D(LIMIT)
    assert worksheet.get(IMMEDIATE_EXPENSING_TOTAL_CLAIM).value == D("1400000")


def test_the_trace_compares_the_limits_before_the_days_scaling() -> None:
    trace = run_cw(shops=(shop("600000", **SHORT_PERIOD),), farms=(farm("800000"),)).trace

    (line,) = (line for line in trace if isinstance(line, ImmediateExpensingAgreedLimitLine))
    assert [
        (kind.identifier, position, claim, limit)
        for kind, position, claim, limit in line.statements
    ] == [
        ("ca/t2125.business_immediate_expensing_limit_unprorated", 1, D("600000"), D(LIMIT)),
        ("ca/t2042.farm_immediate_expensing_limit_unprorated", 1, D("800000"), D(LIMIT)),
    ]


def test_a_short_period_shop_and_a_full_year_farm_over_the_limit_together_are_refused() -> None:
    # Each is within its own limit (628767.12 and 1500000), together 1528767.12 is above 1500000.
    run_cw(shops=(shop(SHORT_PERIOD_LIMIT, **SHORT_PERIOD),))
    run_cw(farms=(farm("900000"),))

    with pytest.raises(
        InputAboveBoundError,
        match=(
            r"ca/immediate_expensing_claims_total 1528767\.12 is above "
            r"ca/immediate_expensing_agreed_limit 1500000"
        ),
    ):
        run_cw(
            shops=(shop(SHORT_PERIOD_LIMIT, **SHORT_PERIOD),),
            farms=(farm("900000"),),
        )


def test_a_short_period_shop_above_its_own_scaled_limit_is_still_refused_by_the_form() -> None:
    # The form's own check stays on the limit scaled by its days: 628767.13 is one cent above it.
    with pytest.raises(
        InputAboveBoundError,
        match=r"total of column 9 \(628767\.13\) is above the immediate expensing limit",
    ):
        run_cw(shops=(shop("628767.13", **SHORT_PERIOD),), farms=(farm("100000"),))


# --- statements whose limits disagree -------------------------------------------------------------


def test_statements_claiming_with_different_limits_are_refused_naming_both() -> None:
    # The rental is associated at 40% (amount iii 600000); the shop is not (1500000).
    with pytest.raises(ValidationError) as raised:
        run_cw(
            rentals=(rental("100000", **associated("rental", "40")),),
            shops=(shop("100000"),),
        )

    assert str(raised.value).endswith(
        "immediate expensing limit differs between statements: "
        "ca/t776.rental_immediate_expensing_limit_unprorated statement 1 has 600000.00, "
        "ca/t2125.business_immediate_expensing_limit_unprorated statement 1 has 1500000.00"
    )


def test_two_statements_of_one_form_with_different_limits_are_refused_naming_both() -> None:
    with pytest.raises(ValidationError) as raised:
        run_cw(farms=(farm("100000"), farm("100000", **associated("farm", "60"))))

    assert str(raised.value).endswith(
        "immediate expensing limit differs between statements: "
        "ca/t2042.farm_immediate_expensing_limit_unprorated statement 1 has 1500000.00, "
        "ca/t2042.farm_immediate_expensing_limit_unprorated statement 2 has 900000.00"
    )


def test_a_statement_claiming_nothing_with_a_different_limit_is_not_compared() -> None:
    # The rental has no write-off and no Area G (limit 1500000); the shop is associated at 60%
    # (900000) and claims 500000: no refusal, and the person's limit is the shop's.
    worksheet = run_cw(
        rentals=(rental("0"),),
        shops=(shop("500000", **associated("business", "60")),),
    )

    assert worksheet.get(IMMEDIATE_EXPENSING_AGREED_LIMIT).value == D("900000")
    assert worksheet.get(IMMEDIATE_EXPENSING_TOTAL_CLAIM).value == D("500000")


def test_a_total_above_the_limit_of_the_claiming_statements_is_refused_not_the_unused_limit() -> (
    None
):
    # The rental claims nothing (1500000); the shop's 900000 limit is the person's, and 950000 is
    # above it, refused at the form.
    with pytest.raises(InputAboveBoundError, match="immediate expensing limit"):
        run_cw(
            rentals=(rental("0"),),
            shops=(shop("950000", **associated("business", "60")),),
        )


# --- no immediate expensing ----------------------------------------------------------------------


def test_no_statements_give_a_limit_of_zero_and_a_total_of_zero() -> None:
    worksheet = run_cw()

    assert worksheet.get(IMMEDIATE_EXPENSING_CLAIMS_TOTAL).value == D("0")
    assert worksheet.get(IMMEDIATE_EXPENSING_AGREED_LIMIT).value == D("0")
    assert worksheet.get(IMMEDIATE_EXPENSING_TOTAL_CLAIM).value == D("0")


def test_statements_claiming_nothing_give_a_limit_of_zero_and_a_total_of_zero() -> None:
    worksheet = run_cw(
        rentals=(rental("0"),),
        shops=(shop("0", **associated("business", "60")),),
    )

    assert worksheet.get(IMMEDIATE_EXPENSING_AGREED_LIMIT).value == D("0")
    assert worksheet.get(IMMEDIATE_EXPENSING_TOTAL_CLAIM).value == D("0")
