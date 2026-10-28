"""Trace lines for arithmetic and comparisons: totals and sums, rates, fractions and ratios
applied, differences, caps and bounds, the lesser or greater of figures, quotients and
gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.artifact import ArtifactKind, Money
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.parameters.credit import Credit
from tax_calculator.domain.parameters.factor import Factor
from tax_calculator.domain.parameters.fraction import Fraction
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.parameters.threshold_rate import ThresholdRate
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.domain.trace.base import TraceLine

__all__ = [
    "RoundedTotalLine",
    "SumLine",
    "SumNotBelowZeroLine",
    "RateAppliedLine",
    "DividedByRateLine",
    "SignChosenDifferenceLine",
    "SubtractedLine",
    "SubtractedNotBelowZeroLine",
    "CreditAmountLine",
    "CappedAmountLine",
    "LesserOfLine",
    "LesserOfWithMaximumLine",
    "GreaterOfLine",
    "PerUnitAmountLine",
    "MultipleOverLine",
    "AtMostLine",
    "ClaimAtMostLine",
    "FractionAppliedLine",
    "PercentageAppliedLine",
    "RatioAppliedLine",
    "TimesCountLine",
    "QuotientLine",
    "ThresholdGateLine",
    "AmountOrDividedByRateLine",
    "CountAtLeastLine",
    "CountAtMostLine",
    "CountNotRefusedLine",
    "MoreThanPerUnitLine",
    "YesOrNoCountLine",
    "CountWithoutRecordsLine",
    "AmountWhenMoreLine",
    "RatioTruncatedLine",
    "PositivePartOfNegationLine",
    "LesserOfWhenPositiveLine",
]


@dataclass(frozen=True)
class RoundedTotalLine(TraceLine):
    """The total produced as `output` on `base` (worth `base_amount`), rounded with `rounding`."""

    output: Money
    base: Money
    base_amount: Decimal
    rounding: RoundingRule
    total: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded total."""
        return self.total


@dataclass(frozen=True)
class SumLine(TraceLine):
    """The `total` produced as `output` by adding `parts`, each a kind and its value, in order."""

    output: Money
    parts: tuple[tuple[Money, Decimal], ...]
    total: Decimal

    @property
    def amount(self) -> Decimal:
        """The total of the parts."""
        return self.total


@dataclass(frozen=True)
class SumNotBelowZeroLine(TraceLine):
    """The `total` produced as `output` by adding `parts`, each a kind and its value, in order, and
    taking 0 when the sum would not be above zero.

    Its own class, not a `SumLine`: the floor is a different fact, and a renderer or a check
    matching plain sums must not catch floored ones.
    """

    output: Money
    parts: tuple[tuple[Money, Decimal], ...]
    total: Decimal

    @property
    def amount(self) -> Decimal:
        """The floored total."""
        return self.total


@dataclass(frozen=True)
class RateAppliedLine(TraceLine):
    """The `result` produced as `output` by `base` (worth `base_amount`) × `rate`, rounded."""

    output: Money
    base: Money
    base_amount: Decimal
    rate: Rate
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded product."""
        return self.result


@dataclass(frozen=True)
class DividedByRateLine(TraceLine):
    """The `result` produced as `output` by `dividend` (worth `dividend_amount`) ÷ `rate`, rounded.

    Its own class, not a `RateAppliedLine`: the figure is divided by the rate, not multiplied.
    """

    output: Money
    dividend: Money
    dividend_amount: Decimal
    rate: Rate
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded quotient."""
        return self.result


@dataclass(frozen=True)
class SignChosenDifferenceLine(TraceLine):
    """The `result` produced as `output` from `difference` (worth `difference_amount`), picked by
    the sign of `sign` (worth `sign_amount`) against `reference` (worth `reference_amount`).

    A sign amount that is not negative gives the difference as it is; a negative one gives the
    lesser of the reference and the magnitude of the difference, as a negative number.
    """

    output: Money
    sign: Money
    sign_amount: Decimal
    reference: Money
    reference_amount: Decimal
    difference: Money
    difference_amount: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The chosen, signed figure."""
        return self.result


@dataclass(frozen=True)
class SubtractedLine(TraceLine):
    """`output` = `minuend` (worth `minuend_amount`) less `subtrahend` (worth `subtrahend_amount`),
    exact; `result` may be negative."""

    output: Money
    minuend: Money
    minuend_amount: Decimal
    subtrahend: Money
    subtrahend_amount: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The difference."""
        return self.result


@dataclass(frozen=True)
class SubtractedNotBelowZeroLine(TraceLine):
    """`output` = `minuend` (worth `minuend_amount`) less `subtrahend` (worth `subtrahend_amount`),
    not below zero: `result` is the exact difference, or 0 when that would not be above zero.

    Its own class, not a `SubtractedLine`: the floor is a different fact, and a renderer or a
    check matching plain subtractions must not catch floored ones.
    """

    output: Money
    minuend: Money
    minuend_amount: Decimal
    subtrahend: Money
    subtrahend_amount: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The floored result."""
        return self.result


@dataclass(frozen=True)
class CreditAmountLine(TraceLine):
    """A credit dataset's amount `basis` produced as `output`, rounded with `rounding` to `value`.

    Its own class, not a `RateAppliedLine`: no rate is applied, and the amount itself is the result.
    """

    output: Money
    basis: Credit
    rounding: RoundingRule
    value: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded credit amount."""
        return self.value


@dataclass(frozen=True)
class CappedAmountLine(TraceLine):
    """The `result` produced as `output`: the lesser of `base` (worth `base_amount`) and `cap`,
    rounded with `rounding`."""

    output: Money
    base: Money
    base_amount: Decimal
    cap: Amount
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded lesser."""
        return self.result


@dataclass(frozen=True)
class LesserOfLine(TraceLine):
    """The `result` produced as `output`: the least of `parts`, each a kind and its value."""

    output: Money
    parts: tuple[tuple[Money, Decimal], ...]
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The least of the parts."""
        return self.result


@dataclass(frozen=True)
class LesserOfWithMaximumLine(TraceLine):
    """The `result` produced as `output`: the least of `parts`, each a kind and its value, and the
    `maximum`, rounded with `rounding`.

    Its own class, not a `LesserOfLine` or `CappedAmountLine`: it compares several amounts and a
    dataset's figure.
    """

    output: Money
    parts: tuple[tuple[Money, Decimal], ...]
    maximum: Amount
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded lesser."""
        return self.result


@dataclass(frozen=True)
class GreaterOfLine(TraceLine):
    """The `result` produced as `output`: the greatest of `parts`, each a kind and its value."""

    output: Money
    parts: tuple[tuple[Money, Decimal], ...]
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The greatest of the parts."""
        return self.result


@dataclass(frozen=True)
class PerUnitAmountLine(TraceLine):
    """The `result` produced as `output`: `per_unit` for each of `count` units of `count_kind`,
    rounded once with `rounding`."""

    output: Money
    count_kind: ArtifactKind[int]
    count: int
    per_unit: Amount
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded product."""
        return self.result


@dataclass(frozen=True)
class MultipleOverLine(TraceLine):
    """The `result` produced as `output`: `factor` × `base` (worth `base_amount`) less `less`
    (worth `less_amount`), not below zero, rounded once with `rounding`.

    Its own class, not a `SubtractedNotBelowZeroLine`: the multiple is a different fact.
    """

    output: Money
    base: Money
    base_amount: Decimal
    factor: Factor
    less: Money
    less_amount: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The floored, rounded result."""
        return self.result


@dataclass(frozen=True)
class AtMostLine(TraceLine):
    """`output` = `amount_kind` (worth `amount_value`), unchanged, being at most `bound` (worth
    `bound_value`).

    Its own class, not a `LesserOfLine` or `CappedAmountLine`: the amount is not capped, it is
    checked; an amount above its bound is an error, and no line is recorded for it.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    bound: Money
    bound_value: Decimal

    @property
    def amount(self) -> Decimal:
        """The amount, as produced."""
        return self.amount_value


@dataclass(frozen=True)
class ClaimAtMostLine(TraceLine):
    """`output` = `claim_kind` (worth `claim_value`), unchanged, being at most `maximum_kind`
    (worth `maximum_value`), or being 0 when the maximum is negative.

    Its own class, not an `AtMostLine`: a maximum below zero lets a claim of 0 through, and a
    claim above a maximum is an error, so no line is recorded for it.
    """

    output: Money
    claim_kind: Money
    claim_value: Decimal
    maximum_kind: Money
    maximum_value: Decimal

    @property
    def amount(self) -> Decimal:
        """The claim, as produced."""
        return self.claim_value


@dataclass(frozen=True)
class FractionAppliedLine(TraceLine):
    """The `result` produced as `output` by `base` (worth `base_amount`) × `fraction`, rounded.

    Its own class, not a `RateAppliedLine`: a fraction is not a rate, and its amount may be
    unrounded (a quotient with no finite decimal expansion is never recorded under no rounding).
    """

    output: Money
    base: Money
    base_amount: Decimal
    fraction: Fraction
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded product."""
        return self.result


@dataclass(frozen=True)
class PercentageAppliedLine(TraceLine):
    """The `result` produced as `output` by `amount_kind` (worth `amount_value`) ×
    `percentage_kind` (worth `percentage_value`) / 100, rounded once with `rounding`.

    Its own class, not a `RateAppliedLine`: the percentage is an artifact, not a dataset's rate,
    so the line names the kind it came from.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    percentage_kind: Money
    percentage_value: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        return self.result


@dataclass(frozen=True)
class RatioAppliedLine(TraceLine):
    """The `result` produced as `output` by `amount_kind` (worth `amount_value`) ×
    `numerator_kind` (worth `numerator_value`) / `denominator_kind` (worth `denominator_value`),
    rounded once with `rounding`.

    Its own class, not a `FractionAppliedLine`: the ratio is two artifacts, not a dataset's
    fraction, so the line names the kinds it came from.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    numerator_kind: Money
    numerator_value: Decimal
    denominator_kind: Money
    denominator_value: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded quotient."""
        return self.result


@dataclass(frozen=True)
class TimesCountLine(TraceLine):
    """The `result` produced as `output`: `amount_kind` (worth `amount_value`) for each of
    `count` units of `count_kind`, exactly.

    Its own class, not a `PerUnitAmountLine`: the amount is an artifact, not a dataset's amount,
    and the product is never rounded.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    count_kind: ArtifactKind[int]
    count: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The exact product."""
        return self.result


@dataclass(frozen=True)
class QuotientLine(TraceLine):
    """The `result` produced as `output`: `dividend` (worth `dividend_amount`) divided by
    `divisor` (worth `divisor_amount`), exactly.

    Its own class, not a `FractionAppliedLine`: both parts are artifacts, no dataset is read and
    nothing is rounded.
    """

    output: Money
    dividend: Money
    dividend_amount: Decimal
    divisor: Money
    divisor_amount: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The exact quotient."""
        return self.result


@dataclass(frozen=True)
class ThresholdGateLine(TraceLine):
    """The `result` produced as `output`: `amount_kind` (worth `amount_value`) when `gate_kind`
    (worth `gate_value`) is at least `threshold`, otherwise 0, rounded with `rounding`.

    Its own class, not a `CappedAmountLine`: the gate decides whether the amount passes at all,
    it does not limit it.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    gate_kind: Money
    gate_value: Decimal
    threshold: Amount
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded amount, or 0 when gated off."""
        return self.result


@dataclass(frozen=True)
class AmountOrDividedByRateLine(TraceLine):
    """The figure `result` for `output`: the tested amount passed through, or a figure divided.

    The tested amount (`amount_kind`, `amount_value`) is compared with the `limit`'s threshold.
    At or below it the amount is the result; over it the result is the `dividend_value` of
    `dividend_kind` divided by the limit's rate. Either way it is rounded with `rounding`.

    The tested amount's fields are named `amount_kind` and `amount_value` because `amount` is
    the result.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    dividend_kind: Money
    dividend_value: Decimal
    limit: ThresholdRate
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The figure chosen."""
        return self.result


@dataclass(frozen=True)
class CountAtLeastLine(TraceLine):
    """`output` = `count_kind` (worth `count`), unchanged, being at least `minimum_kind` (worth
    `minimum`).

    Its own class, not an `AtMostLine`: the figures are whole numbers, and a count below its
    minimum is an error, so no line is recorded for it.
    """

    output: ArtifactKind[int]
    count_kind: ArtifactKind[int]
    count: int
    minimum_kind: ArtifactKind[int]
    minimum: int

    @property
    def amount(self) -> Decimal:
        """The count, as produced."""
        return Decimal(self.count)


@dataclass(frozen=True)
class MoreThanPerUnitLine(TraceLine):
    """`output` = `total_kind` (worth `total`), unchanged, being more than `minimum_total`:
    `per_unit` for each of `count` units of `count_kind`, rounded once with `rounding`.

    Its own class, not a `PerUnitAmountLine`: the line is about the total that was checked, and it
    records no product as a result. A total not more than the minimum is an error, so no line is
    recorded for it.
    """

    output: Money
    total_kind: Money
    total: Decimal
    count_kind: ArtifactKind[int]
    count: int
    per_unit: Amount
    rounding: RoundingRule
    minimum_total: Decimal

    @property
    def amount(self) -> Decimal:
        """The total, as produced."""
        return self.total


@dataclass(frozen=True)
class CountAtMostLine(TraceLine):
    """`output` = `count_kind` (worth `count`), unchanged, being at most `maximum_kind` (worth
    `maximum`).

    Its own class, not a `CountAtLeastLine`: the figures are whole numbers, and a count above
    its maximum is an error, so no line is recorded for it.
    """

    output: ArtifactKind[int]
    count_kind: ArtifactKind[int]
    count: int
    maximum_kind: ArtifactKind[int]
    maximum: int

    @property
    def amount(self) -> Decimal:
        """The count, as produced."""
        return Decimal(self.count)


@dataclass(frozen=True)
class YesOrNoCountLine(TraceLine):
    """`output` = `count_kind` (worth `count`), unchanged, being a yes or no answer of 0 or 1.

    Its own class, not a `CountAtLeastLine`: there is no minimum, and a count above 1 is an error,
    so no line is recorded for it.
    """

    output: ArtifactKind[int]
    count_kind: ArtifactKind[int]
    count: int

    @property
    def amount(self) -> Decimal:
        """The count, as produced."""
        return Decimal(self.count)


@dataclass(frozen=True)
class CountWithoutRecordsLine(TraceLine):
    """`output` = `count_kind` (worth `count`), unchanged, checked against `record_count` records
    of `records_kind`: the count is 0, or no record is held.

    Its own class, not a `CountAtLeastLine`: there is no minimum, and a count above 0 with a record
    is an error, so no line is recorded for it.
    """

    output: ArtifactKind[int]
    count_kind: ArtifactKind[int]
    count: int
    records_kind: RecordListKind
    record_count: int

    @property
    def amount(self) -> Decimal:
        """The count, as produced."""
        return Decimal(self.count)


@dataclass(frozen=True)
class CountNotRefusedLine(TraceLine):
    """`output` = `count_kind` (worth `count`), unchanged, no listed condition refusing it.

    Its own class, not a `YesOrNoCountLine`: the count is checked against a dataset's conditions,
    not against 0 and 1, and a refused count is an error, so no line is recorded for it.
    """

    output: ArtifactKind[int]
    count_kind: ArtifactKind[int]
    count: int

    @property
    def amount(self) -> Decimal:
        """The count, as produced."""
        return Decimal(self.count)


@dataclass(frozen=True)
class AmountWhenMoreLine(TraceLine):
    """The `result` produced as `output`: `amount_kind` (worth `amount_value`) if `more_kind`
    (worth `more_value`) is more than `than_kind` (worth `than_value`), else 0.

    Its own class, not a `ThresholdGateLine`: the figure it is compared with is an artifact, not
    a threshold dataset's amount, and nothing is rounded.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    more_kind: Money
    more_value: Decimal
    than_kind: Money
    than_value: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The amount passed through, or 0."""
        return self.result


@dataclass(frozen=True)
class RatioTruncatedLine(TraceLine):
    """The `result` (a rate, 0 to 1) produced as `output` by `dividend` (worth `dividend_amount`)
    divided by `divisor` (worth `divisor_amount`), rounded once with `rounding`.

    `cap_at_one` is whether a dividend above the divisor gives 1. Its own class, not a
    `QuotientLine`: the quotient is rounded by a rule, and a zero divisor gives 0.
    """

    output: ArtifactKind[Rate]
    dividend: Money
    dividend_amount: Decimal
    divisor: Money
    divisor_amount: Decimal
    rounding: RoundingRule
    cap_at_one: bool
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded ratio."""
        return self.result


@dataclass(frozen=True)
class PositivePartOfNegationLine(TraceLine):
    """The `result` produced as `output`: the negation of `amount_kind` (worth `amount_value`),
    not below zero.

    Its own class, not a `SubtractedNotBelowZeroLine`: nothing is taken off, the one figure is
    negated.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The negation, or 0 when the amount is not negative."""
        return self.result


@dataclass(frozen=True)
class LesserOfWhenPositiveLine(TraceLine):
    """The `result` produced as `output` by the least of `parts`, each a kind and its value, only
    when every part is above zero (`all_positive`), else 0.

    `bracket` is whether the least is shown negated ("in brackets"). Its own class, not a
    `LesserOfLine`: the least is gated, and may be negated.
    """

    output: Money
    parts: tuple[tuple[Money, Decimal], ...]
    all_positive: bool
    bracket: bool
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The least (negated when shown in brackets), or 0."""
        return self.result
