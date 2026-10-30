"""Trace lines for gains: a principal residence's taxable gain, its Part 2 lines, and one
disposition's gain or loss.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "PrincipalResidenceDesignationBox",
    "PrincipalResidenceGainLine",
    "PrincipalResidenceLine27",
    "PrincipalResidenceLine29",
    "PrincipalResidenceLine30",
    "PrincipalResidenceLine32",
    "PrincipalResidenceLine33",
    "PrincipalResidenceLine38",
    "PrincipalResidenceLine39",
    "PrincipalResidenceLine42",
    "PrincipalResidenceLine44",
    "PrincipalResidenceLine45",
    "PrincipalResidenceLine48",
    "PrincipalResidenceLine51",
    "PrincipalResidenceLine53",
    "PrincipalResidenceWorksheetLine3",
    "PrincipalResidenceWorksheetLine6",
    "PrincipalResidenceWorksheetLine16",
    "PrincipalResidenceWorksheetLine17",
    "PrincipalResidenceWorksheetLine18",
    "PrincipalResidenceWorksheetLine19",
    "PrincipalResidenceWorksheetLine21",
    "PrincipalResidenceWorksheetLine23",
    "PrincipalResidenceWorksheetLine24",
    "PrincipalResidenceWorksheetLine26",
    "PrincipalResidenceWorksheetLine27",
    "PrincipalResidenceWorksheetLine30",
    "PrincipalResidenceWorksheetLine32",
    "PrincipalResidenceWorksheetLine33",
    "PrincipalResidenceWorksheetLine35",
    "PrincipalResidenceWorksheetLine36",
    "PrincipalResidenceWorksheetLine40",
    "PrincipalResidenceWorksheetLine41",
    "PrincipalResidenceWorksheetLine44",
    "PrincipalResidenceWorksheetLine46",
    "PrincipalResidenceWorksheetLine47",
    "PrincipalResidenceWorksheetLine50",
    "PrincipalResidenceWorksheetLine53",
    "PrincipalResidenceWorksheetLine55",
    "PrincipalResidenceWorksheetLine58",
    "PrincipalResidenceWorksheetLine59",
    "PrincipalResidenceWorksheetLine61",
    "PrincipalResidenceWorksheetLine63",
    "PrincipalResidenceWorksheetLine64",
    "PrincipalResidenceWorksheetLine66",
    "PrincipalResidenceLine56",
    "PrincipalResidenceLine57",
    "DispositionGainLine",
    "DispositionGainOnlyLine",
    "DepreciablePropertyGainLine",
    "QffpGainLine",
    "FarmLossAppliedLine",
    "PersonalUsePropertyGainLine",
    "DispositionProceedsLine",
    "NetCapitalLossesRowLine",
    "ReserveRowForPeriodLine",
    "QbtBeforeQccLine",
]


@dataclass(frozen=True)
class PrincipalResidenceGainLine(TraceLine):
    """The taxable gain `result` of one property, by `position` (from 1), for `output`.

    It follows Part 1 of the form designating a property as a principal residence: the years
    designated after 1981 and from 1972 to 1981 (lines 1 and 2) and their total `designated` (line
    3, carried to line 4), the years owned in the same periods (lines 5 and 6) and their total
    `owned` (line 7), and `plus_one` (1 if the "plus one" applies, else 0); `proceeds`,
    `adjusted_cost_base` and `outlays` (lines 8 to 10) and `gain` (line 18) the proceeds less the
    other two; `line_20` the designated years plus the "plus one" and `line_21` the gain multiplied
    by it; `exempt` (line 23) line 21 divided by the years owned, rounded with `rounding`.

    Part 2: `part_2_applies` (1 if the property is one of two or more principal residences a family
    member owned on December 31, 1981, else 0); `line_53` the net capital gain of Part 2 and
    `line_24` the gain of Part 1 (line 24, not below 0). `result` is line 54, the lesser of
    `line_53` and `line_24` when Part 2 applies, else `line_24`. Lines 14 to 21 are exact.

    Its own class, not a `DisabilityTransferLine`: the property is worked in steps of its own that
    the English rendering shows one by one.
    """

    output: Money
    position: int
    years_designated_after_1981: int
    years_designated_1972_to_1981: int
    designated: int
    years_owned_after_1981: int
    years_owned_1972_to_1981: int
    owned: int
    plus_one: int
    proceeds: Decimal
    adjusted_cost_base: Decimal
    outlays: Decimal
    gain: Decimal
    line_20: int
    line_21: Decimal
    rounding: RoundingRule
    exempt: Decimal
    part_2_applies: int
    line_53: Decimal
    line_24: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's total capital gain, line 54."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceDesignationBox(TraceLine):
    """Form 5000-S3 Part 1 line 17900, the principal residence designation box, for `output`: the
    box, 0 with no property, 3 with more than one property, else for the one property 1 when its
    years designated (`designated`, Form T2091(IND) line 3) are at least its years owned (`owned`,
    line 7) less one, else 2. `properties` is the count of properties; `designated` and `owned`
    are the one property's years, 0 when there is not exactly one property.
    """

    output: ArtifactKind[int]
    properties: int
    designated: int
    owned: int
    box: int

    @property
    def amount(self) -> Decimal:
        """The box."""
        return Decimal(self.box)


@dataclass(frozen=True)
class PrincipalResidenceLine27(TraceLine):
    """Form T2091(IND) Part 2 line 27 "Line 25 minus line 26" of the property at `position` (from
    1), for `output`: the fair market value on December 31, 1981 (`line_12`) less the adjusted cost
    base on that date (`line_11`), not floored, `result`. `completed` is False when area A is not
    completed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_12: Decimal
    line_11: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 27."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine29(TraceLine):
    """Form T2091(IND) Part 2 line 29 "Line 2 plus 1 (see note on page 4)" of the property at
    `position` (from 1), for `output`: the years designated from 1972 to 1981 (`line_2`) plus
    `plus_one`, `result`. `completed` is False when area A is not completed, and then `result` is
    0.
    """

    output: Money
    position: int
    completed: bool
    line_2: int
    plus_one: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 29."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine30(TraceLine):
    """Form T2091(IND) Part 2 line 30 "Multiply line 28 by line 29." of the property at `position`
    (from 1), for `output`: line 27 (`line_27`) multiplied by line 29 (`line_29`), `result`.
    `completed` is False when area A is not completed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_27: Decimal
    line_29: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 30."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine32(TraceLine):
    """Form T2091(IND) Part 2 line 32 "Divide line 30 by line 31." of the property at `position`
    (from 1), for `output`: line 30 (`line_30`) divided by the years owned from 1972 to 1981
    (`line_6`), rounded with `rounding`, `result`. `completed` is False when area A is not
    completed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_30: Decimal
    line_6: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 32."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine33(TraceLine):
    """Form T2091(IND) Part 2 line 33 "Line 27 minus line 32 (if negative, enter "0")" of the
    property at `position` (from 1), for `output`: line 27 (`line_27`) less line 32 (`line_32`), not
    below 0, `result`. `completed` is False when area A is not completed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_27: Decimal
    line_32: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 33, the pre-1982 gain."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine38(TraceLine):
    """Form T2091(IND) Part 2 line 38 "Add lines 35 to 37." of the property at `position` (from 1),
    for `output`: the fair market value on December 31, 1981 (`line_12`), the adjustments made to
    the cost base after 1981 (`line_13`) and the outlays (`line_9`), added, `result`. `completed` is
    False when area B is not completed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_12: Decimal
    line_13: Decimal
    line_9: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 38."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine39(TraceLine):
    """Form T2091(IND) Part 2 line 39 "Line 34 minus line 38" of the property at `position` (from
    1), for `output`: the proceeds (`line_8`, line 34) less line 38 (`line_38`), not floored,
    `result`. `completed` is False when area B is not completed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_8: Decimal
    line_38: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 39."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine42(TraceLine):
    """Form T2091(IND) Part 2 line 42 "Multiply line 40 by line 41." of the property at `position`
    (from 1), for `output`: line 39 (`line_39`) multiplied by the years designated after 1981
    (`line_1`), not floored, `result`. `completed` is False when area B is not completed, and then
    `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_39: Decimal
    line_1: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 42."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine44(TraceLine):
    """Form T2091(IND) Part 2 line 44 "Divide line 42 by line 43." of the property at `position`
    (from 1), for `output`: line 42 (`line_42`) divided by the years owned after 1981 (`line_5`),
    rounded with `rounding`, `result`. `completed` is False when area B is not completed, and then
    `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_42: Decimal
    line_5: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 44."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine45(TraceLine):
    """Form T2091(IND) Part 2 line 45 "Line 39 minus line 44 (if negative, enter "0")" of the
    property at `position` (from 1), for `output`: line 39 (`line_39`) less line 44 (`line_44`), not
    below 0, `result`. `completed` is False when area B is not completed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_39: Decimal
    line_44: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 45, the post-1981 gain."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine48(TraceLine):
    """Form T2091(IND) Part 2 line 48 "Line 46 minus line 47 (if negative, enter "0")" of the
    property at `position` (from 1), for `output`: the fair market value on December 31, 1981
    (`line_12`, line 46) less the proceeds (`line_8`, line 47), not below 0, `result`. `completed`
    is False when area C is not completed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_12: Decimal
    line_8: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 48, the post-1981 loss."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine51(TraceLine):
    """Form T2091(IND) Part 2 line 51 "Line 49 plus line 50" of the property at `position` (from
    1), for `output`: the pre-1982 gain (`line_33`, line 49) plus the post-1981 gain (`line_45`,
    line 50), `result`. `completed` is False when Part 2 does not apply, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_33: Decimal
    line_45: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 51."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine53(TraceLine):
    """Form T2091(IND) Part 2 line 53 "Line 51 minus line 52 (if negative, enter "0")" of the
    property at `position` (from 1), for `output`: line 51 (`line_51`) less the post-1981 loss
    (`line_48`, line 52), not below 0, `result`. `completed` is False when Part 2 does not apply,
    and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_51: Decimal
    line_48: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 53, the net capital gain of Part 2."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine3(TraceLine):
    """Form T2091(IND)-WS line 3 "Total number of years designated before 1995 (line 1 plus line 2)"
    of the property at `position` (from 1), for `output`: the years designated after 1981 and before
    1995 (`line_1`) plus the years designated before 1982 (`line_2`, line 2 of Form T2091(IND)),
    `result`. `completed` is False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_1: int
    line_2: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 3."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine6(TraceLine):
    """Form T2091(IND)-WS line 6 "Total number of years owned before 1995 (line 4 plus line 5)" of
    the property at `position` (from 1), for `output`: the years owned after 1981 and before 1995
    (`line_4`) plus the years owned before 1982 (`line_5`, line 6 of Form T2091(IND)), `result`.
    `completed` is False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_4: int
    line_5: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 6."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine16(TraceLine):
    """Form T2091(IND)-WS Chart 1 line 16 "Multiply line 14 by 1.1." of the property at `position`
    (from 1), for `output`: line 14 (`line_14`) times the printed factor (`factor`), rounded with
    `rounding`, `result`. `completed` is False unless Chart 1 applies, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_14: Decimal
    factor: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's Chart 1 line 16."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine17(TraceLine):
    """Form T2091(IND)-WS Chart 1 line 17 "Line 15 minus line 16 (if negative, enter "0")" of the
    property at `position` (from 1), for `output`: line 15 (`line_15`) less line 16 (`line_16`), not
    below 0, `result`. `completed` is False unless Chart 1 applies, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_15: Decimal
    line_16: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's Chart 1 line 17."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine18(TraceLine):
    """Form T2091(IND)-WS Chart 1 line 18 "Line 14 minus line 17" of the property at `position`
    (from 1), for `output`: line 14 (`line_14`) less line 17 (`line_17`), `result`, not floored.
    `completed` is False unless Chart 1 applies, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_14: Decimal
    line_17: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's Chart 1 line 18."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine19(TraceLine):
    """Form T2091(IND)-WS line 19 "Enter the amount from line 18 if you completed Chart 1.
    Otherwise, enter the amount from line 10." of the property at `position` (from 1), for `output`:
    line 18 (`line_18`) when `chart_completed`, else line 10 (`line_10`), `result`. `completed` is
    False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    chart_completed: bool
    line_18: Decimal
    line_10: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 19."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine21(TraceLine):
    """Form T2091(IND)-WS line 21 "Line 19 minus line 20" of the property at `position` (from 1),
    for `output`: line 19 (`line_19`) less line 20 (`line_20`), not floored, `result`.
    `completed` is False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_19: Decimal
    line_20: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 21, the adjusted gain before the exemption."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine23(TraceLine):
    """Form T2091(IND)-WS line 23 "Line 3 plus 1 (see note below)" of the property at `position`
    (from 1), for `output`: line 3 (`line_3`) plus `plus_one`, `result`. `completed` is False when
    the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_3: int
    plus_one: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 23."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine24(TraceLine):
    """Form T2091(IND)-WS line 24 "Multiply line 22 by line 23." of the property at `position`
    (from 1), for `output`: line 22 (`line_22`) times line 23 (`line_23`), `result`. `completed` is
    False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_22: Decimal
    line_23: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 24."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine26(TraceLine):
    """Form T2091(IND)-WS line 26 "Divide line 24 by line 25." of the property at `position` (from
    1), for `output`: line 24 (`line_24`) divided by line 25 (`line_25`), rounded with `rounding`,
    `result`. `completed` is False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_24: Decimal
    line_25: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 26."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine27(TraceLine):
    """Form T2091(IND)-WS line 27 "Line 21 minus line 26" of the property at `position` (from 1),
    for `output`: line 21 (`line_21`) less line 26 (`line_26`), not floored, `result`.
    `completed` is False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_21: Decimal
    line_26: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 27, the net adjusted gain."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine30(TraceLine):
    """Form T2091(IND)-WS line 30 "Line 28 minus line 29" of the property at `position` (from 1),
    for `output`: line 28 (`line_28`) less line 29 (`line_29`), not floored, `result`. `completed`
    is False when the T664 election was not filed, Part 2 does not apply or the area the line is in
    is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_28: Decimal
    line_29: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 30."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine32(TraceLine):
    """Form T2091(IND)-WS line 32 "Line 2 plus 1 (see note below)" of the property at `position`
    (from 1), for `output`: line 2 (`line_2`) plus `plus_one`, `result`. `completed` is False when
    the T664 election was not filed, Part 2 does not apply or the area the line is in is skipped,
    and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_2: int
    plus_one: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 32."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine33(TraceLine):
    """Form T2091(IND)-WS line 33 "Multiply line 31 by line 32." of the property at `position` (from
    1), for `output`: line 31 (`line_31`) times line 32 (`line_32`), `result`. `completed` is False
    when the T664 election was not filed, Part 2 does not apply or the area the line is in is
    skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_31: Decimal
    line_32: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 33."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine35(TraceLine):
    """Form T2091(IND)-WS line 35 "Divide line 33 by line 34." of the property at `position` (from
    1), for `output`: line 33 (`line_33`) divided by line 34 (`line_34`), rounded with `rounding`,
    `result`. `completed` is False when the T664 election was not filed, Part 2 does not apply or
    the area the line is in is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_33: Decimal
    line_34: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 35."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine36(TraceLine):
    """Form T2091(IND)-WS line 36 "Line 30 minus line 35 (if negative, enter "0")" of the property
    at `position` (from 1), for `output`: line 30 (`line_30`) less line 35 (`line_35`), not below 0,
    `result`. `completed` is False when the T664 election was not filed, Part 2 does not apply or
    the area the line is in is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_30: Decimal
    line_35: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 36."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine40(TraceLine):
    """Form T2091(IND)-WS line 40 "Line 38 plus line 39" of the property at `position` (from 1), for
    `output`: line 38 (`line_38`) plus line 39 (`line_39`), `result`. `completed` is False when the
    T664 election was not filed, Part 2 does not apply or the area the line is in is skipped, and
    then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_38: Decimal
    line_39: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 40."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine41(TraceLine):
    """Form T2091(IND)-WS line 41 "Line 37 minus line 40" of the property at `position` (from 1),
    for `output`: line 37 (`line_37`) less line 40 (`line_40`), not floored, `result`. `completed`
    is False when the T664 election was not filed, Part 2 does not apply or the area the line is in
    is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_37: Decimal
    line_40: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 41."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine44(TraceLine):
    """Form T2091(IND)-WS line 44 "Multiply line 42 by line 43." of the property at `position` (from
    1), for `output`: line 42 (`line_42`) times line 43 (`line_43`), `result`. `completed` is False
    when the T664 election was not filed, Part 2 does not apply or the area the line is in is
    skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_42: Decimal
    line_43: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 44."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine46(TraceLine):
    """Form T2091(IND)-WS line 46 "Divide line 44 by line 45." of the property at `position` (from
    1), for `output`: line 44 (`line_44`) divided by line 45 (`line_45`), rounded with `rounding`,
    `result`. `completed` is False when the T664 election was not filed, Part 2 does not apply or
    the area the line is in is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_44: Decimal
    line_45: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 46."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine47(TraceLine):
    """Form T2091(IND)-WS line 47 "Line 41 minus line 46 (if negative, enter "0")" of the property
    at `position` (from 1), for `output`: line 41 (`line_41`) less line 46 (`line_46`), not below 0,
    `result`. `completed` is False when the T664 election was not filed, Part 2 does not apply or
    the area the line is in is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_41: Decimal
    line_46: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 47."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine50(TraceLine):
    """Form T2091(IND)-WS line 50 "Line 48 minus line 49 (if negative, enter "0")" of the property
    at `position` (from 1), for `output`: line 48 (`line_48`) less line 49 (`line_49`), not below 0,
    `result`. `completed` is False when the T664 election was not filed, Part 2 does not apply or
    the area the line is in is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_48: Decimal
    line_49: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 50."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine53(TraceLine):
    """Form T2091(IND)-WS line 53 "Line 51 plus line 52" of the property at `position` (from 1), for
    `output`: line 51 (`line_51`) plus line 52 (`line_52`), `result`. `completed` is False when the
    T664 election was not filed, Part 2 does not apply or the area the line is in is skipped, and
    then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_51: Decimal
    line_52: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 53."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine55(TraceLine):
    """Form T2091(IND)-WS line 55 "Line 53 minus line 54 (if negative, enter "0")" of the property
    at `position` (from 1), for `output`: line 53 (`line_53`) less line 54 (`line_54`), not below 0,
    `result`. `completed` is False when the T664 election was not filed, Part 2 does not apply or
    the area the line is in is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_53: Decimal
    line_54: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 55."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine58(TraceLine):
    """Form T2091(IND)-WS line 58 "Enter whichever amount is less: line 56 or line 57." of the
    property at `position` (from 1), for `output`: the lesser of line 56 (`line_56`) and line 57
    (`line_57`), `result`. `completed` is False when the T664 election was not filed, Part 2 does
    not apply or the area the line is in is skipped, and then `result` is 0."""

    output: Money
    position: int
    completed: bool
    line_56: Decimal
    line_57: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 58."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine59(TraceLine):
    """Form T2091(IND)-WS line 59 "If you completed Part 2, enter the amount from line 58.
    Otherwise, enter the amount from line 27." of the property at `position` (from 1), for
    `output`: line 58 (`line_58`) when `part_2_completed`, else line 27 (`line_27`), `result`.
    `completed` is False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    part_2_completed: bool
    line_27: Decimal
    line_58: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 59."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine61(TraceLine):
    """Form T2091(IND)-WS line 61 "Multiply line 59 by line 60." of the property at `position` (from
    1), for `output`: line 59 (`line_59`) times line 60 (`line_60`), `result`. `completed` is False
    when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_59: Decimal
    line_60: int
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 61."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine63(TraceLine):
    """Form T2091(IND)-WS line 63 "Divide line 61 by line 62." of the property at `position` (from
    1), for `output`: line 61 (`line_61`) divided by line 62 (`line_62`), rounded with `rounding`,
    `result`. `completed` is False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_61: Decimal
    line_62: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 63."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine64(TraceLine):
    """Form T2091(IND)-WS line 64 "Line 59 minus line 63" of the property at `position` (from 1),
    for `output`: line 59 (`line_59`) less line 63 (`line_63`), not floored, `result`.
    `completed` is False when the T664 election was not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_59: Decimal
    line_63: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 64, the total adjusted gain."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceWorksheetLine66(TraceLine):
    """Form T2091(IND)-WS line 66 "Enter whichever amount is less: line 64 or line 65." of the
    property at `position` (from 1), for `output`: the lesser of line 64 (`line_64`) and line 65
    (`line_65`, the elected capital gain), `result`. `completed` is False when the T664 election was
    not filed, and then `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_64: Decimal
    line_65: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's worksheet line 66, the reduction as a result of the election."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine56(TraceLine):
    """Form T2091(IND) Part 4 line 56 "Reduction as a result of the capital gains election (line 66
    of Form T2091(IND)-WS)" of the property at `position` (from 1), for `output`: worksheet line 66
    (`line_66`), `result`. `completed` is False when the T664 election was not filed, and then
    `result` is 0.
    """

    output: Money
    position: int
    completed: bool
    line_66: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 56."""
        return self.result


@dataclass(frozen=True)
class PrincipalResidenceLine57(TraceLine):
    """Form T2091(IND) Part 4 line 57 "Line 55 minus line 56 (if negative, enter "0")" of the
    property at `position` (from 1), for `output`: line 55 (`line_55`, the total capital gain before
    the reduction) less line 56 (`line_56`), not below 0, `result`. It has no `completed` flag, as
    the form has none for it.
    """

    output: Money
    position: int
    line_55: Decimal
    line_56: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The property's line 57, the total capital gain after the election."""
        return self.result


@dataclass(frozen=True)
class DispositionGainLine(TraceLine):
    """The gain or loss `result` of one disposition, by `position` (from 1), for `output`.

    It follows a row of Schedule 3 Part 3: column 5 "Gain or loss (column 2 minus columns 3 and
    4)", the `proceeds` (column 2) less the `adjusted_cost_base` (column 3) and the `outlays`
    (column 4). A loss is a negative `result`. Exact.

    Its own class, not a `PrincipalResidenceGainLine`: a row has only the three columns and no
    exemption.
    """

    output: Money
    position: int
    proceeds: Decimal
    adjusted_cost_base: Decimal
    outlays: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The row's gain or loss, signed."""
        return self.result


@dataclass(frozen=True)
class DispositionGainOnlyLine(TraceLine):
    """The figure `result` counted for one disposition, by `position` (from 1), for `output`.

    It follows a row of Schedule 3 Part 3 whose line is "Total gain only": the `gain` is column 5
    (the `proceeds` less the `adjusted_cost_base` and the `outlays`), and `result` is that gain
    not below 0, a loss counting 0. Exact.

    Its own class, not a `DispositionGainLine`: it carries the gain and the figure counted.
    """

    output: Money
    position: int
    proceeds: Decimal
    adjusted_cost_base: Decimal
    outlays: Decimal
    gain: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The figure counted, never negative."""
        return self.result


@dataclass(frozen=True)
class DepreciablePropertyGainLine(TraceLine):
    """The figure `result` counted for one real estate disposition, by `position` (from 1), for
    `output`.

    It follows a row of Schedule 3 Part 3 line 5: the `gain` is column 5 (the `proceeds` less the
    `adjusted_cost_base`, the restricted farm loss applied, `farm_loss_applied` (the Guide's line C,
    `farm_loss_property_taxes`, plus line D, `farm_loss_interest`), which Guide T4037 p.34 adds
    to the adjusted cost base, and the `outlays`), and `depreciable` is the filer's 0 or
    1 answer. When it is 1, `result` is the gain not below 0, as Guide T4037 p.19 says "A loss from
    the sale of depreciable property is not considered to be a capital loss."; when it is 0,
    `result` is the signed gain. Exact.

    Its own class, not a `DispositionGainOnlyLine`: it carries the answer, and a loss counts as it
    is when the answer is 0.
    """

    output: Money
    position: int
    proceeds: Decimal
    adjusted_cost_base: Decimal
    outlays: Decimal
    farm_loss_property_taxes: Decimal
    farm_loss_interest: Decimal
    farm_loss_applied: Decimal
    depreciable: int
    gain: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The figure counted: not below 0 for depreciable property, else the signed gain."""
        return self.result


@dataclass(frozen=True)
class QffpGainLine(TraceLine):
    """The gain or loss `result` of one qualified farm or fishing property disposition, by
    `position` (from 1), for `output`.

    It follows a row of Schedule 3 Part 3 line 2, 3 or 8: column 5 "Gain or loss (column 2 minus
    columns 3 and 4)", the `proceeds` less the `adjusted_cost_base`, the restricted farm loss
    applied, `farm_loss_applied` (the Guide's line C, `farm_loss_property_taxes`, plus line D,
    `farm_loss_interest`), which Guide T4037 p.34 adds to the adjusted cost base, and the
    `outlays`. A loss is a negative `result`. Exact.

    Its own class, not a `DispositionGainLine`: it carries the restricted farm loss applied.
    """

    output: Money
    position: int
    proceeds: Decimal
    adjusted_cost_base: Decimal
    outlays: Decimal
    farm_loss_property_taxes: Decimal
    farm_loss_interest: Decimal
    farm_loss_applied: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The row's gain or loss, signed."""
        return self.result


@dataclass(frozen=True)
class FarmLossAppliedLine(TraceLine):
    """The restricted farm loss `result` applied on one farmland disposition, by `position` (from
    1), for `output`.

    It follows Guide T4037 p.34 lines C and D: line C, `property_taxes`, the property taxes of the
    restricted farm loss, and line D, `interest`, the interest, both added to the adjusted cost
    base of the farmland ("Reduce your capital gain by adding these amounts to the adjusted cost
    base (ACB) of your farmland."), and "Also, you have to reduce your RFL balance by these
    amounts." The `result` is their sum. Exact.
    """

    output: Money
    position: int
    property_taxes: Decimal
    interest: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The amount applied on the row."""
        return self.result


@dataclass(frozen=True)
class PersonalUsePropertyGainLine(TraceLine):
    """The figure `result` counted for one personal-use property, by `position` (from 1), for
    `output`.

    It follows a row of Schedule 3 Part 3 under Guide T4037 p.24: each `proceeds` and
    `adjusted_cost_base` is raised to the `minimum` ("whichever is more: selling price or $1,000"
    and "whichever is more: cost or $1,000"), giving the `proceeds_used` and `cost_base_used`. The
    `gain` is the proceeds used less the cost base used and the `outlays`, and `result` is that gain
    not below 0, a loss counting 0. Exact.

    Its own class, not a `DispositionGainOnlyLine`: it also carries the minimum and the floored
    proceeds and cost base.
    """

    output: Money
    position: int
    proceeds: Decimal
    adjusted_cost_base: Decimal
    outlays: Decimal
    minimum: Decimal
    proceeds_used: Decimal
    cost_base_used: Decimal
    gain: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The figure counted, never negative."""
        return self.result


@dataclass(frozen=True)
class DispositionProceedsLine(TraceLine):
    """The `proceeds` of one disposition, by `position` (from 1), for `output`.

    It follows a row of Schedule 3 Part 3 whose line is "Total proceeds of disposition": column 2
    "Proceeds of disposition", the figure the row adds. Exact.

    Its own class, not a `DispositionGainLine`: it carries only the proceeds.
    """

    output: Money
    position: int
    proceeds: Decimal

    @property
    def amount(self) -> Decimal:
        """The row's proceeds of disposition."""
        return self.proceeds


@dataclass(frozen=True)
class NetCapitalLossesRowLine(TraceLine):
    """One year row of Form T657 Chart 1, "Calculate your net capital losses of other years (line 14
    of Step 2)", by `position` (from 1), for `output`: the columns A to D the filer enters, column E
    (C minus D, not below 0), column F (B plus E) and column G (A minus F, not below 0), which is
    the amount added to line 14 of Step 2 for the row."""

    output: Money
    position: int
    column_a: Decimal
    column_b: Decimal
    column_c: Decimal
    column_d: Decimal
    column_e: Decimal
    column_f: Decimal
    column_g: Decimal

    @property
    def amount(self) -> Decimal:
        """Column G."""
        return self.column_g


@dataclass(frozen=True)
class ReserveRowForPeriodLine(TraceLine):
    """One disposition of a Form T2017 reserve list, by `list_position` (from 1) among the lists
    read and `position` (from 1) in its list, for `output`: its `years_after` the disposition, its
    yes or no answers `period_1` (disposed of in Period 1 of 2024) and `on_slip` (reserve reported
    on a T5013 slip or letter), `partnership_year_before_june_25` (the partnership's fiscal period
    began before June 25, 2024), its `change` (the reserve change Form T657 reads), and `counted`,
    whether the dispositions the chart takes include it.
    """

    output: Money
    list_position: int
    position: int
    years_after: int
    period_1: int
    on_slip: int
    partnership_year_before_june_25: int
    change: Decimal
    counted: bool

    @property
    def amount(self) -> Decimal:
        """The reserve change when the disposition is counted, else 0."""
        return self.change if self.counted else Decimal(0)


@dataclass(frozen=True)
class QbtBeforeQccLine(TraceLine):
    """`output` = `is_qbt_kind` (worth `is_qbt`, 1 for a QBT and 0 for a QCC), unchanged, after
    `earlier` earlier dispositions of which `earlier_qbts` are QBTs.

    It follows Form T2048, "You must claim any deduction under a QBT before any deduction under a
    QCC": a QBT after a QCC is an error, so no line is recorded for it.
    """

    output: ArtifactKind[int]
    is_qbt_kind: ArtifactKind[int]
    is_qbt: int
    earlier: int
    earlier_qbts: int

    @property
    def amount(self) -> Decimal:
        """The answer, as produced."""
        return Decimal(self.is_qbt)
