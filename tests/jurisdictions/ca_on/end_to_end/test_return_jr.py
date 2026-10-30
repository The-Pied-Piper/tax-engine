"""CA-ON 2025 end to end: return jr, Guide T4036's Salvador with a smaller loss on the third
building, rental properties each on its own Form T776 whose CCA is limited as a whole."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    NET_RENTAL_INCOME,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES,
    RENTAL_CCA_CLAIMS_TOTAL,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_LIMIT_ALL_STATEMENTS,
    RENTAL_CCA_TOTAL_CLAIM,
    RENTAL_INCOME_BEFORE_CCA,
    RENTAL_INCOME_BEFORE_CCA_TOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, run

# Guide T4036, "Limits on CCA": "If you own more than one rental property, you have to calculate
# your overall net income or loss for the year from all your rental properties before you can claim
# CCA. If you are a partner, include the net rental income or loss from your T5013 slip in the
# calculation. ... You cannot use CCA to create or increase a rental loss." Salvador's three
# buildings, with the third building's loss changed from (4,000) to (1,000): the net income before
# CCA of each is a chosen figure, other income (line 8230) of 1,500 and 2,000 and an advertising
# expense (line 8521) of 1,000, an overall 2,500. Each building's UCC at the start is a chosen
# figure, as in Return ED.


def class_row(
    class_number: str, ucc_at_start: str, claim: str = "0"
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str]:
    """An Area A row: the class, its UCC at the start (column 2, a chosen figure), no additions,
    no proceeds, the CCA claimed (column 23), property left in the class, no DIEP, no immediate
    expensing and no remaining personal part of the property's cost."""
    return (class_number, ucc_at_start, "0", "0", "0", "0", claim, 0, "0", "0", "0", "0")


def building_1(claim: str = "1000.00") -> dict[str, Any]:
    return {
        "rental_other_income": "1500",
        "rental_cca_classes_rows": (class_row("1", "100000.00", claim), class_row("8", "10000.00")),
    }


def building_2(claim: str = "1500.00") -> dict[str, Any]:
    return {
        "rental_other_income": "2000",
        "rental_cca_classes_rows": (class_row("1", "80000.00", claim), class_row("8", "5000.00")),
    }


def building_3(loss: str = "1000") -> dict[str, Any]:
    return {
        "rental_expenses": {"advertising": (loss, "0", "0")},
        "rental_cca_classes_rows": (class_row("3", "60000.00"), class_row("8", "8000.00")),
    }


def jr_inputs(statements: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    """Return JR's inputs, as in `returns/2025_return_jr.yaml`: a landlord with the T776
    `statements` given, no employment income, no RRSP, no union dues, no business, no farm, no
    fishing and no other income."""
    return {
        "employment_income": "0",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "rental_statements": statements,
        "business_statements": (),
        "farm_statements": (),
        "fish_statements": (),
    }


def return_jr(*statements: dict[str, Any]) -> Worksheet:
    """The worksheet of return JR's form `ca-on/return` with the T776 `statements`."""
    return compute(**jr_inputs(statements))


def run_jr(*statements: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return JR with the T776 `statements`."""
    return run(**jr_inputs(statements))


def three_buildings() -> dict[str, tuple[Worksheet, ...]]:
    return run_jr(building_1(), building_2(), building_3())


def test_each_statements_line_9936_is_its_claim() -> None:
    statements = three_buildings()["ca/t776"]

    assert [statement.get(RENTAL_CCA_CLAIM).value for statement in statements] == [
        D("1000.00"),
        D("1500.00"),
        D("0"),
    ]


def test_each_statements_net_income_before_cca_is_its_amount_5() -> None:
    statements = three_buildings()["ca/t776"]

    assert [statement.get(RENTAL_INCOME_BEFORE_CCA).value for statement in statements] == [
        D("1500"),
        D("2000"),
        D("-1000"),
    ]


def test_the_overall_net_income_before_cca_is_the_limit_of_all_the_claims() -> None:
    # Guide T4036: "Combine the rental income and loss from all your properties": 1,500 + 2,000 +
    # (-1,000) = 2,500, the most the CCA of all the buildings may be.
    worksheet = return_jr(building_1(), building_2(), building_3())

    assert worksheet.get(RENTAL_INCOME_BEFORE_CCA_TOTAL).value == D("2500")
    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("2500")


def test_claims_equal_to_the_overall_limit_are_accepted_and_line_12600_is_0() -> None:
    # 1,000.00 + 1,500.00 = 2,500.00, equal to the limit: accepted. Line 12600 is the overall
    # 2,500 less the 2,500.00 of CCA: no loss is created or increased.
    worksheet = return_jr(building_1(), building_2(), building_3())

    assert worksheet.get(RENTAL_CCA_CLAIMS_TOTAL).value == D("2500.00")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("2500.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("0.00")


def test_a_cent_more_in_total_is_refused_by_the_combined_limit() -> None:
    # 1,000.00 + 1,500.01 is 2,500.01, above the overall 2,500: refused, not capped.
    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 2500\.01 is above ca/rental_cca_limit_all_statements 2500",
    ):
        return_jr(building_1(), building_2("1500.01"), building_3())


def test_a_loss_on_another_building_lowers_the_limit_of_every_claim() -> None:
    # Building 3's loss of 1,500 instead of 1,000 makes the overall figure 2,000, so the same
    # claims of 2,500.00 are refused.
    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 2500\.00 is above ca/rental_cca_limit_all_statements 2000",
    ):
        return_jr(building_1(), building_2(), building_3("1500"))


def test_guide_t4036_salvador_with_an_overall_loss_cannot_claim_cca_on_building_1() -> None:
    # The Guide's example: 1,500 + 2,000 + (-4,000) = (-500), so "he cannot claim any CCA". Building
    # 1's claim of 1,000.00 is refused by the overall limit, 0.
    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 1000\.00 is above ca/rental_cca_limit_all_statements 0",
    ):
        return_jr(building_1(), building_2("0"), building_3("4000"))


def test_a_claim_above_its_own_statements_income_is_accepted_within_the_combined_limit() -> None:
    # Statement A has 10,000 of net income before CCA and no claim; statement B has an advertising
    # expense of 2,000 (amount 5 of -2,000) and a CCA claim of 3,000.00. No limit applies to one
    # statement alone, and the combined limit is 10,000 - 2,000 = 8,000, so 3,000.00 is accepted.
    statement_a: dict[str, Any] = {"rental_other_income": "10000"}
    statement_b: dict[str, Any] = {
        "rental_expenses": {"advertising": ("2000", "0", "0")},
        "rental_cca_classes_rows": (class_row("1", "100000.00", "3000.00"),),
    }

    worksheet = return_jr(statement_a, statement_b)

    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("8000")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("3000.00")


def test_no_claim_is_accepted_with_an_overall_loss() -> None:
    worksheet = return_jr(building_1("0"), building_2("0"), building_3("4000"))

    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("0")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("0")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("-500.00")


def test_a_t5013_slip_partners_loss_counts_in_the_overall_figure() -> None:
    # "If you are a partner, include the net rental income or loss from your T5013 slip in the
    # calculation": building 1's 1,500 and a slip loss of (1,000) on amount 7 are an overall 500, so
    # the 1,000.00 claim on building 1 is refused.
    partnership: dict[str, Any] = {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 1,
        "rental_partner_share": "-1000",
    }

    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 1000\.00 is above ca/rental_cca_limit_all_statements 500",
    ):
        return_jr(building_1(), partnership)


def test_a_slip_partners_own_expenses_and_rebate_are_not_in_the_overall_figure() -> None:
    # Regulation 1100(11)(b) and (d), as printed in IT-195R4: "the income of a partnership for the
    # year from renting or leasing rental property of the partnership, to the extent of the
    # taxpayer's share of such income". Lines 9943 (own expenses, 1,000) and 9974 (rebate) are
    # the partner's own and are not in the share: a slip of 600 and an own building earning 500
    # before CCA make an overall 1,100.
    partnership: dict[str, Any] = {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 1,
        "rental_partner_share": "600",
        "rental_partner_other_expenses": "1000",
        "rental_partner_gst_hst_rebate": "50",
    }
    own = own_building("1100.00", rental_other_income="500")

    worksheet = return_jr(own, partnership)

    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("1100")
    with pytest.raises(InputAboveBoundError, match=r"1100\.01 is above"):
        return_jr(own_building("1100.01", rental_other_income="500"), partnership)


def test_a_t5013_slip_partners_income_raises_the_overall_figure_and_claims_nothing() -> None:
    # Building 1's 1,500 and a slip income of 600 on amount 7 are an overall 2,100; the slip's CCA
    # is already in box 110, so the only claim is building 1's 1,000.00.
    partnership: dict[str, Any] = {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 1,
        "rental_partner_share": "600",
    }

    worksheet = return_jr(building_1(), partnership)

    assert worksheet.get(RENTAL_CCA_CLAIMS_TOTAL).value == D("1000.00")
    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("2100")


def test_a_cca_claim_on_the_form_of_a_t5013_slip_partner_is_refused() -> None:
    # Guide T4036: "Do not use the amount from line 9936 if you are a member of a partnership that
    # has to file Form T5013 SUM ... Your CCA amount is already included in box 110".
    partnership: dict[str, Any] = {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 1,
        "rental_partner_share": "600",
        "rental_cca_classes_rows": (class_row("1", "50000.00", "100.00"),),
    }

    with pytest.raises(InputOutOfRangeError, match=r"rental_t5013_slip_conflict"):
        return_jr(partnership)


def test_the_t5013_slip_answer_yes_needs_the_partner_answer_yes() -> None:
    with pytest.raises(InputOutOfRangeError, match=r"rental_t5013_slip_conflict"):
        return_jr({"rental_partner": 0, "rental_partner_t5013_slip": 1})


def test_the_t5013_slip_answer_of_2_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=r"rental_partner_t5013_slip 2"):
        return_jr({"rental_partner": 1, "rental_partner_t5013_slip": 2})


# IT-195R4 (docs/cra-forms-2025/web/it195r4-rental-property-cca-restrictions.txt, web page) para
# 10: "A partnership that is subject to the CCA restriction calculates the amount of CCA it can
# claim and allocates the resulting net rental income or loss among the members of the
# partnership. ... The share of partnership rental income or loss allocated to the member will be
# combined with the total rental income or loss after expenses, but before CCA, from the member's
# own rental properties. CCA may be claimed on the member's rental properties (subject to
# prescribed rates) only to the extent of that combined rental income, if any." So a partner
# statement (a slip or no slip) contributes its amount 7 alone (the slip's amount, or its share of
# amount 6), which is already after the partnership's CCA, and its own line 9936 is the
# partnership's depreciation, not a claim on the member's own properties.


def partner_without_slip(percentage: str, **figures: Any) -> dict[str, Any]:
    """A statement of a partner who received no slip, with "Your percentage of the partnership %"
    `percentage`, so amount 7 is that percentage of amount 6."""
    return {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 0,
        "rental_partner_percentage": percentage,
        **figures,
    }


def own_building(claim: str = "0", **figures: Any) -> dict[str, Any]:
    """A statement of the member's own building, with the CCA `claim` of a Class 1 row."""
    return {
        "rental_cca_classes_rows": (class_row("1", "100000.00", claim),),
        **figures,
    }


def test_a_partner_without_a_slip_contributes_its_share_alone_to_the_overall_figure() -> None:
    # The partnership's net income is 300 after its own CCA, so amount 6 is 300 and the share at
    # 100% is 300; the own building earns 200 before CCA. Limit: 300 + 200 = 500.
    partner = partner_without_slip("100", rental_other_income="300")
    own = own_building(rental_other_income="200")

    statements = run_jr(own, partner)["ca/t776"]

    assert [statement.get(RENTAL_INCOME_BEFORE_CCA).value for statement in statements] == [
        D("200"),
        D("300"),
    ]
    assert return_jr(own, partner).get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("500")


def test_the_own_claim_equal_to_the_share_plus_the_own_income_is_accepted() -> None:
    # Limit 300 + 200 = 500; the own claim of 500.00 equals it. T1 line 12600 = 300 (the share) +
    # (200 - 500.00) (the own building) = 0.00, which is 300 + 200 - 500.00, not below zero.
    partner = partner_without_slip("100", rental_other_income="300")
    own = own_building("500.00", rental_other_income="200")

    worksheet = return_jr(own, partner)

    assert worksheet.get(RENTAL_CCA_CLAIMS_TOTAL).value == D("500.00")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("500.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("0.00")


def test_a_cent_more_own_claim_than_the_share_plus_the_own_income_is_refused() -> None:
    partner = partner_without_slip("100", rental_other_income="300")
    own = own_building("500.01", rental_other_income="200")

    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 500\.01 is above ca/rental_cca_limit_all_statements 500",
    ):
        return_jr(own, partner)


def test_the_partner_statements_own_line_9936_is_not_a_claim_on_the_own_properties() -> None:
    # The partnership rents 1500 and spends 500, so amount 5 is 1000; its own line 9936 of 1000 is
    # the depreciation allocated to the partner, so amount 6 and the share are 0. The own
    # building loses 100 and claims nothing: the limit is 0 + (-100), floored at 0, and the claims
    # on the own properties are 0, so it is accepted. T1 line 12600 = 0 + (-100) = -100.
    partner = partner_without_slip(
        "100",
        rental_other_income="1500",
        rental_expenses={"advertising": ("500", "0", "0")},
        rental_cca_classes_rows=(class_row("1", "100000.00", "1000.00"),),
    )
    own: dict[str, Any] = {"rental_expenses": {"advertising": ("100", "0", "0")}}

    worksheet = return_jr(own, partner)
    statements = run_jr(own, partner)["ca/t776"]

    assert statements[1].get(RENTAL_CCA_CLAIM).value == D("1000.00")
    assert statements[1].get(RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES).value == D("0")
    assert statements[0].get(RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES).value == D("0")
    assert worksheet.get(RENTAL_CCA_CLAIMS_TOTAL).value == D("0")
    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("0")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("0")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("-100")


def test_a_partner_statements_negative_line_9936_is_not_a_claim_on_the_own_properties() -> None:
    # No form line bounds the personal part of the CCA, so the partner statement's line 9936 is
    # 100 - 300 = -200; it is the partnership's figure, not a claim on the own properties, so the
    # claims on the own properties and their total stay 0 and nothing is refused.
    partner = partner_without_slip(
        "100",
        rental_other_income="1500",
        rental_expenses={"advertising": ("500", "0", "0")},
        rental_cca_classes_rows=(class_row("1", "100000.00", "100.00"),),
        rental_cca_personal_part="300",
    )
    own: dict[str, Any] = {"rental_expenses": {"advertising": ("100", "0", "0")}}

    worksheet = return_jr(own, partner)
    statements = run_jr(own, partner)["ca/t776"]

    assert statements[1].get(RENTAL_CCA_CLAIM).value == D("-200.00")
    assert statements[1].get(RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES).value == D("0")
    assert worksheet.get(RENTAL_CCA_CLAIMS_TOTAL).value == D("0")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("0")


def test_an_owner_statement_keeps_its_line_9936_as_a_claim_on_the_own_properties() -> None:
    statements = run_jr(building_1(), building_2(), building_3())["ca/t776"]

    assert [
        statement.get(RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES).value for statement in statements
    ] == [D("1000.00"), D("1500.00"), D("0")]


def test_a_co_owner_statement_is_unchanged_amount_5_and_its_line_9936() -> None:
    # A co-owner (a partner answer of 0) takes amount 5: the whole of line 9369 is 1000 and the
    # co-owner's share of it 400, so amount 5 is 400, and its line 9936 is a claim on the own
    # properties.
    co_owner_statement: dict[str, Any] = {
        "rental_coowner": 1,
        "rental_coowner_share": "400",
        "rental_coowner_cca_claim": "400.00",
        "rental_other_income": "1000",
        "rental_cca_classes_rows": (class_row("1", "100000.00", "400.00"),),
    }

    worksheet = return_jr(co_owner_statement)

    assert worksheet.get(RENTAL_INCOME_BEFORE_CCA_TOTAL).value == D("400")
    assert worksheet.get(RENTAL_CCA_CLAIMS_TOTAL).value == D("400.00")


def test_a_partner_claim_above_amount_5_is_not_refused() -> None:
    # Amount 5 is 1000 (other income, no expenses) and the partner's own line 9936 is 1500.00,
    # more than that: T776 prints no check of a partner's line 9936 against amount 5 (the
    # partnership's return is where its CCA is limited), so amount 6 is 1000 - 1500.00 = -500.00
    # and the share of that loss at 100%, -500.00, is accepted. The claim is the partnership's, so
    # it adds nothing to the member's own CCA.
    partner = partner_without_slip(
        "100",
        rental_other_income="1000",
        rental_cca_classes_rows=(class_row("1", "100000.00", "1500.00"),),
    )

    statement = run_jr(partner)["ca/t776"][0]

    assert statement.get(RENTAL_CCA_LIMIT).value == D("1000")
    assert return_jr(partner).get(RENTAL_CCA_TOTAL_CLAIM).value == D("0")


def test_an_owner_statement_has_no_limit_of_its_own_beside_another_statement() -> None:
    # The owner's statement has amount 5 of -3000 and a claim of 4000.00, more than its own
    # amount 5; the other statement earns 10000, so the combined limit is 7000 and the claim is
    # accepted.
    loss_owner: dict[str, Any] = {
        "rental_expenses": {"advertising": ("3000", "0", "0")},
        "rental_cca_classes_rows": (class_row("1", "100000.00", "4000.00"),),
    }
    other: dict[str, Any] = {"rental_other_income": "10000"}

    worksheet = return_jr(loss_owner, other)

    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("7000")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("4000.00")


def test_a_co_owner_statement_has_no_limit_of_its_own_either() -> None:
    # A co-owner's share of line 9369 is -300 (400 of other income less 700 advertising is -300, all
    # of it the co-owner's) and a claim of 300.00 is accepted beside a statement that earns 1000.
    co_owner: dict[str, Any] = {
        "rental_coowner": 1,
        "rental_coowner_share": "-300",
        "rental_coowner_cca_claim": "300.00",
        "rental_other_income": "400",
        "rental_expenses": {"advertising": ("700", "0", "0")},
        "rental_cca_classes_rows": (class_row("1", "100000.00", "300.00"),),
    }
    other: dict[str, Any] = {"rental_other_income": "1000"}

    worksheet = return_jr(co_owner, other)

    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("700")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("300.00")


def test_a_t5013_slip_partner_cannot_enter_a_claim() -> None:
    partnership: dict[str, Any] = {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 1,
        "rental_partner_share": "600",
    }

    with pytest.raises(InputOutOfRangeError, match=r"rental_t5013_slip_conflict"):
        return_jr(
            {**partnership, "rental_cca_classes_rows": (class_row("1", "50000.00", "100.00"),)}
        )


def test_a_partner_without_a_slip_contributes_its_percentage_of_amount_6_to_the_total() -> None:
    # Amount 6 is 300 (other income, no expenses, no CCA) and the partner's percentage is 50, so
    # amount 7 is 150.00; the own building earns 200 before CCA. Limit: 150.00 + 200 = 350.00.
    partner = partner_without_slip("50", rental_other_income="300")
    own = own_building(rental_other_income="200")

    worksheet = return_jr(own, partner)

    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("350.00")


def test_a_t5013_slip_partners_amount_7_is_the_slip_as_typed() -> None:
    # The slip's amount is not a share of amount 6, which is 0 here: 600 and -600 are accepted and
    # the statement's figure for the limit is the slip's amount alone.
    for share in ("600", "-600"):
        partnership: dict[str, Any] = {
            "rental_partner": 1,
            "rental_partner_t5013_slip": 1,
            "rental_partner_share": share,
        }
        statement = run_jr(partnership)["ca/t776"][0]

        assert statement.get(RENTAL_INCOME_BEFORE_CCA).value == D(share)


def test_a_t5013_slip_partner_may_adjust_amount_7_by_lines_9974_and_9943() -> None:
    # Guide T4036: "You may need to adjust your share ... on amount 7 if: you received a GST/HST
    # rebate for partners (line 9974); you are claiming deductible expenses you had as a partner
    # that you did not deduct elsewhere (line 9943)": these two are no conflict.
    partnership: dict[str, Any] = {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 1,
        "rental_partner_share": "600",
        "rental_partner_gst_hst_rebate": "50",
        "rental_partner_other_expenses": "20",
    }

    worksheet = return_jr(partnership)

    assert worksheet.get(NET_RENTAL_INCOME).value == D("630")


T5013_SLIP_PARTNER_FIGURES: dict[str, dict[str, Any]] = {
    "gross rents": {"rental_properties": ((1, "0", "1200"),)},
    "other income": {"rental_other_income": "1"},
    "an expense": {"rental_expenses": {"utilities": ("1", "0", "0")}},
    "a recapture": {
        "rental_cca_classes_rows": (
            ("8", "1000", "0", "5000", "0", "0", "0", 0, "0", "0", "0", "0"),
        )
    },
    "a terminal loss": {
        "rental_cca_classes_rows": (("8", "1000", "0", "0", "0", "0", "0", 1, "0", "0", "0", "0"),)
    },
    "a land addition": {"rental_land_additions": "1"},
    "a land disposition": {"rental_land_dispositions": "1"},
}


@pytest.mark.parametrize("figure", T5013_SLIP_PARTNER_FIGURES)
def test_a_t5013_slip_partner_with_a_figure_other_than_amount_7_is_refused(figure: str) -> None:
    # Guide T4036: a partner who received the slip fills in only the business number, the
    # percentage and amount 7 (adjusted by lines 9974 and 9943).
    partnership: dict[str, Any] = {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 1,
        "rental_partner_share": "600",
        **T5013_SLIP_PARTNER_FIGURES[figure],
    }

    with pytest.raises(InputOutOfRangeError, match=r"rental_t5013_slip_conflict"):
        return_jr(partnership)


# Area A rows with a claim of 0 (column 23) that still enter a figure of the form: the columns are
# class, 2, 3, 5, 11, 12, 23, property left, 4, 6, 9 and the Note 9 amount.
T5013_SLIP_PARTNER_AREA_A_ROWS: dict[str, tuple[Any, ...]] = {
    "an opening UCC": ("1", "1000", "0", "0", "0", "0", "0", 0, "0", "0", "0", "0"),
    "additions": ("1", "0", "500", "0", "0", "0", "0", 0, "0", "0", "0", "0"),
    # The Note 9 amount is at most column 7 less the claim, so the row needs a UCC for it.
    "a remaining personal part": ("1", "1000", "0", "0", "0", "0", "0", 0, "0", "0", "0", "500"),
}


@pytest.mark.parametrize("entry", T5013_SLIP_PARTNER_AREA_A_ROWS)
def test_a_t5013_slip_partner_with_an_area_a_entry_and_a_claim_of_0_is_refused(entry: str) -> None:
    # Guide T4036 p.13 (confirmed 2026-10-27 from the PDF; no .txt published): a partner who
    # received the slip fills in only the business number, the percentage and amount 7, so a row of
    # Area A with an entry is refused even when its claim is 0.
    partnership: dict[str, Any] = {
        "rental_partner": 1,
        "rental_partner_t5013_slip": 1,
        "rental_partner_share": "600",
        "rental_cca_classes_rows": (T5013_SLIP_PARTNER_AREA_A_ROWS[entry],),
    }

    with pytest.raises(InputOutOfRangeError, match=r"rental_t5013_slip_conflict"):
        return_jr(partnership)


def test_with_no_statement_there_is_nothing_to_claim() -> None:
    worksheet = return_jr()

    assert worksheet.get(RENTAL_CCA_LIMIT_ALL_STATEMENTS).value == D("0")
    assert worksheet.get(RENTAL_CCA_TOTAL_CLAIM).value == D("0")
