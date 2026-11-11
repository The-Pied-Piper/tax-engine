"""Unit tests for the English text of the arithmetic trace lines, with made-up kinds.

Each test builds a line directly and asserts the exact sentence; with no worksheet a figure is
printed by its label.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from tax_engine.adapters.inbound.trace_english import EnglishNames, EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.renderer import _sentence
from tax_engine.domain.kinds import AmountKind, CountKind, RateKind, RecordListKind
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.factor import Factor
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.parameters.threshold_rate import ThresholdRate
from tax_engine.domain.trace import (
    AmountOrDividedByRateLine,
    AmountWhenMoreLine,
    AtMostLine,
    CappedAmountLine,
    ClaimAtMostLine,
    CountAtLeastLine,
    CountAtMostLine,
    CountNotRefusedLine,
    CountWithoutRecordsLine,
    DividedByRateLine,
    GreaterOfLine,
    LesserOfLine,
    LesserOfWhenPositiveLine,
    LesserOfWithMaximumLine,
    MoreThanPerUnitLine,
    MultipleOverLine,
    PercentageAppliedLine,
    PerUnitAmountLine,
    PositivePartOfNegationLine,
    QuotientLine,
    RatioAppliedLine,
    RatioTruncatedLine,
    RoundedTotalLine,
    SignChosenDifferenceLine,
    ThresholdGateLine,
    TraceLine,
    YesOrNoCountLine,
)

D = Decimal
OUT = AmountKind("ex/result")
WAGES = AmountKind("ex/wages")
BONUS = AmountKind("ex/bonus")
EXTRA = AmountKind("ex/extra")
INCOME = AmountKind("ex/income")
FLOOR = AmountKind("ex/floor")
LOSS = AmountKind("ex/loss")
CHILDREN = CountKind("ex/children")
FLAG = CountKind("ex/flag")
MINIMUM = CountKind("ex/minimum")
ROWS = RecordListKind("ex/rows", fields=())
CENT = RoundTo(increment=D("0.01"), mode=RoundingMode.HALF_UP)
DOWN_TENTH = RoundTo(increment=D("0.001"), mode=RoundingMode.DOWN)
RATE_OUT = RateKind("ex/rate_result")


class _Printed:
    """A stand-in for a worksheet: what the form prints for some figures."""

    def __init__(self, titles: dict[str, str], references: dict[str, str]) -> None:
        self._titles = titles
        self._references = references

    def title(self, label: str) -> str | None:
        return self._titles.get(label)

    def reference(self, label: str) -> str | None:
        return self._references.get(label)


def render(line: TraceLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_a_rounded_total() -> None:
    line = RoundedTotalLine(OUT, WAGES, D("100.004"), CENT, D("100.00"))

    assert render(line) == "Based on wages (100.004) gives 100.00 (rounded to the nearest cent)."


def test_a_quotient_by_a_rate() -> None:
    line = DividedByRateLine(OUT, WAGES, D("50"), Rate(D("0.25")), NO_ROUNDING, D("200"))

    assert render(line) == "Wages (50.00) divided by 25% gives 200.00 (not rounded)."


def test_a_sign_chosen_difference_that_is_not_negative() -> None:
    line = SignChosenDifferenceLine(OUT, BONUS, D("5"), FLOOR, D("10"), WAGES, D("30"), D("30"))

    assert render(line) == "Wages (30.00), because bonus (5.00) is not negative, gives 30.00."


def amount_dataset(family: str, value: str) -> ParameterDataset[Amount]:
    return ParameterDataset(family, 2025, AMOUNT, Amount(D(value)), NO_ROUNDING, ("https://x.org",))


def test_a_sign_chosen_difference_that_is_negative() -> None:
    line = SignChosenDifferenceLine(OUT, BONUS, D("-5"), FLOOR, D("10"), WAGES, D("30"), D("-10"))

    assert render(line) == (
        "Bonus (-5.00) is negative, so the lesser of floor (10.00) and the size of wages (30.00), "
        "as a negative, gives -10.00."
    )


def test_the_lesser_of_two_and_the_least_of_more() -> None:
    two = LesserOfLine(OUT, ((WAGES, D("10")), (BONUS, D("4.5"))), D("4.5"))
    three = LesserOfLine(OUT, ((WAGES, D("10")), (BONUS, D("4.5")), (EXTRA, D("7"))), D("4.5"))

    assert render(two) == "Lesser of wages (10.00) and bonus (4.50) gives 4.50."
    assert render(three) == "Least of wages (10.00), bonus (4.50) and extra (7.00) gives 4.50."


def test_the_lesser_of_a_figure_and_a_limit() -> None:
    maximum = amount_dataset("ex/wage_maximum", "80")
    one = LesserOfWithMaximumLine(OUT, ((WAGES, D("100")),), maximum, NO_ROUNDING, D("80"))
    two = LesserOfWithMaximumLine(
        OUT, ((WAGES, D("100")), (BONUS, D("60"))), maximum, CENT, D("60")
    )

    assert (
        render(one)
        == "Lesser of wages (100.00) and the wage maximum (80.00) gives 80.00 (not rounded)."
    )
    assert render(two) == (
        "Least of wages (100.00), bonus (60.00) and the wage maximum (80.00) gives 60.00 "
        "(rounded to the nearest cent)."
    )


def test_a_capped_amount_names_its_cap_by_the_title_the_form_prints() -> None:
    cap = replace(amount_dataset("ca/some_year_maximum", "80"), title="maximum per slip")
    line = CappedAmountLine(OUT, WAGES, D("100"), cap, NO_ROUNDING, D("80"))

    assert render(line) == (
        "Lesser of wages (100.00) and the maximum per slip (80.00) gives 80.00 (not rounded)."
    )


def test_a_capped_amount_without_a_title_names_its_cap_by_the_dataset_family() -> None:
    cap = amount_dataset("ca/some_year_maximum", "80")
    line = CappedAmountLine(OUT, WAGES, D("100"), cap, NO_ROUNDING, D("80"))

    assert render(line) == (
        "Lesser of wages (100.00) and the some year maximum (80.00) gives 80.00 (not rounded)."
    )


def test_the_greater_of_two_and_the_greatest_of_more() -> None:
    two = GreaterOfLine(OUT, ((WAGES, D("10")), (BONUS, D("4.5"))), D("10"))
    three = GreaterOfLine(OUT, ((WAGES, D("10")), (BONUS, D("4.5")), (EXTRA, D("17"))), D("17"))

    assert render(two) == "Greater of wages (10.00) and bonus (4.50) gives 10.00."
    assert render(three) == "Greatest of wages (10.00), bonus (4.50) and extra (17.00) gives 17.00."


def test_an_amount_for_each_unit() -> None:
    line = PerUnitAmountLine(OUT, CHILDREN, 3, Amount(D("2500")), NO_ROUNDING, D("7500"))

    assert render(line) == "2500.00 for each of children (3) gives 7500.00 (not rounded)."


def test_an_at_most_check_on_an_amount() -> None:
    assert render(AtMostLine(OUT, WAGES, D("100"), FLOOR, D("150"))) == (
        "Wages (100.00), at most floor (150.00)."
    )


def test_a_claim_at_most_a_maximum() -> None:
    within = ClaimAtMostLine(OUT, WAGES, D("40"), FLOOR, D("50"))
    negative_maximum = ClaimAtMostLine(OUT, WAGES, D("0"), FLOOR, D("-1"))

    assert render(within) == "Wages (40.00), at most floor (50.00)."
    assert render(negative_maximum) == "Wages (0.00), allowed because floor (-1.00) is negative."


def test_a_ratio_applied() -> None:
    line = RatioAppliedLine(
        OUT, WAGES, D("100"), BONUS, D("1"), EXTRA, D("4"), NO_ROUNDING, D("25")
    )

    assert render(line) == "Wages (100.00) × bonus (1.00) / extra (4.00) gives 25.00 (not rounded)."


def test_an_exact_quotient() -> None:
    line = QuotientLine(OUT, WAGES, D("10"), BONUS, D("4"), D("2.5"))

    assert render(line) == "Wages (10.00) divided by bonus (4.00) gives 2.50."


def test_a_threshold_gate_that_is_met() -> None:
    line = ThresholdGateLine(
        OUT, WAGES, D("500"), INCOME, D("1000"), Amount(D("800")), NO_ROUNDING, D("500")
    )

    assert render(line) == (
        "Wages (500.00), because income (1000.00) is at least 800.00, gives 500.00 (not rounded)."
    )


def test_a_threshold_gate_that_is_not_met() -> None:
    line = ThresholdGateLine(
        OUT, WAGES, D("500"), INCOME, D("700"), Amount(D("800")), NO_ROUNDING, D("0")
    )

    assert render(line) == (
        "0.00, because income (700.00) is below 800.00, so wages (500.00) does not apply."
    )


def test_an_amount_that_stands_or_is_divided_by_a_rate() -> None:
    limit = ThresholdRate(Rate(D("0.5")), D("1000"))
    stands = AmountOrDividedByRateLine(
        OUT, WAGES, D("900"), BONUS, D("600"), limit, NO_ROUNDING, D("900")
    )
    divided = AmountOrDividedByRateLine(
        OUT, WAGES, D("1200"), BONUS, D("600"), limit, NO_ROUNDING, D("1200")
    )

    assert (
        render(stands) == "Wages (900.00) is 1000.00 or less, so it stands as 900.00 (not rounded)."
    )
    assert render(divided) == (
        "Wages (1200.00) is over 1000.00, so bonus (600.00) divided by 50% gives 1200.00 "
        "(not rounded)."
    )


def test_a_count_at_least_and_at_most() -> None:
    assert render(CountAtLeastLine(MINIMUM, CHILDREN, 3, MINIMUM, 1)) == (
        "Children (3), at least minimum (1)."
    )
    assert render(CountAtMostLine(MINIMUM, CHILDREN, 3, MINIMUM, 5)) == (
        "Children (3), at most minimum (5)."
    )


def test_a_total_more_than_an_amount_for_each_unit() -> None:
    line = MoreThanPerUnitLine(
        OUT, WAGES, D("500"), CHILDREN, 2, Amount(D("200")), NO_ROUNDING, D("400")
    )

    assert render(line) == (
        "Wages (500.00), more than 400.00 (200.00 for each of children (2), not rounded)."
    )


def test_a_total_with_no_units() -> None:
    line = MoreThanPerUnitLine(
        OUT, WAGES, D("500"), CHILDREN, 0, Amount(D("200")), NO_ROUNDING, D("0")
    )

    assert render(line) == "Wages (500.00), with no children."


def test_a_yes_or_no_count() -> None:
    assert render(YesOrNoCountLine(FLAG, FLAG, 1)) == "Flag (1), a yes or no answer of 0 or 1."


def test_a_count_checked_against_the_records_held() -> None:
    none = CountWithoutRecordsLine(FLAG, FLAG, 2, ROWS, 0)
    one = CountWithoutRecordsLine(FLAG, FLAG, 0, ROWS, 1)
    many = CountWithoutRecordsLine(FLAG, FLAG, 0, ROWS, 3)

    assert render(none) == "Flag (2), with no rows (0 records)."
    assert render(one) == "Flag (0), with 1 record of rows."
    assert render(many) == "Flag (0), with 3 records of rows."


def test_a_count_not_refused() -> None:
    assert render(CountNotRefusedLine(FLAG, FLAG, 1)) == (
        "Flag (1), not refused by the listed conditions."
    )


def test_a_ratio_truncated_with_and_without_a_cap() -> None:
    plain = RatioTruncatedLine(
        RATE_OUT, WAGES, D("1"), BONUS, D("3"), DOWN_TENTH, False, D("0.333")
    )
    capped = RatioTruncatedLine(
        RATE_OUT, WAGES, D("5"), BONUS, D("3"), DOWN_TENTH, True, D("1.000")
    )

    assert (
        render(plain) == "Wages (1.00) divided by bonus (3.00) gives 0.333 (rounded down to 0.001)."
    )
    assert render(capped) == (
        "Wages (5.00) divided by bonus (3.00), capped at 1, gives 1.000 (rounded down to 0.001)."
    )


def test_the_positive_part_of_a_negation() -> None:
    assert render(PositivePartOfNegationLine(OUT, LOSS, D("-30"), D("30"))) == (
        "Negation of loss (-30.00), not below 0, gives 30.00."
    )
    assert render(PositivePartOfNegationLine(OUT, LOSS, D("30"), D("0"))) == (
        "Negation of loss (30.00), not below 0, gives 0.00."
    )


def test_the_lesser_of_figures_when_all_are_positive() -> None:
    parts = ((WAGES, D("5")), (BONUS, D("3")))
    plain = LesserOfWhenPositiveLine(OUT, parts, True, False, D("3"))
    bracketed = LesserOfWhenPositiveLine(OUT, parts, True, True, D("-3"))
    gated = LesserOfWhenPositiveLine(OUT, ((WAGES, D("5")), (BONUS, D("0"))), False, False, D("0"))
    three = LesserOfWhenPositiveLine(OUT, (*parts, (EXTRA, D("9"))), True, False, D("3"))
    single = LesserOfWhenPositiveLine(OUT, ((WAGES, D("5")),), True, False, D("5"))

    assert render(plain) == "Lesser of wages (5.00) and bonus (3.00) gives 3.00."
    assert (
        render(bracketed)
        == "Lesser of wages (5.00) and bonus (3.00), shown in brackets, gives -3.00."
    )
    assert render(gated) == "Lesser of wages (5.00) and bonus (0.00), not all positive, gives 0.00."
    assert render(three) == "Least of wages (5.00), bonus (3.00) and extra (9.00) gives 3.00."
    assert render(single) == "Wages (5.00) gives 5.00."


def test_an_amount_when_one_figure_is_more_than_another() -> None:
    more = AmountWhenMoreLine(OUT, BONUS, D("50"), INCOME, D("900"), FLOOR, D("800"), D("50"))
    not_more = AmountWhenMoreLine(OUT, BONUS, D("50"), INCOME, D("800"), FLOOR, D("800"), D("0"))

    assert render(more) == (
        "Bonus (50.00), because income (900.00) is more than floor (800.00), gives 50.00."
    )
    assert render(not_more) == "0.00, because income (800.00) is not more than floor (800.00)."


def test_figures_are_named_as_lines_when_the_form_prints_references() -> None:
    printed = _Printed({}, {"wages": "2", "bonus": "B", "floor": "5a"})
    quotient = QuotientLine(OUT, WAGES, D("10"), BONUS, D("4"), D("2.5"))
    at_most = AtMostLine(OUT, WAGES, D("100"), FLOOR, D("150"))
    two = LesserOfLine(OUT, ((WAGES, D("10")), (EXTRA, D("4.5"))), D("4.5"))
    renderer = EnglishTraceRenderer()

    assert (
        renderer.render(quotient, printed) == "Line 2 (10.00) divided by line B (4.00) gives 2.50."
    )
    assert renderer.render(at_most, printed) == "Line 2 (100.00), at most line 5a (150.00)."
    assert renderer.render(two, printed) == "Lesser of line 2 (10.00) and extra (4.50) gives 4.50."


def test_a_sentence_is_capitalised_whether_it_opens_with_a_fallback_label_or_a_printed_name() -> (
    None
):
    labelled = EnglishNames()
    printed = EnglishNames(_Printed({}, {"wages": "2"}))

    assert _sentence(f"{labelled.of(WAGES)} (1.00) less nothing") == "Wages (1.00) less nothing."
    assert _sentence(f"{printed.of(WAGES)} (1.00) less nothing") == "Line 2 (1.00) less nothing."
    assert _sentence("lesser of two") == "Lesser of two."


def test_a_sentence_that_ends_in_a_full_stop_gets_no_second_one() -> None:
    assert _sentence("Done.") == "Done."
    assert _sentence("Done") == "Done."


def test_a_multiple_over_is_the_multiple_less_the_amount_not_the_part_over() -> None:
    line = MultipleOverLine(
        OUT,
        WAGES,
        Decimal("100"),
        Factor(Decimal("2")),
        BONUS,
        Decimal("50"),
        CENT,
        Decimal("150"),
    )

    assert render(line) == (
        "2 × wages (100.00) less bonus (50.00), not below 0, gives 150.00 "
        "(rounded to the nearest cent)."
    )


def test_a_percentage_applied_prints_the_percentage_as_stored() -> None:
    line = PercentageAppliedLine(
        OUT, WAGES, Decimal("200"), BONUS, Decimal("25"), CENT, Decimal("50")
    )

    assert render(line) == (
        "Bonus (25%) of wages (200.00) gives 50.00 (rounded to the nearest cent)."
    )
