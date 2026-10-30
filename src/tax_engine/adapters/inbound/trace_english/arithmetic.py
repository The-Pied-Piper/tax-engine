"""English text for the trace lines of `tax_engine.domain.trace.arithmetic`: one renderer class
per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.domain.trace.arithmetic import (
    AmountOrDividedByRateLine,
    AmountWhenMoreLine,
    AtMostLine,
    CappedAmountLine,
    ClaimAtMostLine,
    CountAtLeastLine,
    CountAtMostLine,
    CountNotRefusedLine,
    CountWithoutRecordsLine,
    CreditAmountLine,
    DividedByRateLine,
    FractionAppliedLine,
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
    RateAppliedLine,
    RatioAppliedLine,
    RatioTruncatedLine,
    RoundedTotalLine,
    SignChosenDifferenceLine,
    SubtractedLine,
    SubtractedNotBelowZeroLine,
    SumLine,
    SumNotBelowZeroLine,
    ThresholdGateLine,
    TimesCountLine,
    YesOrNoCountLine,
)


@english_renderer
class RoundedTotalRenderer:
    """English text for RoundedTotalLine."""

    line_class = RoundedTotalLine

    def render(self, line: RoundedTotalLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        base = line.base
        amount = line.base_amount
        rule = line.rounding
        return (
            f"{output.label} on {base.label} {EnglishFigures.money(amount)} "
            f"({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class SumRenderer:
    """English text for SumLine."""

    line_class = SumLine

    def render(self, line: SumLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        parts = line.parts
        total = line.total
        terms = " + ".join(f"{kind.label} {EnglishFigures.money(amount)}" for kind, amount in parts)
        return f"{output.label}: {terms or 'no parts'} = {EnglishFigures.money(total)}"


@english_renderer
class SumNotBelowZeroRenderer:
    """English text for SumNotBelowZeroLine."""

    line_class = SumNotBelowZeroLine

    def render(self, line: SumNotBelowZeroLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        parts = line.parts
        total = line.total
        terms = " + ".join(f"{kind.label} {EnglishFigures.money(amount)}" for kind, amount in parts)
        return f"{output.label}: {terms or 'no parts'}, not below 0 = {EnglishFigures.money(total)}"


@english_renderer
class RateAppliedRenderer:
    """English text for RateAppliedLine."""

    line_class = RateAppliedLine

    def render(self, line: RateAppliedLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        base = line.base
        amount = line.base_amount
        rate = line.rate
        rule = line.rounding
        return (
            f"{output.label}: {EnglishFigures.percent(rate.value)}% of {base.label} "
            f"{EnglishFigures.money(amount)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class DividedByRateRenderer:
    """English text for DividedByRateLine."""

    line_class = DividedByRateLine

    def render(self, line: DividedByRateLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        dividend = line.dividend
        amount = line.dividend_amount
        rate = line.rate
        rule = line.rounding
        return (
            f"{output.label}: {dividend.label} {EnglishFigures.money(amount)} divided by "
            f"{EnglishFigures.percent(rate.value)}% ({EnglishFigures.rounding(rule)}) "
            f"= {EnglishFigures.money(line.result)}"
        )


@english_renderer
class SignChosenDifferenceRenderer:
    """English text for SignChosenDifferenceLine."""

    line_class = SignChosenDifferenceLine

    def render(self, line: SignChosenDifferenceLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        sign = line.sign
        sign_amount = EnglishFigures.money(line.sign_amount)
        reference = line.reference
        difference = line.difference
        difference_amount = EnglishFigures.money(line.difference_amount)
        result = EnglishFigures.money(line.result)
        if line.sign_amount >= 0:
            return (
                f"{output.label}: {difference.label} {difference_amount} "
                f"({sign.label} {sign_amount} is not negative) = {result}"
            )
        return (
            f"{output.label}: {sign.label} {sign_amount} is negative, lesser of "
            f"{reference.label} {EnglishFigures.money(line.reference_amount)} and "
            f"{difference.label} {difference_amount}, as a negative = {result}"
        )


@english_renderer
class SubtractedRenderer:
    """English text for SubtractedLine."""

    line_class = SubtractedLine

    def render(self, line: SubtractedLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        minuend = line.minuend
        minuend_amount = line.minuend_amount
        subtrahend = line.subtrahend
        subtrahend_amount = line.subtrahend_amount
        result = line.result
        return (
            f"{output.label}: {minuend.label} {EnglishFigures.money(minuend_amount)} "
            f"less {subtrahend.label} {EnglishFigures.money(subtrahend_amount)} "
            f"= {EnglishFigures.money(result)}"
        )


@english_renderer
class SubtractedNotBelowZeroRenderer:
    """English text for SubtractedNotBelowZeroLine."""

    line_class = SubtractedNotBelowZeroLine

    def render(self, line: SubtractedNotBelowZeroLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        minuend = line.minuend
        minuend_amount = line.minuend_amount
        subtrahend = line.subtrahend
        subtrahend_amount = line.subtrahend_amount
        result = line.result
        return (
            f"{output.label}: {minuend.label} {EnglishFigures.money(minuend_amount)} "
            f"less {subtrahend.label} {EnglishFigures.money(subtrahend_amount)}, "
            f"not below 0 = {EnglishFigures.money(result)}"
        )


@english_renderer
class CreditAmountRenderer:
    """English text for CreditAmountLine."""

    line_class = CreditAmountLine

    def render(self, line: CreditAmountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        basis = line.basis
        rule = line.rounding
        return (
            f"{output.label}: credit amount {EnglishFigures.money(basis.amount)} "
            f"({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class CappedAmountRenderer:
    """English text for CappedAmountLine."""

    line_class = CappedAmountLine

    def render(self, line: CappedAmountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        base = line.base
        amount = line.base_amount
        cap = line.cap
        rule = line.rounding
        return (
            f"{output.label}: lesser of {base.label} {EnglishFigures.money(amount)} "
            f"and {EnglishFigures.money(cap.value)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class LesserOfRenderer:
    """English text for LesserOfLine."""

    line_class = LesserOfLine

    def render(self, line: LesserOfLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        parts = line.parts
        result = line.result
        terms = " and ".join(
            f"{kind.label} {EnglishFigures.money(amount)}" for kind, amount in parts
        )
        return f"{output.label}: lesser of {terms} = {EnglishFigures.money(result)}"


@english_renderer
class LesserOfWithMaximumRenderer:
    """English text for LesserOfWithMaximumLine."""

    line_class = LesserOfWithMaximumLine

    def render(self, line: LesserOfWithMaximumLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        maximum = line.maximum
        rule = line.rounding
        terms = " and ".join(
            f"{kind.label} {EnglishFigures.money(amount)}" for kind, amount in line.parts
        )
        return (
            f"{output.label}: lesser of {terms} and {EnglishFigures.money(maximum.value)} "
            f"({EnglishFigures.rounding(rule)}) = {EnglishFigures.money(line.result)}"
        )


@english_renderer
class GreaterOfRenderer:
    """English text for GreaterOfLine."""

    line_class = GreaterOfLine

    def render(self, line: GreaterOfLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        parts = line.parts
        result = line.result
        terms = " and ".join(
            f"{kind.label} {EnglishFigures.money(amount)}" for kind, amount in parts
        )
        return f"{output.label}: greater of {terms} = {EnglishFigures.money(result)}"


@english_renderer
class PerUnitAmountRenderer:
    """English text for PerUnitAmountLine."""

    line_class = PerUnitAmountLine

    def render(self, line: PerUnitAmountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        count_kind = line.count_kind
        count = line.count
        per_unit = line.per_unit
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: {EnglishFigures.money(per_unit.value)} for each of {count} "
            f"{count_kind.label} = {EnglishFigures.money(result)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class MultipleOverRenderer:
    """English text for MultipleOverLine."""

    line_class = MultipleOverLine

    def render(self, line: MultipleOverLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        base = line.base
        amount = line.base_amount
        factor = line.factor
        less = line.less
        less_amount = line.less_amount
        rule = line.rounding
        return (
            f"{output.label}: {EnglishFigures.money(factor.value)} × {base.label} "
            f"{EnglishFigures.money(amount)} over {less.label} "
            f"{EnglishFigures.money(less_amount)}, "
            f"not below 0 ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class AtMostRenderer:
    """English text for AtMostLine."""

    line_class = AtMostLine

    def render(self, line: AtMostLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        amount_kind = line.amount_kind
        amount = line.amount_value
        bound = line.bound
        bound_value = line.bound_value
        return (
            f"{output.label}: {amount_kind.label} {EnglishFigures.money(amount)}, "
            f"at most {bound.label} {EnglishFigures.money(bound_value)}"
        )


@english_renderer
class ClaimAtMostRenderer:
    """English text for ClaimAtMostLine."""

    line_class = ClaimAtMostLine

    def render(self, line: ClaimAtMostLine) -> str:
        """The English sentence for `line`."""
        claim = EnglishFigures.money(line.claim_value)
        maximum = EnglishFigures.money(line.maximum_value)
        if line.maximum_value < 0:
            return (
                f"{line.output.label}: {line.claim_kind.label} {claim}, "
                f"allowed because {line.maximum_kind.label} {maximum} is negative"
            )
        return (
            f"{line.output.label}: {line.claim_kind.label} {claim}, "
            f"at most {line.maximum_kind.label} {maximum}"
        )


@english_renderer
class FractionAppliedRenderer:
    """English text for FractionAppliedLine."""

    line_class = FractionAppliedLine

    def render(self, line: FractionAppliedLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        base = line.base
        amount = line.base_amount
        fraction = line.fraction
        rule = line.rounding
        return (
            f"{output.label}: {fraction.numerator}/{fraction.denominator} of {base.label} "
            f"{EnglishFigures.money(amount)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class PercentageAppliedRenderer:
    """English text for PercentageAppliedLine."""

    line_class = PercentageAppliedLine

    def render(self, line: PercentageAppliedLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.percentage_kind.label} "
            f"{EnglishFigures.money(line.percentage_value)}% of {line.amount_kind.label} "
            f"{EnglishFigures.money(line.amount_value)} = {EnglishFigures.money(line.result)} "
            f"({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class RatioAppliedRenderer:
    """English text for RatioAppliedLine."""

    line_class = RatioAppliedLine

    def render(self, line: RatioAppliedLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        amount_kind = line.amount_kind
        amount = line.amount_value
        numerator_kind = line.numerator_kind
        numerator = line.numerator_value
        denominator_kind = line.denominator_kind
        denominator = line.denominator_value
        rule = line.rounding
        return (
            f"{output.label}: {amount_kind.label} {EnglishFigures.money(amount)} × "
            f"{numerator_kind.label} {EnglishFigures.money(numerator)} / "
            f"{denominator_kind.label} {EnglishFigures.money(denominator)} "
            f"({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class TimesCountRenderer:
    """English text for TimesCountLine."""

    line_class = TimesCountLine

    def render(self, line: TimesCountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        amount_kind = line.amount_kind
        amount = line.amount_value
        count_kind = line.count_kind
        count = line.count
        result = line.result
        return (
            f"{output.label}: {amount_kind.label} {EnglishFigures.money(amount)} for each of "
            f"{count} {count_kind.label} = {EnglishFigures.money(result)}"
        )


@english_renderer
class QuotientRenderer:
    """English text for QuotientLine."""

    line_class = QuotientLine

    def render(self, line: QuotientLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        dividend = line.dividend
        dividend_amount = line.dividend_amount
        divisor = line.divisor
        divisor_amount = line.divisor_amount
        result = line.result
        return (
            f"{output.label}: {dividend.label} {EnglishFigures.money(dividend_amount)} "
            f"divided by {divisor.label} {EnglishFigures.money(divisor_amount)} "
            f"= {EnglishFigures.money(result)}"
        )


@english_renderer
class ThresholdGateRenderer:
    """English text for ThresholdGateLine."""

    line_class = ThresholdGateLine

    def render(self, line: ThresholdGateLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        amount_kind = line.amount_kind
        amount = line.amount_value
        gate_kind = line.gate_kind
        gate_value = line.gate_value
        threshold = line.threshold
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: {amount_kind.label} {EnglishFigures.money(amount)} "
            f"if {gate_kind.label} {EnglishFigures.money(gate_value)} is at least "
            f"{EnglishFigures.money(threshold.value)} ({EnglishFigures.rounding(rule)}) = "
            f"{EnglishFigures.money(result)}"
        )


@english_renderer
class AmountOrDividedByRateRenderer:
    """English text for AmountOrDividedByRateLine."""

    line_class = AmountOrDividedByRateLine

    def render(self, line: AmountOrDividedByRateLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        amount_kind = line.amount_kind
        amount_value = line.amount_value
        dividend_kind = line.dividend_kind
        dividend_value = line.dividend_value
        limit = line.limit
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: {amount_kind.label} {EnglishFigures.money(amount_value)} "
            f"if {EnglishFigures.money(limit.threshold)} or less, otherwise {dividend_kind.label} "
            f"{EnglishFigures.money(dividend_value)} divided by "
            f"{EnglishFigures.percent(limit.rate.value)}% ({EnglishFigures.rounding(rule)}) = "
            f"{EnglishFigures.money(result)}"
        )


@english_renderer
class CountAtLeastRenderer:
    """English text for CountAtLeastLine."""

    line_class = CountAtLeastLine

    def render(self, line: CountAtLeastLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.count_kind.label} {line.count}, "
            f"at least {line.minimum_kind.label} {line.minimum}"
        )


@english_renderer
class MoreThanPerUnitRenderer:
    """English text for MoreThanPerUnitLine."""

    line_class = MoreThanPerUnitLine

    def render(self, line: MoreThanPerUnitLine) -> str:
        """The English sentence for `line`."""
        if line.count == 0:
            return (
                f"{line.output.label}: {line.total_kind.label} "
                f"{EnglishFigures.money(line.total)}, no {line.count_kind.label}"
            )
        return (
            f"{line.output.label}: {line.total_kind.label} {EnglishFigures.money(line.total)}, "
            f"more than {EnglishFigures.money(line.minimum_total)} "
            f"({EnglishFigures.money(line.per_unit.value)} for each of {line.count} "
            f"{line.count_kind.label}, {EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class CountAtMostRenderer:
    """English text for CountAtMostLine."""

    line_class = CountAtMostLine

    def render(self, line: CountAtMostLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.count_kind.label} {line.count}, "
            f"at most {line.maximum_kind.label} {line.maximum}"
        )


@english_renderer
class YesOrNoCountRenderer:
    """English text for YesOrNoCountLine."""

    line_class = YesOrNoCountLine

    def render(self, line: YesOrNoCountLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.count_kind.label} {line.count}, "
            "a yes or no answer of 0 or 1"
        )


@english_renderer
class CountWithoutRecordsRenderer:
    """English text for CountWithoutRecordsLine."""

    line_class = CountWithoutRecordsLine

    def render(self, line: CountWithoutRecordsLine) -> str:
        """The English sentence for `line`."""
        head = f"{line.output.label}: {line.count_kind.label} {line.count}, "
        if line.record_count == 0:
            return f"{head}with no {line.records_kind.label} (0 records)"
        noun = "record" if line.record_count == 1 else "records"
        return f"{head}with {line.record_count} {noun} of {line.records_kind.label}"


@english_renderer
class CountNotRefusedRenderer:
    """English text for CountNotRefusedLine."""

    line_class = CountNotRefusedLine

    def render(self, line: CountNotRefusedLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.count_kind.label} {line.count}, "
            "not refused by the listed conditions"
        )


@english_renderer
class RatioTruncatedRenderer:
    """English text for RatioTruncatedLine."""

    line_class = RatioTruncatedLine

    def render(self, line: RatioTruncatedLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        dividend = line.dividend
        divisor = line.divisor
        cap = ", at most 1" if line.cap_at_one else ""
        return (
            f"{output.label}: {dividend.label} {EnglishFigures.money(line.dividend_amount)} "
            f"divided by {divisor.label} {EnglishFigures.money(line.divisor_amount)} "
            f"({EnglishFigures.rounding(line.rounding)}){cap} = {EnglishFigures.money(line.result)}"
        )


@english_renderer
class PositivePartOfNegationRenderer:
    """English text for PositivePartOfNegationLine."""

    line_class = PositivePartOfNegationLine

    def render(self, line: PositivePartOfNegationLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: negation of {line.amount_kind.label} "
            f"{EnglishFigures.money(line.amount_value)}, not below 0 = "
            f"{EnglishFigures.money(line.result)}"
        )


@english_renderer
class LesserOfWhenPositiveRenderer:
    """English text for LesserOfWhenPositiveLine."""

    line_class = LesserOfWhenPositiveLine

    def render(self, line: LesserOfWhenPositiveLine) -> str:
        """The English sentence for `line`."""
        terms = " and ".join(
            f"{kind.label} {EnglishFigures.money(amount)}" for kind, amount in line.parts
        )
        lesser = f"lesser of {terms}" if len(line.parts) > 1 else terms
        brackets = ", shown in brackets" if line.bracket else ""
        gate = "" if line.all_positive else ", not all positive"
        return (
            f"{line.output.label}: {lesser}{brackets}{gate} = {EnglishFigures.money(line.result)}"
        )


@english_renderer
class AmountWhenMoreRenderer:
    """English text for AmountWhenMoreLine."""

    line_class = AmountWhenMoreLine

    def render(self, line: AmountWhenMoreLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.amount_kind.label} "
            f"{EnglishFigures.money(line.amount_value)} if {line.more_kind.label} "
            f"{EnglishFigures.money(line.more_value)} is more than {line.than_kind.label} "
            f"{EnglishFigures.money(line.than_value)} = {EnglishFigures.money(line.result)}"
        )
