"""Unit tests for the English text of the record list trace lines, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind, CountKind, RecordListKind
from tax_engine.domain.trace import (
    ItemLesserOfLine,
    ItemsTotalLine,
    ItemSumLine,
    RecordCountLine,
    TraceLine,
)

D = Decimal
OUT = AmountKind("ex/total")
WAGES = AmountKind("ex/wages")
BONUS = AmountKind("ex/bonus")
COUNT_OUT = CountKind("ex/job_count")
JOBS = RecordListKind("ex/jobs", fields=())


def render(line: TraceLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_a_count_of_the_items_of_a_list() -> None:
    assert render(RecordCountLine(COUNT_OUT, JOBS, 0)) == "No items in jobs, so the count is 0."
    assert render(RecordCountLine(COUNT_OUT, JOBS, 1)) == "1 item in jobs, so the count is 1."
    assert render(RecordCountLine(COUNT_OUT, JOBS, 3)) == "3 items in jobs, so the count is 3."


def test_the_total_of_some_items() -> None:
    line = ItemsTotalLine(OUT, ((1, D("10")), (3, D("20.5"))), D("30.5"))

    assert render(line) == "Item 1 (10.00) plus item 3 (20.50) gives 30.50."


def test_the_total_of_no_items() -> None:
    assert render(ItemsTotalLine(OUT, (), D("0"))) == "No items, so 0.00."


def test_the_sum_of_the_fields_of_one_item() -> None:
    line = ItemSumLine(OUT, 2, ((WAGES, D("10")), (BONUS, D("5"))), D("15"))

    assert render(line) == "Item 2: wages (10.00) plus bonus (5.00) gives 15.00."


def test_the_lesser_of_the_fields_of_one_item() -> None:
    line = ItemLesserOfLine(OUT, 2, ((WAGES, D("10")), (BONUS, D("5"))), D("5"))

    assert render(line) == "Item 2: lesser of wages (10.00) and bonus (5.00) gives 5.00."
