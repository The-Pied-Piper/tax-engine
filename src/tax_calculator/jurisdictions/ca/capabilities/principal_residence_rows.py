"""PrincipalResidenceRows: the base of the capabilities of Form T2091(IND) Part 1 and Part 2 for a
principal residence, not registered itself.

Form T2091(IND), "Complete a separate form for each property you sold." Each property of the
consumed `properties` record list is worked on its own, never pooled with the others: a
`PrincipalResidenceRow` holds the property's lines. Part 1: the years designated and owned (lines 1
to 7), the proceeds, outlays and adjusted cost base (lines 8 to 10), the gain (line 18), the "plus
one" (line 20), line 21 and the exemption (line 23, rounded once with the `rounding` dataset's
rule), and line 24, the gain less the exemption, not below 0. Part 2, for a property that is one of
two or more principal residences a family member owned on December 31, 1981: area A (lines 27 to 33)
is completed when the years designated before 1982 do not cover the years owned before 1982; area B
(lines 38 to 45) when the years designated after 1981 do not cover the years owned after 1981 and
the fair market value on December 31, 1981 is not more than the proceeds; area C (line 48) when the
years designated after 1981 do not cover the years owned after 1981; area D gives line 53, and line
54 is the lesser of line 53 and line 24 when Part 2 applies, else line 24. A step the form says not
to complete is 0. Lines 23, 32 and 44 divide, each quotient rounded once with the dataset's rule.

A property owned for no years is refused with a ValidationError, line 23 being divided by them. A
property is also refused when its "plus one" or Part 2 flag is above 1 (a flag is 0 or 1), or when
the years designated after 1981 (line 1) are above the years owned after 1981 (line 5), or the
years designated 1972 to 1981 (line 2) above the years owned 1972 to 1981 (line 6). No properties
give no rows. A subclass is one capability for each form line, building its own trace
lines and output.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_ratio import ApplyRatio
from tax_calculator.domain.capability import Capability, CapabilityResult
from tax_calculator.domain.errors import ValidationError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.domain.trace.base import TraceLine
from tax_calculator.jurisdictions.ca.catalog import (
    RESIDENCE_ADJUSTED_COST_BASE,
    RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
    RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
    RESIDENCE_FMV_DEC_31_1981,
    RESIDENCE_OUTLAYS,
    RESIDENCE_PART_2_APPLIES,
    RESIDENCE_PLUS_ONE_YEAR,
    RESIDENCE_PROCEEDS,
    RESIDENCE_YEARS_DESIGNATED_1972_TO_1981,
    RESIDENCE_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_YEARS_OWNED_1972_TO_1981,
    RESIDENCE_YEARS_OWNED_AFTER_1981,
)


@dataclass(frozen=True)
class PrincipalResidenceRow:
    """One property worked, by `position` (from 1): its Part 1 lines and its Part 2 lines.

    The years are the form's lines 1 and 2 (`designated_after`, `designated_before`), 5 and 6
    (`owned_after`, `owned_before`), with their totals `designated` (line 3) and `owned` (line 7);
    `plus_one` is the "plus one" (1 or 0). `part_2_applies` is 1 when Part 2 applies, else 0, and
    `applies` says the same as a flag. The money of lines 8 to 13 is `proceeds`, `outlays`,
    `adjusted_cost_base`, `cost_base_1981`, `fmv_1981` and `adjustments_after_1981`. Part 1 is
    `gain` (line 18), `line_20`, `line_21`, `exempt` (line 23, rounded with `rounding`) and
    `line_24`. Part 2 lines are the `line_N` fields: a step the form says not to complete is 0, and
    its `*_completed` flag is False. `line_54` is the property's total capital gain.
    """

    position: int
    designated_after: int
    designated_before: int
    designated: int
    owned_after: int
    owned_before: int
    owned: int
    plus_one: int
    part_2_applies: int
    applies: bool
    proceeds: Decimal
    outlays: Decimal
    adjusted_cost_base: Decimal
    cost_base_1981: Decimal
    fmv_1981: Decimal
    adjustments_after_1981: Decimal
    gain: Decimal
    line_20: int
    line_21: Decimal
    rounding: RoundingRule
    exempt: Decimal
    line_24: Decimal
    pre_1982_completed: bool
    post_1981_completed: bool
    post_1981_loss_completed: bool
    line_27: Decimal
    line_29: int
    line_30: Decimal
    line_32: Decimal
    line_33: Decimal
    line_38: Decimal
    line_39: Decimal
    line_42: Decimal
    line_44: Decimal
    line_45: Decimal
    line_48: Decimal
    line_51: Decimal
    line_53: Decimal
    line_54: Decimal


class PrincipalResidenceRows(Capability):
    """Reads the consumed `properties` and works Part 1 and Part 2 of each property; a subclass
    produces `output` from the rows."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"properties": RecordList}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        properties: ArtifactKind[RecordList],
        output: ArtifactKind[Any],
    ) -> None:
        """Wire the rounding dataset, the record list read and the kind the subclass produces."""
        super().__init__(properties=properties, output=output)
        self._rounding = rounding
        self._properties = properties
        self._output_kind = output

    def _rows(self, inputs: tuple[Artifact[Any], ...]) -> tuple[PrincipalResidenceRow, ...]:
        """Each consumed property, in order, as a row with its lines worked."""
        records = self._input(inputs, self._properties).value.records
        rule = self._rounding.rounding
        rows: list[PrincipalResidenceRow] = []
        for position, record in enumerate(records, start=1):
            designated_after = record[RESIDENCE_YEARS_DESIGNATED_AFTER_1981]
            designated_before = record[RESIDENCE_YEARS_DESIGNATED_1972_TO_1981]
            owned_after = record[RESIDENCE_YEARS_OWNED_AFTER_1981]
            owned_before = record[RESIDENCE_YEARS_OWNED_1972_TO_1981]
            plus_one = record[RESIDENCE_PLUS_ONE_YEAR]
            proceeds = record[RESIDENCE_PROCEEDS]
            outlays = record[RESIDENCE_OUTLAYS]
            cost_base = record[RESIDENCE_ADJUSTED_COST_BASE]
            part_2_flag = record[RESIDENCE_PART_2_APPLIES]
            applies = part_2_flag == 1
            cost_base_1981 = record[RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981]
            fmv_1981 = record[RESIDENCE_FMV_DEC_31_1981]
            adjustments = record[RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981]
            designated = designated_after + designated_before
            owned = owned_after + owned_before
            if owned == 0:
                raise ValidationError(
                    f"property {position}: the years owned (lines 5 and 6) are 0, "
                    "so the exemption (line 23) cannot be divided by them"
                )
            if plus_one > 1:
                raise ValidationError(
                    f"property {position}: the plus one (line 20) is {plus_one}; "
                    "it is one year by law, so it must be 0 or 1"
                )
            if part_2_flag > 1:
                raise ValidationError(
                    f"property {position}: the Part 2 flag is {part_2_flag}; "
                    "it must be 0 or 1, as Part 2 applies only when it is 1"
                )
            if designated_after > owned_after:
                raise ValidationError(
                    f"property {position}: the years designated after 1981 (line 1) are "
                    f"{designated_after}, more than the years owned after 1981 (line 5), "
                    f"{owned_after}"
                )
            if designated_before > owned_before:
                raise ValidationError(
                    f"property {position}: the years designated 1972 to 1981 (line 2) are "
                    f"{designated_before}, more than the years owned 1972 to 1981 (line 6), "
                    f"{owned_before}"
                )
            # `+ zero` after each product: a zero product of a negative figure is -0, which
            # prints as "-0"; adding a positive zero makes it 0.
            zero = Decimal(0)
            gain = proceeds - (cost_base + outlays)
            line_20 = designated + plus_one
            line_21 = gain * line_20 + zero
            exempt = ApplyRatio.ratio_of(line_21, Decimal(1), Decimal(owned), rule)
            line_24 = max(zero, gain - exempt)

            pre = applies and designated_before < owned_before
            post = applies and designated_after < owned_after and fmv_1981 <= proceeds
            loss = applies and designated_after < owned_after
            line_27 = fmv_1981 - cost_base_1981 if pre else zero
            line_29 = designated_before + plus_one if pre else 0
            line_30 = line_27 * line_29 + zero if pre else zero
            line_32 = (
                ApplyRatio.ratio_of(line_30, Decimal(1), Decimal(owned_before), rule)
                if pre
                else zero
            )
            line_33 = max(zero, line_27 - line_32) if pre else zero
            line_38 = fmv_1981 + adjustments + outlays if post else zero
            line_39 = proceeds - line_38 if post else zero
            line_42 = line_39 * designated_after + zero if post else zero
            line_44 = (
                ApplyRatio.ratio_of(line_42, Decimal(1), Decimal(owned_after), rule)
                if post
                else zero
            )
            line_45 = max(zero, line_39 - line_44) if post else zero
            line_48 = max(zero, fmv_1981 - proceeds) if loss else zero
            line_51 = line_33 + line_45
            line_53 = max(zero, line_51 - line_48)
            line_54 = min(line_53, line_24) if applies else line_24
            rows.append(
                PrincipalResidenceRow(
                    position=position,
                    designated_after=designated_after,
                    designated_before=designated_before,
                    designated=designated,
                    owned_after=owned_after,
                    owned_before=owned_before,
                    owned=owned,
                    plus_one=plus_one,
                    part_2_applies=1 if applies else 0,
                    applies=applies,
                    proceeds=proceeds,
                    outlays=outlays,
                    adjusted_cost_base=cost_base,
                    cost_base_1981=cost_base_1981,
                    fmv_1981=fmv_1981,
                    adjustments_after_1981=adjustments,
                    gain=gain,
                    line_20=line_20,
                    line_21=line_21,
                    rounding=rule,
                    exempt=exempt,
                    line_24=line_24,
                    pre_1982_completed=pre,
                    post_1981_completed=post,
                    post_1981_loss_completed=loss,
                    line_27=line_27,
                    line_29=line_29,
                    line_30=line_30,
                    line_32=line_32,
                    line_33=line_33,
                    line_38=line_38,
                    line_39=line_39,
                    line_42=line_42,
                    line_44=line_44,
                    line_45=line_45,
                    line_48=line_48,
                    line_51=line_51,
                    line_53=line_53,
                    line_54=line_54,
                )
            )
        return tuple(rows)

    def _result(self, lines: list[Any]) -> CapabilityResult:
        """The `output` as the total of the `lines` (each with a `position` and a `result`), and
        the trace: those lines, then an `ItemsTotalLine`."""
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        trace: tuple[TraceLine, ...] = (
            *lines,
            ItemsTotalLine(self._output_kind, items, total),
        )
        return CapabilityResult(outputs=(Artifact(self._output_kind, total),), trace=trace)
