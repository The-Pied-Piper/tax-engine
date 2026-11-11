"""English text for the trace lines of `tax_engine.domain.trace.arithmetic`: one renderer class
per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
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
    MultipliedByRateLine,
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

    def render(self, line: RoundedTotalLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"Based on {names.figure(line.base, line.base_amount)}, "
            f"{EnglishFigures.rounding(line.rounding)}"
        )


@english_renderer
class SumRenderer:
    """English text for SumLine."""

    line_class = SumLine

    def render(self, line: SumLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        terms = " plus ".join(names.figure(kind, amount) for kind, amount in line.parts)
        return (
            f"{terms or 'No parts'} gives {EnglishFigures.money(line.total)} "
            f"({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class SumNotBelowZeroRenderer:
    """English text for SumNotBelowZeroLine."""

    line_class = SumNotBelowZeroLine

    def render(self, line: SumNotBelowZeroLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        terms = " plus ".join(names.figure(kind, amount) for kind, amount in line.parts)
        return (
            f"{terms or 'No parts'}, not below 0, gives {EnglishFigures.money(line.total)} "
            f"({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class RateAppliedRenderer:
    """English text for RateAppliedLine."""

    line_class = RateAppliedLine

    def render(self, line: RateAppliedLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{EnglishFigures.percent(line.rate.value)}% of "
            f"{names.figure(line.base, line.base_amount)}, "
            f"{EnglishFigures.rounding(line.rounding)}"
        )


@english_renderer
class DividedByRateRenderer:
    """English text for DividedByRateLine."""

    line_class = DividedByRateLine

    def render(self, line: DividedByRateLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.dividend, line.dividend_amount)} divided by "
            f"{EnglishFigures.percent(line.rate.value)}% gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class SignChosenDifferenceRenderer:
    """English text for SignChosenDifferenceLine."""

    line_class = SignChosenDifferenceLine

    def render(self, line: SignChosenDifferenceLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        if line.sign_amount >= 0:
            return (
                f"{names.figure(line.difference, line.difference_amount)}, because "
                f"{names.figure(line.sign, line.sign_amount)} is not negative, "
                f"gives {EnglishFigures.money(line.result)}"
            )
        return (
            f"{names.figure(line.sign, line.sign_amount)} is negative, so the lesser of "
            f"{names.figure(line.reference, line.reference_amount)} and "
            f"{names.figure(line.difference, line.difference_amount)}, as a negative, "
            f"gives {EnglishFigures.money(line.result)}"
        )


@english_renderer
class SubtractedRenderer:
    """English text for SubtractedLine."""

    line_class = SubtractedLine

    def render(self, line: SubtractedLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.minuend, line.minuend_amount)} less "
            f"{names.figure(line.subtrahend, line.subtrahend_amount)} gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class SubtractedNotBelowZeroRenderer:
    """English text for SubtractedNotBelowZeroLine."""

    line_class = SubtractedNotBelowZeroLine

    def render(self, line: SubtractedNotBelowZeroLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.minuend, line.minuend_amount)} less "
            f"{names.figure(line.subtrahend, line.subtrahend_amount)}, not below 0, gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class CreditAmountRenderer:
    """English text for CreditAmountLine."""

    line_class = CreditAmountLine

    def render(self, line: CreditAmountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"Credit amount of {EnglishFigures.money(line.basis.amount)} "
            f"({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class CappedAmountRenderer:
    """English text for CappedAmountLine."""

    line_class = CappedAmountLine

    def render(self, line: CappedAmountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"Lesser of {names.figure(line.base, line.base_amount)} and "
            f"{EnglishFigures.money(line.cap.value)}, {EnglishFigures.rounding(line.rounding)}"
        )


@english_renderer
class LesserOfRenderer:
    """English text for LesserOfLine."""

    line_class = LesserOfLine

    def render(self, line: LesserOfLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        terms = " and ".join(names.figure(kind, amount) for kind, amount in line.parts)
        return f"Lesser of {terms} gives {EnglishFigures.money(line.result)}"


@english_renderer
class LesserOfWithMaximumRenderer:
    """English text for LesserOfWithMaximumLine."""

    line_class = LesserOfWithMaximumLine

    def render(self, line: LesserOfWithMaximumLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        terms = " and ".join(names.figure(kind, amount) for kind, amount in line.parts)
        return (
            f"Lesser of {terms} and {EnglishFigures.money(line.maximum.value)} gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class GreaterOfRenderer:
    """English text for GreaterOfLine."""

    line_class = GreaterOfLine

    def render(self, line: GreaterOfLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        terms = " and ".join(names.figure(kind, amount) for kind, amount in line.parts)
        return f"Greater of {terms} gives {EnglishFigures.money(line.result)}"


@english_renderer
class PerUnitAmountRenderer:
    """English text for PerUnitAmountLine."""

    line_class = PerUnitAmountLine

    def render(self, line: PerUnitAmountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{EnglishFigures.money(line.per_unit.value)} for each of "
            f"{names.figure(line.count_kind, line.count)} gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class MultipleOverRenderer:
    """English text for MultipleOverLine."""

    line_class = MultipleOverLine

    def render(self, line: MultipleOverLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{EnglishFigures.money(line.factor.value)} × the part of "
            f"{names.figure(line.base, line.base_amount)} over "
            f"{names.figure(line.less, line.less_amount)}, not below 0, "
            f"{EnglishFigures.rounding(line.rounding)}"
        )


@english_renderer
class AtMostRenderer:
    """English text for AtMostLine."""

    line_class = AtMostLine

    def render(self, line: AtMostLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.amount_kind, line.amount_value)}, at most "
            f"{names.figure(line.bound, line.bound_value)}"
        )


@english_renderer
class ClaimAtMostRenderer:
    """English text for ClaimAtMostLine."""

    line_class = ClaimAtMostLine

    def render(self, line: ClaimAtMostLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        if line.maximum_value < 0:
            return (
                f"{names.figure(line.claim_kind, line.claim_value)}, allowed because "
                f"{names.figure(line.maximum_kind, line.maximum_value)} is negative"
            )
        return (
            f"{names.figure(line.claim_kind, line.claim_value)}, at most "
            f"{names.figure(line.maximum_kind, line.maximum_value)}"
        )


@english_renderer
class FractionAppliedRenderer:
    """English text for FractionAppliedLine."""

    line_class = FractionAppliedLine

    def render(self, line: FractionAppliedLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.fraction.numerator}/{line.fraction.denominator} of "
            f"{names.figure(line.base, line.base_amount)}, "
            f"{EnglishFigures.rounding(line.rounding)}"
        )


@english_renderer
class PercentageAppliedRenderer:
    """English text for PercentageAppliedLine."""

    line_class = PercentageAppliedLine

    def render(self, line: PercentageAppliedLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.of(line.percentage_kind)} "
            f"({EnglishFigures.money(line.percentage_value)}%) of "
            f"{names.figure(line.amount_kind, line.amount_value)} gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class MultipliedByRateRenderer:
    """English text for MultipliedByRateLine."""

    line_class = MultipliedByRateLine

    def render(self, line: MultipliedByRateLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.of(line.rate_kind)} ({EnglishFigures.percent(line.rate_value)}%) of "
            f"{names.figure(line.base_kind, line.base_value)} gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class RatioAppliedRenderer:
    """English text for RatioAppliedLine."""

    line_class = RatioAppliedLine

    def render(self, line: RatioAppliedLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.amount_kind, line.amount_value)} × "
            f"{names.figure(line.numerator_kind, line.numerator_value)} / "
            f"{names.figure(line.denominator_kind, line.denominator_value)}, "
            f"{EnglishFigures.rounding(line.rounding)}"
        )


@english_renderer
class TimesCountRenderer:
    """English text for TimesCountLine."""

    line_class = TimesCountLine

    def render(self, line: TimesCountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.amount_kind, line.amount_value)} for each of "
            f"{names.figure(line.count_kind, line.count)} gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class QuotientRenderer:
    """English text for QuotientLine."""

    line_class = QuotientLine

    def render(self, line: QuotientLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.dividend, line.dividend_amount)} divided by "
            f"{names.figure(line.divisor, line.divisor_amount)} gives "
            f"{EnglishFigures.money(line.result)}"
        )


@english_renderer
class ThresholdGateRenderer:
    """English text for ThresholdGateLine."""

    line_class = ThresholdGateLine

    def render(self, line: ThresholdGateLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.amount_kind, line.amount_value)}, as "
            f"{names.figure(line.gate_kind, line.gate_value)} is at least "
            f"{EnglishFigures.money(line.threshold.value)}, gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class AmountOrDividedByRateRenderer:
    """English text for AmountOrDividedByRateLine."""

    line_class = AmountOrDividedByRateLine

    def render(self, line: AmountOrDividedByRateLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.amount_kind, line.amount_value)} if "
            f"{EnglishFigures.money(line.limit.threshold)} or less, otherwise "
            f"{names.figure(line.dividend_kind, line.dividend_value)} divided by "
            f"{EnglishFigures.percent(line.limit.rate.value)}%, gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class CountAtLeastRenderer:
    """English text for CountAtLeastLine."""

    line_class = CountAtLeastLine

    def render(self, line: CountAtLeastLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.count_kind, line.count)}, at least "
            f"{names.figure(line.minimum_kind, line.minimum)}"
        )


@english_renderer
class MoreThanPerUnitRenderer:
    """English text for MoreThanPerUnitLine."""

    line_class = MoreThanPerUnitLine

    def render(self, line: MoreThanPerUnitLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        if line.count == 0:
            return (
                f"{names.figure(line.total_kind, line.total)}, with no {names.of(line.count_kind)}"
            )
        return (
            f"{names.figure(line.total_kind, line.total)}, more than "
            f"{EnglishFigures.money(line.minimum_total)} "
            f"({EnglishFigures.money(line.per_unit.value)} for each of "
            f"{names.figure(line.count_kind, line.count)}, "
            f"{EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class CountAtMostRenderer:
    """English text for CountAtMostLine."""

    line_class = CountAtMostLine

    def render(self, line: CountAtMostLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.count_kind, line.count)}, at most "
            f"{names.figure(line.maximum_kind, line.maximum)}"
        )


@english_renderer
class YesOrNoCountRenderer:
    """English text for YesOrNoCountLine."""

    line_class = YesOrNoCountLine

    def render(self, line: YesOrNoCountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return f"{names.figure(line.count_kind, line.count)}, a yes or no answer of 0 or 1"


@english_renderer
class CountWithoutRecordsRenderer:
    """English text for CountWithoutRecordsLine."""

    line_class = CountWithoutRecordsLine

    def render(self, line: CountWithoutRecordsLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        head = f"{names.figure(line.count_kind, line.count)}, "
        if line.record_count == 0:
            return f"{head}with no {names.of(line.records_kind)} (0 records)"
        noun = "record" if line.record_count == 1 else "records"
        return f"{head}with {line.record_count} {noun} of {names.of(line.records_kind)}"


@english_renderer
class CountNotRefusedRenderer:
    """English text for CountNotRefusedLine."""

    line_class = CountNotRefusedLine

    def render(self, line: CountNotRefusedLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return f"{names.figure(line.count_kind, line.count)}, not refused by the listed conditions"


@english_renderer
class RatioTruncatedRenderer:
    """English text for RatioTruncatedLine."""

    line_class = RatioTruncatedLine

    def render(self, line: RatioTruncatedLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        cap = ", at most 1" if line.cap_at_one else ""
        return (
            f"{names.figure(line.dividend, line.dividend_amount)} divided by "
            f"{names.figure(line.divisor, line.divisor_amount)}{cap} gives "
            f"{EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class PositivePartOfNegationRenderer:
    """English text for PositivePartOfNegationLine."""

    line_class = PositivePartOfNegationLine

    def render(self, line: PositivePartOfNegationLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"Negation of {names.figure(line.amount_kind, line.amount_value)}, not below 0, "
            f"gives {EnglishFigures.money(line.result)}"
        )


@english_renderer
class LesserOfWhenPositiveRenderer:
    """English text for LesserOfWhenPositiveLine."""

    line_class = LesserOfWhenPositiveLine

    def render(self, line: LesserOfWhenPositiveLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        terms = " and ".join(names.figure(kind, amount) for kind, amount in line.parts)
        lesser = f"Lesser of {terms}" if len(line.parts) > 1 else terms
        brackets = ", shown in brackets" if line.bracket else ""
        gate = "" if line.all_positive else ", not all positive"
        return f"{lesser}{brackets}{gate} gives {EnglishFigures.money(line.result)}"


@english_renderer
class AmountWhenMoreRenderer:
    """English text for AmountWhenMoreLine."""

    line_class = AmountWhenMoreLine

    def render(self, line: AmountWhenMoreLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"{names.figure(line.amount_kind, line.amount_value)} if "
            f"{names.figure(line.more_kind, line.more_value)} is more than "
            f"{names.figure(line.than_kind, line.than_value)} gives "
            f"{EnglishFigures.money(line.result)}"
        )
