"""CA-ON 2025 end to end: return IR (returns/2025_return_ir.yaml), the fishing boat used mainly for
personal use.

Return IR is Return BD's T2121 with fish products of 4000 and expenses of 25000 (here all on line
9136, fishing gear; the worked return splits them as Return BD does), and the filer's answer 1 to
the question of the fishing boat used mainly for personal use. Guide T4002 (page 51, "Use of a
fishing boat mainly for personal use"; confirmed from the PDF, no .txt published): "You may have
used a fishing boat mainly for personal use, but sometimes caught a small amount of fish to sell. In
this case, you can deduct expenses and CCA. However, the amount you deduct cannot be more than your
income from the catch."
The income from the catch is the gross income of Part 3 (line 8299, amount 4A); the expenses and
the CCA are line 9368. Form T2121 prints no line for the limit. Every figure is worked by hand from
that sentence in the comments below, not from the engine's output.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FISH_BOAT_MAINLY_PERSONAL_CHECKED,
    FISH_CCA_CLAIM,
    FISH_EXPENSES_LIMITED_TO_CATCH_INCOME,
    FISH_GROSS_INCOME_BEFORE_EXPENSES,
    FISH_INCOME_BEFORE_CCA,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISH_TOTAL_EXPENSES,
    FISH_TOTAL_EXPENSES_DEDUCTIBLE,
    FISHING_INCOME,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Class 8 with an undepreciated capital cost at the start of the year of 20000, no additions or
# dispositions and the full 20% claimed: 4000 (column 21), as in Return GY.
FISH_CLASS_8 = ("8", "20000", "0", "0", "0", "0", "4000", 0, "0", "0", "0")


def statement(
    products: str = "4000",
    expenses: str = "25000",
    answer: int = 1,
    *,
    cca: bool = False,
) -> dict[str, Any]:
    """One T2121 statement of Return IR: fish products `products` (3A), expenses `expenses`
    (fishing gear, line 9136), the answer `answer` to the question of the boat, and with `cca` the
    Class 8 row (a CCA claim of 4000 on line 9936)."""
    return {
        "fish": {"fish_products": products, "fishing_gear": expenses},
        "fish_boat_mainly_personal": answer,
        "fish_cca_classes_rows": (FISH_CLASS_8,) if cca else (),
    }


def run_statements(*statements: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    return run("0", (), "0", "0", "0", "0", "0", fish_statements=statements)


def run_ir(
    products: str = "4000", expenses: str = "25000", answer: int = 1, *, cca: bool = False
) -> dict[str, tuple[Worksheet, ...]]:
    return run_statements(statement(products, expenses, answer, cca=cca))


def statement_ir(
    products: str = "4000", expenses: str = "25000", answer: int = 1, *, cca: bool = False
) -> Worksheet:
    """The worksheet of the one T2121 statement of Return IR."""
    return run_ir(products, expenses, answer, cca=cca)["ca/t2121"][0]


def test_return_irs_deduction_is_the_4000_of_the_catch_not_the_25000_of_expenses() -> None:
    # Line 8299 is 4000 (amount 4A), amount 4Q and line 9368 are 25000 + 0 (no CCA). "The amount you
    # deduct cannot be more than your income from the catch": the lesser of 25000 and 4000 is 4000.
    # The answer is 1, so the deductible total is that 4000.
    worksheet = statement_ir()

    assert worksheet.get(FISH_BOAT_MAINLY_PERSONAL_CHECKED).value == 1
    assert worksheet.get(FISH_GROSS_INCOME_BEFORE_EXPENSES).value == D("4000")
    assert worksheet.get(FISH_TOTAL_EXPENSES).value == D("25000")
    assert worksheet.get(FISH_EXPENSES_LIMITED_TO_CATCH_INCOME).value == D("4000")
    assert worksheet.get(FISH_TOTAL_EXPENSES_DEDUCTIBLE).value == D("4000")


def test_return_irs_line_9369_and_net_fishing_income_are_0_not_a_loss_of_21000() -> None:
    # Line 9369 is amount 4A minus the deductible total: 4000 - 4000 = 0.00 (4000 - 25000 = -21000
    # without the answer). With no partner, no CCA personal part and no business-use-of-home
    # amount, line 9946 and T1 line 14300 are 0.00; line 27 and total income (line 15000) are 0.
    result = run_ir()

    assert result["ca/t2121"][0].get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("0.00")
    assert result["ca/t2121"][0].get(FISHING_INCOME).value == D("0.00")
    worksheet = result["ca-on/return"][0]
    assert worksheet.get(FISHING_INCOME).value == D("0.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("0.00")
    assert worksheet.get(TOTAL_INCOME).value == D("0.00")
    assert worksheet.get(NET_INCOME).value == D("0.00")


def test_the_same_return_with_the_answer_0_keeps_the_loss_of_21000() -> None:
    # Nothing changes without the answer: the deductible total is line 9368, 25000, and line 9369
    # is 4000 - 25000 = -21000.00, which is T1 line 14300 (negative); net income is still 0.00 after
    # the floor at line 23600. The lesser amount is worked all the same, 4000.
    result = run_ir(answer=0)
    worksheet = result["ca/t2121"][0]

    assert worksheet.get(FISH_BOAT_MAINLY_PERSONAL_CHECKED).value == 0
    assert worksheet.get(FISH_EXPENSES_LIMITED_TO_CATCH_INCOME).value == D("4000")
    assert worksheet.get(FISH_TOTAL_EXPENSES_DEDUCTIBLE).value == D("25000")
    assert worksheet.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-21000.00")
    assert worksheet.get(FISHING_INCOME).value == D("-21000.00")
    assert result["ca-on/return"][0].get(FISHING_INCOME).value == D("-21000.00")
    assert result["ca-on/return"][0].get(NET_INCOME).value == D("0.00")


@pytest.mark.parametrize(
    ("products", "expenses", "deductible", "net"),
    [
        # Return BD: 25000 is below the income of 40000: the lesser is the expenses, unchanged;
        # 40000 - 25000 = 15000.
        ("40000", "25000", "25000", "15000"),
        # 15000 on 40000: the lesser is 15000, 40000 - 15000 = 25000.
        ("40000", "15000", "15000", "25000"),
        # Equal: the lesser is 4000 either way, 4000 - 4000 = 0.
        ("4000", "4000", "4000", "0"),
        # 25000 on 25000: 25000 - 25000 = 0.
        ("25000", "25000", "25000", "0"),
        # 3999 of expenses on 4000: all of them, 4000 - 3999 = 1.
        ("4000", "3999", "3999", "1"),
        # 4001 of expenses on 4000: the catch, 4000 - 4000 = 0, not a loss of 1.
        ("4000", "4001", "4000", "0"),
        # No expenses: nothing to limit, 4000 - 0 = 4000.
        ("4000", "0", "0", "4000"),
        # No income from the catch: nothing is deductible, 0 - 0 = 0 (not -25000).
        ("0", "25000", "0", "0"),
    ],
)
def test_the_amount_deducted_is_the_lesser_of_the_expenses_and_the_income_from_the_catch(
    products: str, expenses: str, deductible: str, net: str
) -> None:
    result = run_ir(products, expenses, 1)

    assert result["ca/t2121"][0].get(FISH_TOTAL_EXPENSES_DEDUCTIBLE).value == D(deductible)
    assert result["ca/t2121"][0].get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D(net)
    assert result["ca/t2121"][0].get(FISHING_INCOME).value == D(net)
    assert result["ca-on/return"][0].get(FISHING_INCOME).value == D(net)
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D(net)


@pytest.mark.parametrize(
    ("products", "expenses"), [("40000", "25000"), ("40000", "15000"), ("4000", "25000")]
)
def test_the_answer_0_deducts_the_whole_of_line_9368(products: str, expenses: str) -> None:
    worksheet = statement_ir(products, expenses, 0)
    net = D(products) - D(expenses)

    assert worksheet.get(FISH_TOTAL_EXPENSES_DEDUCTIBLE).value == D(expenses)
    assert worksheet.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == net


def test_the_cca_is_part_of_the_amount_that_cannot_be_more_than_the_catch() -> None:
    # "you can deduct expenses and CCA. However, the amount you deduct cannot be more than your
    # income from the catch": line 9368 is 4Q 25000 plus line 9936 4000 (Class 8: 20% of 20000)
    # = 29000. With income of 27000 the lesser of 29000 and 27000 is 27000, so line 9369 is 0.00.
    # (Limiting the expenses alone, 25000, and then deducting the CCA would give 2000 - 4000.)
    worksheet = statement_ir("27000", "25000", 1, cca=True)

    assert worksheet.get(FISH_CCA_CLAIM).value == D("4000")
    assert worksheet.get(FISH_TOTAL_EXPENSES).value == D("29000")
    assert worksheet.get(FISH_EXPENSES_LIMITED_TO_CATCH_INCOME).value == D("27000")
    assert worksheet.get(FISH_TOTAL_EXPENSES_DEDUCTIBLE).value == D("27000")
    assert worksheet.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("0.00")


def test_the_cca_below_the_catch_is_deducted_in_full() -> None:
    # Income of 40000, expenses 25000 and CCA 4000: line 9368 is 29000, below 40000, so it is all
    # deducted and line 9369 is 40000 - 29000 = 11000.
    worksheet = statement_ir("40000", "25000", 1, cca=True)

    assert worksheet.get(FISH_TOTAL_EXPENSES_DEDUCTIBLE).value == D("29000")
    assert worksheet.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("11000.00")


def test_the_answer_is_for_each_statement() -> None:
    # The first statement is a boat mainly for personal use: 4000 on income of 4000, 0.00. The
    # second is a fishing business (answer 0): 40000 - 25000 = 15000.00. T1 line 14300 totals them,
    # 0 + 15000 = 15000.00, and so do line 27 and total income.
    result = run_statements(statement("4000", "25000", 1), statement("40000", "25000", 0))

    assert [w.get(FISHING_INCOME).value for w in result["ca/t2121"]] == [D("0.00"), D("15000.00")]
    assert result["ca-on/return"][0].get(FISHING_INCOME).value == D("15000.00")
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("15000.00")


def test_a_boat_mainly_for_personal_use_does_not_limit_the_other_statements_loss() -> None:
    # A statement with the answer 0 keeps its whole loss: 4000 - 25000 = -21000.00 next to the
    # other statement's 0.00, so T1 line 14300 is -21000.00.
    result = run_statements(statement("4000", "25000", 1), statement("4000", "25000", 0))

    assert [w.get(FISHING_INCOME).value for w in result["ca/t2121"]] == [D("0.00"), D("-21000.00")]
    assert result["ca-on/return"][0].get(FISHING_INCOME).value == D("-21000.00")


@pytest.mark.parametrize(
    ("products", "expenses"), [("4000", "25000"), ("40000", "25000"), ("0", "0")]
)
def test_an_answer_of_2_is_refused_and_not_read_as_a_yes(products: str, expenses: str) -> None:
    # A count of 2 is an input error, not a "yes" that quietly limits the deduction.
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/fish_boat_mainly_personal 2\S* is above a yes or no answer of 1",
    ):
        run_ir(products, expenses, 2)


def test_the_trace_checks_the_answer_and_shows_the_lesser_amount_and_the_choice() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_ir().trace)

    for rendered_line in (
        "fish_boat_mainly_personal_checked: fish_boat_mainly_personal 1, "
        "a yes or no answer of 0 or 1",
        "fish_expenses_limited_to_catch_income: lesser of fish_total_expenses 25000 "
        "and fish_gross_income_before_expenses 4000 = 4000",
        "fish_total_expenses_deductible: fish_expenses_limited_to_catch_income 4000, "
        "chosen as fish_boat_mainly_personal_checked is 1",
        "fish_net_income_before_adjustments: fish_gross_income_before_expenses 4000 "
        "less fish_total_expenses_deductible 4000 = 0",
    ):
        assert rendered_line in rendered, rendered_line


def test_the_trace_chooses_line_9368_with_the_answer_0() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_ir(answer=0).trace)

    assert (
        "fish_total_expenses_deductible: fish_total_expenses 25000, "
        "chosen as fish_boat_mainly_personal_checked is 0"
    ) in rendered


def diep_row(
    claim: str, expensed: str
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Class 8 with a UCC of 20000 and additions of `expensed`, all DIEPs, all expensed at once
    (column 9): column 7 is 20000 + `expensed`, column 13 is 20000, so column 21 is 20% x 20000 =
    4000 plus `expensed`, which is `claim`."""
    return ("8", "20000", expensed, "0", "0", "0", claim, 0, expensed, "0", expensed)


def run_diep(answer: int, expensed: str, claim: str) -> Worksheet:
    return run_statements(
        {
            "fish": {"fish_products": "4000", "fishing_gear": "3000"},
            "fish_boat_mainly_personal": answer,
            "fish_cca_classes_rows": (diep_row(claim, expensed),),
        }
    )["ca/t2121"][0]


@pytest.mark.parametrize("answer", [0, 1])
def test_a_column_9_above_the_income_before_cca_is_refused_with_either_answer(answer: int) -> None:
    # Endnote 5 "the amount of income, if any, earned from the source of income that is a business
    # (before any CCA deductions)": amount 4A 4000 less expenses 3000 and the CCA claim 9000 (4000 +
    # the 5000 of column 9) is -8000; plus line 9936 (9000) the income before CCA is 1000. The
    # limit of the boat mainly for personal use does not move it, so the 5000 of column 9 is
    # refused with the answer 1 as with the answer 0.
    with pytest.raises(InputAboveBoundError) as raised:
        run_diep(answer, "5000", "9000")

    assert str(raised.value) == (
        "ca/t2121, instance 1: total of column 9 (5000) is above the income before CCA (1000)"
    )


def test_a_column_9_within_the_income_before_cca_is_accepted_with_the_answer_1() -> None:
    # Column 9 of 1000: the CCA claim is 4000 + 1000 = 5000, amount 4A less 3000 and 5000 is -4000,
    # plus line 9936 the income before CCA is 1000, so the 1000 of column 9 is accepted. Line 9369
    # is limited to the catch: expenses 8000, deductible 4000, 4000 - 4000 = 0.
    worksheet = run_diep(1, "1000", "5000")

    assert worksheet.get(FISH_INCOME_BEFORE_CCA).value == D("1000")
    assert worksheet.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("0")
