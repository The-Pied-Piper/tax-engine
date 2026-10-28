"""English text for the trace lines of `tax_calculator.jurisdictions.ca.trace.gains`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.adapters.inbound.trace_english.figures import EnglishFigures
from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.domain.artifact import Money
from tax_calculator.jurisdictions.ca.trace.gains import (
    DepreciablePropertyGainLine,
    DispositionGainLine,
    DispositionGainOnlyLine,
    DispositionProceedsLine,
    FarmLossAppliedLine,
    NetCapitalLossesRowLine,
    PersonalUsePropertyGainLine,
    PrincipalResidenceDesignationBox,
    PrincipalResidenceGainLine,
    PrincipalResidenceLine27,
    PrincipalResidenceLine29,
    PrincipalResidenceLine30,
    PrincipalResidenceLine32,
    PrincipalResidenceLine33,
    PrincipalResidenceLine38,
    PrincipalResidenceLine39,
    PrincipalResidenceLine42,
    PrincipalResidenceLine44,
    PrincipalResidenceLine45,
    PrincipalResidenceLine48,
    PrincipalResidenceLine51,
    PrincipalResidenceLine53,
    PrincipalResidenceLine56,
    PrincipalResidenceLine57,
    PrincipalResidenceWorksheetLine3,
    PrincipalResidenceWorksheetLine6,
    PrincipalResidenceWorksheetLine16,
    PrincipalResidenceWorksheetLine17,
    PrincipalResidenceWorksheetLine18,
    PrincipalResidenceWorksheetLine19,
    PrincipalResidenceWorksheetLine21,
    PrincipalResidenceWorksheetLine23,
    PrincipalResidenceWorksheetLine24,
    PrincipalResidenceWorksheetLine26,
    PrincipalResidenceWorksheetLine27,
    PrincipalResidenceWorksheetLine30,
    PrincipalResidenceWorksheetLine32,
    PrincipalResidenceWorksheetLine33,
    PrincipalResidenceWorksheetLine35,
    PrincipalResidenceWorksheetLine36,
    PrincipalResidenceWorksheetLine40,
    PrincipalResidenceWorksheetLine41,
    PrincipalResidenceWorksheetLine44,
    PrincipalResidenceWorksheetLine46,
    PrincipalResidenceWorksheetLine47,
    PrincipalResidenceWorksheetLine50,
    PrincipalResidenceWorksheetLine53,
    PrincipalResidenceWorksheetLine55,
    PrincipalResidenceWorksheetLine58,
    PrincipalResidenceWorksheetLine59,
    PrincipalResidenceWorksheetLine61,
    PrincipalResidenceWorksheetLine63,
    PrincipalResidenceWorksheetLine64,
    PrincipalResidenceWorksheetLine66,
    QbtBeforeQccLine,
    QffpGainLine,
    ReserveRowForPeriodLine,
)


def _part_2_step(
    output: Money, position: int, number: int, result: Decimal, body: str, completed: bool
) -> str:
    """The sentence of Part 2 line `number`: its figure, then `body` (the figures it takes). A step
    the form says not to complete reads as 0."""
    if not completed:
        return f"{output.label}: property {position}: line {number} not completed, 0"
    return (
        f"{output.label}: property {position}: line {number} "
        f"{EnglishFigures.money(result)} = {body}"
    )


@english_renderer
class PrincipalResidenceGainRenderer:
    """English text for PrincipalResidenceGainLine."""

    line_class = PrincipalResidenceGainLine

    def render(self, line: PrincipalResidenceGainLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        designated = line.designated
        owned = line.owned
        plus_one = line.plus_one
        proceeds = line.proceeds
        cost_base = line.adjusted_cost_base
        outlays = line.outlays
        gain = line.gain
        exempt = line.exempt
        rule = line.rounding
        result = line.result
        line_24 = line.line_24
        text = (
            f"{output.label}: property {position}: gain {EnglishFigures.money(gain)} = proceeds "
            f"{EnglishFigures.money(proceeds)} less adjusted cost base "
            f"{EnglishFigures.money(cost_base)} "
            f"less outlays {EnglishFigures.money(outlays)}; exempt {EnglishFigures.money(exempt)} "
            f"= "
            f"{EnglishFigures.money(gain)} × ({designated} designated + {plus_one}) ÷ {owned} "
            f"owned ({EnglishFigures.rounding(rule)}); taxable gain "
            f"{EnglishFigures.money(line_24)} "
            f"= "
            f"{EnglishFigures.money(gain)} less {EnglishFigures.money(exempt)}, not below 0"
        )
        if line.part_2_applies != 1:
            return text
        return (
            f"{text}; Part 2 net capital gain {EnglishFigures.money(line.line_53)}; "
            f"total capital gain {EnglishFigures.money(result)} = lesser of "
            f"{EnglishFigures.money(line.line_53)} and {EnglishFigures.money(line_24)}"
        )


@english_renderer
class PrincipalResidenceDesignationBoxRenderer:
    """English text for PrincipalResidenceDesignationBox."""

    line_class = PrincipalResidenceDesignationBox

    def render(self, line: PrincipalResidenceDesignationBox) -> str:
        """The English sentence for `line`: the box and the figures it is worked from."""
        name = line.output.label
        if line.properties == 0:
            return f"{name}: 0 = no property, so no box is ticked"
        if line.properties > 1:
            return f"{name}: 3 = box 3, {line.properties} properties (more than one property)"
        if line.box == 1:
            return (
                f"{name}: 1 = box 1, one property designated for {line.designated} of its "
                f"{line.owned} years owned (all, or all but one)"
            )
        return (
            f"{name}: 2 = box 2, one property designated for {line.designated} of its "
            f"{line.owned} years owned (some but not all)"
        )


@english_renderer
class PrincipalResidenceLine27Renderer:
    """English text for PrincipalResidenceLine27."""

    line_class = PrincipalResidenceLine27

    def render(self, line: PrincipalResidenceLine27) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            27,
            line.result,
            f"line 12 {EnglishFigures.money(line.line_12)} less line 11 "
            f"{EnglishFigures.money(line.line_11)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine29Renderer:
    """English text for PrincipalResidenceLine29."""

    line_class = PrincipalResidenceLine29

    def render(self, line: PrincipalResidenceLine29) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            29,
            line.result,
            f"line 2 {line.line_2} plus {line.plus_one}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine30Renderer:
    """English text for PrincipalResidenceLine30."""

    line_class = PrincipalResidenceLine30

    def render(self, line: PrincipalResidenceLine30) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            30,
            line.result,
            f"line 27 {EnglishFigures.money(line.line_27)} times line 29 {int(line.line_29)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine32Renderer:
    """English text for PrincipalResidenceLine32."""

    line_class = PrincipalResidenceLine32

    def render(self, line: PrincipalResidenceLine32) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            32,
            line.result,
            f"line 30 {EnglishFigures.money(line.line_30)} divided by line 6 {line.line_6} "
            f"({EnglishFigures.rounding(line.rounding)})",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine33Renderer:
    """English text for PrincipalResidenceLine33."""

    line_class = PrincipalResidenceLine33

    def render(self, line: PrincipalResidenceLine33) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            33,
            line.result,
            f"line 27 {EnglishFigures.money(line.line_27)} less line 32 "
            f"{EnglishFigures.money(line.line_32)}, not below 0",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine38Renderer:
    """English text for PrincipalResidenceLine38."""

    line_class = PrincipalResidenceLine38

    def render(self, line: PrincipalResidenceLine38) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            38,
            line.result,
            f"line 12 {EnglishFigures.money(line.line_12)} plus line 13 "
            f"{EnglishFigures.money(line.line_13)} plus line 9 {EnglishFigures.money(line.line_9)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine39Renderer:
    """English text for PrincipalResidenceLine39."""

    line_class = PrincipalResidenceLine39

    def render(self, line: PrincipalResidenceLine39) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            39,
            line.result,
            f"line 8 {EnglishFigures.money(line.line_8)} less line 38 "
            f"{EnglishFigures.money(line.line_38)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine42Renderer:
    """English text for PrincipalResidenceLine42."""

    line_class = PrincipalResidenceLine42

    def render(self, line: PrincipalResidenceLine42) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            42,
            line.result,
            f"line 39 {EnglishFigures.money(line.line_39)} times line 1 {line.line_1}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine44Renderer:
    """English text for PrincipalResidenceLine44."""

    line_class = PrincipalResidenceLine44

    def render(self, line: PrincipalResidenceLine44) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            44,
            line.result,
            f"line 42 {EnglishFigures.money(line.line_42)} divided by line 5 {line.line_5} "
            f"({EnglishFigures.rounding(line.rounding)})",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine45Renderer:
    """English text for PrincipalResidenceLine45."""

    line_class = PrincipalResidenceLine45

    def render(self, line: PrincipalResidenceLine45) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            45,
            line.result,
            f"line 39 {EnglishFigures.money(line.line_39)} less line 44 "
            f"{EnglishFigures.money(line.line_44)}, not below 0",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine48Renderer:
    """English text for PrincipalResidenceLine48."""

    line_class = PrincipalResidenceLine48

    def render(self, line: PrincipalResidenceLine48) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            48,
            line.result,
            f"line 12 {EnglishFigures.money(line.line_12)} less line 8 "
            f"{EnglishFigures.money(line.line_8)}, not below 0",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine51Renderer:
    """English text for PrincipalResidenceLine51."""

    line_class = PrincipalResidenceLine51

    def render(self, line: PrincipalResidenceLine51) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            51,
            line.result,
            f"line 33 {EnglishFigures.money(line.line_33)} plus line 45 "
            f"{EnglishFigures.money(line.line_45)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine53Renderer:
    """English text for PrincipalResidenceLine53."""

    line_class = PrincipalResidenceLine53

    def render(self, line: PrincipalResidenceLine53) -> str:
        """The English sentence for `line`."""
        return _part_2_step(
            line.output,
            line.position,
            53,
            line.result,
            f"line 51 {EnglishFigures.money(line.line_51)} less line 48 "
            f"{EnglishFigures.money(line.line_48)}, not below 0",
            line.completed,
        )


def _worksheet_step(
    output: Money, position: int, label: str, result: Decimal, body: str, completed: bool
) -> str:
    """The sentence of one step of Form T2091(IND)-WS (`label`, "worksheet line N") or of Part 4
    (`label`, "line N"): its figure, then `body` (the figures it takes). A step the form says not
    to complete reads as 0."""
    if not completed:
        return f"{output.label}: property {position}: {label} not completed, 0"
    return f"{output.label}: property {position}: {label} {EnglishFigures.money(result)} = {body}"


@english_renderer
class PrincipalResidenceWorksheetLine3Renderer:
    """English text for PrincipalResidenceWorksheetLine3."""

    line_class = PrincipalResidenceWorksheetLine3

    def render(self, line: PrincipalResidenceWorksheetLine3) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 3",
            line.result,
            f"worksheet line 1 {line.line_1} plus T2091 line 2 {line.line_2}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine6Renderer:
    """English text for PrincipalResidenceWorksheetLine6."""

    line_class = PrincipalResidenceWorksheetLine6

    def render(self, line: PrincipalResidenceWorksheetLine6) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 6",
            line.result,
            f"worksheet line 4 {line.line_4} plus T2091 line 6 {line.line_5}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine16Renderer:
    """English text for PrincipalResidenceWorksheetLine16."""

    line_class = PrincipalResidenceWorksheetLine16

    def render(self, line: PrincipalResidenceWorksheetLine16) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 16",
            line.result,
            f"worksheet line 14 {EnglishFigures.money(line.line_14)} times "
            f"{EnglishFigures.money(line.factor)} ({EnglishFigures.rounding(line.rounding)})",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine17Renderer:
    """English text for PrincipalResidenceWorksheetLine17."""

    line_class = PrincipalResidenceWorksheetLine17

    def render(self, line: PrincipalResidenceWorksheetLine17) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 17",
            line.result,
            f"worksheet line 15 {EnglishFigures.money(line.line_15)} less worksheet line 16 "
            f"{EnglishFigures.money(line.line_16)}, not below 0",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine18Renderer:
    """English text for PrincipalResidenceWorksheetLine18."""

    line_class = PrincipalResidenceWorksheetLine18

    def render(self, line: PrincipalResidenceWorksheetLine18) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 18",
            line.result,
            f"worksheet line 14 {EnglishFigures.money(line.line_14)} less worksheet line 17 "
            f"{EnglishFigures.money(line.line_17)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine19Renderer:
    """English text for PrincipalResidenceWorksheetLine19."""

    line_class = PrincipalResidenceWorksheetLine19

    def render(self, line: PrincipalResidenceWorksheetLine19) -> str:
        """The English sentence for `line`."""
        if line.chart_completed:
            body = f"worksheet line 18 {EnglishFigures.money(line.line_18)} (Chart 1 completed)"
        else:
            body = f"worksheet line 10 {EnglishFigures.money(line.line_10)} (Chart 1 not completed)"
        return _worksheet_step(
            line.output, line.position, "worksheet line 19", line.result, body, line.completed
        )


@english_renderer
class PrincipalResidenceWorksheetLine21Renderer:
    """English text for PrincipalResidenceWorksheetLine21."""

    line_class = PrincipalResidenceWorksheetLine21

    def render(self, line: PrincipalResidenceWorksheetLine21) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 21",
            line.result,
            f"worksheet line 19 {EnglishFigures.money(line.line_19)} less worksheet line 20 "
            f"{EnglishFigures.money(line.line_20)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine23Renderer:
    """English text for PrincipalResidenceWorksheetLine23."""

    line_class = PrincipalResidenceWorksheetLine23

    def render(self, line: PrincipalResidenceWorksheetLine23) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 23",
            line.result,
            f"worksheet line 3 {line.line_3} plus {line.plus_one}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine24Renderer:
    """English text for PrincipalResidenceWorksheetLine24."""

    line_class = PrincipalResidenceWorksheetLine24

    def render(self, line: PrincipalResidenceWorksheetLine24) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 24",
            line.result,
            f"worksheet line 22 {EnglishFigures.money(line.line_22)} times worksheet line 23 "
            f"{line.line_23}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine26Renderer:
    """English text for PrincipalResidenceWorksheetLine26."""

    line_class = PrincipalResidenceWorksheetLine26

    def render(self, line: PrincipalResidenceWorksheetLine26) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 26",
            line.result,
            f"worksheet line 24 {EnglishFigures.money(line.line_24)} divided by worksheet "
            f"line 25 {line.line_25} ({EnglishFigures.rounding(line.rounding)})",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine27Renderer:
    """English text for PrincipalResidenceWorksheetLine27."""

    line_class = PrincipalResidenceWorksheetLine27

    def render(self, line: PrincipalResidenceWorksheetLine27) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 27",
            line.result,
            f"worksheet line 21 {EnglishFigures.money(line.line_21)} less worksheet line 26 "
            f"{EnglishFigures.money(line.line_26)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine30Renderer:
    """English text for PrincipalResidenceWorksheetLine30."""

    line_class = PrincipalResidenceWorksheetLine30

    def render(self, line: PrincipalResidenceWorksheetLine30) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 30",
            line.result,
            f"worksheet line 28 {EnglishFigures.money(line.line_28)} less worksheet line 29 "
            f"{EnglishFigures.money(line.line_29)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine32Renderer:
    """English text for PrincipalResidenceWorksheetLine32."""

    line_class = PrincipalResidenceWorksheetLine32

    def render(self, line: PrincipalResidenceWorksheetLine32) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 32",
            line.result,
            f"worksheet line 2 {line.line_2} plus {line.plus_one}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine33Renderer:
    """English text for PrincipalResidenceWorksheetLine33."""

    line_class = PrincipalResidenceWorksheetLine33

    def render(self, line: PrincipalResidenceWorksheetLine33) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 33",
            line.result,
            f"worksheet line 31 {EnglishFigures.money(line.line_31)} times worksheet line 32 "
            f"{line.line_32}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine35Renderer:
    """English text for PrincipalResidenceWorksheetLine35."""

    line_class = PrincipalResidenceWorksheetLine35

    def render(self, line: PrincipalResidenceWorksheetLine35) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 35",
            line.result,
            f"worksheet line 33 {EnglishFigures.money(line.line_33)} divided by worksheet "
            f"line 34 {line.line_34} ({EnglishFigures.rounding(line.rounding)})",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine36Renderer:
    """English text for PrincipalResidenceWorksheetLine36."""

    line_class = PrincipalResidenceWorksheetLine36

    def render(self, line: PrincipalResidenceWorksheetLine36) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 36",
            line.result,
            f"worksheet line 30 {EnglishFigures.money(line.line_30)} less worksheet line 35 "
            f"{EnglishFigures.money(line.line_35)}, not below 0",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine40Renderer:
    """English text for PrincipalResidenceWorksheetLine40."""

    line_class = PrincipalResidenceWorksheetLine40

    def render(self, line: PrincipalResidenceWorksheetLine40) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 40",
            line.result,
            f"worksheet line 38 {EnglishFigures.money(line.line_38)} plus worksheet line 39 "
            f"{EnglishFigures.money(line.line_39)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine41Renderer:
    """English text for PrincipalResidenceWorksheetLine41."""

    line_class = PrincipalResidenceWorksheetLine41

    def render(self, line: PrincipalResidenceWorksheetLine41) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 41",
            line.result,
            f"worksheet line 37 {EnglishFigures.money(line.line_37)} less worksheet line 40 "
            f"{EnglishFigures.money(line.line_40)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine44Renderer:
    """English text for PrincipalResidenceWorksheetLine44."""

    line_class = PrincipalResidenceWorksheetLine44

    def render(self, line: PrincipalResidenceWorksheetLine44) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 44",
            line.result,
            f"worksheet line 42 {EnglishFigures.money(line.line_42)} times worksheet line 43 "
            f"{line.line_43}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine46Renderer:
    """English text for PrincipalResidenceWorksheetLine46."""

    line_class = PrincipalResidenceWorksheetLine46

    def render(self, line: PrincipalResidenceWorksheetLine46) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 46",
            line.result,
            f"worksheet line 44 {EnglishFigures.money(line.line_44)} divided by worksheet "
            f"line 45 {line.line_45} ({EnglishFigures.rounding(line.rounding)})",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine47Renderer:
    """English text for PrincipalResidenceWorksheetLine47."""

    line_class = PrincipalResidenceWorksheetLine47

    def render(self, line: PrincipalResidenceWorksheetLine47) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 47",
            line.result,
            f"worksheet line 41 {EnglishFigures.money(line.line_41)} less worksheet line 46 "
            f"{EnglishFigures.money(line.line_46)}, not below 0",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine50Renderer:
    """English text for PrincipalResidenceWorksheetLine50."""

    line_class = PrincipalResidenceWorksheetLine50

    def render(self, line: PrincipalResidenceWorksheetLine50) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 50",
            line.result,
            f"worksheet line 48 {EnglishFigures.money(line.line_48)} less worksheet line 49 "
            f"{EnglishFigures.money(line.line_49)}, not below 0",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine53Renderer:
    """English text for PrincipalResidenceWorksheetLine53."""

    line_class = PrincipalResidenceWorksheetLine53

    def render(self, line: PrincipalResidenceWorksheetLine53) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 53",
            line.result,
            f"worksheet line 51 {EnglishFigures.money(line.line_51)} plus worksheet line 52 "
            f"{EnglishFigures.money(line.line_52)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine55Renderer:
    """English text for PrincipalResidenceWorksheetLine55."""

    line_class = PrincipalResidenceWorksheetLine55

    def render(self, line: PrincipalResidenceWorksheetLine55) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 55",
            line.result,
            f"worksheet line 53 {EnglishFigures.money(line.line_53)} less worksheet line 54 "
            f"{EnglishFigures.money(line.line_54)}, not below 0",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine58Renderer:
    """English text for PrincipalResidenceWorksheetLine58."""

    line_class = PrincipalResidenceWorksheetLine58

    def render(self, line: PrincipalResidenceWorksheetLine58) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 58",
            line.result,
            f"lesser of worksheet line 56 {EnglishFigures.money(line.line_56)} and worksheet "
            f"line 57 {EnglishFigures.money(line.line_57)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine59Renderer:
    """English text for PrincipalResidenceWorksheetLine59."""

    line_class = PrincipalResidenceWorksheetLine59

    def render(self, line: PrincipalResidenceWorksheetLine59) -> str:
        """The English sentence for `line`."""
        if line.part_2_completed:
            body = f"worksheet line 58 {EnglishFigures.money(line.line_58)} (Part 2 completed)"
        else:
            body = f"worksheet line 27 {EnglishFigures.money(line.line_27)}"
        return _worksheet_step(
            line.output, line.position, "worksheet line 59", line.result, body, line.completed
        )


@english_renderer
class PrincipalResidenceWorksheetLine61Renderer:
    """English text for PrincipalResidenceWorksheetLine61."""

    line_class = PrincipalResidenceWorksheetLine61

    def render(self, line: PrincipalResidenceWorksheetLine61) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 61",
            line.result,
            f"worksheet line 59 {EnglishFigures.money(line.line_59)} times worksheet line 60 "
            f"{line.line_60}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine63Renderer:
    """English text for PrincipalResidenceWorksheetLine63."""

    line_class = PrincipalResidenceWorksheetLine63

    def render(self, line: PrincipalResidenceWorksheetLine63) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 63",
            line.result,
            f"worksheet line 61 {EnglishFigures.money(line.line_61)} divided by worksheet "
            f"line 62 {line.line_62} ({EnglishFigures.rounding(line.rounding)})",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine64Renderer:
    """English text for PrincipalResidenceWorksheetLine64."""

    line_class = PrincipalResidenceWorksheetLine64

    def render(self, line: PrincipalResidenceWorksheetLine64) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 64",
            line.result,
            f"worksheet line 59 {EnglishFigures.money(line.line_59)} less worksheet line 63 "
            f"{EnglishFigures.money(line.line_63)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceWorksheetLine66Renderer:
    """English text for PrincipalResidenceWorksheetLine66."""

    line_class = PrincipalResidenceWorksheetLine66

    def render(self, line: PrincipalResidenceWorksheetLine66) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "worksheet line 66",
            line.result,
            f"lesser of worksheet line 64 {EnglishFigures.money(line.line_64)} and worksheet "
            f"line 65 {EnglishFigures.money(line.line_65)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine56Renderer:
    """English text for PrincipalResidenceLine56."""

    line_class = PrincipalResidenceLine56

    def render(self, line: PrincipalResidenceLine56) -> str:
        """The English sentence for `line`."""
        return _worksheet_step(
            line.output,
            line.position,
            "line 56",
            line.result,
            f"worksheet line 66 {EnglishFigures.money(line.line_66)}",
            line.completed,
        )


@english_renderer
class PrincipalResidenceLine57Renderer:
    """English text for PrincipalResidenceLine57."""

    line_class = PrincipalResidenceLine57

    def render(self, line: PrincipalResidenceLine57) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: property {line.position}: line 57 "
            f"{EnglishFigures.money(line.result)} = line 55 {EnglishFigures.money(line.line_55)} "
            f"less line 56 {EnglishFigures.money(line.line_56)}, not below 0"
        )


@english_renderer
class DispositionGainRenderer:
    """English text for DispositionGainLine."""

    line_class = DispositionGainLine

    def render(self, line: DispositionGainLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        proceeds = line.proceeds
        cost_base = line.adjusted_cost_base
        outlays = line.outlays
        result = line.result
        return (
            f"{output.label}: disposition {position}: gain or loss {EnglishFigures.money(result)} "
            f"= proceeds {EnglishFigures.money(proceeds)} less adjusted cost base "
            f"{EnglishFigures.money(cost_base)} less outlays {EnglishFigures.money(outlays)}"
        )


@english_renderer
class DispositionGainOnlyRenderer:
    """English text for DispositionGainOnlyLine."""

    line_class = DispositionGainOnlyLine

    def render(self, line: DispositionGainOnlyLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        proceeds = line.proceeds
        cost_base = line.adjusted_cost_base
        outlays = line.outlays
        gain = line.gain
        result = line.result
        return (
            f"{output.label}: disposition {position}: gain {EnglishFigures.money(gain)} = "
            f"proceeds {EnglishFigures.money(proceeds)} less adjusted cost base "
            f"{EnglishFigures.money(cost_base)} less outlays {EnglishFigures.money(outlays)}; gain "
            f"only "
            f"{EnglishFigures.money(result)}, not below 0"
        )


@english_renderer
class DepreciablePropertyGainRenderer:
    """English text for DepreciablePropertyGainLine."""

    line_class = DepreciablePropertyGainLine

    def render(self, line: DepreciablePropertyGainLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        proceeds = line.proceeds
        cost_base = line.adjusted_cost_base
        outlays = line.outlays
        gain = line.gain
        result = line.result
        text = (
            f"{output.label}: disposition {position}: gain {EnglishFigures.money(gain)} = "
            f"proceeds {EnglishFigures.money(proceeds)} less adjusted cost base "
            f"{EnglishFigures.money(cost_base)} less outlays {EnglishFigures.money(outlays)}"
        )
        if line.farm_loss_applied:
            text += (
                f" less restricted farm loss applied {EnglishFigures.money(line.farm_loss_applied)}"
                f" (property taxes {EnglishFigures.money(line.farm_loss_property_taxes)} plus "
                f"interest {EnglishFigures.money(line.farm_loss_interest)})"
            )
        if line.depreciable:
            text += f"; depreciable property: a loss counts 0 -> {EnglishFigures.money(result)}"
        return text


@english_renderer
class QffpGainRenderer:
    """English text for QffpGainLine."""

    line_class = QffpGainLine

    def render(self, line: QffpGainLine) -> str:
        """The English sentence for `line`."""
        text = (
            f"{line.output.label}: disposition {line.position}: gain or loss "
            f"{EnglishFigures.money(line.result)} = proceeds {EnglishFigures.money(line.proceeds)} "
            f"less adjusted cost base {EnglishFigures.money(line.adjusted_cost_base)} less outlays "
            f"{EnglishFigures.money(line.outlays)}"
        )
        if line.farm_loss_applied:
            text += (
                f" less restricted farm loss applied {EnglishFigures.money(line.farm_loss_applied)}"
                f" (property taxes {EnglishFigures.money(line.farm_loss_property_taxes)} plus "
                f"interest {EnglishFigures.money(line.farm_loss_interest)})"
            )
        return text


@english_renderer
class FarmLossAppliedRenderer:
    """English text for FarmLossAppliedLine."""

    line_class = FarmLossAppliedLine

    def render(self, line: FarmLossAppliedLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: disposition {line.position}: restricted farm loss applied "
            f"{EnglishFigures.money(line.result)} = property taxes "
            f"{EnglishFigures.money(line.property_taxes)} plus interest "
            f"{EnglishFigures.money(line.interest)}"
        )


@english_renderer
class PersonalUsePropertyGainRenderer:
    """English text for PersonalUsePropertyGainLine."""

    line_class = PersonalUsePropertyGainLine

    def render(self, line: PersonalUsePropertyGainLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        proceeds = line.proceeds
        cost_base = line.adjusted_cost_base
        outlays = line.outlays
        minimum = EnglishFigures.money(line.minimum)
        proceeds_used = line.proceeds_used
        cost_base_used = line.cost_base_used
        gain = line.gain
        result = line.result
        return (
            f"{output.label}: disposition {position}: gain {EnglishFigures.money(gain)} = "
            f"proceeds {EnglishFigures.money(proceeds_used)} (greater of "
            f"{EnglishFigures.money(proceeds)} and minimum {minimum}) less adjusted cost base "
            f"{EnglishFigures.money(cost_base_used)} (greater of {EnglishFigures.money(cost_base)} "
            f"and minimum {minimum}) less outlays {EnglishFigures.money(outlays)}; gain only "
            f"{EnglishFigures.money(result)}, not below 0"
        )


@english_renderer
class DispositionProceedsRenderer:
    """English text for DispositionProceedsLine."""

    line_class = DispositionProceedsLine

    def render(self, line: DispositionProceedsLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        proceeds = line.proceeds
        return f"{output.label}: disposition {position}: proceeds {EnglishFigures.money(proceeds)}"


@english_renderer
class NetCapitalLossesRowRenderer:
    """English text for NetCapitalLossesRowLine."""

    line_class = NetCapitalLossesRowLine

    def render(self, line: NetCapitalLossesRowLine) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: item {line.position}: column E {money(line.column_e)} = "
            f"column C {money(line.column_c)} less column D {money(line.column_d)}, not below 0; "
            f"column F {money(line.column_f)} = column B {money(line.column_b)} plus column E "
            f"{money(line.column_e)}; column G {money(line.column_g)} = column A "
            f"{money(line.column_a)} less column F {money(line.column_f)}, not below 0"
        )


@english_renderer
class ReserveRowForPeriodRenderer:
    """English text for ReserveRowForPeriodLine."""

    line_class = ReserveRowForPeriodLine

    def render(self, line: ReserveRowForPeriodLine) -> str:
        """The English sentence for `line`."""
        answer = {0: "no", 1: "yes"}
        counted = "counted" if line.counted else "not counted"
        partnership = answer.get(
            line.partnership_year_before_june_25, line.partnership_year_before_june_25
        )
        return (
            f"{line.output.label}: list {line.list_position} item {line.position}: "
            f"{line.years_after} years after the disposition, disposed of in Period 1 of 2024 "
            f"{answer.get(line.period_1, line.period_1)}, reported on a T5013 slip or letter "
            f"{answer.get(line.on_slip, line.on_slip)}, partnership year began before June 25, "
            f"2024 {partnership}: {EnglishFigures.money(line.change)} {counted}"
        )


@english_renderer
class QbtBeforeQccRenderer:
    """English text for QbtBeforeQccLine."""

    line_class = QbtBeforeQccLine

    def render(self, line: QbtBeforeQccLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.is_qbt_kind.label} {line.is_qbt}, "
            f"after {line.earlier} earlier dispositions, {line.earlier_qbts} of them QBTs"
        )
