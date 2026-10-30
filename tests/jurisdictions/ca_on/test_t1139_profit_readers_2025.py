"""CA-ON 2025: the profit that the readers of "net self-employment income (not including losses)"
take from the businesses on T1 line 13500, through Form T1139's summary form.

Form T929 line 4 "Enter your earned income ... (not including losses)", Form T1-M line 28 and the
medical expense supplement "use only the profit amounts": each business counts its own profit, a
loss counts 0, and a Form T1139 counts its amount G or L in place of the statements it takes the
place of. The readers take the summary form's `ca/t1139_return.t1139_business_profit_on_return`,
which this module computes through the Form T929 worksheet (`ca/t929_net_business_income`). Line
13500 of the return (`BUSINESS_INCOME`) still nets the businesses, so the two figures differ by the
losses.

The inputs are those of the end-to-end modules: the statements are the Form T2125 statements of
line 13500 and the Forms T1139 are those of `test_return_mk.py`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    MOVING_BUSINESS_INCOME,
    NET_COMMISSION_INCOME,
    NET_PROFESSIONAL_INCOME,
    PROFESSIONAL_INCOME,
    T929_NET_BUSINESS_INCOME,
    T929_NET_COMMISSION_INCOME,
    T929_NET_FARMING_INCOME,
    T929_NET_FISHING_INCOME,
    T929_NET_PROFESSIONAL_INCOME,
    T1139_AMOUNT_A,
    T1139_AMOUNT_C,
    T1139_AMOUNT_G,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    routed_statement,
    service,
    starting,
)

T1139 = "ca/t1139"
T929 = "ca/t929"
RETURN = "ca-on/return"


def run(
    businesses: Iterable[Mapping[str, Any]] = (),
    statements: Iterable[Mapping[str, Any]] = (),
    *,
    farms: Iterable[Mapping[str, Any]] = (),
    fishes: Iterable[Mapping[str, Any]] = (),
    moves: Iterable[Mapping[str, Any]] = (),
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of a return with the business statements given, the Forms T1139
    given and one copy of Form T929, and no other income. `farms` and `fishes` are the Form T2042
    and Form T2121 statements, `moves` the Form T1-M moves (line 28 takes the business income)."""
    farm_list = tuple(farms)
    fish_list = tuple(fishes)
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=tuple(statements),
        t1139_businesses=list(businesses),
        t929_copies=1,
        t929_weeks_attended=0,
        t929_expenses_paid="0",
        farm_statements=farm_list or None,
        fish_statements=fish_list or None,
        moving_moves=tuple(moves),
    )
    return service().compute(CA_ON, 2025, *artifacts)


def test_each_statement_counts_its_own_profit_and_a_loss_counts_0_in_the_profit() -> None:
    # Two statements on line 13500: +100 and -30. Line 13500 nets them to 70; the readers' profit
    # is 100, the loss of the second statement counting 0.
    result = run(statements=(routed_statement("100", 1), routed_statement("-30", 1)))
    (form,) = result[T929]
    (return_form,) = result[RETURN]

    assert form.get(T929_NET_BUSINESS_INCOME).value == D("100.00")
    assert return_form.get(BUSINESS_INCOME).value == D("70.00")


def test_a_t1139_that_replaces_a_loss_gives_the_profit_of_its_amount_g_when_positive() -> None:
    # The -500 statement is the one amount A takes (part 2 position 1) and no cancelling election
    # is made, so amount G replaces it. Formula C: 1,000 x 275 / 365 = 753.42, so G is -500 + 753.42
    # = 253.42. The loss counts 0 in the replaced profits, and G is the profit reported.
    result = run(
        businesses=(
            {
                "line": 1,
                "formula": 2,
                "a": (1,),
                "2h": "1000",
                "2m": "275",
                "2n": "365",
            },
        ),
        statements=(routed_statement("-500", 1),),
    )
    (t1139,) = result[T1139]
    (form,) = result[T929]

    assert t1139.get(T1139_AMOUNT_A).value == D("-500.00")
    assert t1139.get(T1139_AMOUNT_C).value == D("753.42")
    assert t1139.get(T1139_AMOUNT_G).value == D("253.42")
    assert form.get(T929_NET_BUSINESS_INCOME).value == D("253.42")


def test_a_t1139_whose_amount_g_is_a_loss_gives_no_profit() -> None:
    # Formula none: amount G is amount A, the -500 loss, which counts 0 in the profit.
    result = run(
        businesses=({"line": 1, "formula": 0, "a": (1,)},),
        statements=(routed_statement("-500", 1),),
    )
    (form,) = result[T929]

    assert form.get(T929_NET_BUSINESS_INCOME).value == D("0")


def test_professional_and_commission_readers_take_each_line_profit_and_a_loss_counts_0() -> None:
    # Professional line 13700: +100 and -30 net to 70 (the professional income of the return), and
    # the readers take 100. Commission line 13900: -50 is a loss, so the readers take 0.
    result = run(
        statements=(
            routed_statement("100", 2),
            routed_statement("-30", 2),
            routed_statement("-50", 3),
        )
    )
    (form,) = result[T929]
    (return_form,) = result[RETURN]

    assert return_form.get(PROFESSIONAL_INCOME).value == D("70.00")
    assert return_form.get(NET_PROFESSIONAL_INCOME).value == D("100.00")
    assert return_form.get(NET_COMMISSION_INCOME).value == D("0")
    assert form.get(T929_NET_PROFESSIONAL_INCOME).value == D("100.00")
    assert form.get(T929_NET_COMMISSION_INCOME).value == D("0")


def test_line_28_business_income_is_the_profit_of_a_mixed_line_and_a_loss_counts_0() -> None:
    # Business line 13500: +100 and -30 net to 70; the Form T1-M line 28 business income is the
    # positive net, 100, the loss counting 0.
    result = run(
        statements=(routed_statement("100", 1), routed_statement("-30", 1)),
        moves=({},),
    )
    (move,) = result["ca/t1_m"]

    assert move.get(MOVING_BUSINESS_INCOME).value == D("100.00")


def test_line_28_business_income_with_a_t1139_is_its_amount_g_and_the_unnamed_profit() -> None:
    # Statements +100, -30 and +40 on line 13500. The Form T1139 (formula 0, line 1) names
    # statements 1 and 2, so amount G is 100 - 30 = 70. Statement 3, +40, is not named and counts
    # its profit, so line 28 is 70 + 40 = 110.
    result = run(
        businesses=({"line": 1, "formula": 0, "a": (1, 2)},),
        statements=(
            routed_statement("100", 1),
            routed_statement("-30", 1),
            routed_statement("40", 1),
        ),
        moves=({},),
    )
    (t1139,) = result[T1139]
    (move,) = result["ca/t1_m"]

    assert t1139.get(T1139_AMOUNT_G).value == D("70.00")
    assert move.get(MOVING_BUSINESS_INCOME).value == D("110.00")


def test_t929_farming_income_is_the_profit_of_each_statement_and_a_loss_counts_0() -> None:
    # Farm statement 2 is a loss of 1,000 (seeds and plants, no sales): it counts 0, so the readers
    # take the profit of statement 1, 12,000.
    (form,) = run(
        farms=({"farm": {"wheat": "12000"}}, {"farm": {"seeds_and_plants": "1000"}}),
    )[T929]
    (loss_only,) = run(farms=({"farm": {"seeds_and_plants": "1000"}},))[T929]

    assert form.get(T929_NET_FARMING_INCOME).value == D("12000.00")
    assert loss_only.get(T929_NET_FARMING_INCOME).value == D("0")


def test_t929_fishing_income_is_the_profit_of_each_statement_and_a_loss_counts_0() -> None:
    # Fishing statement 1 is a profit of 15,000; statement 2 is a loss of 1,000 (salt, bait and ice
    # as an expense with no sales), so it counts 0.
    (form,) = run(
        fishes=(
            {"fish": {"fish_products": "15000"}},
            {"fish": {"salt_bait_and_ice": "1000"}},
        ),
    )[T929]
    (loss_only,) = run(fishes=({"fish": {"salt_bait_and_ice": "1000"}},))[T929]

    assert form.get(T929_NET_FISHING_INCOME).value == D("15000.00")
    assert loss_only.get(T929_NET_FISHING_INCOME).value == D("0")
