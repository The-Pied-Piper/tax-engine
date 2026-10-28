"""CA-ON 2025 end to end: return IQ (returns/2025_return_iq.yaml), the restricted farm loss.

Return IQ is Guide T4002's Sharon: employment income of 30,000 and one Form T2042 statement with a
net farm loss of 9,200 on line 9946, farming being neither her main source of income nor her main
source of income in addition to a subordinate one (the return's answer, asked once, is 1). The
restricted farm loss is worked once, on the net of all the statements' line 9946 ("your net farm
loss for the year"), by the form ca/farm_loss. Guide T4002
(docs/cra-forms-2025/t4002-25e.pdf, "Restricted farm losses (partly deductible)", pages 95 and 96;
confirmed from the PDF, no .txt published): "When your net farm loss is $32,500 or more, you can
deduct $17,500 from your other income. The rest of your net farm loss is your restricted farm
loss. When your net farm loss is less than $32,500, the amount you can deduct from your other
income is the lesser of: A) your net farm loss for the year B) $2,500 plus 50% × (your net farm
loss minus $2,500) The amount remaining is your restricted farm loss." The farm loss figures are
worked by hand from those lines in the comments below; the tax figures are derived by hand in
returns/2025_return_iq.yaml and checked against the engine's trace.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FARM_LOSS_DEDUCTIBLE,
    FARM_NET_INCOME_LINE_9946,
    FARM_NET_LOSS,
    FARM_NET_LOSS_LESS_BASE_AMOUNT,
    FARM_NET_LOSS_LESS_FULL_THRESHOLD,
    FARM_NOT_MAIN_SOURCE_OF_INCOME_CHECKED,
    FARM_RESTRICTED_LOSS,
    FARM_RESTRICTED_LOSS_ADDED_BACK,
    FARM_RESTRICTED_LOSS_AMOUNT_B,
    FARM_RESTRICTED_LOSS_HALF_OF_EXCESS,
    FARM_RESTRICTED_LOSS_LESSER_OF_A_AND_B,
    FARMING_INCOME,
    NET_FARMING_INCOME,
    NET_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_iq(
    loss: str = "9200", answer: int = 1, *, profit: str = "0"
) -> dict[str, tuple[Worksheet, ...]]:
    """Return IQ: employment income of 30,000 and one T2042 statement with the net farm loss
    `loss` (fertilizers and lime 9662, no income) or the net farm profit `profit` (wheat 9371), and
    the return's answer `answer` to the question of the restricted farm loss."""
    statement: dict[str, Any] = {"farm": {"fertilizers_and_lime": loss, "wheat": profit}}
    return run(
        "30000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=(statement,),
        farm_not_main_source_of_income=answer,
    )


def run_iq_statements(
    *statements: tuple[str, str], answer: int = 1
) -> dict[str, tuple[Worksheet, ...]]:
    """Return IQ with one T2042 statement for each (loss, profit) pair, in the order given."""
    return run(
        "30000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=tuple(
            {"farm": {"fertilizers_and_lime": loss, "wheat": profit}} for loss, profit in statements
        ),
        farm_not_main_source_of_income=answer,
    )


def farm_loss_iq(loss: str = "9200", answer: int = 1, *, profit: str = "0") -> Worksheet:
    """The worksheet of the once-a-return form ca/farm_loss of Return IQ."""
    return run_iq(loss, answer, profit=profit)["ca/farm_loss"][0]


def test_sharons_net_farm_loss_of_9200_is_the_negation_of_line_9946() -> None:
    # Line 9946 = 0 - 9,200 = -9,200 (no income, no business-use-of-home claim): the net farm loss
    # is 9,200, the guide's "net farm loss of $9,200, which she calculated on line 9946".
    worksheet = farm_loss_iq()

    assert worksheet.get(FARM_NET_INCOME_LINE_9946).value == D("-9200")
    assert worksheet.get(FARM_NET_LOSS).value == D("9200")
    assert worksheet.get(FARM_NOT_MAIN_SOURCE_OF_INCOME_CHECKED).value == 1


def test_sharons_amount_b_is_5850_and_she_deducts_the_lesser_of_a_and_b() -> None:
    # B = $2,500 plus 50% x ($9,200 minus $2,500) = 2,500 + 50% x 6,700 = 2,500 + 3,350 = 5,850.
    # Less than 32,500: the lesser of A 9,200 and B 5,850, 5,850.
    worksheet = farm_loss_iq()

    assert worksheet.get(FARM_NET_LOSS_LESS_BASE_AMOUNT).value == D("6700")
    assert worksheet.get(FARM_RESTRICTED_LOSS_HALF_OF_EXCESS).value == D("3350")
    assert worksheet.get(FARM_RESTRICTED_LOSS_AMOUNT_B).value == D("5850")
    assert worksheet.get(FARM_RESTRICTED_LOSS_LESSER_OF_A_AND_B).value == D("5850")
    assert worksheet.get(FARM_NET_LOSS_LESS_FULL_THRESHOLD).value == D("-23300")
    assert worksheet.get(FARM_LOSS_DEDUCTIBLE).value == D("5850")


def test_sharons_line_14100_is_minus_5850_and_her_restricted_farm_loss_is_3350() -> None:
    # "she enters $5,850 on line 14100 ... Her restricted farm loss is the amount that remains,
    # which is $3,350 ($9,200 minus $5,850)." Line 14100 is the loss as negative: -9,200 + 3,350.
    result = run_iq()
    form = result["ca/farm_loss"][0]

    assert form.get(FARM_RESTRICTED_LOSS).value == D("3350")
    assert form.get(FARM_RESTRICTED_LOSS_ADDED_BACK).value == D("3350")
    assert form.get(FARMING_INCOME).value == D("-5850.00")
    # The statement itself keeps its line 9946, the loss of 9,200.
    assert result["ca/t2042"][0].get(FARMING_INCOME).value == D("-9200.00")
    # The net farming income kind is non-negative (a loss counts 0): the loss goes to line 14100.
    assert result["ca-on/return"][0].get(NET_FARMING_INCOME).value == D("0.00")


def test_sharons_total_income_is_24150_and_net_income_23885() -> None:
    # Total income = 30,000 - 5,850 = 24,150.00 (not 20,800 with the whole loss); net income takes
    # off the enhanced CPP contributions 1% x (30,000 - 3,500) = 265.00: 23,885.00 (the whole loss
    # gave 20,535.00, 3,350 too low).
    worksheet = run_iq()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("24150.00")
    assert worksheet.get(NET_INCOME).value == D("23885.00")


def test_two_losses_of_20000_are_one_net_farm_loss_of_40000() -> None:
    # "your net farm loss for the year": two statements of a 20,000 loss each are one net farm
    # loss of 20,000 + 20,000 = 40,000, which is 32,500 or more: "you can deduct $17,500 from your
    # other income", the restricted farm loss 40,000 - 17,500 = 22,500. Line 14100 is -17,500.00
    # and total income is 30,000 - 17,500 = 12,500.00. (Restricting each statement alone would give
    # 2 x 11,250 = 22,500 deductible and total income 7,500.)
    result = run_iq_statements(("20000", "0"), ("20000", "0"))
    form = result["ca/farm_loss"][0]

    assert [w.get(FARMING_INCOME).value for w in result["ca/t2042"]] == [D("-20000.00")] * 2
    assert form.get(FARM_NET_INCOME_LINE_9946).value == D("-40000.00")
    assert form.get(FARM_NET_LOSS).value == D("40000.00")
    assert form.get(FARM_LOSS_DEDUCTIBLE).value == D("17500")
    assert form.get(FARM_RESTRICTED_LOSS).value == D("22500")
    assert form.get(FARMING_INCOME).value == D("-17500.00")
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("12500.00")


def test_a_loss_of_9200_next_to_a_profit_of_9200_nets_to_nothing_and_restricts_nothing() -> None:
    # The statements net to -9,200 + 9,200 = 0: there is no net farm loss for the year, so the
    # restricted farm loss is 0 and line 14100 is 0.00; total income is 30,000.00. (Restricting
    # the loss alone would give 5,850 deductible and a total income of 30,000 + 9,200 - 5,850 =
    # 33,350, 3,350 too high.)
    result = run_iq_statements(("9200", "0"), ("0", "9200"))
    form = result["ca/farm_loss"][0]

    assert form.get(FARM_NET_INCOME_LINE_9946).value == D("0.00")
    assert form.get(FARM_NET_LOSS).value == D("0")
    assert form.get(FARM_RESTRICTED_LOSS).value == D("0")
    assert form.get(FARM_RESTRICTED_LOSS_ADDED_BACK).value == D("0")
    assert form.get(FARMING_INCOME).value == D("0.00")
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("30000.00")


def test_the_statements_order_does_not_matter() -> None:
    forward = run_iq_statements(("20000", "0"), ("0", "5000"))
    backward = run_iq_statements(("0", "5000"), ("20000", "0"))

    # Net farm loss 20,000 - 5,000 = 15,000: B = 2,500 + 50% x 12,500 = 8,750, below A: deductible
    # 8,750, so line 14100 is -8,750.00 and total income 30,000 - 8,750 = 21,250.00.
    for result in (forward, backward):
        assert result["ca/farm_loss"][0].get(FARMING_INCOME).value == D("-8750.00")
        assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("21250.00")


@pytest.mark.parametrize(
    ("loss", "deductible", "restricted"),
    [
        # 40,000 is 32,500 or more: the annual maximum 17,500; the rest, 22,500, is restricted.
        ("40000", "17500", "22500"),
        # Exactly 32,500: "32,500 or more", 17,500 (also B = 2,500 + 50% x 30,000 = 17,500).
        ("32500", "17500", "15000"),
        # 32,499 is less than 32,500: B = 2,500 + 50% x 29,999 = 17,499.50, below A.
        ("32499", "17499.50", "14999.50"),
        # 9,200 is Sharon's.
        ("9200", "5850", "3350"),
        # 2,501: B = 2,500 + 50% x 1 = 2,500.50, below A 2,501.
        ("2501", "2500.50", "0.50"),
        # Exactly 2,500: B = 2,500 + 0 = 2,500, equal to A: all of it is deductible.
        ("2500", "2500", "0"),
        # 1,000 is below the base: B = 2,500 + 50% x (-1,500) = 1,750, above A 1,000: all of it.
        ("1000", "1000", "0"),
        # No loss: nothing to restrict.
        ("0", "0", "0"),
    ],
)
def test_the_deductible_loss_and_the_restricted_loss_follow_the_guides_rule(
    loss: str, deductible: str, restricted: str
) -> None:
    result = run_iq(loss)
    statement = result["ca/farm_loss"][0]

    assert statement.get(FARM_LOSS_DEDUCTIBLE).value == D(deductible)
    assert statement.get(FARM_RESTRICTED_LOSS).value == D(restricted)
    assert statement.get(FARMING_INCOME).value == -D(deductible)
    assert result["ca-on/return"][0].get(NET_FARMING_INCOME).value == D("0.00")


def test_a_loss_of_40000_gives_minus_17500_on_line_14100() -> None:
    result = run_iq("40000")

    assert result["ca/farm_loss"][0].get(FARMING_INCOME).value == D("-17500.00")
    assert result["ca-on/return"][0].get(NET_FARMING_INCOME).value == D("0.00")
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("12500.00")


def test_a_loss_of_9200_with_the_answer_0_stays_minus_9200() -> None:
    # Farming is the main source of income (or the main one with a subordinate one): nothing is
    # restricted, the whole loss is deducted, as before the answer existed.
    result = run_iq("9200", 0)
    statement = result["ca/farm_loss"][0]

    assert statement.get(FARM_NOT_MAIN_SOURCE_OF_INCOME_CHECKED).value == 0
    assert statement.get(FARM_RESTRICTED_LOSS_ADDED_BACK).value == D("0")
    assert statement.get(FARMING_INCOME).value == D("-9200.00")
    assert result["ca-on/return"][0].get(NET_FARMING_INCOME).value == D("0.00")
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("20800.00")


def test_a_loss_of_40000_with_the_answer_0_stays_minus_40000() -> None:
    assert run_iq("40000", 0)["ca/t2042"][0].get(FARMING_INCOME).value == D("-40000.00")


def test_a_farm_profit_with_the_answer_1_is_unchanged() -> None:
    # Line 9946 is 9,200, so there is no net farm loss: nothing is restricted or added back.
    result = run_iq("0", 1, profit="9200")
    statement = result["ca/farm_loss"][0]

    assert statement.get(FARM_NET_LOSS).value == D("0")
    assert statement.get(FARM_RESTRICTED_LOSS).value == D("0")
    assert statement.get(FARM_RESTRICTED_LOSS_ADDED_BACK).value == D("0")
    assert statement.get(FARMING_INCOME).value == D("9200.00")
    assert result["ca-on/return"][0].get(NET_FARMING_INCOME).value == D("9200.00")


def test_the_answer_0_and_the_answer_1_give_the_same_for_a_farm_profit() -> None:
    no = run_iq("0", 0, profit="9200")["ca-on/return"][0]
    yes = run_iq("0", 1, profit="9200")["ca-on/return"][0]

    assert no.get(NET_INCOME) == yes.get(NET_INCOME)


@pytest.mark.parametrize(("loss", "profit"), [("9200", "0"), ("0", "9200"), ("0", "0")])
def test_an_answer_of_2_is_refused_and_not_read_as_a_yes(loss: str, profit: str) -> None:
    # A count of 2 is an input error, not a "yes" that quietly restricts the loss: refused for a
    # loss, a profit and no farm figure alike.
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/farm_not_main_source_of_income 2\S* is above a yes or no answer of 1",
    ):
        run_iq(loss, 2, profit=profit)


def test_the_trace_checks_the_answer_as_a_yes_or_no_count() -> None:
    rendered = EnglishTraceRenderer().render_all(farm_loss_iq().trace)

    assert (
        "farm_not_main_source_of_income_checked: farm_not_main_source_of_income 1, "
        "a yes or no answer of 0 or 1"
    ) in rendered


def test_an_answer_of_2_is_refused_when_the_return_has_no_statement() -> None:
    # The answer is the return's, asked once: it is checked even with no T2042 statement.
    with pytest.raises(InputAboveBoundError, match=r"ca/farm_not_main_source_of_income 2"):
        run_iq_statements(answer=2)


def test_a_return_without_the_answer_or_statements_has_no_farming_income() -> None:
    result = run_iq_statements()

    assert result["ca/farm_loss"][0].get(FARMING_INCOME).value == D("0")
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("30000.00")
