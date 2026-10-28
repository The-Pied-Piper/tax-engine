"""ChooseBySign: one of up to five money artifacts, chosen by the sign of an amount.

For a line whose amount depends on whether an earlier line is positive, zero or negative: it is
`core/choose_by_count` for the sign of an amount. Each sign branch is covered by at most one
candidate, wired as `when_positive`, `when_zero` or `when_negative`, or as `when_non_positive`
(zero or negative) or `when_non_negative` (zero or positive); every candidate slot is optional.
The output is the candidate of the branch the sign falls in, unchanged with its scale kept, and
only that candidate is read; a branch no candidate covers gives a plain `Decimal(0)`. Only the
sign is read, so nothing is scaled or rounded. It records one `ChosenBySignLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidCapabilityError
from tax_calculator.domain.trace import ChosenBySignLine


@capability(identifier="choose_by_sign")
class ChooseBySign(Capability):
    """Produces `output`: the consumed candidate of the branch (positive, zero or negative) that
    the sign of the consumed `sign` falls in, else 0."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "sign": Decimal,
        "when_positive": list[Decimal],
        "when_zero": list[Decimal],
        "when_negative": list[Decimal],
        "when_non_positive": list[Decimal],
        "when_non_negative": list[Decimal],
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    _COVERS: ClassVar[Mapping[str, tuple[str, ...]]] = {
        "when_positive": ("positive",),
        "when_zero": ("zero",),
        "when_negative": ("negative",),
        "when_non_positive": ("zero", "negative"),
        "when_non_negative": ("positive", "zero"),
    }

    def __init__(
        self,
        *,
        sign: Money,
        when_positive: tuple[Money, ...] = (),
        when_zero: tuple[Money, ...] = (),
        when_negative: tuple[Money, ...] = (),
        when_non_positive: tuple[Money, ...] = (),
        when_non_negative: tuple[Money, ...] = (),
        output: Money,
    ) -> None:
        """Wire the capability: the amount whose sign it reads, the candidate (none or one) for
        each branch, the kind produced.

        Raises InvalidCapabilityError when a candidate slot lists more than one kind or two
        candidate slots cover the same sign branch.
        """
        super().__init__(
            sign=sign,
            when_positive=when_positive,
            when_zero=when_zero,
            when_negative=when_negative,
            when_non_positive=when_non_positive,
            when_non_negative=when_non_negative,
            output=output,
        )
        wired = {
            "when_positive": when_positive,
            "when_zero": when_zero,
            "when_negative": when_negative,
            "when_non_positive": when_non_positive,
            "when_non_negative": when_non_negative,
        }
        self._by_branch: dict[str, tuple[Money, ...]] = {}
        covered_by: dict[str, str] = {}
        for slot, kinds in wired.items():
            if len(kinds) > 1:
                raise InvalidCapabilityError(
                    f"{type(self).__name__}: list slot {slot!r} takes at most one kind, "
                    f"got {len(kinds)}"
                )
            if not kinds:
                continue
            for branch in self._COVERS[slot]:
                if branch in covered_by:
                    raise InvalidCapabilityError(
                        f"{type(self).__name__}: the {branch} branch is covered by both "
                        f"{covered_by[branch]!r} and {slot!r}"
                    )
                covered_by[branch] = slot
                self._by_branch[branch] = kinds
        self._sign = sign
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        sign = self._input(inputs, self._sign).value
        branch = "positive" if sign > 0 else "negative" if sign < 0 else "zero"
        candidates = self._by_branch.get(branch, ())
        if candidates:
            chosen_kind: Money | None = candidates[0]
            chosen = self._input(inputs, candidates[0]).value
        else:
            chosen_kind, chosen = None, Decimal(0)
        return CapabilityResult(
            outputs=(Artifact(self._output, chosen),),
            trace=(
                ChosenBySignLine(
                    output=self._output,
                    sign_kind=self._sign,
                    sign=sign,
                    chosen_kind=chosen_kind,
                    chosen_value=chosen,
                ),
            ),
        )
