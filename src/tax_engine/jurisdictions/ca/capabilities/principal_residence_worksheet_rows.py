"""PrincipalResidenceWorksheetRows: the base of the capabilities of Form T2091(IND)-WS, the
Principal Residence Worksheet, and of Part 4 of Form T2091(IND), not registered itself.

Part 4 of Form T2091(IND) applies to a property for which Form T664 or T664(Seniors) was filed
(the 1994 capital gains election). The worksheet works that property's figures: Chart 1 (lines
14 to 19), Part 1 (lines 21 to 27) and Part 3 (lines 59 to 66). Part 4 takes line 66 as the
reduction (line 56) of the total capital gain (line 55, line 54 of Part 3), floored at 0 (line
57). Each property is worked on its own, as in `PrincipalResidenceRows`, which supplies its Part
1 and Part 2 lines. A property not filed has every worksheet line 0 and not completed, and its
line 57 is its line 54. Worksheet Part 2 (lines 28 to 58) is worked for a property filed with Part 2
of Form T2091(IND) applying, and Part 3 line 59 is then its line 58, else its line 27. The row
dataclass is `PrincipalResidenceWorksheetRow`.

Line 16 multiplies line 14 by the printed factor of the `chart_1_factor` dataset and rounds it
with that dataset's rule; lines 26, 35, 46 and 63 divide and round with the `rounding` dataset's
rule. A filed property whose years owned before 1995 (lines 4 and 5, so line 6) are 0, or whose
months owned after 1971 (line 62) are 0, is refused, as the quotient would have no divisor. A
T664 flag above 1 (a flag is 0 or 1) is refused too, as it would be read as "not filed". So is a
filed property whose worksheet line 1 is above its line 4 or above Part 1 line 1, or whose line 60
is above its line 62, a part never being more than its whole. Every other line is exact.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_ratio import ApplyRatio
from tax_engine.domain.errors import ValidationError
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.factor import FACTOR, Factor
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import Record, RecordList
from tax_engine.jurisdictions.ca.capabilities.principal_residence_rows import (
    PrincipalResidenceRow,
    PrincipalResidenceRows,
)
from tax_engine.jurisdictions.ca.catalog import (
    RESIDENCE_T664_FILED,
    RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994,
    RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994,
    RESIDENCE_WS_DESIGNATED_PROCEEDS,
    RESIDENCE_WS_ELECTED_CAPITAL_GAIN,
    RESIDENCE_WS_FMV_FEB_22_1994,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_1971,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992,
    RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_WS_YEARS_OWNED_AFTER_1981,
)


@dataclass(frozen=True)
class PrincipalResidenceWorksheetRow:
    """One property's worksheet and Part 4 lines, by `position` (from 1).

    `filed` is True when Form T664 or T664(Seniors) was filed for the property, and
    `chart_completed` when Chart 1 applies (line 7 is more than line 10, and the election was
    filed). A line the form says not to complete is 0. The worksheet lines are `line_N` with N the
    worksheet's number. Copies of earlier figures are kept where a trace line reads them: `line_2`
    and `line_5` are the form's lines 2 and 6, `line_15` is line 7, `line_20` is line 8, and
    `line_54` is the property's total capital gain (Part 3 line 54, which is line 55 of Part 4).
    Lines 28 to 58 are Part 2 (`part_2_completed` when the election was filed and Part 2 of Form
    T2091(IND) applies; `pre_1982_completed`, `post_1981_completed` and `post_1981_loss_completed`
    for areas A, B and C); its lines 56 and 57 are `part_2_line_56` and `part_2_line_57`, as
    `line_56` and `line_57` are those of Part 4. `line_59` is line 58 when Part 2 is completed,
    else line 27. `factor` is the printed 1.1, `rounding` the worksheet's rule for
    lines 26, 35, 46 and 63, and `chart_rounding` the rule of line 16.
    """

    position: int
    filed: bool
    chart_completed: bool
    plus_one: int
    factor: Decimal
    rounding: RoundingRule
    chart_rounding: RoundingRule
    line_1: int
    line_2: int
    line_3: int
    line_4: int
    line_5: int
    line_6: int
    line_10: Decimal
    line_14: Decimal
    line_15: Decimal
    line_16: Decimal
    line_17: Decimal
    line_18: Decimal
    line_19: Decimal
    line_20: Decimal
    line_21: Decimal
    line_22: Decimal
    line_23: int
    line_24: Decimal
    line_26: Decimal
    line_27: Decimal
    line_54: Decimal
    part_2_completed: bool
    pre_1982_completed: bool
    post_1981_completed: bool
    post_1981_loss_completed: bool
    line_28: Decimal
    line_29: Decimal
    line_30: Decimal
    line_31: Decimal
    line_32: int
    line_33: Decimal
    line_34: int
    line_35: Decimal
    line_36: Decimal
    line_37: Decimal
    line_38: Decimal
    line_39: Decimal
    line_40: Decimal
    line_41: Decimal
    line_42: Decimal
    line_43: int
    line_44: Decimal
    line_45: int
    line_46: Decimal
    line_47: Decimal
    line_48: Decimal
    line_49: Decimal
    line_50: Decimal
    line_51: Decimal
    line_52: Decimal
    line_53: Decimal
    part_2_line_54: Decimal
    line_55: Decimal
    part_2_line_56: Decimal
    part_2_line_57: Decimal
    line_58: Decimal
    line_56: Decimal
    line_57: Decimal
    line_59: Decimal
    line_60: int
    line_61: Decimal
    line_62: int
    line_63: Decimal
    line_64: Decimal
    line_65: Decimal
    line_66: Decimal


class PrincipalResidenceWorksheetRows(PrincipalResidenceRows):
    """Works the worksheet and Part 4 lines of each consumed property; a subclass produces
    `output` from the rows, one line per capability."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "rounding": ROUNDING_ONLY,
        "chart_1_factor": FACTOR,
    }

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        chart_1_factor: ParameterDataset[Factor],
        properties: ArtifactKind[RecordList],
        output: ArtifactKind[Any],
    ) -> None:
        """Wire the rounding dataset, the Chart 1 factor dataset, the record list read and the kind
        the subclass produces."""
        super().__init__(rounding, properties, output)
        self._chart_1_factor = chart_1_factor

    def _worksheet_rows(
        self, inputs: tuple[Artifact[Any], ...]
    ) -> tuple[PrincipalResidenceWorksheetRow, ...]:
        """Each consumed property's worksheet and Part 4 lines, in order."""
        bases = self._rows(inputs)
        records = self._input(inputs, self._properties).value.records
        return tuple(
            self._worksheet_row(base, record) for base, record in zip(bases, records, strict=True)
        )

    def _worksheet_row(
        self, base: PrincipalResidenceRow, record: Record
    ) -> PrincipalResidenceWorksheetRow:
        """The worksheet and Part 4 lines of one property, from its Part 1 row and its record."""
        factor = self._chart_1_factor.values.value
        chart_rounding = self._chart_1_factor.rounding
        rule = self._rounding.rounding
        t664_flag = record[RESIDENCE_T664_FILED]
        if t664_flag > 1:
            raise ValidationError(
                f"property {base.position}: the T664 flag is {t664_flag}; it must be 0 or 1, "
                "as Form T664 was filed when it is 1"
            )
        if t664_flag != 1:
            return self._not_filed(base, factor, chart_rounding, rule)
        zero = Decimal(0)
        line_1 = record[RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981]
        line_4 = record[RESIDENCE_WS_YEARS_OWNED_AFTER_1981]
        line_3 = line_1 + base.designated_before
        line_6 = line_4 + base.owned_before
        if line_6 == 0:
            raise ValidationError(
                f"property {base.position}: worksheet line 4 plus line 5 (line 6) is 0, "
                "so worksheet line 26 cannot be divided by it"
            )
        line_62 = record[RESIDENCE_WS_MONTHS_OWNED_AFTER_1971]
        if line_62 == 0:
            raise ValidationError(
                f"property {base.position}: worksheet line 62 (months owned after 1971) is 0, "
                "so worksheet line 63 cannot be divided by it"
            )
        if line_1 > line_4:
            raise ValidationError(
                f"property {base.position}: worksheet line 1 (years designated before 1995) is "
                f"{line_1}, more than line 4 (years owned in the same period), {line_4}"
            )
        if line_1 > base.designated_after:
            raise ValidationError(
                f"property {base.position}: worksheet line 1 (years designated before 1995) is "
                f"{line_1}, more than the years designated after 1981 (line 1 of Form "
                f"T2091(IND)), {base.designated_after}"
            )
        line_60 = record[RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992]
        if line_60 > line_62:
            raise ValidationError(
                f"property {base.position}: worksheet line 60 (months owned after February 1992 "
                f"and before March 1994) is {line_60}, more than line 62 (months owned after "
                f"1971 and before March 1994), {line_62}"
            )
        # Chart 1: line 14 is the fair market value at February 22, 1994 (line 10); line 15 the
        # designated proceeds (line 7). Chart 1 applies only when line 15 is more than line 14.
        line_14 = record[RESIDENCE_WS_FMV_FEB_22_1994]
        line_15 = record[RESIDENCE_WS_DESIGNATED_PROCEEDS]
        chart = line_15 > line_14
        line_16 = (
            ApplyRatio.ratio_of(line_14, factor, Decimal(1), chart_rounding) if chart else zero
        )
        line_17 = max(zero, line_15 - line_16) if chart else zero
        line_18 = line_14 - line_17 if chart else zero
        line_19 = line_18 if chart else line_14
        # Part 1 of the worksheet.
        line_20 = record[RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994]
        line_21 = line_19 - line_20
        line_22 = line_21
        line_23 = line_3 + base.plus_one
        line_24 = line_22 * line_23 + zero
        line_26 = ApplyRatio.ratio_of(line_24, Decimal(1), Decimal(line_6), rule)
        line_27 = line_21 - line_26
        # Part 2 of the worksheet, completed when Part 2 of Form T2091(IND) applies. Area A is
        # skipped when every year owned before 1982 was designated, area B when every year owned
        # after 1981 was designated or line 11 is more than line 19, and area C as area B's years.
        part_2 = base.applies
        area_a = part_2 and base.designated_before < base.owned_before
        area_b = part_2 and line_1 < line_4 and base.fmv_1981 <= line_19
        area_c = part_2 and line_1 < line_4
        line_28 = base.fmv_1981 if area_a else zero
        line_29 = base.cost_base_1981 if area_a else zero
        line_30 = line_28 - line_29
        line_31 = line_30
        line_32 = base.designated_before + base.plus_one if area_a else 0
        line_33 = line_31 * line_32 + zero
        line_34 = base.owned_before if area_a else 0
        line_35 = (
            ApplyRatio.ratio_of(line_33, Decimal(1), Decimal(line_34), rule) if area_a else zero
        )
        line_36 = max(zero, line_30 - line_35)
        line_37 = line_19 if area_b else zero
        line_38 = base.fmv_1981 if area_b else zero
        line_39 = record[RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994] if area_b else zero
        line_40 = line_38 + line_39
        line_41 = line_37 - line_40
        line_42 = line_41
        line_43 = line_1 if area_b else 0
        line_44 = line_42 * line_43 + zero
        line_45 = line_4 if area_b else 0
        line_46 = (
            ApplyRatio.ratio_of(line_44, Decimal(1), Decimal(line_45), rule) if area_b else zero
        )
        line_47 = max(zero, line_41 - line_46)
        line_48 = base.fmv_1981 if area_c else zero
        line_49 = line_19 if area_c else zero
        line_50 = max(zero, line_48 - line_49)
        line_51 = line_36
        line_52 = line_47
        line_53 = line_51 + line_52
        part_2_line_54 = line_50
        line_55 = max(zero, line_53 - part_2_line_54) if part_2 else zero
        part_2_line_56 = line_27 if part_2 else zero
        part_2_line_57 = line_55
        line_58 = min(part_2_line_56, part_2_line_57)
        # Part 3 of the worksheet.
        line_59 = line_58 if part_2 else line_27
        line_61 = line_59 * line_60 + zero
        line_63 = ApplyRatio.ratio_of(line_61, Decimal(1), Decimal(line_62), rule)
        line_64 = line_59 - line_63
        line_65 = record[RESIDENCE_WS_ELECTED_CAPITAL_GAIN]
        line_66 = min(line_64, line_65)
        # Part 4 of Form T2091(IND): line 56 is worksheet line 66; line 57 is line 54 less it.
        line_56 = line_66
        line_57 = max(zero, base.line_54 - line_56)
        return PrincipalResidenceWorksheetRow(
            position=base.position,
            filed=True,
            chart_completed=chart,
            plus_one=base.plus_one,
            factor=factor,
            rounding=rule,
            chart_rounding=chart_rounding,
            line_1=line_1,
            line_2=base.designated_before,
            line_3=line_3,
            line_4=line_4,
            line_5=base.owned_before,
            line_6=line_6,
            line_10=line_14,
            line_14=line_14,
            line_15=line_15,
            line_16=line_16,
            line_17=line_17,
            line_18=line_18,
            line_19=line_19,
            line_20=line_20,
            line_21=line_21,
            line_22=line_22,
            line_23=line_23,
            line_24=line_24,
            line_26=line_26,
            line_27=line_27,
            line_54=base.line_54,
            part_2_completed=part_2,
            pre_1982_completed=area_a,
            post_1981_completed=area_b,
            post_1981_loss_completed=area_c,
            line_28=line_28,
            line_29=line_29,
            line_30=line_30,
            line_31=line_31,
            line_32=line_32,
            line_33=line_33,
            line_34=line_34,
            line_35=line_35,
            line_36=line_36,
            line_37=line_37,
            line_38=line_38,
            line_39=line_39,
            line_40=line_40,
            line_41=line_41,
            line_42=line_42,
            line_43=line_43,
            line_44=line_44,
            line_45=line_45,
            line_46=line_46,
            line_47=line_47,
            line_48=line_48,
            line_49=line_49,
            line_50=line_50,
            line_51=line_51,
            line_52=line_52,
            line_53=line_53,
            part_2_line_54=part_2_line_54,
            line_55=line_55,
            part_2_line_56=part_2_line_56,
            part_2_line_57=part_2_line_57,
            line_58=line_58,
            line_56=line_56,
            line_57=line_57,
            line_59=line_59,
            line_60=line_60,
            line_61=line_61,
            line_62=line_62,
            line_63=line_63,
            line_64=line_64,
            line_65=line_65,
            line_66=line_66,
        )

    @staticmethod
    def _not_filed(
        base: PrincipalResidenceRow,
        factor: Decimal,
        chart_rounding: RoundingRule,
        rule: RoundingRule,
    ) -> PrincipalResidenceWorksheetRow:
        """The row of a property whose T664 election was not filed: every worksheet line is 0, and
        line 57 is its line 54."""
        zero = Decimal(0)
        return PrincipalResidenceWorksheetRow(
            position=base.position,
            filed=False,
            chart_completed=False,
            plus_one=base.plus_one,
            factor=factor,
            rounding=rule,
            chart_rounding=chart_rounding,
            line_1=0,
            line_2=base.designated_before,
            line_3=0,
            line_4=0,
            line_5=base.owned_before,
            line_6=0,
            line_10=zero,
            line_14=zero,
            line_15=zero,
            line_16=zero,
            line_17=zero,
            line_18=zero,
            line_19=zero,
            line_20=zero,
            line_21=zero,
            line_22=zero,
            line_23=0,
            line_24=zero,
            line_26=zero,
            line_27=zero,
            line_54=base.line_54,
            part_2_completed=False,
            pre_1982_completed=False,
            post_1981_completed=False,
            post_1981_loss_completed=False,
            line_28=zero,
            line_29=zero,
            line_30=zero,
            line_31=zero,
            line_32=0,
            line_33=zero,
            line_34=0,
            line_35=zero,
            line_36=zero,
            line_37=zero,
            line_38=zero,
            line_39=zero,
            line_40=zero,
            line_41=zero,
            line_42=zero,
            line_43=0,
            line_44=zero,
            line_45=0,
            line_46=zero,
            line_47=zero,
            line_48=zero,
            line_49=zero,
            line_50=zero,
            line_51=zero,
            line_52=zero,
            line_53=zero,
            part_2_line_54=zero,
            line_55=zero,
            part_2_line_56=zero,
            part_2_line_57=zero,
            line_58=zero,
            line_56=zero,
            line_57=base.line_54,
            line_59=zero,
            line_60=0,
            line_61=zero,
            line_62=0,
            line_63=zero,
            line_64=zero,
            line_65=zero,
            line_66=zero,
        )
