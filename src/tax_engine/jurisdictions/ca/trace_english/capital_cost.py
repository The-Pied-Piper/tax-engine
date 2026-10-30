"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.capital_cost`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction as ExactFraction

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.domain.parameters.class_rates import RecaptureAndTerminalLoss
from tax_engine.jurisdictions.ca.trace.capital_cost import (
    CcaChangeInUseCheckLine,
    CcaClaimLine,
    CcaPartACheckLine,
    CcaPartBCheckLine,
    CcaVehicleAdditionsCheckLine,
    CcaVehicleChangeInUseCheckLine,
    CcaVehicleClassCheckLine,
    CcaVehicleNonArmsLengthCheckLine,
    CcaVehicleProceedsLine,
    CcaZepvProceedsLine,
    CcaZeroReason,
    ClosingUccLine,
    FiscalPeriodDaysFromDatesLine,
    FiscalPeriodDaysLine,
    ImmediateExpensingAgreedLimitLine,
    ImmediateExpensingLine,
    ProratedByDaysInPeriodLine,
    ProratedByDaysLine,
    RecapturedCcaLine,
    TerminalLossLine,
)


@english_renderer
class CcaClaimRenderer:
    """English text for CcaClaimLine."""

    line_class = CcaClaimLine

    def render(self, line: CcaClaimLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        class_rate = line.class_rate
        column_7 = line.column_7
        column_14 = line.column_14
        column_15 = line.column_15
        column_16 = line.column_16
        column_17 = line.column_17
        column_18 = line.column_18
        column_19 = line.column_19
        zero_reason = line.zero_reason
        maximum = line.maximum
        rule = line.rounding
        claim = line.claim
        column_9 = line.column_9
        on_sale = " (half-year rule on sale)" if line.half_year_rule_on_sale else ""
        columns = ", ".join(
            f"column {number} {EnglishFigures.money(amount)}{note}"
            for number, amount, note in (
                (7, column_7, ""),
                *(((9, column_9, ""),) if column_9 > 0 else ()),
                (14, column_14, ""),
                (15, column_15, ""),
                (16, column_16, ""),
                (17, column_17, ""),
                (18, column_18, ""),
                (19, column_19, on_sale),
            )
        )
        if zero_reason is CcaZeroReason.COLUMN_7_NEGATIVE and not line.half_year_rule_on_sale:
            available = "maximum 0 as column 7 is negative"
        elif zero_reason is CcaZeroReason.NO_PROPERTY_LEFT:
            available = "maximum 0 as no property is left in the class"
        else:
            percent = EnglishFigures.percent(class_rate.rate.value)
            rate_of_column_19 = column_19 * class_rate.rate.value
            days = line.fiscal_period_days
            full_year = line.full_year_days
            reached = maximum
            if days != full_year:
                # The rate of column 19 as worked, before the proration.
                reached = rule.apply(rate_of_column_19)
            available = (
                f"maximum {percent}% of column 19 = {EnglishFigures.money(reached)} "
                f"({EnglishFigures.rounding(rule)})"
            )
            if days != full_year:
                reached = rule.apply(ExactFraction(rate_of_column_19) * days / full_year)
                available += f", prorated {days}/{full_year} = {EnglishFigures.money(reached)}"
        return (
            f"{EnglishFigures.cca_class(output.label, position, class_rate)}: {columns}, "
            f"{available}, claim {EnglishFigures.money(claim)}"
        )


@english_renderer
class RecapturedCcaRenderer:
    """English text for RecapturedCcaLine."""

    line_class = RecapturedCcaLine

    def render(self, line: RecapturedCcaLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        class_rate = line.class_rate
        column_7 = line.column_7
        zero_reason = line.zero_reason
        result = line.result
        if zero_reason is not CcaZeroReason.COLUMN_7_NEGATIVE:
            found = f"column 7 {EnglishFigures.money(column_7)} is not negative"
        elif (
            class_rate.recapture_and_terminal_loss is RecaptureAndTerminalLoss.EXCLUDED
            and not line.has_diep
        ):
            found = (
                f"column 7 {EnglishFigures.money(column_7)} is negative, but recapture does not "
                f"apply to class {EnglishFigures.money(class_rate.class_number)}"
            )
        else:
            found = f"column 7 {EnglishFigures.money(column_7)} is negative"
        return (
            f"{EnglishFigures.cca_class(output.label, position, class_rate)}: {found}: "
            f"recapture {EnglishFigures.money(result)}"
        )


@english_renderer
class TerminalLossRenderer:
    """English text for TerminalLossLine."""

    line_class = TerminalLossLine

    def render(self, line: TerminalLossLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        class_rate = line.class_rate
        column_7 = line.column_7
        zero_reason = line.zero_reason
        column_7_positive = line.column_7_positive
        column_9 = line.column_9
        result = line.result
        if line.half_year_rule_on_sale:
            found = (
                f"column 7 {EnglishFigures.money(column_7)} with no property left, but a terminal "
                f"loss does not apply to class {EnglishFigures.money(class_rate.class_number)} "
                f"(half-year rule on sale used)"
            )
        elif zero_reason is CcaZeroReason.NO_PROPERTY_LEFT:
            expensed = f" less column 9 {EnglishFigures.money(column_9)}" if column_9 > 0 else ""
            if (
                class_rate.recapture_and_terminal_loss is RecaptureAndTerminalLoss.EXCLUDED
                and not line.has_diep
            ):
                found = (
                    f"column 7 {EnglishFigures.money(column_7)}{expensed} with no property left, "
                    f"but a terminal loss does not apply to class "
                    f"{EnglishFigures.money(class_rate.class_number)}"
                )
            else:
                found = f"column 7 {EnglishFigures.money(column_7)}{expensed} with no property left"
        elif zero_reason is CcaZeroReason.NONE and column_7_positive:
            found = f"column 7 {EnglishFigures.money(column_7)} with property left"
        else:
            found = f"column 7 {EnglishFigures.money(column_7)} is not positive"
        return (
            f"{EnglishFigures.cca_class(output.label, position, class_rate)}: {found}: "
            f"terminal loss {EnglishFigures.money(result)}"
        )


@english_renderer
class CcaPartACheckRenderer:
    """English text for CcaPartACheckLine."""

    line_class = CcaPartACheckLine

    def render(self, line: CcaPartACheckLine) -> str:
        """The English sentence for `line`."""
        return f"{line.output.label}: item {line.position}: class {line.class_number}: checked"


@english_renderer
class CcaChangeInUseCheckRenderer:
    """English text for CcaChangeInUseCheckLine."""

    line_class = CcaChangeInUseCheckLine

    def render(self, line: CcaChangeInUseCheckLine) -> str:
        """The English sentence for `line`."""
        start = f"{line.output_kind.label}: item {line.position}"
        if not line.applied:
            return f"{start}: not checked, no change in use with additions"
        return (
            f"{start}: change in use, additions {EnglishFigures.money(line.additions)} are the "
            f"fair market value {EnglishFigures.money(line.fair_market_value)}: checked"
        )


@english_renderer
class CcaPartBCheckRenderer:
    """English text for CcaPartBCheckLine."""

    line_class = CcaPartBCheckLine

    def render(self, line: CcaPartBCheckLine) -> str:
        """The English sentence for `line`."""
        sold = "sold in the year" if line.sold_in_year else "not sold in the year"
        return (
            f"{line.output.label}: item {line.position}: UCC at start "
            f"{EnglishFigures.money(line.ucc_at_start)}, additions "
            f"{EnglishFigures.money(line.additions)}, proceeds "
            f"{EnglishFigures.money(line.proceeds)}, {sold}: checked"
        )


@english_renderer
class CcaVehicleAdditionsCheckRenderer:
    """English text for CcaVehicleAdditionsCheckLine."""

    line_class = CcaVehicleAdditionsCheckLine

    def render(self, line: CcaVehicleAdditionsCheckLine) -> str:
        """The English sentence for `line`."""
        additions = EnglishFigures.money(line.additions)
        start = f"{line.output_kind.label}: item {line.position}: additions {additions}"
        if not line.applied:
            return f"{start}: not checked, no Class 10.1 limit applies"
        return f"{start}, limit with tax {EnglishFigures.money(line.limit)}: checked"


@english_renderer
class CcaVehicleClassCheckRenderer:
    """English text for CcaVehicleClassCheckLine."""

    line_class = CcaVehicleClassCheckLine

    def render(self, line: CcaVehicleClassCheckLine) -> str:
        """The English sentence for `line`."""
        start = f"{line.output_kind.label}: item {line.position}"
        if not line.applied:
            return f"{start}: not checked, not a Class 10.1 vehicle"
        return (
            f"{start}: acquired in {line.year}, cost {EnglishFigures.money(line.cost)}, "
            f"more than {EnglishFigures.money(line.minimum)}: Class 10.1"
        )


@english_renderer
class CcaVehicleNonArmsLengthCheckRenderer:
    """English text for CcaVehicleNonArmsLengthCheckLine."""

    line_class = CcaVehicleNonArmsLengthCheckLine

    def render(self, line: CcaVehicleNonArmsLengthCheckLine) -> str:
        """The English sentence for `line`."""
        start = f"{line.output_kind.label}: item {line.position}"
        if not line.applied:
            return (
                f"{start}: not checked, not a Class 10.1 vehicle bought from a non-arm's-length "
                f"person"
            )
        return (
            f"{start}: bought from a non-arm's-length person, fair market value "
            f"{EnglishFigures.money(line.fair_market_value)}, limit with tax "
            f"{EnglishFigures.money(line.limit)}, seller's cost "
            f"{EnglishFigures.money(line.seller_cost)}, additions "
            f"{EnglishFigures.money(line.additions)} are the least of the three: checked"
        )


@english_renderer
class CcaVehicleChangeInUseCheckRenderer:
    """English text for CcaVehicleChangeInUseCheckLine."""

    line_class = CcaVehicleChangeInUseCheckLine

    def render(self, line: CcaVehicleChangeInUseCheckLine) -> str:
        """The English sentence for `line`."""
        start = f"{line.output_kind.label}: item {line.position}"
        if not line.applied:
            return f"{start}: not checked, not a Class 10.1 vehicle with a change in use"
        return (
            f"{start}: change in use, additions {EnglishFigures.money(line.additions)} are the "
            f"fair market value {EnglishFigures.money(line.fair_market_value)}: checked"
        )


@english_renderer
class CcaVehicleProceedsRenderer:
    """English text for CcaVehicleProceedsLine."""

    line_class = CcaVehicleProceedsLine

    def render(self, line: CcaVehicleProceedsLine) -> str:
        """The English sentence for `line`."""
        start = f"{line.output.label}: item {line.position}: "
        proceeds = (
            f"proceeds {EnglishFigures.money(line.proceeds)} and DIEP proceeds "
            f"{EnglishFigures.money(line.diep_proceeds)}"
        )
        if not line.applied:
            return f"{start}{proceeds} not adjusted"
        return (
            f"{start}{proceeds} adjusted by prescribed amount "
            f"{EnglishFigures.money(line.prescribed_amount)} / actual cost "
            f"{EnglishFigures.money(line.actual_cost)} = proceeds "
            f"{EnglishFigures.money(line.adjusted_proceeds)} and DIEP proceeds "
            f"{EnglishFigures.money(line.adjusted_diep_proceeds)}"
        )


@english_renderer
class CcaZepvProceedsRenderer:
    """English text for CcaZepvProceedsLine."""

    line_class = CcaZepvProceedsLine

    def render(self, line: CcaZepvProceedsLine) -> str:
        """The English sentence for `line`."""
        start = f"{line.output.label}: item {line.position} vehicle {line.vehicle}: "
        proceeds = (
            f"proceeds {EnglishFigures.money(line.proceeds)} and DIEP proceeds "
            f"{EnglishFigures.money(line.diep_proceeds)}"
        )
        if not line.applied:
            return f"{start}{proceeds} not adjusted"
        return (
            f"{start}{proceeds} adjusted by prescribed amount "
            f"{EnglishFigures.money(line.prescribed_amount)} / actual cost "
            f"{EnglishFigures.money(line.actual_cost)} = proceeds "
            f"{EnglishFigures.money(line.adjusted_proceeds)} and DIEP proceeds "
            f"{EnglishFigures.money(line.adjusted_diep_proceeds)}"
        )


@english_renderer
class ClosingUccRenderer:
    """English text for ClosingUccLine."""

    line_class = ClosingUccLine

    def render(self, line: ClosingUccLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        class_rate = line.class_rate
        column_7 = line.column_7
        zero_reason = line.zero_reason
        claim = line.claim
        result = line.result
        column_9 = line.column_9
        on_sale = " (half-year rule on sale)" if line.half_year_rule_on_sale else ""
        if line.half_year_rule_on_sale:
            found = (
                f"column 7 {EnglishFigures.money(column_7)} less claim "
                f"{EnglishFigures.money(claim)}{on_sale}, the rest is not deductible later:"
            )
        elif zero_reason is CcaZeroReason.COLUMN_7_NEGATIVE:
            found = f"column 7 {EnglishFigures.money(column_7)} is negative:"
        elif zero_reason is CcaZeroReason.NO_PROPERTY_LEFT:
            found = f"column 7 {EnglishFigures.money(column_7)} with no property left:"
        else:
            including = (
                f" (including column 9 {EnglishFigures.money(column_9)})" if column_9 > 0 else ""
            )
            prorated = (
                f" (prorated {line.fiscal_period_days}/{line.full_year_days})"
                if line.fiscal_period_days != line.full_year_days
                else ""
            )
            part = (
                f" less personal part {EnglishFigures.money(line.personal_part_remaining)}"
                if line.personal_part_remaining > 0
                else ""
            )
            found = (
                f"column 7 {EnglishFigures.money(column_7)} less claim "
                f"{EnglishFigures.money(claim)}{on_sale}{prorated}{including}{part} ="
            )
        return (
            f"{EnglishFigures.cca_class(output.label, position, class_rate)}: {found} "
            f"{EnglishFigures.money(result)}"
        )


@english_renderer
class ImmediateExpensingRenderer:
    """English text for ImmediateExpensingLine."""

    line_class = ImmediateExpensingLine

    def render(self, line: ImmediateExpensingLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{EnglishFigures.cca_class(line.output.label, line.position, line.class_rate)}: "
            f"column 4 {EnglishFigures.money(line.column_4)} less column 6 "
            f"{EnglishFigures.money(line.column_6)}, column 7 "
            f"{EnglishFigures.money(line.column_7)}: "
            f"column 8 {EnglishFigures.money(line.column_8)}, column 9 "
            f"{EnglishFigures.money(line.column_9)}"
        )


@english_renderer
class ImmediateExpensingAgreedLimitRenderer:
    """English text for ImmediateExpensingAgreedLimitLine."""

    line_class = ImmediateExpensingAgreedLimitLine

    def render(self, line: ImmediateExpensingAgreedLimitLine) -> str:
        """The English sentence for `line`."""
        limit = EnglishFigures.money(line.limit)
        if not line.statements:
            return (
                f"{line.output.label}: no statement claims immediate expensing: "
                f"agreed limit {limit}"
            )
        compared = ", ".join(
            f"{kind.identifier} statement {position} claims {EnglishFigures.money(claim)} under "
            f"{EnglishFigures.money(statement_limit)}"
            for kind, position, claim, statement_limit in line.statements
        )
        return f"{line.output.label}: {compared}: agreed limit {limit}"


@english_renderer
class FiscalPeriodDaysRenderer:
    """English text for FiscalPeriodDaysLine."""

    line_class = FiscalPeriodDaysLine

    def render(self, line: FiscalPeriodDaysLine) -> str:
        """The English sentence for `line`."""
        found = (
            f"a full year of {line.full_year_days} days"
            if line.entered == 0
            else f"fiscal period {line.fiscal_period_days} days"
        )
        return f"{line.output.label}: entered {line.entered}, {found}"


@english_renderer
class FiscalPeriodDaysFromDatesRenderer:
    """English text for FiscalPeriodDaysFromDatesLine."""

    line_class = FiscalPeriodDaysFromDatesLine

    def render(self, line: FiscalPeriodDaysFromDatesLine) -> str:
        """The English sentence for `line`."""
        if line.from_date == 0 and line.to_date == 0:
            return (
                f"{line.output.label}: no dates entered, a full year of {line.full_year_days} days"
            )
        return (
            f"{line.output.label}: from {line.from_date} to {line.to_date}, "
            f"fiscal period {line.fiscal_period_days} days"
        )


@english_renderer
class ProratedByDaysRenderer:
    """English text for ProratedByDaysLine."""

    line_class = ProratedByDaysLine

    def render(self, line: ProratedByDaysLine) -> str:
        """The English sentence for `line`: the proration with its reason when the days are below
        the short-year figure, else the amount with the reason it is not prorated. A prorated
        result keeps the places the rounding rule gave it (1463013.70 keeps its cents)."""
        short_year = EnglishFigures.money(line.short_year_days)
        if Decimal(line.fiscal_period_days) < line.short_year_days:
            return (
                f"{line.output.label}: {line.amount_kind.label} "
                f"{EnglishFigures.money(line.amount_value)} × {line.days_kind.label} "
                f"{line.fiscal_period_days} / {line.full_year_days} = "
                f"{format(line.result, 'f')}, as {line.days_kind.label} "
                f"{line.fiscal_period_days} is below {short_year} days"
            )
        return (
            f"{line.output.label}: {line.amount_kind.label} "
            f"{EnglishFigures.money(line.amount_value)} = "
            f"{EnglishFigures.money(line.result)}, not prorated as {line.days_kind.label} "
            f"{line.fiscal_period_days} is not below {short_year} days"
        )


@english_renderer
class ProratedByDaysInPeriodRenderer:
    """English text for ProratedByDaysInPeriodLine."""

    line_class = ProratedByDaysInPeriodLine

    def render(self, line: ProratedByDaysInPeriodLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.amount_kind.label} "
            f"{EnglishFigures.money(line.amount_value)} × {line.days_kind.label} "
            f"{line.days} / {line.period_days_kind.label} {line.period_days} = "
            f"{EnglishFigures.money(line.result)}"
        )
