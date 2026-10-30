"""Unit tests for EnglishTraceRenderer: structured trace lines as English text, made-up values.

The renderer reproduces the trace text capabilities used to compose themselves, so the move to
structured lines changes only the structure. Rates print as percentages, `(rate * 100)` normalised
in fixed-point notation; money figures print the same way, normalised in fixed-point notation, so
no figure carries trailing zeros after the decimal point or an exponent (the value is untouched;
only its text changes); rounding rules print as "no rounding" or "<mode> to <increment>".
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, cast

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.parameters.amount import Amount
from tax_engine.domain.parameters.claim_reduction import ClaimReduction
from tax_engine.domain.parameters.class_rates import (
    ClassRate,
    HalfYearRule,
    HalfYearRuleOnSale,
    RecaptureAndTerminalLoss,
)
from tax_engine.domain.parameters.contribution_tier import ContributionTier
from tax_engine.domain.parameters.credit import Credit
from tax_engine.domain.parameters.factor import Factor
from tax_engine.domain.parameters.fraction import Fraction
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rate_table import RateTableRow
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.parameters.taper import Taper
from tax_engine.domain.parameters.threshold_rate import ThresholdRate
from tax_engine.domain.record_list import RecordListKind
from tax_engine.domain.trace import (
    AmountByCountLine,
    AmountOrDividedByRateLine,
    AmountWhenMoreLine,
    AtMostLine,
    BracketColumnLine,
    CappedAmountLine,
    ChosenByCountLine,
    ChosenByRangeLine,
    ChosenBySignLine,
    ChosenRateAppliedLine,
    ClaimAtMostLine,
    ConditionLine,
    ConditionsCountLine,
    ContributionTierLine,
    CountAtLeastLine,
    CountAtMostLine,
    CountNotRefusedLine,
    CountWithoutRecordsLine,
    CreditAmountLine,
    DividedByRateLine,
    FirstRecordCountLine,
    FractionAppliedLine,
    GreaterOfLine,
    ItemLesserOfLine,
    ItemsTotalLine,
    ItemSumLine,
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
    RateByIncomeBandLine,
    RatioAppliedLine,
    RatioTruncatedLine,
    RecordCountLine,
    RecordPositiveTotalLine,
    RecordTotalLine,
    RoundedTotalLine,
    SignChosenDifferenceLine,
    SubtractedLine,
    SubtractedNotBelowZeroLine,
    SumLine,
    SumNotBelowZeroLine,
    SurchargeTierLine,
    TaperedAmountLine,
    ThresholdGateLine,
    TimesCountLine,
    TraceLine,
    YesOrNoCountLine,
)
from tax_engine.jurisdictions.ca.catalog import (
    CCA_UCC_AT_END,
    RENTAL_BUILDING_ADDITIONS_TOTAL,
    RENTAL_EQUIPMENT_ADDITIONS_TOTAL,
)
from tax_engine.jurisdictions.ca.trace import (
    ApprenticeWagesLine,
    BusinessVehicleLine,
    CaregiverClaimLine,
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
    DepreciablePropertyGainLine,
    DisabilityTransferLine,
    DispositionGainLine,
    DispositionGainOnlyLine,
    DispositionProceedsLine,
    FarmLossAppliedLine,
    FiscalPeriodDaysFromDatesLine,
    FiscalPeriodDaysLine,
    ForeignBusinessLine4,
    ForeignBusinessLine5,
    ForeignBusinessLine7,
    ForeignBusinessLine8,
    ForeignBusinessLine10,
    ForeignBusinessLine11,
    ForeignPropertyTaxLine,
    ForeignTaxCreditLine,
    ImmediateExpensingAgreedLimitLine,
    ImmediateExpensingLine,
    LoggingTaxCreditLine,
    NetCapitalLossesRowLine,
    OtherDependantMedicalLine,
    PercentageOfLine,
    PersonalUsePropertyGainLine,
    PooledForeignTaxCreditLine,
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
    ProratedByDaysInPeriodLine,
    ProratedByDaysLine,
    QffpGainLine,
    RecapturedCcaLine,
    RenovationLine3,
    RenovationLine6,
    RenovationLine7,
    RentalAdditionLine,
    ShortTermRentalNonCompliantCcaByClassLine,
    ShortTermRentalNonCompliantCcaLine,
    ShortTermRentalNonCompliantLine,
    TerminalLossLine,
    YearAmountLine,
)
from tax_engine.jurisdictions.ca_on.trace import (
    CappedRecordLine,
    CaregiverClaimLessClaimedLine,
    PlacementCreditLine,
    PooledProvincialForeignTaxCreditLine,
    ProvincialForeignTaxCreditLine,
)
from tests.jurisdictions.ca.capabilities.cca_table import CLASS_8

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FIVE_DECIMALS_DOWN = RoundTo(D("0.00001"), RoundingMode.DOWN)

TAXABLE_BASE = ArtifactKind("ex/taxable_base", Decimal)
BASIC_TAX = ArtifactKind("ex/basic_tax", Decimal)
PART_ONE = ArtifactKind("ex/part_one", Decimal)
PART_TWO = ArtifactKind("ex/part_two", Decimal)
PART_THREE = ArtifactKind("ex/part_three", Decimal)
TOTAL = ArtifactKind("ex/total", Decimal)
GROSS_AMOUNT = ArtifactKind("ex/gross_amount", Decimal)
RATED_AMOUNT = ArtifactKind("ex/rated_amount", Decimal)
RATED_AMOUNT_RATE = ArtifactKind("ex/rated_amount", Rate)
REDUCTION = ArtifactKind("ex/reduction", Decimal)
NET_AMOUNT = ArtifactKind("ex/net_amount", Decimal)
PERSONAL_AMOUNT = ArtifactKind("ex/personal_amount", Decimal)
CAPPED_AMOUNT = ArtifactKind("ex/capped_amount", Decimal)
LESSER_AMOUNT = ArtifactKind("ex/lesser_amount", Decimal)
GREATER_AMOUNT = ArtifactKind("ex/greater_amount", Decimal)
EARNINGS = ArtifactKind("ex/earnings", Decimal)
CONTRIBUTION = ArtifactKind("ex/contribution", Decimal)
TIER = ContributionTier(Rate(D("0.05")), D("3000"), D("50000"), D("2350"))
SURCHARGE = ArtifactKind("ex/surcharge", Decimal)
TAX_SO_FAR = ArtifactKind("ex/tax_so_far", Decimal)
INCOME = ArtifactKind("ex/income", Decimal)
TAPER = Taper(D("1000"), D("500"), D("20000"), D("10000"))
CHILDREN = ArtifactKind("ex/child_count", int)
CHILD_AMOUNT = ArtifactKind("ex/child_amount", Decimal)
REDUCTION_AMOUNTS = ArtifactKind("ex/reduction_amounts", Decimal)
CLAIMED_AMOUNT = ArtifactKind("ex/claimed_amount", Decimal)
CLAIM_LIMIT = ArtifactKind("ex/claim_limit", Decimal)
ALLOWED_AMOUNT = ArtifactKind("ex/allowed_amount", Decimal)
EARNED_INCOME = ArtifactKind("ex/earned_income", Decimal)
EARNED_PORTION = ArtifactKind("ex/earned_portion", Decimal)
AMOUNT_EACH = ArtifactKind("ex/amount_each", Decimal)
PERSONS = ArtifactKind("ex/person_count", int)
AMOUNT_CLAIMED = ArtifactKind("ex/amount_claimed", Decimal)
DEPENDANTS = ArtifactKind("ex/dependant_count", int)
AMOUNT_ALONE = ArtifactKind("ex/amount_alone", Decimal)
AMOUNT_WITH_FAMILY = ArtifactKind("ex/amount_with_family", Decimal)
AMOUNT_CHOSEN = ArtifactKind("ex/amount_chosen", Decimal)
TAX_PAYABLE = ArtifactKind("ex/tax_payable", Decimal)
FOREIGN_INCOME = ArtifactKind("ex/foreign_income", Decimal)
WORLD_INCOME = ArtifactKind("ex/worldwide_income", Decimal)
CREDIT_SHARE = ArtifactKind("ex/credit_share", Decimal)
ITEM_AMOUNT = ArtifactKind("ex/item_amount", Decimal)
GATED_AMOUNT = ArtifactKind("ex/gated_amount", Decimal)
GATE_AMOUNT = ArtifactKind("ex/gate_amount", Decimal)
AMOUNT_TESTED = ArtifactKind("ex/amount_tested", Decimal)
AMOUNT_IN_RANGE = ArtifactKind("ex/amount_in_range", Decimal)
FAMILY_INCOME = ArtifactKind("ex/family_income", Decimal)
BAND_RATE = ArtifactKind("ex/band_rate", Rate)
CARE_EXPENSES = ArtifactKind("ex/care_expenses", Decimal)
CARE_CREDIT = ArtifactKind("ex/care_credit", Decimal)
CAREGIVER_AMOUNT = ArtifactKind("ex/caregiver_amount", Decimal)
ADOPTION_CREDIT = ArtifactKind("ex/adoption_credit", Decimal)
DEPENDANTS_MEDICAL = ArtifactKind("ex/dependants_medical", Decimal)
LIMITED_AMOUNT = ArtifactKind("ex/limited_amount", Decimal)
DIVIDED_AMOUNT = ArtifactKind("ex/divided_amount", Decimal)
NON_COMPLIANT_EXPENSES = ArtifactKind("ex/non_compliant_expenses", Decimal)
NON_COMPLIANT_CCA = ArtifactKind("ex/non_compliant_cca", Decimal)
TRANSFERRED_AMOUNT = ArtifactKind("ex/transferred_amount", Decimal)
RESIDENCE_GAIN = ArtifactKind("ex/residence_gain", Decimal)
MONTHS = ArtifactKind("ex/month_count", int)
MONTHLY_AMOUNT = ArtifactKind("ex/monthly_amount", Decimal)


def render(line: TraceLine) -> str:
    return EnglishTraceRenderer().render(line)


# --- bracket columns ----------------------------
#
# One line for the bracket the base falls in, read like the form's column: the rate on the
# excess over the bracket's lower, plus the tax at the bracket's start.


def test_renders_the_bracket_the_base_falls_in() -> None:
    line = BracketColumnLine(D(100), D("0.20"), D(150), D("10.00"), D("40.00"))

    assert render(line) == "20% on 150 over 100 plus 10"


def test_renders_a_constant_with_its_cents() -> None:
    line = BracketColumnLine(D(105), D("0.205"), D("45.00"), D("11.03"), D("20.255"))

    assert render(line) == "20.5% on 45 over 105 plus 11.03"


def test_renders_the_first_bracket_over_zero_plus_zero() -> None:
    line = BracketColumnLine(D(0), D("0.10"), D(100), D(0), D("10.0"))

    assert render(line) == "10% on 100 over 0 plus 0"


def test_renders_the_open_top_bracket_like_any_other() -> None:
    line = BracketColumnLine(D(300), D("0.30"), D(100), D("50.00"), D("80.00"))

    assert render(line) == "30% on 100 over 300 plus 50"


@pytest.mark.parametrize(
    ("rate", "percent"),
    [
        ("0.10", "10"),
        ("0.1", "10"),
        ("0.125", "12.5"),
        ("0.0505", "5.05"),
        ("0", "0"),
        ("1", "100"),
    ],
)
def test_renders_the_rate_as_a_plain_percentage(rate: str, percent: str) -> None:
    line = BracketColumnLine(D(0), D(rate), D(100), D(0), D(0))

    assert render(line) == f"{percent}% on 100 over 0 plus 0"


# --- rounded totals ----------------------------


def test_renders_a_rounded_total() -> None:
    line = RoundedTotalLine(BASIC_TAX, TAXABLE_BASE, D(250), CENT, D("40.00"))

    assert render(line) == "basic_tax on taxable_base 250 (half-up to 0.01)"


def test_renders_a_total_without_rounding() -> None:
    line = RoundedTotalLine(BASIC_TAX, TAXABLE_BASE, D(400), NO_ROUNDING, D("80.0"))

    assert render(line) == "basic_tax on taxable_base 400 (no rounding)"


@pytest.mark.parametrize(
    ("rounding", "text"),
    [
        (NO_ROUNDING, "no rounding"),
        (CENT, "half-up to 0.01"),
        (RoundTo(D("1"), RoundingMode.FLOOR), "floor to 1"),
        (RoundTo(D("0.05"), RoundingMode.HALF_EVEN), "half-even to 0.05"),
        (RoundTo(D("0.01"), RoundingMode.DOWN), "down to 0.01"),
        (RoundTo(D("0.01"), RoundingMode.UP), "up to 0.01"),
        (RoundTo(D("0.01"), RoundingMode.CEILING), "ceiling to 0.01"),
    ],
)
def test_renders_each_rounding_rule(rounding: RoundingRule, text: str) -> None:
    line = RoundedTotalLine(BASIC_TAX, TAXABLE_BASE, D(250), rounding, D(25))

    assert render(line) == f"basic_tax on taxable_base 250 ({text})"


# --- sums ----------------------------


def test_renders_a_sum_of_three_parts() -> None:
    line = SumLine(
        TOTAL,
        ((PART_ONE, D("100.25")), (PART_TWO, D("40")), (PART_THREE, D("9.75"))),
        D("150.00"),
    )

    assert render(line) == "total: part_one 100.25 + part_two 40 + part_three 9.75 = 150"


def test_renders_the_parts_in_the_order_of_the_line() -> None:
    line = SumLine(TOTAL, ((PART_THREE, D("9.75")), (PART_ONE, D("100.25"))), D("110.00"))

    assert render(line) == "total: part_three 9.75 + part_one 100.25 = 110"


def test_renders_a_sum_of_one_part() -> None:
    line = SumLine(TOTAL, ((PART_TWO, D("40.5")),), D("40.5"))

    assert render(line) == "total: part_two 40.5 = 40.5"


def test_renders_a_sum_of_no_parts() -> None:
    assert render(SumLine(TOTAL, (), D(0))) == "total: no parts = 0"


# --- sums not below zero ----------------------------


def test_renders_a_sum_not_below_zero() -> None:
    line = SumNotBelowZeroLine(
        TOTAL, ((PART_ONE, D("100.25")), (PART_TWO, D("40")), (PART_THREE, D("9.75"))), D("150.00")
    )

    assert render(line) == (
        "total: part_one 100.25 + part_two 40 + part_three 9.75, not below 0 = 150"
    )


def test_renders_a_sum_floored_at_zero() -> None:
    line = SumNotBelowZeroLine(TOTAL, ((PART_ONE, D("10")), (PART_TWO, D("-25.5"))), D("0"))

    assert render(line) == "total: part_one 10 + part_two -25.5, not below 0 = 0"


def test_renders_a_sum_not_below_zero_to_exactly_zero() -> None:
    line = SumNotBelowZeroLine(TOTAL, ((PART_ONE, D("40.50")), (PART_TWO, D("-40.50"))), D("0"))

    assert render(line) == "total: part_one 40.5 + part_two -40.5, not below 0 = 0"


def test_renders_the_parts_of_a_sum_not_below_zero_in_the_order_of_the_line() -> None:
    line = SumNotBelowZeroLine(
        TOTAL, ((PART_THREE, D("9.75")), (PART_ONE, D("100.25"))), D("110.00")
    )

    assert render(line) == "total: part_three 9.75 + part_one 100.25, not below 0 = 110"


def test_renders_a_sum_not_below_zero_of_one_part() -> None:
    line = SumNotBelowZeroLine(TOTAL, ((PART_TWO, D("40.5")),), D("40.5"))

    assert render(line) == "total: part_two 40.5, not below 0 = 40.5"


def test_renders_a_sum_not_below_zero_of_no_parts() -> None:
    assert render(SumNotBelowZeroLine(TOTAL, (), D(0))) == "total: no parts, not below 0 = 0"


# --- rates applied ----------------------------


def test_renders_a_rate_applied_without_rounding() -> None:
    line = RateAppliedLine(
        RATED_AMOUNT, GROSS_AMOUNT, D("1000.05"), Rate(D("0.125")), NO_ROUNDING, D("125.00625")
    )

    assert render(line) == "rated_amount: 12.5% of gross_amount 1000.05 (no rounding)"


def test_renders_a_rounded_rate_applied() -> None:
    line = RateAppliedLine(
        RATED_AMOUNT, GROSS_AMOUNT, D("200.01"), Rate(D("0.5")), CENT, D("100.01")
    )

    assert render(line) == "rated_amount: 50% of gross_amount 200.01 (half-up to 0.01)"


@pytest.mark.parametrize(("rate", "percent"), [("0", "0"), ("1", "100"), ("0.0505", "5.05")])
def test_renders_the_applied_rate_as_a_plain_percentage(rate: str, percent: str) -> None:
    line = RateAppliedLine(RATED_AMOUNT, GROSS_AMOUNT, D("40"), Rate(D(rate)), NO_ROUNDING, D(0))

    assert render(line) == f"rated_amount: {percent}% of gross_amount 40 (no rounding)"


# --- figures divided by a rate ----------------------------
#
# "<output>: <dividend kind> <dividend> divided by <rate>% (<rule>) = <result>", every figure as
# given without trailing zeros, the result last.


def test_renders_a_figure_divided_by_a_rate() -> None:
    line = DividedByRateLine(
        RATED_AMOUNT, GROSS_AMOUNT, D("3795"), Rate(D("0.145")), CENT, D("26172.41")
    )

    assert render(line) == (
        "rated_amount: gross_amount 3795 divided by 14.5% (half-up to 0.01) = 26172.41"
    )


def test_renders_a_second_figure_divided_by_a_rate() -> None:
    line = DividedByRateLine(
        RATED_AMOUNT, GROSS_AMOUNT, D("2360.95"), Rate(D("0.0505")), CENT, D("46751.49")
    )

    assert render(line) == (
        "rated_amount: gross_amount 2360.95 divided by 5.05% (half-up to 0.01) = 46751.49"
    )


def test_renders_a_figure_divided_by_a_rate_without_rounding() -> None:
    line = DividedByRateLine(
        RATED_AMOUNT, GROSS_AMOUNT, D("5.05"), Rate(D("0.0505")), NO_ROUNDING, D("100")
    )

    assert render(line) == "rated_amount: gross_amount 5.05 divided by 5.05% (no rounding) = 100"


def test_renders_the_divided_figures_without_trailing_zeros_or_an_exponent() -> None:
    line = DividedByRateLine(
        RATED_AMOUNT, GROSS_AMOUNT, D("3.795E+3"), Rate(D("0.1450")), CENT, D("26172.410")
    )

    assert render(line) == (
        "rated_amount: gross_amount 3795 divided by 14.5% (half-up to 0.01) = 26172.41"
    )


# --- subtractions ----------------------------
# --- differences chosen by a sign -----------------------------------------------
#
# Not negative: "<output>: <difference kind> <difference> (<sign kind> <sign> is not negative) =
# <result>". Negative: "<output>: <sign kind> <sign> is negative, lesser of <reference kind>
# <reference> and <difference kind> <difference>, as a negative = <result>". Figures as given
# without trailing zeros.


def test_renders_the_difference_when_the_sign_amount_is_positive() -> None:
    line = SignChosenDifferenceLine(
        NET_AMOUNT, GROSS_AMOUNT, D("100"), REDUCTION, D("30"), RATED_AMOUNT, D("70"), D("70")
    )

    assert render(line) == "net_amount: rated_amount 70 (gross_amount 100 is not negative) = 70"


def test_renders_the_difference_when_the_sign_amount_is_zero() -> None:
    line = SignChosenDifferenceLine(
        NET_AMOUNT, GROSS_AMOUNT, D("0.00"), REDUCTION, D("0.00"), RATED_AMOUNT, D("0.00"), D("0")
    )

    assert render(line) == "net_amount: rated_amount 0 (gross_amount 0 is not negative) = 0"


def test_renders_the_lesser_figure_as_a_negative_when_the_sign_amount_is_negative() -> None:
    line = SignChosenDifferenceLine(
        NET_AMOUNT, GROSS_AMOUNT, D("-100"), REDUCTION, D("30"), RATED_AMOUNT, D("130"), D("-30")
    )

    assert render(line) == (
        "net_amount: gross_amount -100 is negative, lesser of reduction 30 and "
        "rated_amount 130, as a negative = -30"
    )


def test_renders_the_sign_chosen_figures_without_trailing_zeros_or_an_exponent() -> None:
    line = SignChosenDifferenceLine(
        NET_AMOUNT,
        GROSS_AMOUNT,
        D("-1.00E+2"),
        REDUCTION,
        D("30.500"),
        RATED_AMOUNT,
        D("130.50"),
        D("-30.500"),
    )

    assert render(line) == (
        "net_amount: gross_amount -100 is negative, lesser of reduction 30.5 and "
        "rated_amount 130.5, as a negative = -30.5"
    )


# --- subtractions ---------------------------------------------------------------


def test_renders_a_subtraction() -> None:
    line = SubtractedLine(NET_AMOUNT, GROSS_AMOUNT, D("100.25"), REDUCTION, D("40"), D("60.25"))

    assert render(line) == "net_amount: gross_amount 100.25 less reduction 40 = 60.25"


def test_renders_a_subtraction_with_a_negative_result() -> None:
    line = SubtractedLine(NET_AMOUNT, GROSS_AMOUNT, D("10"), REDUCTION, D("25.5"), D("-15.5"))

    assert render(line) == "net_amount: gross_amount 10 less reduction 25.5 = -15.5"


def test_renders_a_subtraction_to_zero() -> None:
    line = SubtractedLine(NET_AMOUNT, GROSS_AMOUNT, D("40.50"), REDUCTION, D("40.50"), D("0.00"))

    assert render(line) == "net_amount: gross_amount 40.5 less reduction 40.5 = 0"


# --- subtractions not below zero ----------------------------


def test_renders_a_subtraction_not_below_zero() -> None:
    line = SubtractedNotBelowZeroLine(
        NET_AMOUNT, GROSS_AMOUNT, D("100.25"), REDUCTION, D("40"), D("60.25")
    )

    assert render(line) == "net_amount: gross_amount 100.25 less reduction 40, not below 0 = 60.25"


def test_renders_a_subtraction_floored_at_zero() -> None:
    line = SubtractedNotBelowZeroLine(
        NET_AMOUNT, GROSS_AMOUNT, D("10"), REDUCTION, D("25.5"), D("0")
    )

    assert render(line) == "net_amount: gross_amount 10 less reduction 25.5, not below 0 = 0"


def test_renders_a_subtraction_not_below_zero_to_exactly_zero() -> None:
    line = SubtractedNotBelowZeroLine(
        NET_AMOUNT, GROSS_AMOUNT, D("40.50"), REDUCTION, D("40.50"), D("0")
    )

    assert render(line) == "net_amount: gross_amount 40.5 less reduction 40.5, not below 0 = 0"


# --- credit amounts ----------------------------


def test_renders_a_credit_amount_without_rounding() -> None:
    line = CreditAmountLine(PERSONAL_AMOUNT, Credit(D("1000.005")), NO_ROUNDING, D("1000.005"))

    assert render(line) == "personal_amount: credit amount 1000.005 (no rounding)"


def test_renders_a_rounded_credit_amount() -> None:
    line = CreditAmountLine(PERSONAL_AMOUNT, Credit(D("1000.005")), CENT, D("1000.01"))

    assert render(line) == "personal_amount: credit amount 1000.005 (half-up to 0.01)"


def test_renders_the_credit_amount_with_another_rounding_rule() -> None:
    line = CreditAmountLine(
        PERSONAL_AMOUNT, Credit(D("1000.99")), RoundTo(D("1"), RoundingMode.FLOOR), D("1000")
    )

    assert render(line) == "personal_amount: credit amount 1000.99 (floor to 1)"


# --- capped amounts ----------------------------


def test_renders_a_base_above_the_cap() -> None:
    line = CappedAmountLine(
        CAPPED_AMOUNT, GROSS_AMOUNT, D("1500.25"), Amount(D("1000")), NO_ROUNDING, D("1000")
    )

    assert render(line) == "capped_amount: lesser of gross_amount 1500.25 and 1000 (no rounding)"


def test_renders_a_base_below_the_cap() -> None:
    line = CappedAmountLine(
        CAPPED_AMOUNT, GROSS_AMOUNT, D("400.50"), Amount(D("1000")), NO_ROUNDING, D("400.50")
    )

    assert render(line) == "capped_amount: lesser of gross_amount 400.5 and 1000 (no rounding)"


def test_renders_a_rounded_capped_amount() -> None:
    line = CappedAmountLine(
        CAPPED_AMOUNT, GROSS_AMOUNT, D("400.005"), Amount(D("1000.00")), CENT, D("400.01")
    )

    assert (
        render(line) == "capped_amount: lesser of gross_amount 400.005 and 1000 (half-up to 0.01)"
    )


def test_renders_the_cap_as_given() -> None:
    line = CappedAmountLine(
        CAPPED_AMOUNT, GROSS_AMOUNT, D("0"), Amount(D("1471.5")), NO_ROUNDING, D("0")
    )

    assert render(line) == "capped_amount: lesser of gross_amount 0 and 1471.5 (no rounding)"


# --- lesser of amounts ----------------------------


def test_renders_the_lesser_of_two_amounts() -> None:
    line = LesserOfLine(LESSER_AMOUNT, ((PART_ONE, D("1500.25")), (PART_TWO, D("1000"))), D("1000"))

    assert render(line) == "lesser_amount: lesser of part_one 1500.25 and part_two 1000 = 1000"


def test_renders_the_lesser_of_amounts_in_the_order_of_the_line() -> None:
    line = LesserOfLine(
        LESSER_AMOUNT, ((PART_TWO, D("1000")), (PART_ONE, D("400.50"))), D("400.50")
    )

    assert render(line) == "lesser_amount: lesser of part_two 1000 and part_one 400.5 = 400.5"


def test_renders_the_lesser_of_three_amounts_with_and_between_each() -> None:
    line = LesserOfLine(
        LESSER_AMOUNT,
        ((PART_ONE, D("100.25")), (PART_TWO, D("40")), (PART_THREE, D("9.75"))),
        D("9.75"),
    )

    assert render(line) == (
        "lesser_amount: lesser of part_one 100.25 and part_two 40 and part_three 9.75 = 9.75"
    )


def test_renders_the_lesser_of_equal_amounts() -> None:
    line = LesserOfLine(LESSER_AMOUNT, ((PART_ONE, D("40.50")), (PART_TWO, D("40.5"))), D("40.50"))

    assert render(line) == "lesser_amount: lesser of part_one 40.5 and part_two 40.5 = 40.5"


def test_renders_the_lesser_of_one_amount() -> None:
    line = LesserOfLine(LESSER_AMOUNT, ((PART_TWO, D("40.5")),), D("40.5"))

    assert render(line) == "lesser_amount: lesser of part_two 40.5 = 40.5"


# --- greater of amounts ----------------------------
# --- lesser of amounts and a maximum ---------------------------------------------------
#
# "<output>: lesser of <part> <amount> and <part> <amount> and <maximum> (<rule>) = <result>", every
# figure as given without trailing zeros, the result last.


def test_renders_the_lesser_of_two_amounts_and_a_maximum() -> None:
    line = LesserOfWithMaximumLine(
        LESSER_AMOUNT,
        ((PART_ONE, D("2500")), (PART_TWO, D("3000"))),
        Amount(D("2000")),
        NO_ROUNDING,
        D("2000"),
    )

    assert render(line) == (
        "lesser_amount: lesser of part_one 2500 and part_two 3000 and 2000 (no rounding) = 2000"
    )


def test_renders_the_lesser_of_amounts_and_a_maximum_in_the_order_of_the_line() -> None:
    line = LesserOfWithMaximumLine(
        LESSER_AMOUNT,
        ((PART_TWO, D("150")), (PART_ONE, D("80.50"))),
        Amount(D("2000")),
        NO_ROUNDING,
        D("80.50"),
    )

    assert render(line) == (
        "lesser_amount: lesser of part_two 150 and part_one 80.5 and 2000 (no rounding) = 80.5"
    )


def test_renders_the_lesser_of_one_amount_and_a_maximum() -> None:
    line = LesserOfWithMaximumLine(
        LESSER_AMOUNT, ((PART_TWO, D("40.5")),), Amount(D("2000")), NO_ROUNDING, D("40.5")
    )

    assert render(line) == "lesser_amount: lesser of part_two 40.5 and 2000 (no rounding) = 40.5"


def test_renders_the_lesser_of_amounts_and_a_maximum_with_the_rounding_rule() -> None:
    line = LesserOfWithMaximumLine(
        LESSER_AMOUNT,
        ((PART_ONE, D("80.005")), (PART_TWO, D("150"))),
        Amount(D("2000.00")),
        CENT,
        D("80.01"),
    )

    assert render(line) == (
        "lesser_amount: lesser of part_one 80.005 and part_two 150 and 2000 (half-up to 0.01)"
        " = 80.01"
    )


# --- greater of amounts -------------------------------------------------------------------


def test_renders_the_greater_of_two_amounts() -> None:
    line = GreaterOfLine(
        GREATER_AMOUNT, ((PART_ONE, D("1500.25")), (PART_TWO, D("1000"))), D("1500.25")
    )

    assert render(line) == "greater_amount: greater of part_one 1500.25 and part_two 1000 = 1500.25"


def test_renders_the_greater_of_amounts_in_the_order_of_the_line() -> None:
    line = GreaterOfLine(
        GREATER_AMOUNT, ((PART_TWO, D("1000")), (PART_ONE, D("400.50"))), D("1000")
    )

    assert render(line) == "greater_amount: greater of part_two 1000 and part_one 400.5 = 1000"


def test_renders_the_greater_of_three_amounts_with_and_between_each() -> None:
    line = GreaterOfLine(
        GREATER_AMOUNT,
        ((PART_ONE, D("100.25")), (PART_TWO, D("40")), (PART_THREE, D("9.75"))),
        D("100.25"),
    )

    assert render(line) == (
        "greater_amount: greater of part_one 100.25 and part_two 40 and part_three 9.75 = 100.25"
    )


def test_renders_the_greater_of_equal_amounts() -> None:
    line = GreaterOfLine(
        GREATER_AMOUNT, ((PART_ONE, D("40.50")), (PART_TWO, D("40.5"))), D("40.50")
    )

    assert render(line) == "greater_amount: greater of part_one 40.5 and part_two 40.5 = 40.5"


def test_renders_the_greater_of_one_amount() -> None:
    line = GreaterOfLine(GREATER_AMOUNT, ((PART_TWO, D("40.5")),), D("40.5"))

    assert render(line) == "greater_amount: greater of part_two 40.5 = 40.5"


# --- contribution tiers ----------------------------


def test_renders_a_contribution_tier() -> None:
    line = ContributionTierLine(
        CONTRIBUTION, EARNINGS, D("23000"), TIER, NO_ROUNDING, D("20000"), D("1000")
    )

    assert render(line) == (
        "contribution: 5% of earnings between 3000 and 50000 (20000), at most 2350 (no rounding)"
    )


def test_renders_a_rounded_contribution_tier() -> None:
    line = ContributionTierLine(
        CONTRIBUTION, EARNINGS, D("23000.10"), TIER, CENT, D("20000.10"), D("1000.01")
    )

    assert render(line) == (
        "contribution: 5% of earnings between 3000 and 50000 (20000.1), at most 2350 "
        "(half-up to 0.01)"
    )


def test_renders_earnings_above_the_band_as_the_band() -> None:
    line = ContributionTierLine(
        CONTRIBUTION, EARNINGS, D("80000"), TIER, NO_ROUNDING, D("47000"), D("2350")
    )

    assert render(line) == (
        "contribution: 5% of earnings between 3000 and 50000 (47000), at most 2350 (no rounding)"
    )


def test_renders_zero_contributory_earnings() -> None:
    line = ContributionTierLine(CONTRIBUTION, EARNINGS, D("-500"), TIER, NO_ROUNDING, D(0), D(0))

    assert render(line) == (
        "contribution: 5% of earnings between 3000 and 50000 (0), at most 2350 (no rounding)"
    )


def test_renders_the_tiers_figures() -> None:
    tier = ContributionTier(Rate(D("0.0505")), D("2500.00"), D("61000"), D("2954.20"))
    line = ContributionTierLine(
        CONTRIBUTION, EARNINGS, D("90000"), tier, CENT, D("58500.00"), D("2954.20")
    )

    assert render(line) == (
        "contribution: 5.05% of earnings between 2500 and 61000 (58500), at most 2954.2 "
        "(half-up to 0.01)"
    )


# --- surcharge tiers ----------------------------


def test_renders_a_surcharge_tier() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("400"), D("300"), Rate(D("0.25")), NO_ROUNDING, D("25")
    )

    assert render(line) == "surcharge: 25% of tax_so_far 400 over 300 (no rounding)"


def test_renders_a_rounded_surcharge_tier() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("300.06"), D("100"), Rate(D("0.10")), CENT, D("20.01")
    )

    assert render(line) == "surcharge: 10% of tax_so_far 300.06 over 100 (half-up to 0.01)"


def test_renders_a_surcharge_tier_the_base_does_not_reach() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("200"), D("300"), Rate(D("0.25")), NO_ROUNDING, D("0")
    )

    assert render(line) == "surcharge: 25% of tax_so_far 200 over 300 (no rounding)"


def test_renders_the_threshold_and_base() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("1000.50"), D("1471.5"), Rate(D("0.0505")), NO_ROUNDING, D(0)
    )

    assert render(line) == "surcharge: 5.05% of tax_so_far 1000.5 over 1471.5 (no rounding)"


def test_renders_a_surcharge_tiers_maximum_before_the_rounding() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("400"), D("300"), Rate(D("0.06")), NO_ROUNDING, D("6"), D("300")
    )

    assert render(line) == "surcharge: 6% of tax_so_far 400 over 300, at most 300 (no rounding)"


def test_renders_a_capped_surcharge_tier_with_its_rounding() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("1000"), D("100"), Rate(D("0.10")), CENT, D("15.56"), D("15.555")
    )

    assert render(line) == (
        "surcharge: 10% of tax_so_far 1000 over 100, at most 15.555 (half-up to 0.01)"
    )


def test_renders_a_zero_maximum() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("400"), D("300"), Rate(D("0.25")), NO_ROUNDING, D("0"), D("0")
    )

    assert render(line) == "surcharge: 25% of tax_so_far 400 over 300, at most 0 (no rounding)"


def test_renders_a_maximum_on_a_tier_the_base_does_not_reach() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX_SO_FAR, D("200"), D("300"), Rate(D("0.25")), NO_ROUNDING, D("0"), D("150")
    )

    assert render(line) == "surcharge: 25% of tax_so_far 200 over 300, at most 150 (no rounding)"


@pytest.mark.parametrize(
    ("maximum", "text"),
    [
        (D("1.500E+2"), "at most 150"),
        (D("150.50"), "at most 150.5"),
        (D("0.00"), "at most 0"),
    ],
)
def test_renders_a_surcharge_tiers_maximum_without_trailing_zeros(
    maximum: Decimal, text: str
) -> None:
    line = SurchargeTierLine(
        SURCHARGE,
        TAX_SO_FAR,
        D("400.50"),
        D("3E+2"),
        Rate(D("0.25")),
        NO_ROUNDING,
        D("25"),
        maximum,
    )

    assert render(line) == f"surcharge: 25% of tax_so_far 400.5 over 300, {text} (no rounding)"


# --- tapered amounts ----------------------------


def test_renders_a_tapered_amount() -> None:
    line = TaperedAmountLine(
        PERSONAL_AMOUNT, INCOME, D("22000"), TAPER, NO_ROUNDING, ExactFraction(100), D("1400")
    )

    assert render(line) == (
        "personal_amount: 1000 plus 500 less 100 for income 22000 over 20000 (range 10000), "
        "not below 1000 (no rounding)"
    )


def test_renders_a_rounded_tapered_amount() -> None:
    line = TaperedAmountLine(
        PERSONAL_AMOUNT, INCOME, D("22000.5"), TAPER, CENT, ExactFraction("100.025"), D("1399.98")
    )

    assert render(line) == (
        "personal_amount: 1000 plus 500 less 100.025 for income 22000.5 over 20000 "
        "(range 10000), not below 1000 (half-up to 0.01)"
    )


def test_renders_a_tapered_amount_below_the_threshold() -> None:
    line = TaperedAmountLine(
        PERSONAL_AMOUNT, INCOME, D("15000"), TAPER, NO_ROUNDING, ExactFraction(0), D("1500")
    )

    assert render(line) == (
        "personal_amount: 1000 plus 500 less 0 for income 15000 over 20000 (range 10000), "
        "not below 1000 (no rounding)"
    )


def test_renders_a_reduction_above_the_supplement_as_recorded() -> None:
    line = TaperedAmountLine(
        PERSONAL_AMOUNT, INCOME, D("80000"), TAPER, NO_ROUNDING, ExactFraction(3000), D("1000")
    )

    assert render(line) == (
        "personal_amount: 1000 plus 500 less 3000 for income 80000 over 20000 (range 10000), "
        "not below 1000 (no rounding)"
    )


def test_renders_a_reduction_without_a_finite_expansion_as_a_fraction() -> None:
    # The reduction is an exact fraction: 500 × 1000 / 7000 = 500/7, which has no decimal form.
    taper = Taper(D("1000"), D("500"), D("20000"), D("7000"))
    line = TaperedAmountLine(
        PERSONAL_AMOUNT, INCOME, D("21000"), taper, CENT, ExactFraction(500, 7), D("1428.57")
    )

    assert render(line) == (
        "personal_amount: 1000 plus 500 less 500/7 for income 21000 "
        "over 20000 (range 7000), not below 1000 (half-up to 0.01)"
    )


def test_renders_the_return_e_style_reduction_as_its_lowest_terms_fraction() -> None:
    # 1591 × (198926 − 177882) / 75532 = 33481004 / 75532 = 8370251 / 18883 in lowest terms.
    reduction = ExactFraction(1591 * (198926 - 177882), 75532)
    taper = Taper(D("14538"), D("1591"), D("177882"), D("75532"))
    line = TaperedAmountLine(
        PERSONAL_AMOUNT, INCOME, D("198926"), taper, CENT, reduction, D("15685.73")
    )

    assert render(line) == (
        "personal_amount: 14538 plus 1591 less 8370251/18883 "
        "for income 198926 over 177882 (range 75532), not below 14538 (half-up to 0.01)"
    )


@pytest.mark.parametrize(
    ("reduction", "text"),
    [
        (ExactFraction(0), "0"),
        (ExactFraction(3000), "3000"),
        (ExactFraction(4001, 40), "100.025"),
        (ExactFraction(1, 2), "0.5"),
        (ExactFraction(-3, 4), "-0.75"),
        # A finite expansion longer than any default precision still shows every digit.
        (ExactFraction(1, 2**10), "0.0009765625"),
        (ExactFraction(1, 2**30), "0.000000000931322574615478515625"),
    ],
)
def test_renders_a_reduction_with_a_finite_expansion_as_a_plain_figure(
    reduction: ExactFraction, text: str
) -> None:
    line = TaperedAmountLine(PERSONAL_AMOUNT, INCOME, D("22000"), TAPER, CENT, reduction, D("1400"))

    assert render(line) == (
        f"personal_amount: 1000 plus 500 less {text} for income 22000 "
        "over 20000 (range 10000), not below 1000 (half-up to 0.01)"
    )


# --- per-unit amounts ----------------------------


def test_renders_a_per_unit_amount() -> None:
    line = PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 2, Amount(D("544")), NO_ROUNDING, D("1088"))

    assert render(line) == "child_amount: 544 for each of 2 child_count = 1088 (no rounding)"


def test_renders_a_per_unit_amount_for_one_unit() -> None:
    line = PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 1, Amount(D("544")), NO_ROUNDING, D("544"))

    assert render(line) == "child_amount: 544 for each of 1 child_count = 544 (no rounding)"


def test_renders_a_per_unit_amount_for_no_units() -> None:
    line = PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 0, Amount(D("544")), NO_ROUNDING, D("0"))

    assert render(line) == "child_amount: 544 for each of 0 child_count = 0 (no rounding)"


def test_renders_a_fractional_per_unit_amount() -> None:
    line = PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 3, Amount(D("0.333")), NO_ROUNDING, D("0.999"))

    assert render(line) == "child_amount: 0.333 for each of 3 child_count = 0.999 (no rounding)"


def test_renders_a_rounded_per_unit_amount() -> None:
    line = PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 3, Amount(D("0.333")), CENT, D("1.00"))

    assert render(line) == "child_amount: 0.333 for each of 3 child_count = 1 (half-up to 0.01)"


# --- multiples over a figure ----------------------------


def test_renders_a_multiple_over_a_figure() -> None:
    line = MultipleOverLine(
        REDUCTION,
        REDUCTION_AMOUNTS,
        D("294"),
        Factor(D("2")),
        TAX_SO_FAR,
        D("8195.7644476"),
        NO_ROUNDING,
        D("0"),
    )

    assert render(line) == (
        "reduction: 2 × reduction_amounts 294 over tax_so_far 8195.7644476, not below 0 "
        "(no rounding)"
    )


def test_renders_a_multiple_above_the_figure() -> None:
    line = MultipleOverLine(
        REDUCTION,
        REDUCTION_AMOUNTS,
        D("294"),
        Factor(D("2")),
        TAX_SO_FAR,
        D("100"),
        NO_ROUNDING,
        D("488"),
    )

    assert render(line) == (
        "reduction: 2 × reduction_amounts 294 over tax_so_far 100, not below 0 (no rounding)"
    )


def test_renders_a_rounded_multiple_over_a_figure() -> None:
    line = MultipleOverLine(
        REDUCTION,
        REDUCTION_AMOUNTS,
        D("294.005"),
        Factor(D("2")),
        TAX_SO_FAR,
        D("0.0001"),
        CENT,
        D("588.01"),
    )

    assert render(line) == (
        "reduction: 2 × reduction_amounts 294.005 over tax_so_far 0.0001, not below 0 "
        "(half-up to 0.01)"
    )


def test_renders_a_fractional_factor() -> None:
    line = MultipleOverLine(
        REDUCTION,
        REDUCTION_AMOUNTS,
        D("294"),
        Factor(D("2.5")),
        TAX_SO_FAR,
        D("100.5"),
        NO_ROUNDING,
        D("634.5"),
    )

    assert render(line) == (
        "reduction: 2.5 × reduction_amounts 294 over tax_so_far 100.5, not below 0 (no rounding)"
    )


# --- amounts at most a bound ----------------------------


def test_renders_an_amount_at_most_a_bound() -> None:
    line = AtMostLine(ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("1500.25"), CLAIM_LIMIT, D("1926"))

    assert render(line) == "allowed_amount: claimed_amount 1500.25, at most claim_limit 1926"


def test_renders_an_amount_equal_to_its_bound() -> None:
    line = AtMostLine(ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("1926"), CLAIM_LIMIT, D("1926"))

    assert render(line) == "allowed_amount: claimed_amount 1926, at most claim_limit 1926"


def test_renders_a_zero_amount_at_most_a_zero_bound() -> None:
    line = AtMostLine(ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("0"), CLAIM_LIMIT, D("0"))

    assert render(line) == "allowed_amount: claimed_amount 0, at most claim_limit 0"


def test_renders_an_amount_at_most_a_bound_with_every_digit() -> None:
    line = AtMostLine(ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("0.0049"), CLAIM_LIMIT, D("0.005"))

    assert render(line) == "allowed_amount: claimed_amount 0.0049, at most claim_limit 0.005"


# --- claims at most a signed maximum ----------------------------


def test_renders_a_claim_at_most_a_maximum() -> None:
    line = ClaimAtMostLine(ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("1500.25"), CLAIM_LIMIT, D("1926"))

    assert render(line) == "allowed_amount: claimed_amount 1500.25, at most claim_limit 1926"


def test_renders_a_zero_claim_allowed_against_a_negative_maximum() -> None:
    line = ClaimAtMostLine(ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("0"), CLAIM_LIMIT, D("-9500.00"))

    assert render(line) == (
        "allowed_amount: claimed_amount 0, allowed because claim_limit -9500 is negative"
    )


def test_renders_a_zero_claim_against_a_zero_maximum_as_at_most() -> None:
    line = ClaimAtMostLine(ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("0"), CLAIM_LIMIT, D("0"))

    assert render(line) == "allowed_amount: claimed_amount 0, at most claim_limit 0"


# --- amounts gated by a threshold ----------------------------
#
# "<output>: <amount kind> <amount> if <gate kind> <gate> is at least <threshold> (<rule>) =
# <result>", every figure as given without trailing zeros, the result last.


def test_renders_an_amount_passed_through_a_gate_at_the_threshold() -> None:
    line = ThresholdGateLine(
        GATED_AMOUNT,
        GROSS_AMOUNT,
        D("1500.00"),
        GATE_AMOUNT,
        D("4390"),
        Amount(D("4390.00")),
        NO_ROUNDING,
        D("1500.00"),
    )

    assert render(line) == (
        "gated_amount: gross_amount 1500 if gate_amount 4390 is at least 4390 (no rounding) = 1500"
    )


def test_renders_an_amount_held_back_by_a_gate_below_the_threshold() -> None:
    line = ThresholdGateLine(
        GATED_AMOUNT,
        GROSS_AMOUNT,
        D("1500"),
        GATE_AMOUNT,
        D("4389.99"),
        Amount(D("4390")),
        NO_ROUNDING,
        D("0"),
    )

    assert render(line) == (
        "gated_amount: gross_amount 1500 if gate_amount 4389.99 is at least 4390 (no rounding) = 0"
    )


def test_renders_a_rounded_gated_amount() -> None:
    line = ThresholdGateLine(
        GATED_AMOUNT,
        GROSS_AMOUNT,
        D("400.005"),
        GATE_AMOUNT,
        D("5000"),
        Amount(D("4390")),
        CENT,
        D("400.01"),
    )

    assert render(line) == (
        "gated_amount: gross_amount 400.005 if gate_amount 5000 is at least 4390 "
        "(half-up to 0.01) = 400.01"
    )


# --- amounts passed through or divided by a rate ----------------------------
#
# "<output>: <amount kind> <amount> if <threshold> or less, otherwise <dividend kind> <dividend>
# divided by <rate>% (<rule>) = <result>", one sentence that does not pick the branch, every
# figure as given without trailing zeros, the result last.


def test_renders_an_amount_or_a_figure_divided_by_a_rate() -> None:
    line = AmountOrDividedByRateLine(
        LIMITED_AMOUNT,
        AMOUNT_TESTED,
        D("60000"),
        DIVIDED_AMOUNT,
        D("3321.67"),
        ThresholdRate(Rate(D("0.0505")), D("52886")),
        CENT,
        D("65775.64"),
    )

    assert render(line) == (
        "limited_amount: amount_tested 60000 if 52886 or less, otherwise divided_amount 3321.67 "
        "divided by 5.05% (half-up to 0.01) = 65775.64"
    )


def test_renders_the_same_sentence_when_the_amount_is_passed_through() -> None:
    line = AmountOrDividedByRateLine(
        LIMITED_AMOUNT,
        AMOUNT_TESTED,
        D("50000"),
        DIVIDED_AMOUNT,
        D("3321.67"),
        ThresholdRate(Rate(D("0.0505")), D("52886")),
        CENT,
        D("50000.00"),
    )

    assert render(line) == (
        "limited_amount: amount_tested 50000 if 52886 or less, otherwise divided_amount 3321.67 "
        "divided by 5.05% (half-up to 0.01) = 50000"
    )


def test_renders_a_second_threshold_and_rate_without_rounding() -> None:
    line = AmountOrDividedByRateLine(
        LIMITED_AMOUNT,
        AMOUNT_TESTED,
        D("70000"),
        DIVIDED_AMOUNT,
        D("10907.51"),
        ThresholdRate(Rate(D("0.145")), D("57375")),
        NO_ROUNDING,
        D("75224.2"),
    )

    assert render(line) == (
        "limited_amount: amount_tested 70000 if 57375 or less, otherwise divided_amount 10907.51 "
        "divided by 14.5% (no rounding) = 75224.2"
    )


def test_renders_this_lines_figures_without_trailing_zeros_or_an_exponent() -> None:
    line = AmountOrDividedByRateLine(
        LIMITED_AMOUNT,
        AMOUNT_TESTED,
        D("6.0000E+4"),
        DIVIDED_AMOUNT,
        D("3321.670"),
        ThresholdRate(Rate(D("0.0505")), D("5.2886E+4")),
        CENT,
        D("65775.64"),
    )

    assert render(line) == (
        "limited_amount: amount_tested 60000 if 52886 or less, otherwise divided_amount 3321.67 "
        "divided by 5.05% (half-up to 0.01) = 65775.64"
    )


# --- fractions applied ----------------------------
#
# The fraction prints as its two whole parts, "<numerator>/<denominator>", as given.


def test_renders_a_fraction_applied_without_rounding() -> None:
    line = FractionAppliedLine(
        EARNED_PORTION, EARNED_INCOME, D("60000"), Fraction(2, 3), NO_ROUNDING, D("40000")
    )

    assert render(line) == "earned_portion: 2/3 of earned_income 60000 (no rounding)"


def test_renders_a_rounded_fraction_applied() -> None:
    line = FractionAppliedLine(
        EARNED_PORTION, EARNED_INCOME, D("50000"), Fraction(2, 3), CENT, D("33333.33")
    )

    assert render(line) == "earned_portion: 2/3 of earned_income 50000 (half-up to 0.01)"


def test_renders_an_unrounded_exact_fraction_applied() -> None:
    line = FractionAppliedLine(
        EARNED_PORTION, EARNED_INCOME, D("60000"), Fraction(2, 3), NO_ROUNDING, D("40000")
    )

    assert render(line) == "earned_portion: 2/3 of earned_income 60000 (no rounding)"


@pytest.mark.parametrize(
    ("numerator", "denominator", "text"), [(1, 1, "1/1"), (3, 2, "3/2"), (4, 6, "4/6")]
)
def test_renders_the_fraction_as_given(numerator: int, denominator: int, text: str) -> None:
    line = FractionAppliedLine(
        EARNED_PORTION,
        EARNED_INCOME,
        D("120"),
        Fraction(numerator, denominator),
        NO_ROUNDING,
        D("0"),
    )

    assert render(line) == f"earned_portion: {text} of earned_income 120 (no rounding)"


# --- amounts times a count ----------------------------
#
# The amount is an artifact, so it prints with its label, unlike a per-unit amount's dataset
# figure; there is no rounding rule to print.


def test_renders_an_amount_times_a_count_of_one() -> None:
    line = TimesCountLine(AMOUNT_CLAIMED, AMOUNT_EACH, D("16129"), PERSONS, 1, D("16129"))

    assert render(line) == "amount_claimed: amount_each 16129 for each of 1 person_count = 16129"


def test_renders_an_amount_times_a_count_of_two() -> None:
    line = TimesCountLine(AMOUNT_CLAIMED, AMOUNT_EACH, D("16129"), PERSONS, 2, D("32258"))

    assert render(line) == "amount_claimed: amount_each 16129 for each of 2 person_count = 32258"


def test_renders_an_amount_times_a_count_of_zero() -> None:
    line = TimesCountLine(AMOUNT_CLAIMED, AMOUNT_EACH, D("16129"), PERSONS, 0, D("0"))

    assert render(line) == "amount_claimed: amount_each 16129 for each of 0 person_count = 0"


def test_renders_an_amount_times_a_count_with_every_digit() -> None:
    line = TimesCountLine(AMOUNT_CLAIMED, AMOUNT_EACH, D("0.333"), PERSONS, 3, D("0.999"))

    assert render(line) == "amount_claimed: amount_each 0.333 for each of 3 person_count = 0.999"


def test_renders_a_negative_amount_times_a_count() -> None:
    line = TimesCountLine(AMOUNT_CLAIMED, AMOUNT_EACH, D("-250.75"), PERSONS, 2, D("-501.50"))

    assert render(line) == (
        "amount_claimed: amount_each -250.75 for each of 2 person_count = -501.5"
    )


# --- an amount chosen by a count ----------------------------
#
# The chosen candidate prints with its label and value, and the count that chose it with its
# label and value; the candidate not chosen is not printed. There is no rounding rule to print.


def test_renders_the_first_candidate_chosen_by_a_count_of_zero() -> None:
    line = ChosenByCountLine(AMOUNT_CHOSEN, DEPENDANTS, 0, AMOUNT_ALONE, D("1633"))

    assert render(line) == "amount_chosen: amount_alone 1633, chosen as dependant_count is 0"


def test_renders_the_second_candidate_chosen_by_a_count_of_one() -> None:
    line = ChosenByCountLine(AMOUNT_CHOSEN, DEPENDANTS, 1, AMOUNT_WITH_FAMILY, D("2813"))

    assert render(line) == (
        "amount_chosen: amount_with_family 2813, chosen as dependant_count is 1"
    )


def test_renders_the_second_candidate_chosen_by_a_count_of_three() -> None:
    line = ChosenByCountLine(AMOUNT_CHOSEN, DEPENDANTS, 3, AMOUNT_WITH_FAMILY, D("2813"))

    assert render(line) == (
        "amount_chosen: amount_with_family 2813, chosen as dependant_count is 3"
    )


def test_renders_a_chosen_candidate_with_every_digit() -> None:
    line = ChosenByCountLine(AMOUNT_CHOSEN, DEPENDANTS, 1, AMOUNT_WITH_FAMILY, D("4319.4"))

    assert render(line) == (
        "amount_chosen: amount_with_family 4319.4, chosen as dependant_count is 1"
    )


def test_renders_a_negative_chosen_candidate() -> None:
    line = ChosenByCountLine(AMOUNT_CHOSEN, DEPENDANTS, 0, AMOUNT_ALONE, D("-250.75"))

    assert render(line) == "amount_chosen: amount_alone -250.75, chosen as dependant_count is 0"


def test_renders_a_negative_count_as_given() -> None:
    line = ChosenByCountLine(AMOUNT_CHOSEN, DEPENDANTS, -1, AMOUNT_WITH_FAMILY, D("2813"))

    assert render(line) == (
        "amount_chosen: amount_with_family 2813, chosen as dependant_count is -1"
    )


# --- an amount read from a table by a count ----------------------------
#
# The row's figure prints with the count's label and value, then the rounding rule; the result
# is not repeated (the row and the rule give it).


def test_renders_an_amount_by_count() -> None:
    line = AmountByCountLine(MONTHLY_AMOUNT, MONTHS, 2, D("200.50"), NO_ROUNDING, D("200.50"))

    assert render(line) == "monthly_amount: 200.5 for month_count 2 (no rounding)"


def test_renders_a_rounded_amount_by_count() -> None:
    line = AmountByCountLine(MONTHLY_AMOUNT, MONTHS, 4, D("400.255"), CENT, D("400.26"))

    assert render(line) == "monthly_amount: 400.255 for month_count 4 (half-up to 0.01)"


def test_renders_an_amount_by_count_of_zero_months() -> None:
    line = AmountByCountLine(MONTHLY_AMOUNT, MONTHS, 0, D("0.00"), NO_ROUNDING, D("0.00"))

    assert render(line) == "monthly_amount: 0 for month_count 0 (no rounding)"


# --- the total of a field over a list of records ----------------------------
#
# Each item is named by its position from 1, with the field's label and its amount; the total
# follows "=". An empty list prints "no items".


def test_renders_the_total_of_two_items() -> None:
    line = RecordTotalLine(TOTAL, ITEM_AMOUNT, (D("6000"), D("4000")), D("10000"))

    assert render(line) == "total: item 1 item_amount 6000 + item 2 item_amount 4000 = 10000"


def test_renders_the_total_of_three_items_named_by_position() -> None:
    line = RecordTotalLine(TOTAL, ITEM_AMOUNT, (D("1.5"), D("0"), D("250.25")), D("251.75"))

    assert render(line) == (
        "total: item 1 item_amount 1.5 + item 2 item_amount 0 + item 3 item_amount 250.25 = 251.75"
    )


def test_renders_the_total_of_one_item() -> None:
    line = RecordTotalLine(TOTAL, ITEM_AMOUNT, (D("40.5"),), D("40.5"))

    assert render(line) == "total: item 1 item_amount 40.5 = 40.5"


def test_renders_the_total_of_no_items() -> None:
    assert render(RecordTotalLine(TOTAL, ITEM_AMOUNT, (), D(0))) == "total: no items = 0"


def test_renders_the_items_in_the_order_of_the_line() -> None:
    line = RecordTotalLine(TOTAL, ITEM_AMOUNT, (D("4000"), D("6000")), D("10000"))

    assert render(line) == "total: item 1 item_amount 4000 + item 2 item_amount 6000 = 10000"


def test_renders_the_output_and_field_labels_without_their_namespace() -> None:
    line = RecordTotalLine(GROSS_AMOUNT, PART_ONE, (D("2"),), D("2"))

    assert render(line) == "gross_amount: item 1 part_one 2 = 2"


# --- the total of the positive amounts over a list of records ---------------
#
# Each item is named by its position from 1, with the field's label and the amount as read; an
# item whose amount is zero or negative is followed by "counts 0". The total follows "=", then the
# rule: only positive amounts are added. An empty list prints "no items".

POSITIVE_RULE = "Only positive amounts are added; a zero or negative amount counts 0."


def test_renders_the_positive_total_of_positive_items() -> None:
    line = RecordPositiveTotalLine(TOTAL, ITEM_AMOUNT, (D("6000"), D("4000")), D("10000"))

    assert render(line) == (
        f"total: item 1 item_amount 6000 + item 2 item_amount 4000 = 10000. {POSITIVE_RULE}"
    )


def test_renders_a_negative_item_as_counting_zero() -> None:
    line = RecordPositiveTotalLine(
        TOTAL, ITEM_AMOUNT, (D("6000"), D("-4000"), D("250.25")), D("6250.25")
    )

    assert render(line) == (
        "total: item 1 item_amount 6000 + item 2 item_amount -4000 counts 0"
        f" + item 3 item_amount 250.25 = 6250.25. {POSITIVE_RULE}"
    )


def test_renders_a_zero_item_as_counting_zero() -> None:
    line = RecordPositiveTotalLine(TOTAL, ITEM_AMOUNT, (D("0"),), D("0"))

    assert render(line) == (f"total: item 1 item_amount 0 counts 0 = 0. {POSITIVE_RULE}")


def test_renders_the_positive_total_of_no_items() -> None:
    assert render(RecordPositiveTotalLine(TOTAL, ITEM_AMOUNT, (), D(0))) == (
        f"total: no items = 0. {POSITIVE_RULE}"
    )


def test_renders_the_positive_items_in_the_order_of_the_line() -> None:
    line = RecordPositiveTotalLine(TOTAL, ITEM_AMOUNT, (D("4000"), D("-6000")), D("4000"))

    assert render(line) == (
        "total: item 1 item_amount 4000 + item 2 item_amount -6000 counts 0"
        f" = 4000. {POSITIVE_RULE}"
    )


# --- an amount chosen by a range ----------------------------
#
# The chosen candidate prints with its label and value, and the tested amount with its label and
# value; the candidates not chosen and the limits are not printed. There is no rounding rule to
# print.


def test_renders_a_candidate_chosen_by_the_tested_amount() -> None:
    line = ChosenByRangeLine(AMOUNT_CHOSEN, AMOUNT_TESTED, D("1000"), AMOUNT_IN_RANGE, D("625.01"))

    assert render(line) == "amount_chosen: amount_in_range 625.01, chosen as amount_tested is 1000"


def test_renders_a_tested_amount_and_a_chosen_candidate_with_every_digit() -> None:
    line = ChosenByRangeLine(
        AMOUNT_CHOSEN, AMOUNT_TESTED, D("500.05"), AMOUNT_IN_RANGE, D("4319.4")
    )

    assert (
        render(line) == "amount_chosen: amount_in_range 4319.4, chosen as amount_tested is 500.05"
    )


def test_renders_a_zero_tested_amount() -> None:
    line = ChosenByRangeLine(AMOUNT_CHOSEN, AMOUNT_TESTED, D("0"), AMOUNT_IN_RANGE, D("0"))

    assert render(line) == "amount_chosen: amount_in_range 0, chosen as amount_tested is 0"


def test_renders_a_negative_chosen_candidate_and_a_negative_tested_amount() -> None:
    line = ChosenByRangeLine(AMOUNT_CHOSEN, AMOUNT_TESTED, D("-5"), AMOUNT_IN_RANGE, D("-250.75"))

    assert render(line) == "amount_chosen: amount_in_range -250.75, chosen as amount_tested is -5"


# --- a rate chosen by a band of income ----------------------------
#
# Read like the form's table: the figure with its label, then the row it falls in, "more than
# <lower> but not more than <upper>" (just "more than <lower>" on the unbounded last row), then
# the row's rate as a percentage. A figure of exactly zero names no row: "which is 0". There is no
# rounding rule to print.


def test_renders_a_rate_chosen_by_a_bounded_band() -> None:
    line = RateByIncomeBandLine(
        BAND_RATE,
        FAMILY_INCOME,
        D("50000"),
        RateTableRow(D("45000"), D("50000"), Rate(D("0.55"))),
        Rate(D("0.55")),
    )

    assert render(line) == (
        "band_rate: family_income 50000, more than 45000 but not more than 50000: 55%"
    )


def test_renders_a_rate_chosen_by_the_unbounded_last_band() -> None:
    line = RateByIncomeBandLine(
        BAND_RATE,
        FAMILY_INCOME,
        D("150001"),
        RateTableRow(D("150000"), None, Rate(D("0"))),
        Rate(D("0")),
    )

    assert render(line) == "band_rate: family_income 150001, more than 150000: 0%"


def test_renders_the_rate_at_zero() -> None:
    line = RateByIncomeBandLine(BAND_RATE, FAMILY_INCOME, D("0"), None, Rate(D("0.75")))

    assert render(line) == "band_rate: family_income 0, which is 0: 75%"


def test_renders_a_band_chosen_for_a_figure_with_cents() -> None:
    line = RateByIncomeBandLine(
        BAND_RATE,
        FAMILY_INCOME,
        D("20000.01"),
        RateTableRow(D("20000"), D("22500"), Rate(D("0.73"))),
        Rate(D("0.73")),
    )

    assert render(line) == (
        "band_rate: family_income 20000.01, more than 20000 but not more than 22500: 73%"
    )


def test_renders_a_fractional_band_rate() -> None:
    line = RateByIncomeBandLine(
        BAND_RATE,
        FAMILY_INCOME,
        D("1500"),
        RateTableRow(D("1000"), D("2000"), Rate(D("0.125"))),
        Rate(D("0.125")),
    )

    assert render(line) == (
        "band_rate: family_income 1500, more than 1000 but not more than 2000: 12.5%"
    )


# --- a chosen rate applied ----------------------------
#
# Like a rate applied, with the rate artifact's label before its percentage.


def test_renders_a_chosen_rate_applied_with_rounding() -> None:
    line = ChosenRateAppliedLine(
        CARE_CREDIT, CARE_EXPENSES, D("5000"), BAND_RATE, Rate(D("0.55")), CENT, D("2750.00")
    )

    assert render(line) == "care_credit: band_rate 55% of care_expenses 5000 (half-up to 0.01)"


def test_renders_a_chosen_rate_applied_without_rounding() -> None:
    line = ChosenRateAppliedLine(
        CARE_CREDIT,
        CARE_EXPENSES,
        D("5000.01"),
        BAND_RATE,
        Rate(D("0.55")),
        NO_ROUNDING,
        D("2750.0055"),
    )

    assert render(line) == "care_credit: band_rate 55% of care_expenses 5000.01 (no rounding)"


def test_renders_a_chosen_rate_of_zero() -> None:
    line = ChosenRateAppliedLine(
        CARE_CREDIT, CARE_EXPENSES, D("5000"), BAND_RATE, Rate(D("0")), CENT, D("0.00")
    )

    assert render(line) == "care_credit: band_rate 0% of care_expenses 5000 (half-up to 0.01)"


# --- an amount claimed per dependant ----------------------------
#
# One sentence: the output's label, then one clause per dependant named by its position from 1,
# "dependant 1: <base> less net income <income>, at most <maximum> = <allowable amount>", joined by
# "; ", then "total <total>" and the rounding rule in brackets. With no dependants the clauses
# are "no dependants". Every figure prints without trailing zeros.


def caregiver_claim(
    position: int,
    net_income: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> CaregiverClaimLine:
    return CaregiverClaimLine(
        CAREGIVER_AMOUNT,
        position,
        Amount(D("28798.00")),
        D(net_income),
        Amount(D("8601")),
        rounding,
        D(result),
    )


def test_renders_one_dependants_claim_by_position() -> None:
    assert render(caregiver_claim(1, "5000", "8601.00")) == (
        "caregiver_amount: dependant 1: 28798 less net income 5000, at most 8601 = 8601 "
        "(half-up to 0.01)"
    )


def test_renders_the_second_dependants_claim() -> None:
    assert render(caregiver_claim(2, "25000", "3798.00")) == (
        "caregiver_amount: dependant 2: 28798 less net income 25000, at most 8601 = 3798 "
        "(half-up to 0.01)"
    )


def test_renders_a_dependant_with_nothing_allowed() -> None:
    assert render(caregiver_claim(1, "30000", "0.00")) == (
        "caregiver_amount: dependant 1: 28798 less net income 30000, at most 8601 = 0 "
        "(half-up to 0.01)"
    )


def test_renders_a_dependants_claim_without_rounding() -> None:
    assert render(caregiver_claim(3, "25000.005", "3797.995", NO_ROUNDING)) == (
        "caregiver_amount: dependant 3: 28798 less net income 25000.005, at most 8601 = 3797.995 "
        "(no rounding)"
    )


# --- an amount claimed per dependant, less what is claimed elsewhere ----------------------------
#
# The same sentence with the allowable amount before the claimed amount and the claimed amount
# after it: "dependant 1: <base> less net income <income>, at most <maximum> = <allowable amount>,
# less claimed <claimed> = <result> (<rounding>)". Every figure prints without trailing zeros.


def caregiver_claim_less_claimed(
    position: int,
    net_income: str,
    allowable: str,
    claimed: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> CaregiverClaimLessClaimedLine:
    return CaregiverClaimLessClaimedLine(
        CAREGIVER_AMOUNT,
        position,
        Amount(D("26562.00")),
        D(net_income),
        Amount(D("6008")),
        D(allowable),
        D(claimed),
        rounding,
        D(result),
    )


def test_renders_a_dependant_with_nothing_claimed_elsewhere() -> None:
    assert render(caregiver_claim_less_claimed(1, "5000", "6008.00", "0", "6008.00")) == (
        "caregiver_amount: dependant 1: 26562 less net income 5000, at most 6008 = 6008, "
        "less claimed 0 = 6008 (half-up to 0.01)"
    )


def test_renders_a_dependant_with_an_amount_claimed_elsewhere() -> None:
    assert render(caregiver_claim_less_claimed(2, "5000", "6008.00", "2500.00", "3508.00")) == (
        "caregiver_amount: dependant 2: 26562 less net income 5000, at most 6008 = 6008, "
        "less claimed 2500 = 3508 (half-up to 0.01)"
    )


def test_renders_a_dependant_whose_claimed_amount_is_more_than_the_allowable_amount() -> None:
    assert render(caregiver_claim_less_claimed(1, "25000", "1562.00", "10823.00", "0.00")) == (
        "caregiver_amount: dependant 1: 26562 less net income 25000, at most 6008 = 1562, "
        "less claimed 10823 = 0 (half-up to 0.01)"
    )


def test_renders_a_dependant_with_nothing_allowed_before_the_claimed_amount() -> None:
    assert render(caregiver_claim_less_claimed(3, "30000", "0.00", "0", "0.00")) == (
        "caregiver_amount: dependant 3: 26562 less net income 30000, at most 6008 = 0, "
        "less claimed 0 = 0 (half-up to 0.01)"
    )


def test_renders_a_dependant_without_rounding() -> None:
    line = caregiver_claim_less_claimed(1, "26561.995", "0.005", "0.001", "0.004", NO_ROUNDING)

    assert render(line) == (
        "caregiver_amount: dependant 1: 26562 less net income 26561.995, at most 6008 = 0.005, "
        "less claimed 0.001 = 0.004 (no rounding)"
    )


# --- the lines of a capability that loops over a record list ----------------------------
#
# Each names the item by its position from 1, "item 2", after the produced kind.


def test_renders_an_item_sum() -> None:
    line = ItemSumLine(TOTAL, 2, ((PART_ONE, D("400")), (PART_TWO, D("500"))), D("900"))

    assert render(line) == "total: item 2: part_one 400 + part_two 500 = 900"


def test_renders_an_item_sum_without_trailing_zeros() -> None:
    line = ItemSumLine(TOTAL, 1, ((PART_ONE, D("400.00")), (PART_TWO, D("0.50"))), D("400.50"))

    assert render(line) == "total: item 1: part_one 400 + part_two 0.5 = 400.5"


def test_renders_an_item_lesser_of() -> None:
    line = ItemLesserOfLine(
        TOTAL,
        1,
        ((PART_ONE, D("1500")), (PART_TWO, D("1300")), (PART_THREE, D("750"))),
        D("750"),
    )

    assert render(line) == (
        "total: item 1: lesser of part_one 1500 and part_two 1300 and part_three 750 = 750"
    )


def test_renders_an_item_lesser_of_at_a_later_position_without_trailing_zeros() -> None:
    line = ItemLesserOfLine(
        TOTAL, 3, ((PART_ONE, D("1.50E+3")), (PART_TWO, D("750.50"))), D("750.50")
    )

    assert render(line) == "total: item 3: lesser of part_one 1500 and part_two 750.5 = 750.5"


def test_renders_the_total_of_items_by_position() -> None:
    line = ItemsTotalLine(TOTAL, ((1, D("750")), (3, D("800.50"))), D("1550.50"))

    assert render(line) == "total: item 1 750 + item 3 800.5 = 1550.5"


def test_renders_the_items_total_of_one_item() -> None:
    assert render(ItemsTotalLine(TOTAL, ((2, D("400.00")),), D("400.00"))) == (
        "total: item 2 400 = 400"
    )


def test_renders_the_items_total_of_no_items() -> None:
    assert render(ItemsTotalLine(TOTAL, (), D("0"))) == "total: no items = 0"


def test_renders_the_caregiver_amount_total_of_two_dependants() -> None:
    line = ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("8601.00")), (2, D("3798.00"))), D("12399.00"))

    assert render(line) == "caregiver_amount: item 1 8601 + item 2 3798 = 12399"


# --- a child's adoption expenses, each capped at the maximum for one child ----------------------
#
# One sentence: the output's label, then "item <position>: <amount>, at most <cap> = <result>",
# then the rounding rule in brackets. Every money figure prints without trailing zeros.


def capped_child(
    position: int,
    amount: str,
    cap: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> CappedRecordLine:
    return CappedRecordLine(
        ADOPTION_CREDIT, position, D(amount), Amount(D(cap)), rounding, D(result)
    )


def test_renders_a_child_under_the_cap() -> None:
    assert render(capped_child(1, "8000", "15551", "8000")) == (
        "adoption_credit: item 1: 8000, at most 15551 = 8000 (half-up to 0.01)"
    )


def test_renders_a_child_capped_at_the_maximum() -> None:
    assert render(capped_child(2, "20000", "15551", "15551")) == (
        "adoption_credit: item 2: 20000, at most 15551 = 15551 (half-up to 0.01)"
    )


def test_renders_a_child_without_trailing_zeros() -> None:
    assert render(capped_child(1, "8000.00", "15551.00", "8000.00")) == (
        "adoption_credit: item 1: 8000, at most 15551 = 8000 (half-up to 0.01)"
    )


def test_renders_a_child_rounded_to_the_cent() -> None:
    assert render(capped_child(1, "8000.005", "15551", "8000.01")) == (
        "adoption_credit: item 1: 8000.005, at most 15551 = 8000.01 (half-up to 0.01)"
    )


def test_renders_a_child_without_rounding() -> None:
    assert render(capped_child(1, "8000.005", "15551", "8000.005", NO_ROUNDING)) == (
        "adoption_credit: item 1: 8000.005, at most 15551 = 8000.005 (no rounding)"
    )


def test_renders_the_items_total_of_two_capped_children() -> None:
    line = ItemsTotalLine(ADOPTION_CREDIT, ((1, D("8000.00")), (2, D("15551.00"))), D("23551.00"))

    assert render(line) == "adoption_credit: item 1 8000 + item 2 15551 = 23551"


def test_renders_the_capped_children_then_the_total_in_order() -> None:
    lines = (
        capped_child(1, "8000", "15551", "8000"),
        capped_child(2, "20000", "15551", "15551"),
        ItemsTotalLine(ADOPTION_CREDIT, ((1, D("8000")), (2, D("15551"))), D("23551")),
    )

    assert EnglishTraceRenderer().render_all(lines) == (
        "adoption_credit: item 1: 8000, at most 15551 = 8000 (half-up to 0.01)",
        "adoption_credit: item 2: 20000, at most 15551 = 15551 (half-up to 0.01)",
        "adoption_credit: item 1 8000 + item 2 15551 = 23551",
    )


def test_renders_the_items_total_of_no_children() -> None:
    assert render(ItemsTotalLine(ADOPTION_CREDIT, (), D("0"))) == ("adoption_credit: no items = 0")


# --- an apprentice's salary and wages, the lesser of them and the maximum ----------------------
#
# One sentence: the output's label, then "apprentice <position>: the lesser of eligible salary and
# wages <salary and wages> and the maximum <maximum> is <amount>", then the rounding rule in
# brackets. Every money figure prints without trailing zeros.

APPRENTICESHIP_WAGES_TOTAL = ArtifactKind("ex/apprenticeship_wages_total", Decimal)


def apprentice_wages(
    position: int,
    salary: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> TraceLine:
    return ApprenticeWagesLine(
        APPRENTICESHIP_WAGES_TOTAL,
        position,
        D(salary),
        Amount(D("20000")),
        rounding,
        D(result),
    )


def test_renders_one_apprentices_amount_by_position() -> None:
    assert render(apprentice_wages(1, "25000.00", "20000.00")) == (
        "apprenticeship_wages_total: apprentice 1: the lesser of eligible salary and wages 25000 "
        "and the maximum 20000 is 20000 (half-up to 0.01)"
    )


def test_renders_an_apprentice_under_the_maximum_with_its_cents() -> None:
    assert render(apprentice_wages(2, "15000.005", "15000.01")) == (
        "apprenticeship_wages_total: apprentice 2: the lesser of eligible salary and wages "
        "15000.005 and the maximum 20000 is 15000.01 (half-up to 0.01)"
    )


def test_renders_an_apprentice_without_rounding() -> None:
    assert render(apprentice_wages(3, "15000.5", "15000.5", NO_ROUNDING)) == (
        "apprenticeship_wages_total: apprentice 3: the lesser of eligible salary and wages "
        "15000.5 and the maximum 20000 is 15000.5 (no rounding)"
    )


# --- a medical claim per dependant ----------------------------
#
# One sentence: the output's label, then "dependant <position>: expenses <expenses> less the
# lesser of <rate>% of net income <income> and <ceiling> = <allowable amount>", then
# ", at most <maximum>" when the reduction has a maximum, then the rounding rule in brackets.
# Rates print as plain percentages and every money figure without trailing zeros.


def medical_claim(
    position: int,
    expenses: str,
    net_income: str,
    result: str,
    maximum: str | None = None,
    rounding: RoundingRule = CENT,
    rate: str = "0.03",
    ceiling: str = "2834",
) -> OtherDependantMedicalLine:
    return OtherDependantMedicalLine(
        DEPENDANTS_MEDICAL,
        position,
        D(expenses),
        D(net_income),
        ClaimReduction(Rate(D(rate)), D(ceiling), None if maximum is None else D(maximum)),
        rounding,
        D(result),
    )


def test_renders_one_dependants_medical_claim_by_position() -> None:
    assert render(medical_claim(1, "3000", "10000", "2700.00")) == (
        "dependants_medical: dependant 1: expenses 3000 less the lesser of 3% of net income "
        "10000 and 2834 = 2700 (half-up to 0.01)"
    )


def test_renders_the_second_dependants_medical_claim_with_the_ceiling_applying() -> None:
    assert render(medical_claim(2, "5000", "200000", "2166.00")) == (
        "dependants_medical: dependant 2: expenses 5000 less the lesser of 3% of net income "
        "200000 and 2834 = 2166 (half-up to 0.01)"
    )


def test_renders_a_medical_claim_with_nothing_allowed() -> None:
    assert render(medical_claim(2, "1000", "40000", "0.00")) == (
        "dependants_medical: dependant 2: expenses 1000 less the lesser of 3% of net income "
        "40000 and 2834 = 0 (half-up to 0.01)"
    )


def test_renders_the_maximum_after_the_result_when_there_is_one() -> None:
    assert render(medical_claim(1, "20000", "10000", "15551.00", maximum="15551")) == (
        "dependants_medical: dependant 1: expenses 20000 less the lesser of 3% of net income "
        "10000 and 2834 = 15551, at most 15551 (half-up to 0.01)"
    )


def test_renders_no_maximum_clause_without_a_maximum() -> None:
    assert "at most" not in render(medical_claim(1, "3000", "10000", "2700.00"))


def test_renders_a_medical_claim_without_rounding() -> None:
    line = medical_claim(3, "1000", "10000.50", "699.985", rounding=NO_ROUNDING)

    assert render(line) == (
        "dependants_medical: dependant 3: expenses 1000 less the lesser of 3% of net income "
        "10000.5 and 2834 = 699.985 (no rounding)"
    )


@pytest.mark.parametrize(("rate", "percent"), [("0", "0"), ("0.125", "12.5"), ("1", "100")])
def test_renders_the_medical_claims_rate_as_a_plain_percentage(rate: str, percent: str) -> None:
    assert render(medical_claim(1, "100", "10", "90", rate=rate)) == (
        f"dependants_medical: dependant 1: expenses 100 less the lesser of {percent}% of net "
        "income 10 and 2834 = 90 (half-up to 0.01)"
    )


def test_renders_the_medical_claims_figures_without_trailing_zeros_or_an_exponent() -> None:
    line = medical_claim(
        1,
        "3.00000E+3",
        "1.0000E+4",
        "2.70000E+3",
        maximum="1.5551E+4",
        ceiling="2.83400E+3",
    )

    assert render(line) == (
        "dependants_medical: dependant 1: expenses 3000 less the lesser of 3% of net income "
        "10000 and 2834 = 2700, at most 15551 (half-up to 0.01)"
    )


# --- a short-term rental row of Chart A ------------------------------------------------
#
# One sentence: the output's label, then "row <position>: expenses <column 3> for <column 4>
# non-compliant days of <column 5> short-term days = <column 6>" and the rounding rule in
# brackets. Every money figure prints without trailing zeros; the days print as plain counts.


def non_compliant_row(
    position: int,
    expenses: str,
    non_compliant_days: int,
    days: int,
    result: str,
    rounding: RoundingRule = CENT,
) -> ShortTermRentalNonCompliantLine:
    return ShortTermRentalNonCompliantLine(
        NON_COMPLIANT_EXPENSES,
        position,
        D(expenses),
        non_compliant_days,
        days,
        rounding,
        D(result),
    )


def test_renders_one_non_compliant_row_by_position() -> None:
    assert render(non_compliant_row(1, "900", 30, 90, "300.00")) == (
        "non_compliant_expenses: row 1: expenses 900 for 30 non-compliant days of 90 "
        "short-term days = 300 (half-up to 0.01)"
    )


def test_renders_the_second_non_compliant_row() -> None:
    assert render(non_compliant_row(2, "100", 2, 3, "66.67")) == (
        "non_compliant_expenses: row 2: expenses 100 for 2 non-compliant days of 3 "
        "short-term days = 66.67 (half-up to 0.01)"
    )


def test_renders_a_non_compliant_row_with_no_non_compliant_days() -> None:
    assert render(non_compliant_row(1, "900", 0, 90, "0.00")) == (
        "non_compliant_expenses: row 1: expenses 900 for 0 non-compliant days of 90 "
        "short-term days = 0 (half-up to 0.01)"
    )


def test_renders_a_non_compliant_row_without_rounding() -> None:
    line = non_compliant_row(3, "0.015", 1, 2, "0.0075", rounding=NO_ROUNDING)

    assert render(line) == (
        "non_compliant_expenses: row 3: expenses 0.015 for 1 non-compliant days of 2 "
        "short-term days = 0.0075 (no rounding)"
    )


def test_renders_the_non_compliant_rows_figures_without_trailing_zeros_or_an_exponent() -> None:
    line = non_compliant_row(1, "9.0000E+2", 30, 90, "3.00000E+2")

    assert render(line) == (
        "non_compliant_expenses: row 1: expenses 900 for 30 non-compliant days of 90 "
        "short-term days = 300 (half-up to 0.01)"
    )


# --- a short-term rental row of Chart B ------------------------------------------------
#
# One sentence: the output's label, then "row <position>: class <column 1> CCA <column 4> for
# <column 5> non-compliant days of <column 6> short-term days = <column 7>" and the rounding rule
# in brackets. Every money figure prints without trailing zeros; the days print as plain counts.


def non_compliant_cca_row(
    position: int,
    class_number: str,
    related_cca: str,
    non_compliant_days: int,
    days: int,
    result: str,
    rounding: RoundingRule = CENT,
) -> ShortTermRentalNonCompliantCcaLine:
    return ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA,
        position,
        D(class_number),
        D(related_cca),
        non_compliant_days,
        days,
        rounding,
        D(result),
    )


def test_renders_one_non_compliant_cca_row_by_position() -> None:
    assert render(non_compliant_cca_row(1, "1", "900", 30, 90, "300.00")) == (
        "non_compliant_cca: row 1: class 1 CCA 900 for 30 non-compliant days of 90 "
        "short-term days = 300 (half-up to 0.01)"
    )


def test_renders_the_second_non_compliant_cca_row_of_another_class() -> None:
    assert render(non_compliant_cca_row(2, "10.1", "100", 1, 3, "33.33")) == (
        "non_compliant_cca: row 2: class 10.1 CCA 100 for 1 non-compliant days of 3 "
        "short-term days = 33.33 (half-up to 0.01)"
    )


def test_renders_a_non_compliant_cca_row_without_rounding() -> None:
    line = non_compliant_cca_row(3, "8", "0.015", 1, 2, "0.0075", rounding=NO_ROUNDING)

    assert render(line) == (
        "non_compliant_cca: row 3: class 8 CCA 0.015 for 1 non-compliant days of 2 "
        "short-term days = 0.0075 (no rounding)"
    )


def test_renders_the_non_compliant_cca_rows_figures_without_trailing_zeros_or_an_exponent() -> None:
    line = non_compliant_cca_row(1, "1.0", "9.0000E+2", 30, 90, "3.00000E+2")

    assert render(line) == (
        "non_compliant_cca: row 1: class 1 CCA 900 for 30 non-compliant days of 90 "
        "short-term days = 300 (half-up to 0.01)"
    )


# --- the column 22 total of one class of Chart B ---------------------------------------
#
# One sentence: the output's label, then "item <position> class <column 1>: column 7 " and the
# class's rounded column 7 amounts joined by " + ", then " = " and column 22.

NON_COMPLIANT_CCA_BY_CLASS = RecordListKind(
    "ex/non_compliant_cca_by_class", fields=(ArtifactKind("ex/column_22", Decimal),)
)


def non_compliant_cca_class(
    position: int, class_number: str, amounts: tuple[str, ...], result: str
) -> ShortTermRentalNonCompliantCcaByClassLine:
    return ShortTermRentalNonCompliantCcaByClassLine(
        NON_COMPLIANT_CCA_BY_CLASS,
        position,
        D(class_number),
        tuple(D(amount) for amount in amounts),
        D(result),
    )


def test_renders_a_class_of_one_row() -> None:
    line = non_compliant_cca_class(2, "8", ("250.00",), "250.00")

    assert render(line) == "non_compliant_cca_by_class: item 2 class 8: column 7 250 = 250"


def test_renders_a_class_of_two_rows_added() -> None:
    line = non_compliant_cca_class(1, "1", ("300.00", "33.33"), "333.33")

    assert render(line) == (
        "non_compliant_cca_by_class: item 1 class 1: column 7 300 + 33.33 = 333.33"
    )


def test_renders_a_decimal_class_number_and_figures_without_trailing_zeros() -> None:
    line = non_compliant_cca_class(1, "10.1", ("3.00000E+2", "0.50"), "3.005E+2")

    assert render(line) == (
        "non_compliant_cca_by_class: item 1 class 10.1: column 7 300 + 0.5 = 300.5"
    )


# --- a Form T776 addition of Area B or Area C -----------------------------------------------
#
# One sentence: the output's label, then "addition <position>: class <column 1> cost <column 3>
# less personal portion <column 4> = <column 5>". Every money figure prints without trailing zeros.


def rental_addition(
    output: ArtifactKind[Decimal],
    position: int,
    class_number: str,
    cost: str,
    personal: str,
    result: str,
) -> RentalAdditionLine:
    return RentalAdditionLine(output, position, D(class_number), D(cost), D(personal), D(result))


def test_renders_an_equipment_addition_with_no_personal_portion() -> None:
    line = rental_addition(RENTAL_EQUIPMENT_ADDITIONS_TOTAL, 1, "8", "1000", "0", "1000")

    assert render(line) == (
        "rental_equipment_additions_total: addition 1: class 8 cost 1000 less personal portion 0 "
        "= 1000"
    )


def test_renders_an_addition_less_its_personal_portion() -> None:
    line = rental_addition(RENTAL_EQUIPMENT_ADDITIONS_TOTAL, 2, "50", "1000", "250", "750")

    assert render(line) == (
        "rental_equipment_additions_total: addition 2: class 50 cost 1000 less personal portion "
        "250 = 750"
    )


def test_renders_a_building_addition() -> None:
    line = rental_addition(RENTAL_BUILDING_ADDITIONS_TOTAL, 1, "1", "300000", "0", "300000")

    assert render(line) == (
        "rental_building_additions_total: addition 1: class 1 cost 300000 less personal portion 0 "
        "= 300000"
    )


def test_renders_the_addition_figures_without_trailing_zeros_or_an_exponent() -> None:
    line = rental_addition(RENTAL_EQUIPMENT_ADDITIONS_TOTAL, 1, "8.0", "1.000E+3", "2.50", "997.50")

    assert render(line) == (
        "rental_equipment_additions_total: addition 1: class 8 cost 1000 less personal portion 2.5 "
        "= 997.5"
    )


# --- an amount transferred per dependant ----------------------------
#
# One sentence: the output's label, then "dependant <position>: " (from 1), the age group
# ("under 18" or "18 or older") and one clause per step of the worksheet, joined by "; ". A
# dependant under 18 starts with "care expenses <line 3> less threshold <line 4> = <line 5>" and
# "supplement <line 2> less <line 5> = <line 6>"; one 18 or older has those two clauses left out,
# as the form completes only lines 7 to 13 for them. Then "base <line 1> + <line 7>, at most
# <maximum> = <line 8>", "<line 8> + credit amounts <line 9> less taxable income <line 11> =
# <line 12>" and "the lesser of <line 8> and <line 12> = <line 13>" with the rounding rule in
# brackets. Every figure prints without trailing zeros.


def disability_transfer(
    position: int,
    under_18: int,
    figures: tuple[str, ...],
    rounding: RoundingRule = CENT,
) -> DisabilityTransferLine:
    """`figures` are, in the order of the line's fields, line 3 (care expenses), lines 5 to 8,
    line 9 (credit amounts), line 10, line 11 (taxable income), line 12 and the result."""
    care, line_5, line_6, line_7, line_8, credits, line_10, taxable, line_12, result = figures
    return DisabilityTransferLine(
        TRANSFERRED_AMOUNT,
        position,
        Amount(D("10138.00")),
        Amount(D("5914.00")),
        Amount(D("3464.00")),
        Amount(D("16052")),
        under_18,
        D(care),
        D(line_5),
        D(line_6),
        D(line_7),
        D(line_8),
        D(credits),
        D(line_10),
        D(taxable),
        D(line_12),
        rounding,
        D(result),
    )


def test_renders_the_transfer_for_a_dependant_aged_18_or_older() -> None:
    # The ticket's worked example: line 8 10,138.00, line 12 = 10,138.00 + 16,129 - 20,000.
    line = disability_transfer(
        1,
        0,
        ("0", "0", "5914.00", "0", "10138.00", "16129", "26267.00", "20000", "6267.00", "6267.00"),
    )

    assert render(line) == (
        "transferred_amount: dependant 1: 18 or older: base 10138 + 0, at most 16052 = 10138; "
        "10138 + credit amounts 16129 less taxable income 20000 = 6267; "
        "the lesser of 10138 and 6267 = 6267 (half-up to 0.01)"
    )


def test_renders_the_transfer_for_a_dependant_under_18() -> None:
    line = disability_transfer(
        2,
        1,
        (
            "5000",
            "1536.00",
            "4378.00",
            "4378.00",
            "14516.00",
            "0",
            "14516.00",
            "0",
            "14516.00",
            "14516.00",
        ),
    )

    assert render(line) == (
        "transferred_amount: dependant 2: under 18: care expenses 5000 less threshold 3464 = 1536; "
        "supplement 5914 less 1536 = 4378; base 10138 + 4378, at most 16052 = 14516; "
        "14516 + credit amounts 0 less taxable income 0 = 14516; "
        "the lesser of 14516 and 14516 = 14516 (half-up to 0.01)"
    )


def test_renders_a_dependant_under_18_whose_care_expenses_are_below_the_threshold() -> None:
    # Line 5 is "0" (line 3 minus line 4 is negative), line 6 the whole supplement.
    line = disability_transfer(
        1,
        1,
        (
            "1000",
            "0",
            "5914.00",
            "5914.00",
            "16052.00",
            "0",
            "16052.00",
            "0",
            "16052.00",
            "16052.00",
        ),
    )

    assert render(line) == (
        "transferred_amount: dependant 1: under 18: care expenses 1000 less threshold 3464 = 0; "
        "supplement 5914 less 0 = 5914; base 10138 + 5914, at most 16052 = 16052; "
        "16052 + credit amounts 0 less taxable income 0 = 16052; "
        "the lesser of 16052 and 16052 = 16052 (half-up to 0.01)"
    )


def test_renders_a_dependant_with_nothing_transferable() -> None:
    # Line 12 is "0" (line 10 minus line 11 is negative).
    line = disability_transfer(
        3, 0, ("0", "0", "5914.00", "0", "10138.00", "0", "10138.00", "20000", "0", "0.00")
    )

    assert render(line) == (
        "transferred_amount: dependant 3: 18 or older: base 10138 + 0, at most 16052 = 10138; "
        "10138 + credit amounts 0 less taxable income 20000 = 0; "
        "the lesser of 10138 and 0 = 0 (half-up to 0.01)"
    )


def test_renders_a_dependants_transfer_with_cents_and_the_rounding_rule() -> None:
    line = disability_transfer(
        1,
        0,
        (
            "0",
            "0",
            "5914.00",
            "0",
            "10138.00",
            "16129",
            "26267.00",
            "20000.005",
            "6266.995",
            "6267.00",
        ),
    )

    assert render(line) == (
        "transferred_amount: dependant 1: 18 or older: base 10138 + 0, at most 16052 = 10138; "
        "10138 + credit amounts 16129 less taxable income 20000.005 = 6266.995; "
        "the lesser of 10138 and 6266.995 = 6267 (half-up to 0.01)"
    )


def test_renders_a_dependants_transfer_without_rounding() -> None:
    line = disability_transfer(
        1,
        0,
        (
            "0",
            "0",
            "5914.00",
            "0",
            "10138.00",
            "16129",
            "26267.00",
            "20000.005",
            "6266.995",
            "6266.995",
        ),
        NO_ROUNDING,
    )

    assert render(line).endswith("the lesser of 10138 and 6266.995 = 6266.995 (no rounding)")


def test_renders_the_total_of_the_transfers_by_position() -> None:
    line = ItemsTotalLine(
        TRANSFERRED_AMOUNT, ((1, D("6267.00")), (2, D("14516.00"))), D("20783.00")
    )

    assert render(line) == "transferred_amount: item 1 6267 + item 2 14516 = 20783"


def test_renders_the_total_of_no_dependants() -> None:
    assert render(ItemsTotalLine(TRANSFERRED_AMOUNT, (), D("0"))) == (
        "transferred_amount: no items = 0"
    )


# --- a residence gain per property ----------------------------
#
# One sentence: the output's label, then "property <position>: gain <gain> = proceeds <p> less
# adjusted cost base <a> less outlays <o>; exempt <exempt> = <gain> × (<designated> designated +
# <plus one>) ÷ <owned> owned (<rounding rule>); taxable gain <result> = <gain> less <exempt>, not
# below 0". Every figure prints without trailing zeros.


def residence_gain(
    position: int,
    designated: int,
    owned: int,
    plus_one: int,
    figures: tuple[str, ...],
    rounding: RoundingRule = CENT,
) -> PrincipalResidenceGainLine:
    """`figures` are, in the order of the line's fields, proceeds, adjusted cost base, outlays, the
    gain, line 21, the exemption and the result; the property does not use Part 2."""
    proceeds, cost_base, outlays, gain, line_21, exempt, result = figures
    return PrincipalResidenceGainLine(
        output=RESIDENCE_GAIN,
        position=position,
        years_designated_after_1981=designated,
        years_designated_1972_to_1981=0,
        designated=designated,
        years_owned_after_1981=owned,
        years_owned_1972_to_1981=0,
        owned=owned,
        plus_one=plus_one,
        proceeds=D(proceeds),
        adjusted_cost_base=D(cost_base),
        outlays=D(outlays),
        gain=D(gain),
        line_20=designated + plus_one,
        line_21=D(line_21),
        rounding=rounding,
        exempt=D(exempt),
        part_2_applies=0,
        line_53=D("0"),
        line_24=D(result),
        result=D(result),
    )


def residence_gain_part_2(
    position: int,
    designated: int,
    owned: int,
    plus_one: int,
    figures: tuple[str, ...],
) -> PrincipalResidenceGainLine:
    """A property that uses Part 2. `figures` are the gain-line figures of `residence_gain`, then
    line 24, line 53 and the result (line 54)."""
    proceeds, cost_base, outlays, gain, line_21, exempt, line_24, line_53, result = figures
    return PrincipalResidenceGainLine(
        output=RESIDENCE_GAIN,
        position=position,
        years_designated_after_1981=designated,
        years_designated_1972_to_1981=0,
        designated=designated,
        years_owned_after_1981=owned,
        years_owned_1972_to_1981=0,
        owned=owned,
        plus_one=plus_one,
        proceeds=D(proceeds),
        adjusted_cost_base=D(cost_base),
        outlays=D(outlays),
        gain=D(gain),
        line_20=designated + plus_one,
        line_21=D(line_21),
        rounding=CENT,
        exempt=D(exempt),
        part_2_applies=1,
        line_53=D(line_53),
        line_24=D(line_24),
        result=D(result),
    )


def test_renders_the_gain_left_on_a_property() -> None:
    # The ticket's worked example.
    line = residence_gain(
        1,
        6,
        10,
        1,
        ("400000.00", "95000.00", "5000.00", "300000.00", "2100000.00", "210000.00", "90000.00"),
    )

    assert render(line) == (
        "residence_gain: property 1: gain 300000 = proceeds 400000 less adjusted cost base 95000 "
        "less outlays 5000; exempt 210000 = 300000 × (6 designated + 1) ÷ 10 owned "
        "(half-up to 0.01); taxable gain 90000 = 300000 less 210000, not below 0"
    )


def test_renders_a_property_without_the_plus_one() -> None:
    line = residence_gain(
        2,
        3,
        5,
        0,
        ("250000.00", "200000.00", "10000.00", "40000.00", "120000.00", "24000.00", "16000.00"),
    )

    assert render(line) == (
        "residence_gain: property 2: gain 40000 = proceeds 250000 less adjusted cost base 200000 "
        "less outlays 10000; exempt 24000 = 40000 × (3 designated + 0) ÷ 5 owned "
        "(half-up to 0.01); taxable gain 16000 = 40000 less 24000, not below 0"
    )


def test_renders_a_part_2_property_taking_line_24_as_the_lesser() -> None:
    # The worked example: line 53 is 103,000.00 and line 24 is 83,571.43, so line 54 is line 24.
    line = residence_gain_part_2(
        1,
        7,
        14,
        1,
        (
            "300000.00",
            "100000.00",
            "5000.00",
            "195000.00",
            "1560000.00",
            "111428.57",
            "83571.43",
            "103000.00",
            "83571.43",
        ),
    )

    assert render(line) == (
        "residence_gain: property 1: gain 195000 = proceeds 300000 less adjusted cost base 100000 "
        "less outlays 5000; exempt 111428.57 = 195000 × (7 designated + 1) ÷ 14 owned "
        "(half-up to 0.01); taxable gain 83571.43 = 195000 less 111428.57, not below 0; "
        "Part 2 net capital gain 103000; total capital gain 83571.43 = lesser of 103000 and "
        "83571.43"
    )


def test_renders_a_part_2_property_taking_line_53_as_the_lesser() -> None:
    line = residence_gain_part_2(
        2,
        4,
        12,
        0,
        (
            "300000.00",
            "100000.00",
            "0.00",
            "200000.00",
            "800000.00",
            "66666.67",
            "133333.33",
            "16000.00",
            "16000.00",
        ),
    )

    assert render(line) == (
        "residence_gain: property 2: gain 200000 = proceeds 300000 less adjusted cost base 100000 "
        "less outlays 0; exempt 66666.67 = 200000 × (4 designated + 0) ÷ 12 owned "
        "(half-up to 0.01); taxable gain 133333.33 = 200000 less 66666.67, not below 0; "
        "Part 2 net capital gain 16000; total capital gain 16000 = lesser of 16000 and "
        "133333.33"
    )


def test_renders_a_property_whose_exemption_exceeds_the_gain() -> None:
    # The gain left is "0" (line 18 minus line 23 is negative).
    line = residence_gain(
        3,
        10,
        10,
        1,
        ("400000.00", "95000.00", "5000.00", "300000.00", "3300000.00", "330000.00", "0.00"),
    )

    assert render(line) == (
        "residence_gain: property 3: gain 300000 = proceeds 400000 less adjusted cost base 95000 "
        "less outlays 5000; exempt 330000 = 300000 × (10 designated + 1) ÷ 10 owned "
        "(half-up to 0.01); taxable gain 0 = 300000 less 330000, not below 0"
    )


def test_renders_a_property_sold_at_a_loss() -> None:
    line = residence_gain(
        1,
        6,
        10,
        1,
        ("100000.00", "120000.00", "5000.00", "-25000.00", "-175000.00", "-17500.00", "0.00"),
    )

    assert render(line) == (
        "residence_gain: property 1: gain -25000 = proceeds 100000 less adjusted cost base 120000 "
        "less outlays 5000; exempt -17500 = -25000 × (6 designated + 1) ÷ 10 owned "
        "(half-up to 0.01); taxable gain 0 = -25000 less -17500, not below 0"
    )


def test_renders_a_property_with_cents_and_the_rounding_rule() -> None:
    line = residence_gain(1, 0, 8, 1, ("1.00", "0.00", "0.00", "1.00", "1.00", "0.13", "0.87"))

    assert render(line) == (
        "residence_gain: property 1: gain 1 = proceeds 1 less adjusted cost base 0 "
        "less outlays 0; exempt 0.13 = 1 × (0 designated + 1) ÷ 8 owned "
        "(half-up to 0.01); taxable gain 0.87 = 1 less 0.13, not below 0"
    )


def test_renders_a_property_without_rounding() -> None:
    line = residence_gain(
        1, 0, 8, 1, ("1.00", "0.00", "0.00", "1.00", "1.00", "0.125", "0.875"), NO_ROUNDING
    )

    assert render(line).endswith(
        "exempt 0.125 = 1 × (0 designated + 1) ÷ 8 owned (no rounding); "
        "taxable gain 0.875 = 1 less 0.125, not below 0"
    )


def test_renders_the_total_of_the_gains_by_position() -> None:
    line = ItemsTotalLine(RESIDENCE_GAIN, ((1, D("90000.00")), (2, D("16000.00"))), D("106000.00"))

    assert render(line) == "residence_gain: item 1 90000 + item 2 16000 = 106000"


def test_renders_the_total_of_no_properties() -> None:
    assert render(ItemsTotalLine(RESIDENCE_GAIN, (), D("0"))) == "residence_gain: no items = 0"


# --- disposition gains (Schedule 3 Part 3) ----------------------------------------------------
#
# One line per row: the output's label, "disposition <position>", the gain or loss as column 2
# less columns 3 and 4; a loss prints with its minus sign. The gain-only line adds the figure
# counted, a loss counting 0. Every figure prints without trailing zeros.

DISPOSITION_GAINS = ArtifactKind("ex/share_gain_or_loss", Decimal)


def test_renders_a_gain_row() -> None:
    line = DispositionGainLine(
        DISPOSITION_GAINS, 1, D("1500.00"), D("1000.00"), D("50.00"), D("450.00")
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 1: gain or loss 450 = proceeds 1500 less adjusted cost "
        "base 1000 less outlays 50"
    )


def test_renders_a_loss_row_with_its_minus_sign() -> None:
    line = DispositionGainLine(
        DISPOSITION_GAINS, 2, D("800.00"), D("1000.00"), D("30.00"), D("-230.00")
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 2: gain or loss -230 = proceeds 800 less adjusted cost "
        "base 1000 less outlays 30"
    )


def test_renders_a_gain_only_row_counting_a_gain() -> None:
    line = DispositionGainOnlyLine(
        DISPOSITION_GAINS, 1, D("1500.00"), D("1000.00"), D("50.00"), D("450.00"), D("450.00")
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 1: gain 450 = proceeds 1500 less adjusted cost base "
        "1000 less outlays 50; gain only 450, not below 0"
    )


def test_renders_a_gain_only_row_counting_a_loss_as_0() -> None:
    line = DispositionGainOnlyLine(
        DISPOSITION_GAINS, 2, D("800.00"), D("1000.00"), D("30.00"), D("-230.00"), D("0")
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 2: gain -230 = proceeds 800 less adjusted cost base "
        "1000 less outlays 30; gain only 0, not below 0"
    )


def test_renders_a_depreciable_property_row_counting_a_gain() -> None:
    line = DepreciablePropertyGainLine(
        DISPOSITION_GAINS,
        3,
        D("12000"),
        D("10000"),
        D("0"),
        D("0"),
        D("0"),
        D("0"),
        1,
        D("2000"),
        D("2000"),
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 3: gain 2000 = proceeds 12000 less adjusted cost base "
        "10000 less outlays 0; depreciable property: a loss counts 0 -> 2000"
    )


def test_renders_a_depreciable_property_row_counting_a_loss_as_0() -> None:
    line = DepreciablePropertyGainLine(
        DISPOSITION_GAINS,
        1,
        D("4000"),
        D("10000"),
        D("0"),
        D("0"),
        D("0"),
        D("0"),
        1,
        D("-6000"),
        D("0"),
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 1: gain -6000 = proceeds 4000 less adjusted cost base "
        "10000 less outlays 0; depreciable property: a loss counts 0 -> 0"
    )


def test_renders_an_ordinary_property_row_counting_its_loss_without_the_clause() -> None:
    line = DepreciablePropertyGainLine(
        DISPOSITION_GAINS,
        4,
        D("9500"),
        D("10000"),
        D("0"),
        D("0"),
        D("0"),
        D("0"),
        0,
        D("-500"),
        D("-500"),
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 4: gain -500 = proceeds 9500 less adjusted cost base "
        "10000 less outlays 0"
    )


def test_renders_a_row_with_a_restricted_farm_loss_applied() -> None:
    line = DepreciablePropertyGainLine(
        DISPOSITION_GAINS,
        1,
        D("200000"),
        D("160000"),
        D("0"),
        D("5000"),
        D("5000"),
        D("10000"),
        0,
        D("30000"),
        D("30000"),
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 1: gain 30000 = proceeds 200000 less adjusted cost base "
        "160000 less outlays 0 less restricted farm loss applied 10000 (property taxes 5000 plus "
        "interest 5000)"
    )


def test_renders_a_qffp_row_without_a_farm_loss() -> None:
    line = QffpGainLine(
        DISPOSITION_GAINS, 1, D("800"), D("1000"), D("30"), D("0"), D("0"), D("0"), D("-230")
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 1: gain or loss -230 = proceeds 800 less adjusted cost "
        "base 1000 less outlays 30"
    )


def test_renders_a_qffp_row_with_a_restricted_farm_loss_applied() -> None:
    line = QffpGainLine(
        DISPOSITION_GAINS,
        2,
        D("200000"),
        D("160000"),
        D("0"),
        D("5000"),
        D("5000"),
        D("10000"),
        D("30000"),
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 2: gain or loss 30000 = proceeds 200000 less adjusted "
        "cost base 160000 less outlays 0 less restricted farm loss applied 10000 (property taxes "
        "5000 plus interest 5000)"
    )


def test_renders_a_farm_loss_applied_row() -> None:
    line = FarmLossAppliedLine(DISPOSITION_GAINS, 2, D("5000"), D("5000"), D("10000"))

    assert render(line) == (
        "share_gain_or_loss: disposition 2: restricted farm loss applied 10000 = property taxes "
        "5000 plus interest 5000"
    )


def test_renders_a_farm_loss_applied_row_with_nothing_applied() -> None:
    line = FarmLossAppliedLine(DISPOSITION_GAINS, 1, D("0"), D("0"), D("0"))

    assert render(line) == (
        "share_gain_or_loss: disposition 1: restricted farm loss applied 0 = property taxes 0 "
        "plus interest 0"
    )


def test_renders_a_personal_use_property_row_with_the_minimum_applied() -> None:
    line = PersonalUsePropertyGainLine(
        DISPOSITION_GAINS,
        2,
        D("1200.00"),
        D("850.00"),
        D("50.00"),
        D("1000"),
        D("1200.00"),
        D("1000"),
        D("150.00"),
        D("150.00"),
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 2: gain 150 = proceeds 1200 (greater of 1200 and minimum "
        "1000) less adjusted cost base 1000 (greater of 850 and minimum 1000) less outlays 50; "
        "gain only 150, not below 0"
    )


def test_renders_a_personal_use_property_row_raised_to_the_minimum_as_0() -> None:
    # Guide T4037 p.24: the China cabinet, proceeds 900 and ACB 500, both raised to $1,000.
    line = PersonalUsePropertyGainLine(
        DISPOSITION_GAINS,
        1,
        D("900.00"),
        D("500.00"),
        D("0.00"),
        D("1000"),
        D("1000"),
        D("1000"),
        D("0"),
        D("0"),
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 1: gain 0 = proceeds 1000 (greater of 900 and minimum "
        "1000) less adjusted cost base 1000 (greater of 500 and minimum 1000) less outlays 0; "
        "gain only 0, not below 0"
    )


def test_renders_a_personal_use_property_loss_row_as_0() -> None:
    line = PersonalUsePropertyGainLine(
        DISPOSITION_GAINS,
        3,
        D("1500.00"),
        D("3200.00"),
        D("30.00"),
        D("1000"),
        D("1500.00"),
        D("3200.00"),
        D("-1730.00"),
        D("0"),
    )

    assert render(line) == (
        "share_gain_or_loss: disposition 3: gain -1730 = proceeds 1500 (greater of 1500 and "
        "minimum 1000) less adjusted cost base 3200 (greater of 3200 and minimum 1000) less "
        "outlays 30; gain only 0, not below 0"
    )


def test_renders_a_proceeds_row() -> None:
    line = DispositionProceedsLine(DISPOSITION_GAINS, 2, D("800.00"))

    assert render(line) == "share_gain_or_loss: disposition 2: proceeds 800"


NET_CAPITAL_LOSSES_TOTAL = ArtifactKind("ex/chart_1_column_g_total", Decimal)


def test_renders_a_chart_1_row_with_columns_e_f_and_g() -> None:
    # Form T657 Chart 1, the 1992 row: column E is C less D, F is B plus E, G is A less F.
    line = NetCapitalLossesRowLine(
        NET_CAPITAL_LOSSES_TOTAL,
        2,
        D("5000.00"),
        D("0"),
        D("4000.00"),
        D("1500.00"),
        D("2500.00"),
        D("2500.00"),
        D("2500.00"),
    )

    assert render(line) == (
        "chart_1_column_g_total: item 2: column E 2500 = column C 4000 less column D 1500, not "
        "below 0; column F 2500 = column B 0 plus column E 2500; column G 2500 = column A 5000 "
        "less column F 2500, not below 0"
    )


def test_renders_a_chart_1_row_whose_columns_floor_at_0() -> None:
    line = NetCapitalLossesRowLine(
        NET_CAPITAL_LOSSES_TOTAL,
        1,
        D("1000"),
        D("0"),
        D("300"),
        D("500"),
        D("0"),
        D("0"),
        D("1000"),
    )

    assert render(line) == (
        "chart_1_column_g_total: item 1: column E 0 = column C 300 less column D 500, not below "
        "0; column F 0 = column B 0 plus column E 0; column G 1000 = column A 1000 less column F "
        "0, not below 0"
    )


def test_renders_the_total_of_the_dispositions_by_position() -> None:
    line = ItemsTotalLine(DISPOSITION_GAINS, ((1, D("450.00")), (2, D("-230.00"))), D("220.00"))

    assert render(line) == "share_gain_or_loss: item 1 450 + item 2 -230 = 220"


# --- conditions ----------------------------
#
# One line for each condition: the output's label, "condition <position>", the printed text in
# double quotes, the figures read (each kind's label and value, a count as a whole number, an
# amount like any money figure, in the order read, separated by ", "), then "applies" or "does not
# apply". The total line names the positions that applied ("condition 3 applies", "conditions 2, 3
# apply", "no condition applies") and the count: ", so <count>".

CONDITION_GATE = ArtifactKind("ex/tax_reduction_gate", int)
CONDITION_FLAG = ArtifactKind("ex/bankrupt_flag", int)
CONDITION_LINE_72 = ArtifactKind("ex/amount_on_line_72", Decimal)
CONDITION_OTHER = ArtifactKind("ex/other_income", Decimal)


def test_renders_a_condition_on_a_count_that_applies() -> None:
    line = ConditionLine(
        CONDITION_GATE,
        3,
        "You were bankrupt at any time in 2025",
        ((CONDITION_FLAG, 1),),
        True,
    )

    assert render(line) == (
        'tax_reduction_gate: condition 3 "You were bankrupt at any time in 2025": '
        "bankrupt_flag 1, applies"
    )


def test_renders_a_condition_on_an_amount_that_does_not_apply() -> None:
    line = ConditionLine(
        CONDITION_GATE,
        2,
        "There is an amount on line 72",
        ((CONDITION_LINE_72, D("0.00")),),
        False,
    )

    assert render(line) == (
        'tax_reduction_gate: condition 2 "There is an amount on line 72": '
        "amount_on_line_72 0, does not apply"
    )


def test_renders_a_condition_that_reads_several_figures_in_the_order_read() -> None:
    line = ConditionLine(
        CONDITION_GATE,
        1,
        "first",
        ((CONDITION_FLAG, 0), (CONDITION_LINE_72, D("82125.50")), (CONDITION_OTHER, D("1E+3"))),
        True,
    )

    assert render(line) == (
        'tax_reduction_gate: condition 1 "first": '
        "bankrupt_flag 0, amount_on_line_72 82125.5, other_income 1000, applies"
    )


def test_renders_the_conditions_total_when_one_applies() -> None:
    assert render(ConditionsCountLine(CONDITION_GATE, (3,), 0)) == (
        "tax_reduction_gate: condition 3 applies, so 0"
    )


def test_renders_the_conditions_total_when_several_apply() -> None:
    assert render(ConditionsCountLine(CONDITION_GATE, (2, 3), 0)) == (
        "tax_reduction_gate: conditions 2, 3 apply, so 0"
    )


def test_renders_the_conditions_total_when_none_applies() -> None:
    assert render(ConditionsCountLine(CONDITION_GATE, (), 1)) == (
        "tax_reduction_gate: no condition applies, so 1"
    )


def test_renders_a_condition_without_a_namespace_in_any_label() -> None:
    line = ConditionLine(CONDITION_GATE, 1, "text", ((CONDITION_FLAG, 1),), False)

    assert "ex/" not in render(line)


# --- a percentage of an artifact applied ----------------------------
#
# The percentage prints as entered, with its label, then the amount, then the result and the
# rounding rule in parentheses.


ELECTED_PERCENTAGE = ArtifactKind("ex/elected_percentage", Decimal)


def test_renders_a_percentage_applied_rounded() -> None:
    line = PercentageAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("600000"),
        ELECTED_PERCENTAGE,
        D("50"),
        CENT,
        D("300000"),
    )

    assert render(line) == (
        "credit_share: elected_percentage 50% of tax_payable 600000 = 300000 (half-up to 0.01)"
    )


def test_renders_a_percentage_applied_without_rounding() -> None:
    line = PercentageAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("14000"),
        ELECTED_PERCENTAGE,
        D("10"),
        NO_ROUNDING,
        D("1400"),
    )

    assert render(line) == (
        "credit_share: elected_percentage 10% of tax_payable 14000 = 1400 (no rounding)"
    )


def test_renders_a_negative_percentage_applied_with_every_digit() -> None:
    line = PercentageAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("-250.75"),
        ELECTED_PERCENTAGE,
        D("1.5"),
        NO_ROUNDING,
        D("-3.76125"),
    )

    assert render(line) == (
        "credit_share: elected_percentage 1.5% of tax_payable -250.75 = -3.76125 (no rounding)"
    )


# --- a ratio of two artifacts applied ----------------------------
#
# The amount, the numerator and the denominator print with their labels and values, and the rounding
# rule in parentheses; the result is the line's amount, not printed twice.


def test_renders_a_ratio_applied_without_rounding() -> None:
    line = RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("14000"),
        FOREIGN_INCOME,
        D("10000"),
        WORLD_INCOME,
        D("100000"),
        NO_ROUNDING,
        D("1400"),
    )

    assert render(line) == (
        "credit_share: tax_payable 14000 × foreign_income 10000 / worldwide_income 100000 "
        "(no rounding)"
    )


def test_renders_a_rounded_ratio_applied() -> None:
    line = RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("1000"),
        FOREIGN_INCOME,
        D("1"),
        WORLD_INCOME,
        D("3"),
        CENT,
        D("333.33"),
    )

    assert render(line) == (
        "credit_share: tax_payable 1000 × foreign_income 1 / worldwide_income 3 (half-up to 0.01)"
    )


def test_renders_a_negative_ratio_applied_with_every_digit() -> None:
    line = RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("-250.75"),
        FOREIGN_INCOME,
        D("1.5"),
        WORLD_INCOME,
        D("0.5"),
        NO_ROUNDING,
        D("-752.25"),
    )

    assert render(line) == (
        "credit_share: tax_payable -250.75 × foreign_income 1.5 / worldwide_income 0.5 "
        "(no rounding)"
    )


# --- money figures ----------------------------


@pytest.mark.parametrize(
    ("figure", "text"),
    [
        (D("20146.2500"), "20146.25"),
        (D("115000.00"), "115000"),
        (D("0.00"), "0"),
        (D("8539.5965"), "8539.5965"),
        (D("1.15E+5"), "115000"),
        (D("115000"), "115000"),
        (D("-15.50"), "-15.5"),
        # Longer than the Decimal context precision: the text still shows every digit.
        (D("1234567890123456789012345678.95"), "1234567890123456789012345678.95"),
    ],
)
def test_renders_a_money_figure_without_trailing_zeros_or_an_exponent(
    figure: Decimal, text: str
) -> None:
    line = SumLine(TOTAL, ((PART_ONE, figure),), figure)

    assert render(line) == f"total: part_one {text} = {text}"


@pytest.mark.parametrize(
    ("line", "text"),
    [
        (
            BracketColumnLine(D("100.00"), D("0.20"), D("150.00"), D("10.00"), D("40.00")),
            "20% on 150 over 100 plus 10",
        ),
        (
            BracketColumnLine(D("3E+2"), D("0.30"), D("1.0E+2"), D("5.0E+1"), D("80.0")),
            "30% on 100 over 300 plus 50",
        ),
        (
            RoundedTotalLine(BASIC_TAX, TAXABLE_BASE, D("250.00"), CENT, D("40.00")),
            "basic_tax on taxable_base 250 (half-up to 0.01)",
        ),
        (
            CreditAmountLine(PERSONAL_AMOUNT, Credit(D("1000.50")), NO_ROUNDING, D("1000.50")),
            "personal_amount: credit amount 1000.5 (no rounding)",
        ),
        (
            SumLine(TOTAL, ((PART_ONE, D("100.250")), (PART_TWO, D("4E+1"))), D("140.250")),
            "total: part_one 100.25 + part_two 40 = 140.25",
        ),
        (
            RateAppliedLine(
                RATED_AMOUNT, GROSS_AMOUNT, D("1000.00"), Rate(D("0.5")), NO_ROUNDING, D("500.000")
            ),
            "rated_amount: 50% of gross_amount 1000 (no rounding)",
        ),
        (
            DividedByRateLine(
                RATED_AMOUNT, GROSS_AMOUNT, D("3795.00"), Rate(D("0.145")), CENT, D("26172.410")
            ),
            "rated_amount: gross_amount 3795 divided by 14.5% (half-up to 0.01) = 26172.41",
        ),
        (
            SignChosenDifferenceLine(
                NET_AMOUNT,
                GROSS_AMOUNT,
                D("-100.00"),
                REDUCTION,
                D("30.00"),
                RATED_AMOUNT,
                D("130.00"),
                D("-30.00"),
            ),
            "net_amount: gross_amount -100 is negative, lesser of reduction 30 and "
            "rated_amount 130, as a negative = -30",
        ),
        (
            SubtractedLine(
                NET_AMOUNT, GROSS_AMOUNT, D("100.250"), REDUCTION, D("40.00"), D("60.250")
            ),
            "net_amount: gross_amount 100.25 less reduction 40 = 60.25",
        ),
        (
            SubtractedNotBelowZeroLine(
                NET_AMOUNT, GROSS_AMOUNT, D("100.250"), REDUCTION, D("4.0E+1"), D("60.250")
            ),
            "net_amount: gross_amount 100.25 less reduction 40, not below 0 = 60.25",
        ),
        (
            CappedAmountLine(
                CAPPED_AMOUNT,
                GROSS_AMOUNT,
                D("1500.2500"),
                Amount(D("1471.50")),
                NO_ROUNDING,
                D("1471.50"),
            ),
            "capped_amount: lesser of gross_amount 1500.25 and 1471.5 (no rounding)",
        ),
        (
            LesserOfLine(
                LESSER_AMOUNT, ((PART_ONE, D("1500.2500")), (PART_TWO, D("1E+3"))), D("1E+3")
            ),
            "lesser_amount: lesser of part_one 1500.25 and part_two 1000 = 1000",
        ),
        (
            LesserOfWithMaximumLine(
                LESSER_AMOUNT,
                ((PART_ONE, D("2500.00")), (PART_TWO, D("3E+3"))),
                Amount(D("2000.00")),
                NO_ROUNDING,
                D("2000.00"),
            ),
            "lesser_amount: lesser of part_one 2500 and part_two 3000 and 2000 (no rounding)"
            " = 2000",
        ),
        (
            GreaterOfLine(
                GREATER_AMOUNT, ((PART_ONE, D("1500.2500")), (PART_TWO, D("1E+3"))), D("1500.2500")
            ),
            "greater_amount: greater of part_one 1500.25 and part_two 1000 = 1500.25",
        ),
        (
            ContributionTierLine(
                CONTRIBUTION,
                EARNINGS,
                D("23000.00"),
                ContributionTier(Rate(D("0.05")), D("3.0E+3"), D("50000.00"), D("2350.50")),
                NO_ROUNDING,
                D("2.00E+4"),
                D("1000.000"),
            ),
            "contribution: 5% of earnings between 3000 and 50000 (20000), at most 2350.5 "
            "(no rounding)",
        ),
        (
            SurchargeTierLine(
                SURCHARGE,
                TAX_SO_FAR,
                D("400.50"),
                D("3E+2"),
                Rate(D("0.25")),
                NO_ROUNDING,
                D("25.125"),
            ),
            "surcharge: 25% of tax_so_far 400.5 over 300 (no rounding)",
        ),
        (
            TaperedAmountLine(
                PERSONAL_AMOUNT,
                INCOME,
                D("22000.50"),
                Taper(D("1000.00"), D("5.0E+2"), D("20000.00"), D("1E+4")),
                NO_ROUNDING,
                ExactFraction("100.025"),
                D("1399.9750"),
            ),
            "personal_amount: 1000 plus 500 less 100.025 for income 22000.5 over 20000 "
            "(range 10000), not below 1000 (no rounding)",
        ),
        (
            PerUnitAmountLine(
                CHILD_AMOUNT, CHILDREN, 2, Amount(D("544.00")), NO_ROUNDING, D("1088.00")
            ),
            "child_amount: 544 for each of 2 child_count = 1088 (no rounding)",
        ),
        (
            MultipleOverLine(
                REDUCTION,
                REDUCTION_AMOUNTS,
                D("294.00"),
                Factor(D("2.0")),
                TAX_SO_FAR,
                D("1.000E+2"),
                NO_ROUNDING,
                D("488.00"),
            ),
            "reduction: 2 × reduction_amounts 294 over tax_so_far 100, not below 0 (no rounding)",
        ),
        (
            AtMostLine(ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("1926.00"), CLAIM_LIMIT, D("1.9260E+3")),
            "allowed_amount: claimed_amount 1926, at most claim_limit 1926",
        ),
        (
            ClaimAtMostLine(
                ALLOWED_AMOUNT, CLAIMED_AMOUNT, D("0.00"), CLAIM_LIMIT, D("-9.5000E+3")
            ),
            "allowed_amount: claimed_amount 0, allowed because claim_limit -9500 is negative",
        ),
        (
            FractionAppliedLine(
                EARNED_PORTION,
                EARNED_INCOME,
                D("6.0000E+4"),
                Fraction(2, 3),
                NO_ROUNDING,
                D("40000.00"),
            ),
            "earned_portion: 2/3 of earned_income 60000 (no rounding)",
        ),
        (
            TimesCountLine(
                AMOUNT_CLAIMED, AMOUNT_EACH, D("1.612900E+4"), PERSONS, 2, D("32258.00")
            ),
            "amount_claimed: amount_each 16129 for each of 2 person_count = 32258",
        ),
        (
            CountAtLeastLine(PERSONS, CHILDREN, 3, DEPENDANTS, 2),
            "person_count: child_count 3, at least dependant_count 2",
        ),
        (
            CountAtMostLine(PERSONS, CHILDREN, 3, DEPENDANTS, 4),
            "person_count: child_count 3, at most dependant_count 4",
        ),
        (
            RatioTruncatedLine(
                RATED_AMOUNT_RATE,
                GROSS_AMOUNT,
                D("3.0000E+4"),
                TOTAL,
                D("70000.00"),
                FIVE_DECIMALS_DOWN,
                False,
                D("0.428570"),
            ),
            "rated_amount: gross_amount 30000 divided by total 70000 (down to 0.00001) = 0.42857",
        ),
        (
            PositivePartOfNegationLine(RATED_AMOUNT, NET_AMOUNT, D("-12.500"), D("12.500")),
            "rated_amount: negation of net_amount -12.5, not below 0 = 12.5",
        ),
        (
            LesserOfWhenPositiveLine(
                TOTAL,
                ((PART_ONE, D("1.500E+3")), (PART_TWO, D("750.50"))),
                True,
                True,
                D("-750.50"),
            ),
            "total: lesser of part_one 1500 and part_two 750.5, shown in brackets = -750.5",
        ),
        (
            ChosenBySignLine(AMOUNT_CHOSEN, GATE_AMOUNT, D("-3.0"), AMOUNT_ALONE, D("1633.00")),
            "amount_chosen: amount_alone 1633, chosen as gate_amount -3 is negative",
        ),
        (
            ChosenByCountLine(AMOUNT_CHOSEN, DEPENDANTS, 1, AMOUNT_WITH_FAMILY, D("4.31940E+3")),
            "amount_chosen: amount_with_family 4319.4, chosen as dependant_count is 1",
        ),
        (
            SumNotBelowZeroLine(
                TOTAL, ((PART_ONE, D("100.250")), (PART_TWO, D("4E+1"))), D("140.250")
            ),
            "total: part_one 100.25 + part_two 40, not below 0 = 140.25",
        ),
        (
            AmountByCountLine(MONTHLY_AMOUNT, MONTHS, 2, D("200.5000"), NO_ROUNDING, D("2.005E+2")),
            "monthly_amount: 200.5 for month_count 2 (no rounding)",
        ),
        (
            RecordTotalLine(TOTAL, ITEM_AMOUNT, (D("6000.00"), D("4E+3")), D("10000.00")),
            "total: item 1 item_amount 6000 + item 2 item_amount 4000 = 10000",
        ),
        (
            RecordPositiveTotalLine(TOTAL, ITEM_AMOUNT, (D("6000.00"), D("-4E+3")), D("6000.00")),
            "total: item 1 item_amount 6000 + item 2 item_amount -4000 counts 0 = 6000."
            " Only positive amounts are added; a zero or negative amount counts 0.",
        ),
        (
            ChosenByRangeLine(
                AMOUNT_CHOSEN, AMOUNT_TESTED, D("1.00000E+3"), AMOUNT_IN_RANGE, D("4.31940E+3")
            ),
            "amount_chosen: amount_in_range 4319.4, chosen as amount_tested is 1000",
        ),
        (
            RateByIncomeBandLine(
                BAND_RATE,
                FAMILY_INCOME,
                D("45500.00"),
                RateTableRow(D("4.5E+4"), D("50000.00"), Rate(D("0.550"))),
                Rate(D("0.550")),
            ),
            "band_rate: family_income 45500, more than 45000 but not more than 50000: 55%",
        ),
        (
            ChosenRateAppliedLine(
                CARE_CREDIT,
                CARE_EXPENSES,
                D("5.000E+3"),
                BAND_RATE,
                Rate(D("0.550")),
                NO_ROUNDING,
                D("2750.000"),
            ),
            "care_credit: band_rate 55% of care_expenses 5000 (no rounding)",
        ),
        (
            CaregiverClaimLine(
                CAREGIVER_AMOUNT,
                1,
                Amount(D("2.879800E+4")),
                D("5.000E+3"),
                Amount(D("8.601E+3")),
                CENT,
                D("8.60100E+3"),
            ),
            "caregiver_amount: dependant 1: 28798 less net income 5000, at most 8601 = 8601 "
            "(half-up to 0.01)",
        ),
        (
            CaregiverClaimLessClaimedLine(
                CAREGIVER_AMOUNT,
                1,
                Amount(D("2.656200E+4")),
                D("5.000E+3"),
                Amount(D("6.008E+3")),
                D("6.00800E+3"),
                D("2.50000E+3"),
                CENT,
                D("3.50800E+3"),
            ),
            "caregiver_amount: dependant 1: 26562 less net income 5000, at most 6008 = 6008, "
            "less claimed 2500 = 3508 (half-up to 0.01)",
        ),
        (
            ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("8.60100E+3")),), D("8.60100E+3")),
            "caregiver_amount: item 1 8601 = 8601",
        ),
    ],
)
def test_renders_every_money_figure_of_a_line_without_trailing_zeros(
    line: TraceLine, text: str
) -> None:
    assert render(line) == text


# --- whole traces and unknown lines ----------------------------


def test_render_all_renders_each_line_in_order() -> None:
    trace = (
        BracketColumnLine(D(0), D("0.10"), D(100), D(0), D("10.0")),
        RoundedTotalLine(BASIC_TAX, TAXABLE_BASE, D(100), NO_ROUNDING, D("10.0")),
        SumLine(TOTAL, ((PART_ONE, D("1")), (PART_TWO, D("2"))), D("3")),
        RateAppliedLine(RATED_AMOUNT, TOTAL, D("3"), Rate(D("0.5")), NO_ROUNDING, D("1.5")),
        SubtractedLine(NET_AMOUNT, TOTAL, D("3"), RATED_AMOUNT, D("1.5"), D("1.5")),
        SubtractedNotBelowZeroLine(TOTAL, RATED_AMOUNT, D("1.5"), PART_TWO, D("2"), D("0")),
        CreditAmountLine(PERSONAL_AMOUNT, Credit(D("1000")), NO_ROUNDING, D("1000")),
        CappedAmountLine(CAPPED_AMOUNT, TOTAL, D("3"), Amount(D("2")), NO_ROUNDING, D("2")),
        LesserOfLine(LESSER_AMOUNT, ((TOTAL, D("3")), (CAPPED_AMOUNT, D("2"))), D("2")),
        GreaterOfLine(GREATER_AMOUNT, ((TOTAL, D("3")), (CAPPED_AMOUNT, D("2"))), D("3")),
        ContributionTierLine(
            CONTRIBUTION, EARNINGS, D("23000"), TIER, NO_ROUNDING, D("20000"), D("1000")
        ),
        SurchargeTierLine(SURCHARGE, TOTAL, D("3"), D("1"), Rate(D("0.5")), NO_ROUNDING, D("1")),
        TaperedAmountLine(
            PERSONAL_AMOUNT, INCOME, D("22000"), TAPER, NO_ROUNDING, ExactFraction(100), D("1400")
        ),
        PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 2, Amount(D("544")), NO_ROUNDING, D("1088")),
        MultipleOverLine(
            REDUCTION,
            CHILD_AMOUNT,
            D("1088"),
            Factor(D("2")),
            TOTAL,
            D("3"),
            NO_ROUNDING,
            D("2173"),
        ),
        AtMostLine(ALLOWED_AMOUNT, TOTAL, D("3"), CAPPED_AMOUNT, D("3")),
        ThresholdGateLine(
            GATED_AMOUNT, TOTAL, D("3"), GATE_AMOUNT, D("4"), Amount(D("4")), NO_ROUNDING, D("3")
        ),
        AmountOrDividedByRateLine(
            LIMITED_AMOUNT,
            TOTAL,
            D("3"),
            DIVIDED_AMOUNT,
            D("3321.67"),
            ThresholdRate(Rate(D("0.0505")), D("52886")),
            CENT,
            D("65775.64"),
        ),
        FractionAppliedLine(EARNED_PORTION, TOTAL, D("3"), Fraction(2, 3), NO_ROUNDING, D("2")),
        TimesCountLine(AMOUNT_CLAIMED, TOTAL, D("3"), PERSONS, 1, D("3")),
        ChosenByCountLine(AMOUNT_CHOSEN, PERSONS, 0, TOTAL, D("3")),
        RatioAppliedLine(
            CREDIT_SHARE, TOTAL, D("3"), EARNED_INCOME, D("2"), TOTAL, D("3"), NO_ROUNDING, D("2")
        ),
        SumNotBelowZeroLine(TOTAL, ((PART_ONE, D("1")), (PART_TWO, D("-2"))), D("0")),
        AmountByCountLine(MONTHLY_AMOUNT, MONTHS, 3, D("300"), NO_ROUNDING, D("300")),
        RecordTotalLine(TOTAL, ITEM_AMOUNT, (D("1"), D("2")), D("3")),
        ChosenByRangeLine(AMOUNT_CHOSEN, TOTAL, D("3"), AMOUNT_IN_RANGE, D("3")),
        CaregiverClaimLine(
            CAREGIVER_AMOUNT, 1, Amount(D("5")), D("4"), Amount(D("2")), NO_ROUNDING, D("1")
        ),
        CaregiverClaimLessClaimedLine(
            CAREGIVER_AMOUNT,
            2,
            Amount(D("5")),
            D("4"),
            Amount(D("2")),
            D("1"),
            D("0.5"),
            NO_ROUNDING,
            D("0.5"),
        ),
        ItemSumLine(TOTAL, 1, ((PART_ONE, D("1")), (PART_TWO, D("2"))), D("3")),
        ItemLesserOfLine(TOTAL, 2, ((PART_ONE, D("1")), (PART_TWO, D("2"))), D("1")),
        ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("1")),), D("1")),
        medical_claim(1, "5", "4", "3", maximum="2", rounding=NO_ROUNDING),
        non_compliant_row(1, "5", 4, 3, "2", rounding=NO_ROUNDING),
        non_compliant_cca_row(1, "8", "5", 4, 3, "2", rounding=NO_ROUNDING),
        non_compliant_cca_class(1, "8", ("2",), "2"),
    )

    assert EnglishTraceRenderer().render_all(trace) == (
        "10% on 100 over 0 plus 0",
        "basic_tax on taxable_base 100 (no rounding)",
        "total: part_one 1 + part_two 2 = 3",
        "rated_amount: 50% of total 3 (no rounding)",
        "net_amount: total 3 less rated_amount 1.5 = 1.5",
        "total: rated_amount 1.5 less part_two 2, not below 0 = 0",
        "personal_amount: credit amount 1000 (no rounding)",
        "capped_amount: lesser of total 3 and 2 (no rounding)",
        "lesser_amount: lesser of total 3 and capped_amount 2 = 2",
        "greater_amount: greater of total 3 and capped_amount 2 = 3",
        "contribution: 5% of earnings between 3000 and 50000 (20000), at most 2350 (no rounding)",
        "surcharge: 50% of total 3 over 1 (no rounding)",
        "personal_amount: 1000 plus 500 less 100 for income 22000 over 20000 (range 10000), "
        "not below 1000 (no rounding)",
        "child_amount: 544 for each of 2 child_count = 1088 (no rounding)",
        "reduction: 2 × child_amount 1088 over total 3, not below 0 (no rounding)",
        "allowed_amount: total 3, at most capped_amount 3",
        "gated_amount: total 3 if gate_amount 4 is at least 4 (no rounding) = 3",
        "limited_amount: total 3 if 52886 or less, otherwise divided_amount 3321.67 divided by "
        "5.05% (half-up to 0.01) = 65775.64",
        "earned_portion: 2/3 of total 3 (no rounding)",
        "amount_claimed: total 3 for each of 1 person_count = 3",
        "amount_chosen: total 3, chosen as person_count is 0",
        "credit_share: total 3 × earned_income 2 / total 3 (no rounding)",
        "total: part_one 1 + part_two -2, not below 0 = 0",
        "monthly_amount: 300 for month_count 3 (no rounding)",
        "total: item 1 item_amount 1 + item 2 item_amount 2 = 3",
        "amount_chosen: amount_in_range 3, chosen as total is 3",
        "caregiver_amount: dependant 1: 5 less net income 4, at most 2 = 1 (no rounding)",
        "caregiver_amount: dependant 2: 5 less net income 4, at most 2 = 1, less claimed 0.5 = 0.5 "
        "(no rounding)",
        "total: item 1: part_one 1 + part_two 2 = 3",
        "total: item 2: lesser of part_one 1 and part_two 2 = 1",
        "caregiver_amount: item 1 1 = 1",
        "dependants_medical: dependant 1: expenses 5 less the lesser of 3% of net income 4 and "
        "2834 = 3, at most 2 (no rounding)",
        "non_compliant_expenses: row 1: expenses 5 for 4 non-compliant days of 3 short-term "
        "days = 2 (no rounding)",
        "non_compliant_cca: row 1: class 8 CCA 5 for 4 non-compliant days of 3 short-term "
        "days = 2 (no rounding)",
        "non_compliant_cca_by_class: item 1 class 8: column 7 2 = 2",
    )


def test_render_all_of_an_empty_trace_is_empty() -> None:
    assert EnglishTraceRenderer().render_all(()) == ()


@dataclass(frozen=True)
class MadeUpLine(TraceLine):
    """A made-up line class the renderer does not know."""

    figure: Decimal

    @property
    def amount(self) -> Decimal:
        return self.figure


def test_rejects_a_line_class_it_does_not_know() -> None:
    with pytest.raises(TypeError, match="MadeUpLine"):
        render(MadeUpLine(D(1)))


def test_render_all_rejects_a_line_class_it_does_not_know() -> None:
    with pytest.raises(TypeError, match="MadeUpLine"):
        EnglishTraceRenderer().render_all((SumLine(TOTAL, (), D(1)), MadeUpLine(D(1))))


DIVIDEND_AMOUNT = ArtifactKind("ex/dividend_amount", Decimal)


DIVISOR_AMOUNT = ArtifactKind("ex/divisor_amount", Decimal)


QUOTIENT_AMOUNT = ArtifactKind("ex/quotient_amount", Decimal)


ITEM_COUNT = ArtifactKind("ex/item_count", int)


ITEMS = RecordListKind("ex/items", fields=(ITEM_AMOUNT,))


REMAINING_SHARE = ArtifactKind("ex/remaining_share", Decimal)


def test_renders_a_quotient() -> None:
    line = QuotientLine(
        QUOTIENT_AMOUNT, DIVIDEND_AMOUNT, D("100000.00"), DIVISOR_AMOUNT, D("200000.00"), D("0.5")
    )

    assert render(line) == (
        "quotient_amount: dividend_amount 100000 divided by divisor_amount 200000 = 0.5"
    )


def test_renders_a_quotient_of_zero() -> None:
    line = QuotientLine(
        QUOTIENT_AMOUNT, DIVIDEND_AMOUNT, D("0"), DIVISOR_AMOUNT, D("200000.00"), D("0")
    )

    assert render(line) == (
        "quotient_amount: dividend_amount 0 divided by divisor_amount 200000 = 0"
    )


def test_renders_a_quotient_with_its_exact_decimal_expansion() -> None:
    line = QuotientLine(
        QUOTIENT_AMOUNT, DIVIDEND_AMOUNT, D("1"), DIVISOR_AMOUNT, D("8"), D("0.125")
    )

    assert render(line) == "quotient_amount: dividend_amount 1 divided by divisor_amount 8 = 0.125"


def test_renders_the_count_of_two_records() -> None:
    assert render(RecordCountLine(ITEM_COUNT, ITEMS, 2)) == "item_count: 2 items in items = 2"


def test_renders_the_count_of_one_record_in_the_singular() -> None:
    assert render(RecordCountLine(ITEM_COUNT, ITEMS, 1)) == "item_count: 1 item in items = 1"


def test_renders_the_count_of_no_records() -> None:
    assert render(RecordCountLine(ITEM_COUNT, ITEMS, 0)) == "item_count: no items in items = 0"


def test_renders_the_count_of_twelve_records() -> None:
    assert render(RecordCountLine(ITEM_COUNT, ITEMS, 12)) == "item_count: 12 items in items = 12"


def placement_credit_line(
    position: int,
    expenditure: str,
    line_1: str,
    line_3: str,
    line_12: str,
    line_13: str,
    rounding: RoundingRule = CENT,
) -> PlacementCreditLine:
    return PlacementCreditLine(
        output=TOTAL,
        position=position,
        field=ITEM_AMOUNT,
        expenditure=D(expenditure),
        line_1=D(line_1),
        line_3=D(line_3),
        line_12=D(line_12),
        line_13=D(line_13),
        remaining_share=REMAINING_SHARE,
        remaining_share_amount=D("0.5"),
        expenditure_rate=Rate(D("0.25")),
        supplement_rate=Rate(D("0.05")),
        maximum=Amount(D("3000")),
        rounding=rounding,
    )


def test_renders_the_credit_of_a_placement() -> None:
    line = placement_credit_line(1, "8000", "2000.00", "400.00", "200.000", "2200.00")

    assert render(line) == (
        "total: item 1 item_amount 8000: line 1 2000, line 3 400, line 12 200, line 13 2200 "
        "(half-up to 0.01)"
    )


def test_renders_the_credit_of_a_placement_at_a_later_position() -> None:
    line = placement_credit_line(2, "15000", "3750.00", "750.00", "375.000", "3000.00")

    assert render(line) == (
        "total: item 2 item_amount 15000: line 1 3750, line 3 750, line 12 375, line 13 3000 "
        "(half-up to 0.01)"
    )


def test_renders_the_credit_of_a_placement_with_a_zero_line_12() -> None:
    line = placement_credit_line(1, "8000", "2400.00", "400.00", "0.00", "2400.00")

    assert render(line) == (
        "total: item 1 item_amount 8000: line 1 2400, line 3 400, line 12 0, line 13 2400 "
        "(half-up to 0.01)"
    )


def test_renders_the_credit_of_a_placement_with_unrounded_lines_and_a_rounded_line_13() -> None:
    # Lines 1, 3 and 12 are exact; only line 13 is rounded: 0.14 x 25% = 0.035, x 5% = 0.007.
    line = placement_credit_line(1, "0.14", "0.0350", "0.0070", "0.0070", "0.04")

    assert render(line) == (
        "total: item 1 item_amount 0.14: line 1 0.035, line 3 0.007, line 12 0.007, line 13 0.04 "
        "(half-up to 0.01)"
    )


def test_renders_the_credit_with_no_rounding_named_when_the_rule_is_none() -> None:
    line = placement_credit_line(1, "8000", "2000", "400", "200", "2200", NO_ROUNDING)

    assert render(line) == (
        "total: item 1 item_amount 8000: line 1 2000, line 3 400, line 12 200, line 13 2200 "
        "(no rounding)"
    )


# --- the capital cost allowance table, one line per class ----------------------------


def class_rate(
    number: str,
    rate: str = "0.30",
    recapture_and_terminal_loss: RecaptureAndTerminalLoss = RecaptureAndTerminalLoss.APPLIES,
) -> ClassRate:
    return ClassRate(
        D(number),
        Rate(D(rate)),
        HalfYearRule.APPLIES,
        recapture_and_terminal_loss,
        Fraction(3, 2),
        Fraction(7, 3),
        HalfYearRuleOnSale.DOES_NOT_APPLY,
    )


CCA_CLAIM = ArtifactKind("ex/cca_claim", Decimal)
RECAPTURED_CCA = ArtifactKind("ex/recaptured_cca", Decimal)
TERMINAL_LOSS = ArtifactKind("ex/terminal_loss", Decimal)
CLOSING_UCC = RecordListKind("ex/closing_ucc", fields=(ArtifactKind("ex/ucc_at_end", Decimal),))
EXCLUDED = RecaptureAndTerminalLoss.EXCLUDED


def cca_claim_line(
    number: str,
    rate: str,
    no_property_left: int,
    columns: tuple[str, str, str, str, str, str, str],
    maximum: str,
    claim: str,
    rounding: RoundingRule = CENT,
    position: int = 1,
    zero_reason: CcaZeroReason = CcaZeroReason.NONE,
) -> CcaClaimLine:
    column_7, column_14, column_15, column_16, column_17, column_18, column_19 = columns
    return CcaClaimLine(
        output=CCA_CLAIM,
        position=position,
        class_rate=class_rate(number, rate),
        no_property_left=no_property_left,
        column_7=D(column_7),
        column_14=D(column_14),
        column_15=D(column_15),
        column_16=D(column_16),
        column_17=D(column_17),
        column_18=D(column_18),
        column_19=D(column_19),
        zero_reason=zero_reason,
        maximum=D(maximum),
        rounding=rounding,
        claim=D(claim),
    )


def test_renders_the_cca_claim_of_a_class() -> None:
    line = cca_claim_line(
        "43.1",
        "0.30",
        0,
        ("6000.00", "400.00", "900.00", "0", "0", "0", "6900.00"),
        "2070.00",
        "2000.00",
        position=2,
    )

    assert render(line) == (
        "cca_claim: item 2 class 43.1: column 7 6000, column 14 400, column 15 900, "
        "column 16 0, column 17 0, column 18 0, column 19 6900, "
        "maximum 30% of column 19 = 2070 (half-up to 0.01), claim 2000"
    )


def test_renders_the_cca_claim_of_a_class_with_the_half_year_rule() -> None:
    line = cca_claim_line(
        "8",
        "0.20",
        0,
        ("13000.00", "0", "0", "0", "0", "1500.00", "11500.00"),
        "2300.00",
        "2300.00",
    )

    assert render(line) == (
        "cca_claim: item 1 class 8: column 7 13000, column 14 0, column 15 0, column 16 0, "
        "column 17 0, column 18 1500, column 19 11500, "
        "maximum 20% of column 19 = 2300 (half-up to 0.01), claim 2300"
    )


def test_renders_a_column_18_with_cents() -> None:
    line = cca_claim_line(
        "8", "0.20", 0, ("100.01", "0", "0", "0", "0", "50.01", "50.00"), "10.00", "10.00"
    )

    assert render(line) == (
        "cca_claim: item 1 class 8: column 7 100.01, column 14 0, column 15 0, column 16 0, "
        "column 17 0, column 18 50.01, column 19 50, "
        "maximum 20% of column 19 = 10 (half-up to 0.01), claim 10"
    )


def test_renders_a_claim_below_the_maximum() -> None:
    line = cca_claim_line(
        "8", "0.20", 0, ("13000", "0", "0", "0", "0", "1500", "11500"), "2300.00", "0"
    )

    assert render(line).endswith("maximum 20% of column 19 = 2300 (half-up to 0.01), claim 0")


def test_renders_no_cca_when_column_7_is_negative() -> None:
    line = cca_claim_line(
        "10",
        "0.30",
        0,
        ("-3000.00", "8000.00", "0", "8000.00", "0", "0", "-3000.00"),
        "0",
        "0",
        zero_reason=CcaZeroReason.COLUMN_7_NEGATIVE,
    )

    assert render(line) == (
        "cca_claim: item 1 class 10: column 7 -3000, column 14 8000, column 15 0, "
        "column 16 8000, column 17 0, column 18 0, column 19 -3000, "
        "maximum 0 as column 7 is negative, claim 0"
    )


def test_renders_no_cca_when_no_property_is_left_in_the_class() -> None:
    line = cca_claim_line(
        "1",
        "0.04",
        1,
        ("5000.00", "15000.00", "0", "15000.00", "0", "0", "5000.00"),
        "0",
        "0",
        zero_reason=CcaZeroReason.NO_PROPERTY_LEFT,
    )

    assert render(line) == (
        "cca_claim: item 1 class 1: column 7 5000, column 14 15000, column 15 0, "
        "column 16 15000, column 17 0, column 18 0, column 19 5000, "
        "maximum 0 as no property is left in the class, claim 0"
    )


def test_renders_the_rate_of_a_class_with_no_property_left_and_a_column_7_of_zero() -> None:
    # Note 3's terminal loss needs a positive column 7: a class at 0 with no property left keeps
    # the rate's maximum, which is 0.
    line = cca_claim_line("8", "0.20", 1, ("0", "0", "0", "0", "0", "0", "0"), "0.00", "0")

    assert render(line).endswith("maximum 20% of column 19 = 0 (half-up to 0.01), claim 0")


def test_renders_the_cca_claim_with_no_rounding_named_when_the_rule_is_none() -> None:
    line = cca_claim_line(
        "8",
        "0.20",
        0,
        ("100.01", "0", "0", "0", "0", "50.005", "50.005"),
        "10.001",
        "10",
        rounding=NO_ROUNDING,
    )

    assert render(line).endswith("maximum 20% of column 19 = 10.001 (no rounding), claim 10")


NEGATIVE = CcaZeroReason.COLUMN_7_NEGATIVE
NONE_LEFT = CcaZeroReason.NO_PROPERTY_LEFT
NO_REASON = CcaZeroReason.NONE


def test_renders_a_recapture() -> None:
    line = RecapturedCcaLine(
        RECAPTURED_CCA, 1, class_rate("10"), D("-3000.00"), NEGATIVE, D("3000.00")
    )

    assert (
        render(line)
        == "recaptured_cca: item 1 class 10: column 7 -3000 is negative: recapture 3000"
    )


@pytest.mark.parametrize(
    ("column_7", "zero_reason"),
    [("13000.00", NO_REASON), ("0", NO_REASON), ("5000.00", NONE_LEFT)],
)
def test_renders_no_recapture_when_column_7_is_not_negative(
    column_7: str, zero_reason: CcaZeroReason
) -> None:
    line = RecapturedCcaLine(RECAPTURED_CCA, 2, class_rate("8"), D(column_7), zero_reason, D("0"))

    assert render(line) == (
        f"recaptured_cca: item 2 class 8: column 7 {column_7.removesuffix('.00')} "
        "is not negative: recapture 0"
    )


def test_renders_no_recapture_for_a_class_it_does_not_apply_to() -> None:
    line = RecapturedCcaLine(
        RECAPTURED_CCA,
        1,
        class_rate("10.1", recapture_and_terminal_loss=EXCLUDED),
        D("-3000"),
        NEGATIVE,
        D("0"),
    )

    assert render(line) == (
        "recaptured_cca: item 1 class 10.1: column 7 -3000 is negative, but recapture does not "
        "apply to class 10.1: recapture 0"
    )


def test_renders_the_recapture_case_the_line_records_not_column_7s_sign() -> None:
    # The wording follows `zero_reason`; column 7 is only shown.
    recorded = RecapturedCcaLine(RECAPTURED_CCA, 1, class_rate("8"), D("100"), NEGATIVE, D("0"))
    unrecorded = RecapturedCcaLine(RECAPTURED_CCA, 1, class_rate("8"), D("-100"), NO_REASON, D("0"))

    assert (
        render(recorded) == "recaptured_cca: item 1 class 8: column 7 100 is negative: recapture 0"
    )
    assert render(unrecorded) == (
        "recaptured_cca: item 1 class 8: column 7 -100 is not negative: recapture 0"
    )


MOTOR_VEHICLE_EXPENSES = ArtifactKind("ex/motor_vehicle_expenses", Decimal)


def business_vehicle_line(
    line_12: str, line_13: str, line_19: str, line_28: str, line_16: str, position: int = 1
) -> BusinessVehicleLine:
    return BusinessVehicleLine(
        MOTOR_VEHICLE_EXPENSES,
        position,
        D(line_12),
        D(line_13),
        D(line_19),
        D(line_28),
        D(line_16),
    )


def test_renders_a_business_vehicle() -> None:
    line = business_vehicle_line("5000.00", "2500.00", "400.00", "2147.00", "2500.00")

    assert render(line) == (
        "motor_vehicle_expenses: item 1: line 12 5000, line 13 2500, line 19 400, "
        "line 28 2147, line 16 2500"
    )


def test_renders_a_business_vehicle_by_its_position_and_its_cents() -> None:
    line = business_vehicle_line("3505", "876.25", "0", "2147.00", "936.25", position=2)

    assert render(line) == (
        "motor_vehicle_expenses: item 2: line 12 3505, line 13 876.25, line 19 0, "
        "line 28 2147, line 16 936.25"
    )


def test_renders_a_business_vehicle_with_no_leasing_and_no_interest() -> None:
    line = business_vehicle_line("0", "0", "0", "0", "300")

    assert render(line) == (
        "motor_vehicle_expenses: item 1: line 12 0, line 13 0, line 19 0, line 28 0, line 16 300"
    )


def terminal_loss_line(
    number: str,
    no_property_left: int,
    column_7: str,
    zero_reason: CcaZeroReason,
    column_7_positive: bool,
    result: str,
    position: int = 1,
    recapture_and_terminal_loss: RecaptureAndTerminalLoss = RecaptureAndTerminalLoss.APPLIES,
) -> TerminalLossLine:
    return TerminalLossLine(
        TERMINAL_LOSS,
        position,
        class_rate(number, "0.04", recapture_and_terminal_loss),
        no_property_left,
        D(column_7),
        zero_reason,
        column_7_positive,
        D(result),
    )


def test_renders_a_terminal_loss() -> None:
    line = terminal_loss_line("1", 1, "5000.00", NONE_LEFT, True, "5000.00")

    assert render(line) == (
        "terminal_loss: item 1 class 1: column 7 5000 with no property left: terminal loss 5000"
    )


def test_renders_no_terminal_loss_while_property_is_left() -> None:
    line = terminal_loss_line("1", 0, "5000.00", NO_REASON, True, "0")

    assert render(line) == (
        "terminal_loss: item 1 class 1: column 7 5000 with property left: terminal loss 0"
    )


@pytest.mark.parametrize(
    ("column_7", "shown", "zero_reason"),
    [("-3000.00", "-3000", NEGATIVE), ("0", "0", NO_REASON)],
)
@pytest.mark.parametrize("no_property_left", [0, 1])
def test_renders_no_terminal_loss_when_column_7_is_not_positive(
    column_7: str, shown: str, zero_reason: CcaZeroReason, no_property_left: int
) -> None:
    line = terminal_loss_line("1", no_property_left, column_7, zero_reason, False, "0", position=3)

    assert render(line) == (
        f"terminal_loss: item 3 class 1: column 7 {shown} is not positive: terminal loss 0"
    )


def test_renders_no_terminal_loss_for_a_class_it_does_not_apply_to() -> None:
    line = terminal_loss_line(
        "10.1", 1, "5000", NONE_LEFT, True, "0", recapture_and_terminal_loss=EXCLUDED
    )

    assert render(line) == (
        "terminal_loss: item 1 class 10.1: column 7 5000 with no property left, but a terminal "
        "loss does not apply to class 10.1: terminal loss 0"
    )


def test_renders_the_terminal_loss_case_the_line_records_not_column_7_or_the_flag() -> None:
    # `zero_reason` picks the no-property-left case; with no reason, `column_7_positive` picks
    # "with property left" over "is not positive". Column 7 and the flag are only shown.
    no_property = terminal_loss_line("1", 0, "-5", NONE_LEFT, False, "0")
    property_left = terminal_loss_line("1", 1, "0", NO_REASON, True, "0")
    not_positive = terminal_loss_line("1", 0, "5", NO_REASON, False, "0")
    negative = terminal_loss_line("1", 1, "5", NEGATIVE, True, "0")

    assert render(no_property) == (
        "terminal_loss: item 1 class 1: column 7 -5 with no property left: terminal loss 0"
    )
    assert render(property_left) == (
        "terminal_loss: item 1 class 1: column 7 0 with property left: terminal loss 0"
    )
    assert render(not_positive) == (
        "terminal_loss: item 1 class 1: column 7 5 is not positive: terminal loss 0"
    )
    assert render(negative) == (
        "terminal_loss: item 1 class 1: column 7 5 is not positive: terminal loss 0"
    )


def test_renders_the_ucc_at_the_end_of_the_year() -> None:
    line = ClosingUccLine(
        CLOSING_UCC,
        2,
        class_rate("43.1"),
        0,
        D("6000.00"),
        CcaZeroReason.NONE,
        D("2000.00"),
        D("4000.00"),
    )

    assert render(line) == "closing_ucc: item 2 class 43.1: column 7 6000 less claim 2000 = 4000"


def test_renders_the_ucc_at_the_end_of_the_year_with_no_claim() -> None:
    line = ClosingUccLine(
        CLOSING_UCC, 1, class_rate("8"), 0, D("13000.00"), CcaZeroReason.NONE, D("0"), D("13000.00")
    )

    assert render(line) == "closing_ucc: item 1 class 8: column 7 13000 less claim 0 = 13000"


def test_renders_a_ucc_of_zero_at_the_end_of_the_year_when_column_7_is_negative() -> None:
    line = ClosingUccLine(
        CLOSING_UCC,
        1,
        class_rate("10"),
        0,
        D("-3000.00"),
        CcaZeroReason.COLUMN_7_NEGATIVE,
        D("0"),
        D("0"),
    )

    assert render(line) == "closing_ucc: item 1 class 10: column 7 -3000 is negative: 0"


def test_renders_a_ucc_of_zero_at_the_end_of_the_year_when_no_property_is_left() -> None:
    line = ClosingUccLine(
        CLOSING_UCC,
        1,
        class_rate("1", "0.04"),
        1,
        D("5000.00"),
        CcaZeroReason.NO_PROPERTY_LEFT,
        D("0"),
        D("0"),
    )

    assert render(line) == "closing_ucc: item 1 class 1: column 7 5000 with no property left: 0"


def test_renders_the_reason_the_cca_line_records_without_working_it_out_again() -> None:
    # The line says why its maximum is 0; the renderer reads that, not column 7 or the flag.
    recorded = cca_claim_line(
        "8",
        "0.20",
        0,
        ("13000", "0", "0", "0", "0", "1500", "11500"),
        "0",
        "0",
        zero_reason=CcaZeroReason.NO_PROPERTY_LEFT,
    )
    unrecorded = cca_claim_line(
        "8",
        "0.20",
        1,
        ("-1", "0", "0", "0", "0", "0", "-1"),
        "0",
        "0",
        zero_reason=CcaZeroReason.NONE,
    )

    assert render(recorded).endswith("maximum 0 as no property is left in the class, claim 0")
    assert render(unrecorded).endswith("maximum 20% of column 19 = 0 (half-up to 0.01), claim 0")


def test_renders_the_reason_the_closing_line_records_without_working_it_out_again() -> None:
    recorded = ClosingUccLine(
        CLOSING_UCC,
        1,
        class_rate("8"),
        0,
        D("13000"),
        CcaZeroReason.NO_PROPERTY_LEFT,
        D("0"),
        D("0"),
    )
    unrecorded = ClosingUccLine(
        CLOSING_UCC, 1, class_rate("8"), 1, D("5000"), CcaZeroReason.NONE, D("0"), D("5000")
    )

    assert (
        render(recorded) == "closing_ucc: item 1 class 8: column 7 13000 with no property left: 0"
    )
    assert render(unrecorded) == ("closing_ucc: item 1 class 8: column 7 5000 less claim 0 = 5000")


def test_renders_a_vehicles_adjusted_proceeds() -> None:
    # Area A endnote 2: "adjusted based on a factor equal to its prescribed amount as a proportion
    # of the actual cost of the vehicle": 40000 x 42940 / 56500 = 30400, and a DIEP's part likewise.
    line = CcaVehicleProceedsLine(
        CLOSING_UCC,
        2,
        True,
        D("42940.00"),
        D("56500.00"),
        D("40000.00"),
        D("30400.00"),
        D("20000.00"),
        D("15200.00"),
    )

    assert render(line) == (
        "closing_ucc: item 2: proceeds 40000 and DIEP proceeds 20000 adjusted by prescribed "
        "amount 42940 / actual cost 56500 = proceeds 30400 and DIEP proceeds 15200"
    )


def test_renders_a_part_a_check_line_for_a_class_8_row() -> None:
    line = CcaPartACheckLine(CLOSING_UCC, 2, D("8"))

    assert render(line) == "closing_ucc: item 2: class 8: checked"


def test_renders_a_part_a_check_line_for_a_vehicle_class_row() -> None:
    line = CcaPartACheckLine(CLOSING_UCC, 1, D("54"))

    assert render(line) == "closing_ucc: item 1: class 54: checked"


def test_renders_a_part_a_change_in_use_line_for_a_row_checked_as_its_value() -> None:
    line = CcaChangeInUseCheckLine(CLOSING_UCC, 1, True, D("11000"), D("11000"))

    assert render(line) == (
        "closing_ucc: item 1: change in use, additions 11000 are the fair market value 11000: "
        "checked"
    )


def test_renders_a_part_a_change_in_use_check_line_for_a_row_not_checked() -> None:
    line = CcaChangeInUseCheckLine(CLOSING_UCC, 2, False, D("19000"), D("0"))

    assert render(line) == ("closing_ucc: item 2: not checked, no change in use with additions")


def test_renders_a_part_b_check_line_for_a_row_sold_in_the_year() -> None:
    line = CcaPartBCheckLine(CLOSING_UCC, 2, D("20000"), D("0"), D("12000"), True)

    assert render(line) == (
        "closing_ucc: item 2: UCC at start 20000, additions 0, proceeds 12000, sold in the year: "
        "checked"
    )


def test_renders_a_part_b_check_line_for_a_row_not_sold() -> None:
    line = CcaPartBCheckLine(CLOSING_UCC, 1, D("0"), D("15000"), D("0"), False)

    assert render(line) == (
        "closing_ucc: item 1: UCC at start 0, additions 15000, proceeds 0, not sold in the year: "
        "checked"
    )


def test_renders_a_vehicle_additions_check_line_for_a_row_checked_against_its_limit() -> None:
    line = CcaVehicleAdditionsCheckLine(CLOSING_UCC, 1, True, D("42940"), D("42940"))

    assert render(line) == ("closing_ucc: item 1: additions 42940, limit with tax 42940: checked")


def test_renders_a_vehicle_additions_check_line_for_a_row_not_checked() -> None:
    line = CcaVehicleAdditionsCheckLine(CLOSING_UCC, 2, False, D("31640"), D("0"))

    assert render(line) == (
        "closing_ucc: item 2: additions 31640: not checked, no Class 10.1 limit applies"
    )


def test_renders_a_vehicle_class_check_line_for_a_row_checked_against_its_minimum() -> None:
    line = CcaVehicleClassCheckLine(CLOSING_UCC, 1, True, 2025, D("38000.01"), D("38000"))

    assert render(line) == (
        "closing_ucc: item 1: acquired in 2025, cost 38000.01, more than 38000: Class 10.1"
    )


def test_renders_a_vehicle_class_check_line_for_a_row_not_checked() -> None:
    line = CcaVehicleClassCheckLine(CLOSING_UCC, 2, False, 0, D("0"), D("0"))

    assert render(line) == ("closing_ucc: item 2: not checked, not a Class 10.1 vehicle")


def test_renders_a_vehicle_class_check_line_for_a_row_of_another_class_with_a_date() -> None:
    line = CcaVehicleClassCheckLine(CLOSING_UCC, 3, False, 2025, D("100"), D("0"))

    assert render(line) == ("closing_ucc: item 3: not checked, not a Class 10.1 vehicle")


def test_renders_a_non_arms_length_check_line_for_a_row_checked_against_the_three_amounts() -> None:
    line = CcaVehicleNonArmsLengthCheckLine(
        CLOSING_UCC, 1, True, D("30000"), D("30000"), D("42940"), D("40000"), D("30000")
    )

    assert render(line) == (
        "closing_ucc: item 1: bought from a non-arm's-length person, fair market value 30000, "
        "limit with tax 42940, seller's cost 40000, additions 30000 are the least of the three: "
        "checked"
    )


def test_renders_a_non_arms_length_check_line_for_a_row_not_checked() -> None:
    line = CcaVehicleNonArmsLengthCheckLine(
        CLOSING_UCC, 2, False, D("31640"), D("0"), D("0"), D("0"), D("0")
    )

    assert render(line) == (
        "closing_ucc: item 2: not checked, not a Class 10.1 vehicle bought from a non-arm's-length "
        "person"
    )


def test_renders_a_change_in_use_check_line_for_a_row_checked_against_its_fair_market_value() -> (
    None
):
    line = CcaVehicleChangeInUseCheckLine(CLOSING_UCC, 1, True, D("11000"), D("11000"))

    assert render(line) == (
        "closing_ucc: item 1: change in use, additions 11000 are the fair market value 11000: "
        "checked"
    )


def test_renders_a_change_in_use_check_line_for_a_row_not_checked() -> None:
    line = CcaVehicleChangeInUseCheckLine(CLOSING_UCC, 2, False, D("19000"), D("0"))

    assert render(line) == (
        "closing_ucc: item 2: not checked, not a Class 10.1 vehicle with a change in use"
    )


def test_renders_proceeds_that_are_not_adjusted() -> None:
    line = CcaVehicleProceedsLine(
        CLOSING_UCC, 1, False, D("0"), D("0"), D("12000.00"), D("12000.00"), D("0"), D("0")
    )

    assert render(line) == "closing_ucc: item 1: proceeds 12000 and DIEP proceeds 0 not adjusted"


def test_renders_what_the_vehicle_line_records_without_working_it_out_again() -> None:
    # The line says whether the proceeds were adjusted; the renderer reads that, not the costs.
    recorded = CcaVehicleProceedsLine(
        CLOSING_UCC, 1, True, D("42940"), D("42941"), D("1000"), D("999.98"), D("0"), D("0")
    )
    unrecorded = CcaVehicleProceedsLine(
        CLOSING_UCC, 1, False, D("42940"), D("56500"), D("1000"), D("1000"), D("0"), D("0")
    )

    assert render(recorded).endswith(
        "adjusted by prescribed amount 42940 / actual cost 42941 = proceeds 999.98 and DIEP "
        "proceeds 0"
    )
    assert (
        render(unrecorded) == "closing_ucc: item 1: proceeds 1000 and DIEP proceeds 0 not adjusted"
    )


def test_renders_a_sold_zepvs_adjusted_proceeds() -> None:
    # Guide T4036 "Class 54 (30%)": "the proceeds of disposition will be adjusted based on a factor
    # equal to the prescribed amount as a proportion of the actual cost of the vehicle":
    # 30000 x 61000 / 65000 = 28153.85, and a DIEP's part likewise.
    line = CcaZepvProceedsLine(
        CLOSING_UCC,
        2,
        1,
        True,
        D("61000.00"),
        D("65000.00"),
        D("30000.00"),
        D("28153.85"),
        D("15000.00"),
        D("14076.92"),
    )

    assert render(line) == (
        "closing_ucc: item 2 vehicle 1: proceeds 30000 and DIEP proceeds 15000 adjusted by "
        "prescribed amount 61000 / actual cost 65000 = proceeds 28153.85 and DIEP proceeds "
        "14076.92"
    )


def test_renders_a_sold_zepvs_proceeds_that_are_not_adjusted() -> None:
    line = CcaZepvProceedsLine(
        CLOSING_UCC, 3, 2, False, D("59000"), D("50000"), D("20000"), D("20000"), D("0"), D("0")
    )

    assert render(line) == (
        "closing_ucc: item 3 vehicle 2: proceeds 20000 and DIEP proceeds 0 not adjusted"
    )


def test_renders_what_the_sold_zepv_line_records_without_working_it_out_again() -> None:
    # The line says whether the proceeds were adjusted; the renderer reads that, not the costs.
    recorded = CcaZepvProceedsLine(
        CLOSING_UCC, 1, 1, True, D("61000"), D("61001"), D("1000"), D("999.98"), D("0"), D("0")
    )
    unrecorded = CcaZepvProceedsLine(
        CLOSING_UCC, 1, 1, False, D("61000"), D("65000"), D("1000"), D("1000"), D("0"), D("0")
    )

    assert render(recorded).endswith(
        "adjusted by prescribed amount 61000 / actual cost 61001 = proceeds 999.98 and DIEP "
        "proceeds 0"
    )
    assert render(unrecorded) == (
        "closing_ucc: item 1 vehicle 1: proceeds 1000 and DIEP proceeds 0 not adjusted"
    )


# --- counts at least a minimum ----------------------------
#
# "<output>: <count kind> <count>, at least <minimum kind> <minimum>".


def test_renders_a_count_at_least_a_minimum() -> None:
    line = CountAtLeastLine(PERSONS, CHILDREN, 3, DEPENDANTS, 2)

    assert render(line) == "person_count: child_count 3, at least dependant_count 2"


def test_renders_a_count_equal_to_its_minimum() -> None:
    line = CountAtLeastLine(PERSONS, CHILDREN, 2, DEPENDANTS, 2)

    assert render(line) == "person_count: child_count 2, at least dependant_count 2"


def test_renders_a_zero_count_and_a_negative_minimum() -> None:
    line = CountAtLeastLine(PERSONS, CHILDREN, 0, DEPENDANTS, -1)

    assert render(line) == "person_count: child_count 0, at least dependant_count -1"


# --- a total more than a minimum per unit ---------------------------------
#
# "<output>: <total kind> <total>, more than <minimum> (<per unit> for each of <count> <count kind>,
# <rounding>)" (`ca/more_than_per_unit`), for a count above 0;
# with a count of 0 the line reads "<output>: <total kind> <total>, no <count kind>".

FEE_TOTAL = ArtifactKind("ex/fee_total", Decimal)
FEE_CHECKED = ArtifactKind("ex/fee_checked", Decimal)
INSTITUTIONS = ArtifactKind("ex/institution_count", int)


def test_renders_a_total_more_than_its_minimum_per_unit() -> None:
    line = MoreThanPerUnitLine(
        output=FEE_CHECKED,
        total_kind=FEE_TOTAL,
        total=D("201"),
        count_kind=INSTITUTIONS,
        count=2,
        per_unit=Amount(D("100.00")),
        rounding=CENT,
        minimum_total=D("200.00"),
    )

    assert render(line) == (
        "fee_checked: fee_total 201, more than 200 "
        "(100 for each of 2 institution_count, half-up to 0.01)"
    )


def test_renders_a_total_with_no_rounding() -> None:
    line = MoreThanPerUnitLine(
        output=FEE_CHECKED,
        total_kind=FEE_TOTAL,
        total=D("101"),
        count_kind=INSTITUTIONS,
        count=1,
        per_unit=Amount(D("100.00")),
        rounding=NO_ROUNDING,
        minimum_total=D("100.00"),
    )

    assert render(line) == (
        "fee_checked: fee_total 101, more than 100 "
        "(100 for each of 1 institution_count, no rounding)"
    )


def test_renders_a_zero_count_without_a_more_than_claim() -> None:
    line = MoreThanPerUnitLine(
        output=FEE_CHECKED,
        total_kind=FEE_TOTAL,
        total=D("0"),
        count_kind=INSTITUTIONS,
        count=0,
        per_unit=Amount(D("100.00")),
        rounding=CENT,
        minimum_total=D("0.00"),
    )

    assert render(line) == "fee_checked: fee_total 0, no institution_count"


# --- counts at most a maximum ----------------------------------------------
#
# "<output>: <count kind> <count>, at most <maximum kind> <maximum>" (`ca/count_at_most`).


def test_renders_a_count_at_most_a_maximum() -> None:
    line = CountAtMostLine(PERSONS, CHILDREN, 2, DEPENDANTS, 3)

    assert render(line) == "person_count: child_count 2, at most dependant_count 3"


def test_renders_a_count_equal_to_its_maximum() -> None:
    line = CountAtMostLine(PERSONS, CHILDREN, 3, DEPENDANTS, 3)

    assert render(line) == "person_count: child_count 3, at most dependant_count 3"


def test_renders_a_zero_count_and_a_zero_maximum() -> None:
    line = CountAtMostLine(PERSONS, CHILDREN, 0, DEPENDANTS, 0)

    assert render(line) == "person_count: child_count 0, at most dependant_count 0"


# --- yes or no counts ----------------------------------------------
#
# "<output>: <count kind> <count>, a yes or no answer of 0 or 1" (`ca/yes_or_no_count`).


def test_renders_a_yes_or_no_count_of_1() -> None:
    line = YesOrNoCountLine(PERSONS, CHILDREN, 1)

    assert render(line) == "person_count: child_count 1, a yes or no answer of 0 or 1"


def test_renders_a_yes_or_no_count_of_0() -> None:
    line = YesOrNoCountLine(PERSONS, CHILDREN, 0)

    assert render(line) == "person_count: child_count 0, a yes or no answer of 0 or 1"


# --- counts without records ----------------------------------------
#
# "<output>: <count kind> <count>, with no <records kind> (<n> records)" (the guard
# `ca/count_without_records`); with records: "... with <n> record(s) of <records kind>", recorded
# only for a count of 0.


def test_renders_a_count_of_1_with_no_records() -> None:
    line = CountWithoutRecordsLine(PERSONS, CHILDREN, 1, ITEMS, 0)

    assert render(line) == "person_count: child_count 1, with no items (0 records)"


def test_renders_a_count_of_0_with_no_records() -> None:
    line = CountWithoutRecordsLine(PERSONS, CHILDREN, 0, ITEMS, 0)

    assert render(line) == "person_count: child_count 0, with no items (0 records)"


def test_renders_a_count_of_0_with_one_record() -> None:
    line = CountWithoutRecordsLine(PERSONS, CHILDREN, 0, ITEMS, 1)

    assert render(line) == "person_count: child_count 0, with 1 record of items"


def test_renders_a_count_of_0_with_two_records() -> None:
    line = CountWithoutRecordsLine(PERSONS, CHILDREN, 0, ITEMS, 2)

    assert render(line) == "person_count: child_count 0, with 2 records of items"


# --- counts not refused ----------------------------------------------
#
# "<output>: <count kind> <count>, not refused by the listed conditions"
# (`ca/count_refused_by_conditions`).


def test_renders_a_count_not_refused() -> None:
    line = CountNotRefusedLine(PERSONS, CHILDREN, 2)

    assert render(line) == "person_count: child_count 2, not refused by the listed conditions"


def test_renders_a_count_of_0_not_refused() -> None:
    line = CountNotRefusedLine(PERSONS, CHILDREN, 0)

    assert render(line) == "person_count: child_count 0, not refused by the listed conditions"


# --- ratios, truncated ----------------------------
#
# "<output>: <dividend kind> <dividend> divided by <divisor kind> <divisor> (<rule>) = <result>";
# with the cap, ", at most 1" follows the rule: "(<rule>), at most 1 = <result>".


def test_renders_a_ratio_truncated_to_five_decimals() -> None:
    line = RatioTruncatedLine(
        RATED_AMOUNT_RATE,
        GROSS_AMOUNT,
        D("30000"),
        TOTAL,
        D("70000"),
        FIVE_DECIMALS_DOWN,
        False,
        D("0.42857"),
    )

    assert render(line) == (
        "rated_amount: gross_amount 30000 divided by total 70000 (down to 0.00001) = 0.42857"
    )


def test_renders_a_ratio_with_a_zero_divisor() -> None:
    line = RatioTruncatedLine(
        RATED_AMOUNT_RATE, GROSS_AMOUNT, D("5"), TOTAL, D("0"), FIVE_DECIMALS_DOWN, False, D("0")
    )

    assert render(line) == "rated_amount: gross_amount 5 divided by total 0 (down to 0.00001) = 0"


def test_renders_a_capped_ratio() -> None:
    line = RatioTruncatedLine(
        RATED_AMOUNT_RATE,
        GROSS_AMOUNT,
        D("70000"),
        TOTAL,
        D("30000"),
        FIVE_DECIMALS_DOWN,
        True,
        D("1"),
    )

    assert render(line) == (
        "rated_amount: gross_amount 70000 divided by total 30000 (down to 0.00001), at most 1 = 1"
    )


def test_renders_a_capped_ratio_that_was_not_reduced() -> None:
    line = RatioTruncatedLine(
        RATED_AMOUNT_RATE,
        GROSS_AMOUNT,
        D("30000"),
        TOTAL,
        D("70000"),
        FIVE_DECIMALS_DOWN,
        True,
        D("0.42857"),
    )

    assert render(line) == (
        "rated_amount: gross_amount 30000 divided by total 70000 (down to 0.00001), at most 1 "
        "= 0.42857"
    )


def test_renders_a_ratio_without_rounding() -> None:
    line = RatioTruncatedLine(
        RATED_AMOUNT_RATE, GROSS_AMOUNT, D("1"), TOTAL, D("4"), NO_ROUNDING, False, D("0.25")
    )

    assert render(line) == "rated_amount: gross_amount 1 divided by total 4 (no rounding) = 0.25"


# --- the positive part of a negation ----------------------------
#
# "<output>: negation of <kind> <amount>, not below 0 = <result>".


def test_renders_the_negation_of_a_negative_amount() -> None:
    line = PositivePartOfNegationLine(RATED_AMOUNT, NET_AMOUNT, D("-12.50"), D("12.50"))

    assert render(line) == "rated_amount: negation of net_amount -12.5, not below 0 = 12.5"


def test_renders_the_negation_of_a_positive_amount() -> None:
    line = PositivePartOfNegationLine(RATED_AMOUNT, NET_AMOUNT, D("40"), D("0"))

    assert render(line) == "rated_amount: negation of net_amount 40, not below 0 = 0"


# --- lesser of, when every amount is positive ----------------------------
#
# "<output>: lesser of <part> and <part>[, shown in brackets][, not all positive] = <result>";
# a single part has no "lesser of".


def test_renders_the_lesser_of_two_amounts_when_every_amount_is_positive() -> None:
    line = LesserOfWhenPositiveLine(
        TOTAL, ((PART_ONE, D("1500")), (PART_TWO, D("750.50"))), True, False, D("750.50")
    )

    assert render(line) == "total: lesser of part_one 1500 and part_two 750.5 = 750.5"


def test_renders_the_lesser_of_three_amounts() -> None:
    line = LesserOfWhenPositiveLine(
        TOTAL,
        ((PART_ONE, D("3")), (PART_TWO, D("2")), (GROSS_AMOUNT, D("5"))),
        True,
        False,
        D("2"),
    )

    assert render(line) == "total: lesser of part_one 3 and part_two 2 and gross_amount 5 = 2"


def test_renders_the_lesser_shown_in_brackets() -> None:
    line = LesserOfWhenPositiveLine(
        TOTAL, ((PART_ONE, D("1500")), (PART_TWO, D("750.50"))), True, True, D("-750.50")
    )

    assert render(line) == (
        "total: lesser of part_one 1500 and part_two 750.5, shown in brackets = -750.5"
    )


def test_renders_conditions_that_are_not_met() -> None:
    line = LesserOfWhenPositiveLine(
        TOTAL, ((PART_ONE, D("1500")), (PART_TWO, D("750.50"))), False, False, D("0")
    )

    assert render(line) == (
        "total: lesser of part_one 1500 and part_two 750.5, not all positive = 0"
    )


def test_renders_conditions_that_are_not_met_with_brackets() -> None:
    line = LesserOfWhenPositiveLine(
        TOTAL, ((PART_ONE, D("1500")), (PART_TWO, D("750.50"))), False, True, D("0")
    )

    assert render(line) == (
        "total: lesser of part_one 1500 and part_two 750.5, shown in brackets, not all positive = 0"
    )


def test_renders_a_single_amount_that_is_positive() -> None:
    line = LesserOfWhenPositiveLine(TOTAL, ((PART_ONE, D("12.30")),), True, False, D("12.30"))

    assert render(line) == "total: part_one 12.3 = 12.3"


def test_renders_a_single_amount_that_is_not_positive() -> None:
    line = LesserOfWhenPositiveLine(TOTAL, ((PART_ONE, D("12.30")),), False, False, D("0"))

    assert render(line) == "total: part_one 12.3, not all positive = 0"


# --- amounts chosen by sign ----------------------------
#
# "<output>: <chosen kind> <chosen>, chosen as <sign kind> <sign> is positive|zero|negative";
# an omitted branch: "<output>: 0, no amount when <sign kind> <sign> is positive|zero|negative".


def test_renders_the_amount_chosen_for_a_positive_sign() -> None:
    line = ChosenBySignLine(AMOUNT_CHOSEN, GATE_AMOUNT, D("2.5"), AMOUNT_ALONE, D("1633"))

    assert render(line) == "amount_chosen: amount_alone 1633, chosen as gate_amount 2.5 is positive"


def test_renders_the_amount_chosen_for_a_zero_sign() -> None:
    line = ChosenBySignLine(AMOUNT_CHOSEN, GATE_AMOUNT, D("0.00"), AMOUNT_ALONE, D("1633"))

    assert render(line) == "amount_chosen: amount_alone 1633, chosen as gate_amount 0 is zero"


def test_renders_the_amount_chosen_for_a_negative_sign() -> None:
    line = ChosenBySignLine(AMOUNT_CHOSEN, GATE_AMOUNT, D("-3"), AMOUNT_WITH_FAMILY, D("-250.75"))

    assert render(line) == (
        "amount_chosen: amount_with_family -250.75, chosen as gate_amount -3 is negative"
    )


def test_renders_an_omitted_branch() -> None:
    line = ChosenBySignLine(AMOUNT_CHOSEN, GATE_AMOUNT, D("-3"), None, D("0"))

    assert render(line) == "amount_chosen: 0, no amount when gate_amount -3 is negative"


# --- amounts when one is more than another ----------------------------
#
# "<output>: <amount kind> <amount> if <more kind> <more> is more than <than kind> <than>
# = <result>";
# a gated-off amount reads the same, with its zero result.


def test_renders_an_amount_passed_when_one_figure_is_more_than_another() -> None:
    line = AmountWhenMoreLine(
        ALLOWED_AMOUNT,
        CLAIMED_AMOUNT,
        D("1500.25"),
        GATE_AMOUNT,
        D("70000.01"),
        CLAIM_LIMIT,
        D("70000"),
        D("1500.25"),
    )

    assert render(line) == (
        "allowed_amount: claimed_amount 1500.25 if gate_amount 70000.01 is more than "
        "claim_limit 70000 = 1500.25"
    )


def test_renders_an_amount_gated_off() -> None:
    line = AmountWhenMoreLine(
        ALLOWED_AMOUNT,
        CLAIMED_AMOUNT,
        D("1500.25"),
        GATE_AMOUNT,
        D("70000"),
        CLAIM_LIMIT,
        D("70000"),
        D("0"),
    )

    assert render(line) == (
        "allowed_amount: claimed_amount 1500.25 if gate_amount 70000 is more than "
        "claim_limit 70000 = 0"
    )


def test_renders_an_amount_when_more_without_trailing_zeros() -> None:
    line = AmountWhenMoreLine(
        ALLOWED_AMOUNT,
        CLAIMED_AMOUNT,
        D("1.500E+3"),
        GATE_AMOUNT,
        D("2.0"),
        CLAIM_LIMIT,
        D("1.00"),
        D("1500.00"),
    )

    assert render(line) == (
        "allowed_amount: claimed_amount 1500 if gate_amount 2 is more than claim_limit 1 = 1500"
    )


# --- foreign tax credit (Form T2209 lines 1 to 3) --------------------------------------------


def foreign_country(
    position: int,
    tax_paid: str,
    income: str,
    line_2: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> ForeignTaxCreditLine:
    return ForeignTaxCreditLine(
        NON_COMPLIANT_EXPENSES,
        position,
        D(tax_paid),
        D(income),
        D("100000"),
        D("14000"),
        rounding,
        D(line_2),
        D(result),
    )


def test_renders_one_country_by_position() -> None:
    line = foreign_country(1, "1500", "10000", "1400.00", "1400.00")

    assert render(line) == (
        "non_compliant_expenses: country 1: tax paid 1500, 10000 net foreign income x "
        "14000 basic federal tax / 100000 net income = 1400 (half-up to 0.01); credit 1400"
    )


def test_renders_a_country_whose_tax_paid_is_the_lesser() -> None:
    line = foreign_country(2, "100", "5000", "700.00", "100")

    assert render(line) == (
        "non_compliant_expenses: country 2: tax paid 100, 5000 net foreign income x "
        "14000 basic federal tax / 100000 net income = 700 (half-up to 0.01); credit 100"
    )


def test_renders_a_country_without_rounding() -> None:
    line = foreign_country(1, "100", "0.015", "0.0021", "0.0021", rounding=NO_ROUNDING)

    assert render(line) == (
        "non_compliant_expenses: country 1: tax paid 100, 0.015 net foreign income x "
        "14000 basic federal tax / 100000 net income = 0.0021 (no rounding); credit 0.0021"
    )


def property_tax_line(
    position: int,
    tax_paid: str,
    income: str,
    limit: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> ForeignPropertyTaxLine:
    return ForeignPropertyTaxLine(
        NON_COMPLIANT_EXPENSES,
        position,
        D(tax_paid),
        D(income),
        D("0.15"),
        rounding,
        D(limit),
        D(result),
    )


def test_renders_the_property_tax_over_the_limit_of_a_country() -> None:
    line = property_tax_line(2, "6000", "20000", "3000.00", "3000.00")

    assert render(line) == (
        "non_compliant_expenses: country 2: tax paid on property income 6000, limit 15% of "
        "20000 = 3000 (half-up to 0.01); over the limit 3000"
    )


def test_renders_the_first_country_and_a_tax_under_the_limit() -> None:
    line = property_tax_line(1, "2000", "20000", "3000.00", "0.00")

    assert render(line) == (
        "non_compliant_expenses: country 1: tax paid on property income 2000, limit 15% of "
        "20000 = 3000 (half-up to 0.01); over the limit 0"
    )


def test_renders_the_property_tax_without_rounding() -> None:
    line = property_tax_line(1, "1", "1.10", "0.165", "0.835", rounding=NO_ROUNDING)

    assert render(line) == (
        "non_compliant_expenses: country 1: tax paid on property income 1, limit 15% of "
        "1.1 = 0.165 (no rounding); over the limit 0.835"
    )


def pooled_countries(
    countries: int,
    tax_paid: str,
    income: str,
    line_2: str,
    result: str,
    total_foreign_taxes: str | None = None,
) -> PooledForeignTaxCreditLine:
    return PooledForeignTaxCreditLine(
        NON_COMPLIANT_EXPENSES,
        countries,
        D(tax_paid),
        D(income),
        D("100000"),
        D("14000"),
        D(total_foreign_taxes or tax_paid),
        D("200"),
        CENT,
        D(line_2),
        D(result),
    )


def test_renders_a_pooled_calculation_naming_why_it_is_pooled() -> None:
    line = pooled_countries(2, "200.00", "10100", "1414.00", "200.00")

    assert render(line) == (
        "non_compliant_expenses: all 2 countries pooled, total foreign taxes 200 is not more "
        "than 200: tax paid 200, 10100 net foreign income x 14000 basic federal tax / 100000 "
        "net income = 1414 (half-up to 0.01); credit 200"
    )


def test_renders_a_pooled_calculation_with_business_tax_in_the_foreign_taxes_compared() -> None:
    # Non-business tax paid 150 plus business tax paid 50: the 200 compared with the threshold.
    line = pooled_countries(2, "150.00", "10100", "1414.00", "150.00", total_foreign_taxes="200")

    assert render(line) == (
        "non_compliant_expenses: all 2 countries pooled, total foreign taxes 200 is not more "
        "than 200: tax paid 150, 10100 net foreign income x 14000 basic federal tax / 100000 "
        "net income = 1414 (half-up to 0.01); credit 150"
    )


def test_renders_a_single_country_as_one_country_not_pooled_by_the_threshold() -> None:
    line = pooled_countries(1, "1500", "10000", "1400.00", "1400.00")

    assert render(line) == (
        "non_compliant_expenses: one country: tax paid 1500, 10000 net foreign income x "
        "14000 basic federal tax / 100000 net income = 1400 (half-up to 0.01); credit 1400"
    )


# --- foreign business tax credit (Form T2209 lines 4 to 11) ---------------------------------------


def test_renders_business_line_4() -> None:
    line = ForeignBusinessLine4(NON_COMPLIANT_EXPENSES, 1, D("400.00"), D("50.00"), D("450.00"))

    assert render(line) == (
        "non_compliant_expenses: sheet 1: line 4 = business income tax paid 400 + unused foreign "
        "tax credits 50 = 450"
    )


def test_renders_business_line_5() -> None:
    line = ForeignBusinessLine5(
        NON_COMPLIANT_EXPENSES, 1, D("6000"), D("100000"), D("14500"), CENT, D("870.00")
    )

    assert render(line) == (
        "non_compliant_expenses: sheet 1: line 5 = 6000 net foreign business income x 14500 "
        "basic federal tax / 100000 net income = 870 (half-up to 0.01)"
    )


def test_renders_business_line_5_without_rounding() -> None:
    line = ForeignBusinessLine5(
        NON_COMPLIANT_EXPENSES, 2, D("1"), D("300"), D("100"), NO_ROUNDING, D("0.3333")
    )

    assert render(line) == (
        "non_compliant_expenses: sheet 2: line 5 = 1 net foreign business income x 100 basic "
        "federal tax / 300 net income = 0.3333 (no rounding)"
    )


def test_renders_business_line_7() -> None:
    line = ForeignBusinessLine7(NON_COMPLIANT_EXPENSES, 1, D("870.00"), D("100"), D("970.00"))

    assert render(line) == "non_compliant_expenses: sheet 1: line 7 = line 5 870 + line 6 100 = 970"


def test_renders_business_line_8() -> None:
    line = ForeignBusinessLine8(NON_COMPLIANT_EXPENSES, 3, D("14500"), D("100"), D("14600"))

    assert render(line) == (
        "non_compliant_expenses: sheet 3: line 8 = basic federal tax 14500 + line 6 100 = 14600"
    )


def test_renders_business_line_10() -> None:
    line = ForeignBusinessLine10(NON_COMPLIANT_EXPENSES, 1, D("14500"), D("1400.00"), D("13100"))

    assert render(line) == (
        "non_compliant_expenses: sheet 1: line 10 = line 8 14500 - line 3 1400 = 13100"
    )


def test_renders_a_negative_business_line_10() -> None:
    line = ForeignBusinessLine10(NON_COMPLIANT_EXPENSES, 1, D("100"), D("500"), D("-400"))

    assert render(line) == (
        "non_compliant_expenses: sheet 1: line 10 = line 8 100 - line 3 500 = -400"
    )


def test_renders_business_line_11() -> None:
    line = ForeignBusinessLine11(
        NON_COMPLIANT_EXPENSES, 1, D("450"), D("870.00"), D("13100"), D("450")
    )

    assert render(line) == (
        "non_compliant_expenses: sheet 1: line 11 = least of line 4 450, line 7 870, "
        "line 10 13100 = 450"
    )


# --- provincial foreign tax credit (Form T2036 lines 1 to 5) ----------------------------------


def provincial_sheet(
    position: int,
    tax_paid: str,
    federal_credit: str,
    line_3: str,
    income: str,
    line_4: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> ProvincialForeignTaxCreditLine:
    return ProvincialForeignTaxCreditLine(
        NON_COMPLIANT_EXPENSES,
        position,
        D(tax_paid),
        D(federal_credit),
        D(line_3),
        D(income),
        D("100000"),
        D("5000"),
        rounding,
        D(line_4),
        D(result),
    )


def test_renders_one_sheet_by_position() -> None:
    line = provincial_sheet(1, "1500", "1400.00", "100.00", "10000", "500.00", "100.00")

    assert render(line) == (
        "non_compliant_expenses: sheet 1: tax paid 1500 less federal credit 1400 = 100; "
        "10000 net foreign income x 5000 provincial tax / 100000 net income = 500 "
        "(half-up to 0.01); credit 100"
    )


def test_renders_a_sheet_whose_line_4_is_the_lesser() -> None:
    line = provincial_sheet(2, "1500", "0", "1500", "10000", "500.00", "500.00")

    assert render(line) == (
        "non_compliant_expenses: sheet 2: tax paid 1500 less federal credit 0 = 1500; "
        "10000 net foreign income x 5000 provincial tax / 100000 net income = 500 "
        "(half-up to 0.01); credit 500"
    )


def test_renders_a_sheet_without_rounding() -> None:
    line = provincial_sheet(1, "5", "0", "5", "0.015", "0.00075", "0.00075", rounding=NO_ROUNDING)

    assert render(line) == (
        "non_compliant_expenses: sheet 1: tax paid 5 less federal credit 0 = 5; "
        "0.015 net foreign income x 5000 provincial tax / 100000 net income = 0.00075 "
        "(no rounding); credit 0.00075"
    )


def provincial_minimum_tax_sheet(
    position: int,
    tax_paid: str,
    line_2: str,
    line_3: str,
    income: str,
    line_4: str,
    result: str,
    line_11: str,
    divisor: ExactFraction,
    separate_sheet: bool,
) -> ProvincialForeignTaxCreditLine:
    return ProvincialForeignTaxCreditLine(
        NON_COMPLIANT_EXPENSES,
        position,
        D(tax_paid),
        D(line_2),
        D(line_3),
        D(income),
        D("100000"),
        D("5000"),
        CENT,
        D(line_4),
        D(result),
        D(line_11),
        divisor,
        separate_sheet,
    )


def test_renders_a_sheet_whose_line_2_is_the_one_forms_share_of_the_special_credit() -> None:
    line = provincial_minimum_tax_sheet(
        1, "150", "60.00", "90.00", "10000", "500.00", "90.00", "80", ExactFraction(200), False
    )

    assert render(line) == (
        "non_compliant_expenses: sheet 1: tax paid 150 less minimum tax line 2 60 "
        "(150 tax paid x 80 special foreign tax credit / 200 total tax paid plus business tax, "
        "half-up to 0.01) = 90; "
        "10000 net foreign income x 5000 provincial tax / 100000 net income = 500 "
        "(half-up to 0.01); credit 90"
    )


def test_renders_a_sheet_whose_line_2_is_the_separate_sheet_share_of_the_special_credit() -> None:
    line = provincial_minimum_tax_sheet(
        2, "300", "75.00", "225.00", "10000", "500.00", "225.00", "250", ExactFraction(1000), True
    )

    assert render(line) == (
        "non_compliant_expenses: sheet 2: tax paid 300 less minimum tax line 2 75 "
        "(300 tax paid x 250 special foreign tax credit / 1000 total foreign taxes paid, "
        "separate sheet, half-up to 0.01) = 225; "
        "10000 net foreign income x 5000 provincial tax / 100000 net income = 500 "
        "(half-up to 0.01); credit 225"
    )


def test_a_sheet_without_minimum_tax_keeps_the_federal_credit_wording() -> None:
    line = provincial_sheet(1, "1500", "1400.00", "100.00", "10000", "500.00", "100.00")

    assert "federal credit 1400" in render(line)
    assert "minimum tax" not in render(line)


# T776 Area A "Column 9: Immediate expensing amount for DIEPs (Note 5)": `CcaClaimLine` and
# `ClosingUccLine` name column 9 only when it is above 0; `ImmediateExpensingLine` is line i's line.
CCA_CLAIM = ArtifactKind("ex/cca_claim", Decimal)
CLOSING_UCC = RecordListKind("ex/closing_ucc", fields=(CCA_UCC_AT_END,))
IMMEDIATE_EXPENSING = ArtifactKind("ex/immediate_expensing_claim", Decimal)


def claim_line(column_9: str) -> CcaClaimLine:
    return CcaClaimLine(
        output=CCA_CLAIM,
        position=1,
        class_rate=CLASS_8,
        no_property_left=0,
        column_7=D("6000"),
        column_14=D("0"),
        column_15=D("0"),
        column_16=D("0"),
        column_17=D("0"),
        column_18=D("1000"),
        column_19=D("2000"),
        zero_reason=CcaZeroReason.NONE,
        maximum=D("400.00"),
        rounding=CENT,
        claim=D("3400"),
        column_9=D(column_9),
    )


def closing_line(column_9: str, claim: str, result: str) -> ClosingUccLine:
    return ClosingUccLine(
        CLOSING_UCC,
        1,
        CLASS_8,
        0,
        D("6000"),
        CcaZeroReason.NONE,
        D(claim),
        D(result),
        column_9=D(column_9),
    )


def test_the_claim_line_lists_column_9_after_column_7() -> None:
    assert render(claim_line("3000")) == (
        "cca_claim: item 1 class 8: column 7 6000, column 9 3000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 1000, column 19 2000, "
        "maximum 20% of column 19 = 400 (half-up to 0.01), claim 3400"
    )


def test_the_claim_line_is_unchanged_when_column_9_is_0() -> None:
    assert render(claim_line("0")) == (
        "cca_claim: item 1 class 8: column 7 6000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 1000, column 19 2000, "
        "maximum 20% of column 19 = 400 (half-up to 0.01), claim 3400"
    )


def test_the_claim_line_without_a_column_9_reads_as_one_with_0() -> None:
    without = CcaClaimLine(
        output=CCA_CLAIM,
        position=1,
        class_rate=CLASS_8,
        no_property_left=0,
        column_7=D("6000"),
        column_14=D("0"),
        column_15=D("0"),
        column_16=D("0"),
        column_17=D("0"),
        column_18=D("1000"),
        column_19=D("2000"),
        zero_reason=CcaZeroReason.NONE,
        maximum=D("400.00"),
        rounding=CENT,
        claim=D("3400"),
    )

    assert without == claim_line("0")
    assert without.column_9 == D("0")


def test_the_closing_line_names_the_column_9_in_the_claim() -> None:
    assert render(closing_line("3000", "3400", "2600")) == (
        "closing_ucc: item 1 class 8: column 7 6000 less claim 3400 (including column 9 3000) "
        "= 2600"
    )


def test_the_closing_line_is_unchanged_when_column_9_is_0() -> None:
    assert render(closing_line("0", "2000", "4000")) == (
        "closing_ucc: item 1 class 8: column 7 6000 less claim 2000 = 4000"
    )


def test_column_9_is_the_last_field_of_the_claim_and_closing_lines() -> None:
    assert [f.name for f in fields(CcaClaimLine)][-4:-2] == ["column_9", "half_year_rule_on_sale"]
    # The closing line has one more trailing field, Note 9's personal part.
    assert [f.name for f in fields(ClosingUccLine)][-5:-3] == ["column_9", "half_year_rule_on_sale"]


def expensed_loss_line(column_7: str, column_9: str, result: str) -> TerminalLossLine:
    return TerminalLossLine(
        TERMINAL_LOSS,
        1,
        CLASS_8,
        1,
        D(column_7),
        NONE_LEFT,
        True,
        D(result),
        True,
        column_9=D(column_9),
    )


def test_the_terminal_loss_line_names_the_column_9_it_takes_off() -> None:
    assert render(expensed_loss_line("4000", "1000", "3000")) == (
        "terminal_loss: item 1 class 8: column 7 4000 less column 9 1000 with no property left: "
        "terminal loss 3000"
    )


def test_the_terminal_loss_line_of_a_fully_expensed_class_is_0() -> None:
    assert render(expensed_loss_line("4000", "4000", "0")) == (
        "terminal_loss: item 1 class 8: column 7 4000 less column 9 4000 with no property left: "
        "terminal loss 0"
    )


def test_the_terminal_loss_line_is_unchanged_when_column_9_is_0() -> None:
    assert render(expensed_loss_line("4000", "0", "4000")) == (
        "terminal_loss: item 1 class 8: column 7 4000 with no property left: terminal loss 4000"
    )


def test_the_terminal_loss_line_without_a_column_9_reads_as_one_with_0() -> None:
    without = TerminalLossLine(
        TERMINAL_LOSS, 1, CLASS_8, 1, D("4000"), NONE_LEFT, True, D("4000"), True
    )

    assert without == expensed_loss_line("4000", "0", "4000")
    assert without.column_9 == D("0")


def test_column_9_is_the_last_field_of_the_terminal_loss_line() -> None:
    assert [f.name for f in fields(TerminalLossLine)][-2:] == ["column_9", "half_year_rule_on_sale"]


def test_the_immediate_expensing_line_fields_in_order() -> None:
    assert [f.name for f in fields(ImmediateExpensingLine)] == [
        "output",
        "position",
        "class_rate",
        "column_4",
        "column_6",
        "column_7",
        "column_8",
        "column_9",
    ]


def test_the_immediate_expensing_line_amount_is_column_9() -> None:
    line = ImmediateExpensingLine(
        IMMEDIATE_EXPENSING, 1, CLASS_8, D("4000"), D("0"), D("6000"), D("4000"), D("3000")
    )

    assert line.amount == D("3000")
    assert "amount" not in [f.name for f in fields(line)]


def test_renders_the_immediate_expensing_of_a_class() -> None:
    line = ImmediateExpensingLine(
        IMMEDIATE_EXPENSING, 1, CLASS_8, D("4000.00"), D("0"), D("6000.00"), D("4000.00"), D("3000")
    )

    assert render(line) == (
        "immediate_expensing_claim: item 1 class 8: column 4 4000 less column 6 0, "
        "column 7 6000: column 8 4000, column 9 3000"
    )


def test_renders_a_column_8_cut_by_column_7() -> None:
    line = ImmediateExpensingLine(
        IMMEDIATE_EXPENSING, 2, CLASS_8, D("5000"), D("0"), D("3000"), D("3000"), D("3000")
    )

    assert render(line) == (
        "immediate_expensing_claim: item 2 class 8: column 4 5000 less column 6 0, "
        "column 7 3000: column 8 3000, column 9 3000"
    )


def test_renders_a_column_8_of_0_when_column_6_is_above_column_4() -> None:
    line = ImmediateExpensingLine(
        IMMEDIATE_EXPENSING, 1, CLASS_8, D("1000"), D("1500"), D("1500"), D("0"), D("0")
    )

    assert render(line) == (
        "immediate_expensing_claim: item 1 class 8: column 4 1000 less column 6 1500, "
        "column 7 1500: column 8 0, column 9 0"
    )


# Area A endnote 5 of Forms T776, T2125, T2042 and T2121 limits the total of column 9 to the
# immediate expensing limit; Guides T4002 and T4036: "The deduction is limited to $1.5 million per
# tax year". `ImmediateExpensingAgreedLimitLine` says the statements compared (those claiming
# above 0: the limit list's kind, the position from 1, the claim and the limit) and the agreed
# limit, which is its amount.
AGREED_LIMIT = ArtifactKind("ex/immediate_expensing_agreed_limit", Decimal)
RENTAL_LIMITS = RecordListKind("ex/rental_limits", fields=(CCA_UCC_AT_END,))
BUSINESS_LIMITS = RecordListKind("ex/business_limits", fields=(CCA_UCC_AT_END,))


def test_the_immediate_expensing_agreed_limit_line_fields_in_order() -> None:
    assert [f.name for f in fields(ImmediateExpensingAgreedLimitLine)] == [
        "output",
        "statements",
        "limit",
    ]


def test_the_immediate_expensing_agreed_limit_line_amount_is_the_limit() -> None:
    line = ImmediateExpensingAgreedLimitLine(AGREED_LIMIT, (), D("1500000"))

    assert line.amount == D("1500000")
    assert "amount" not in [f.name for f in fields(line)]


def test_renders_the_statements_compared_and_the_agreed_limit() -> None:
    line = ImmediateExpensingAgreedLimitLine(
        AGREED_LIMIT,
        (
            (RENTAL_LIMITS, 1, D("600000.00"), D("1500000.00")),
            (BUSINESS_LIMITS, 2, D("500000"), D("1500000")),
        ),
        D("1500000.00"),
    )

    assert render(line) == (
        "immediate_expensing_agreed_limit: ex/rental_limits statement 1 claims 600000 under "
        "1500000, ex/business_limits statement 2 claims 500000 under 1500000: "
        "agreed limit 1500000"
    )


def test_renders_one_statement_compared() -> None:
    line = ImmediateExpensingAgreedLimitLine(
        AGREED_LIMIT, ((BUSINESS_LIMITS, 1, D("500000"), D("900000")),), D("900000")
    )

    assert render(line) == (
        "immediate_expensing_agreed_limit: ex/business_limits statement 1 claims 500000 under "
        "900000: agreed limit 900000"
    )


def test_renders_no_statement_claiming_as_a_limit_of_zero() -> None:
    line = ImmediateExpensingAgreedLimitLine(AGREED_LIMIT, (), D("0"))

    assert render(line) == (
        "immediate_expensing_agreed_limit: no statement claims immediate expensing: agreed limit 0"
    )


def test_renders_a_recapture_for_an_excluded_class_with_a_diep() -> None:
    line = RecapturedCcaLine(
        RECAPTURED_CCA,
        1,
        class_rate("10.1", recapture_and_terminal_loss=EXCLUDED),
        D("-2000"),
        NEGATIVE,
        D("2000"),
        True,
    )

    assert render(line) == (
        "recaptured_cca: item 1 class 10.1: column 7 -2000 is negative: recapture 2000"
    )


def test_renders_a_terminal_loss_for_an_excluded_class_with_a_diep() -> None:
    line = TerminalLossLine(
        TERMINAL_LOSS,
        1,
        class_rate("10.1", recapture_and_terminal_loss=EXCLUDED),
        1,
        D("6000"),
        NONE_LEFT,
        True,
        D("6000"),
        True,
    )

    assert render(line) == (
        "terminal_loss: item 1 class 10.1: column 7 6000 with no property left: terminal loss 6000"
    )


# Guides T4036 and T4002, "Column 19 - Base amount for CCA": "This is known as the half-year rule on
# sale." A Class 10.1 row that used it says so on the lines whose figures it changes: column 19 of
# the claim, the terminal loss it does not have and the closing UCC it does not zero.


def sale_class() -> ClassRate:
    return ClassRate(
        D("10.1"),
        Rate(D("0.30")),
        HalfYearRule.APPLIES,
        EXCLUDED,
        Fraction(0, 1),
        Fraction(1, 2),
        HalfYearRuleOnSale.APPLIES,
    )


def sale_claim_line(half_year_rule_on_sale: bool = True) -> CcaClaimLine:
    return CcaClaimLine(
        output=CCA_CLAIM,
        position=1,
        class_rate=sale_class(),
        no_property_left=1,
        column_7=D("8000.00"),
        column_14=D("12000.00"),
        column_15=D("0"),
        column_16=D("12000.00"),
        column_17=D("0"),
        column_18=D("0"),
        column_19=D("10000.00"),
        zero_reason=CcaZeroReason.NONE,
        maximum=D("3000.00"),
        rounding=CENT,
        claim=D("3000.00"),
        half_year_rule_on_sale=half_year_rule_on_sale,
    )


def test_the_claim_line_names_the_half_year_rule_on_sale_at_column_19() -> None:
    assert render(sale_claim_line()) == (
        "cca_claim: item 1 class 10.1: column 7 8000, column 14 12000, column 15 0, "
        "column 16 12000, column 17 0, column 18 0, column 19 10000 (half-year rule on sale), "
        "maximum 30% of column 19 = 3000 (half-up to 0.01), claim 3000"
    )


def test_the_claim_line_does_not_limit_a_sale_rows_maximum_to_column_7() -> None:
    line = replace(sale_claim_line(), column_7=D("10"))

    assert render(line) == (
        "cca_claim: item 1 class 10.1: column 7 10, column 14 12000, column 15 0, "
        "column 16 12000, column 17 0, column 18 0, column 19 10000 (half-year rule on sale), "
        "maximum 30% of column 19 = 3000 (half-up to 0.01), claim 3000"
    )


def test_the_claim_line_of_a_sale_row_with_a_negative_column_7_shows_the_maximum() -> None:
    line = replace(
        sale_claim_line(), column_7=D("-5000"), zero_reason=CcaZeroReason.COLUMN_7_NEGATIVE
    )

    assert "maximum 30% of column 19 = 3000" in render(line)


def test_the_claim_line_is_unchanged_without_the_half_year_rule_on_sale() -> None:
    assert render(sale_claim_line(False)) == (
        "cca_claim: item 1 class 10.1: column 7 8000, column 14 12000, column 15 0, "
        "column 16 12000, column 17 0, column 18 0, column 19 10000, "
        "maximum 30% of column 19 = 3000 (half-up to 0.01), claim 3000"
    )


def test_the_claim_line_names_column_9_and_the_half_year_rule_on_sale() -> None:
    line = replace(sale_claim_line(), column_9=D("1000"))

    assert render(line) == (
        "cca_claim: item 1 class 10.1: column 7 8000, column 9 1000, column 14 12000, "
        "column 15 0, column 16 12000, column 17 0, column 18 0, "
        "column 19 10000 (half-year rule on sale), "
        "maximum 30% of column 19 = 3000 (half-up to 0.01), claim 3000"
    )


def test_the_closing_line_names_the_half_year_rule_on_sale_in_the_claim() -> None:
    line = ClosingUccLine(
        CLOSING_UCC,
        1,
        sale_class(),
        1,
        D("8000.00"),
        CcaZeroReason.NONE,
        D("3000.00"),
        D("0"),
        half_year_rule_on_sale=True,
    )

    assert render(line) == (
        "closing_ucc: item 1 class 10.1: column 7 8000 less claim 3000 (half-year rule on sale), "
        "the rest is not deductible later: 0"
    )


def test_the_closing_line_is_unchanged_without_the_half_year_rule_on_sale() -> None:
    line = ClosingUccLine(
        CLOSING_UCC,
        1,
        sale_class(),
        1,
        D("8000.00"),
        CcaZeroReason.NONE,
        D("3000.00"),
        D("5000.00"),
    )

    assert render(line) == "closing_ucc: item 1 class 10.1: column 7 8000 less claim 3000 = 5000"


def test_the_terminal_loss_line_names_the_half_year_rule_on_sale() -> None:
    line = TerminalLossLine(
        output=TERMINAL_LOSS,
        position=1,
        class_rate=sale_class(),
        no_property_left=1,
        column_7=D("8000.00"),
        zero_reason=CcaZeroReason.NONE,
        column_7_positive=True,
        result=D("0"),
        half_year_rule_on_sale=True,
    )

    assert render(line) == (
        "terminal_loss: item 1 class 10.1: column 7 8000 with no property left, but a terminal "
        "loss does not apply to class 10.1 (half-year rule on sale used): terminal loss 0"
    )


# --- Form T2091(IND) Part 2: one sentence per computed line, 27 to 53 ----------------------------
#
# Each sentence: the output's label, "property <position>: line <n> <result> = <the figures named
# after the form lines>". A step the form says not to complete reads "line <n> not completed, 0".


def part_2_line_examples() -> list[tuple[object, str]]:
    """Each Part 2 line class with an example figure, and its English sentence."""
    return [
        (
            PrincipalResidenceLine27(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_12=D("90000.00"),
                line_11=D("40000.00"),
                result=D("50000.00"),
            ),
            "residence_gain: property 1: line 27 50000 = line 12 90000 less line 11 40000",
        ),
        (
            PrincipalResidenceLine27(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_12=D("30000.00"),
                line_11=D("40000.00"),
                result=D("-10000.00"),
            ),
            "residence_gain: property 1: line 27 -10000 = line 12 30000 less line 11 40000",
        ),
        (
            PrincipalResidenceLine29(
                RESIDENCE_GAIN, 1, completed=True, line_2=1, plus_one=1, result=D("2")
            ),
            "residence_gain: property 1: line 29 2 = line 2 1 plus 1",
        ),
        (
            PrincipalResidenceLine30(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_27=D("50000.00"),
                line_29=D("2"),
                result=D("100000.00"),
            ),
            "residence_gain: property 1: line 30 100000 = line 27 50000 times line 29 2",
        ),
        (
            PrincipalResidenceLine32(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_30=D("100000.00"),
                line_6=4,
                rounding=CENT,
                result=D("25000.00"),
            ),
            "residence_gain: property 1: line 32 25000 = line 30 100000 divided by line 6 4 "
            "(half-up to 0.01)",
        ),
        (
            PrincipalResidenceLine33(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_27=D("50000.00"),
                line_32=D("25000.00"),
                result=D("25000.00"),
            ),
            "residence_gain: property 1: line 33 25000 = line 27 50000 less line 32 25000, not "
            "below 0",
        ),
        (
            PrincipalResidenceLine38(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_12=D("90000.00"),
                line_13=D("10000.00"),
                line_9=D("5000.00"),
                result=D("105000.00"),
            ),
            "residence_gain: property 1: line 38 105000 = line 12 90000 plus line 13 10000 plus "
            "line 9 5000",
        ),
        (
            PrincipalResidenceLine39(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_8=D("300000.00"),
                line_38=D("105000.00"),
                result=D("195000.00"),
            ),
            "residence_gain: property 1: line 39 195000 = line 8 300000 less line 38 105000",
        ),
        (
            PrincipalResidenceLine42(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_39=D("195000.00"),
                line_1=6,
                result=D("1170000.00"),
            ),
            "residence_gain: property 1: line 42 1170000 = line 39 195000 times line 1 6",
        ),
        (
            PrincipalResidenceLine44(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_42=D("1170000.00"),
                line_5=10,
                rounding=NO_ROUNDING,
                result=D("117000.00"),
            ),
            "residence_gain: property 1: line 44 117000 = line 42 1170000 divided by line 5 10 "
            "(no rounding)",
        ),
        (
            PrincipalResidenceLine45(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_39=D("195000.00"),
                line_44=D("117000.00"),
                result=D("78000.00"),
            ),
            "residence_gain: property 1: line 45 78000 = line 39 195000 less line 44 117000, not "
            "below 0",
        ),
        (
            PrincipalResidenceLine48(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_12=D("90000.00"),
                line_8=D("300000.00"),
                result=D("0"),
            ),
            "residence_gain: property 1: line 48 0 = line 12 90000 less line 8 300000, not below 0",
        ),
        (
            PrincipalResidenceLine51(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_33=D("25000.00"),
                line_45=D("78000.00"),
                result=D("103000.00"),
            ),
            "residence_gain: property 1: line 51 103000 = line 33 25000 plus line 45 78000",
        ),
        (
            PrincipalResidenceLine53(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_51=D("103000.00"),
                line_48=D("0"),
                result=D("103000.00"),
            ),
            "residence_gain: property 1: line 53 103000 = line 51 103000 less line 48 0, not "
            "below 0",
        ),
    ]


PART_2_EXAMPLES = part_2_line_examples()


@pytest.mark.parametrize(("line", "text"), PART_2_EXAMPLES)
def test_renders_each_part_2_line_in_its_form_words(line: object, text: str) -> None:
    assert render(cast(TraceLine, line)) == text


def _has_completed_flag(line: object) -> bool:
    return "completed" in [f.name for f in fields(cast(Any, line))]


@pytest.mark.parametrize(
    "line",
    [example for example, _text in PART_2_EXAMPLES if _has_completed_flag(example)],
)
def test_renders_a_step_not_completed_as_zero_whatever_its_figures(line: object) -> None:
    # The figures the line names are still on the line, but the form's step is not completed.
    skipped = replace(cast(Any, line), completed=False, result=D("0"), position=2)

    assert render(skipped) == (
        f"residence_gain: property 2: line {_line_number(skipped)} not completed, 0"
    )


def _line_number(line: object) -> int:
    return int(type(line).__name__.removeprefix("PrincipalResidenceLine"))


# --- Form T2091(IND)-WS and Part 4: one sentence per worksheet line, and for lines 56 and 57 ------
#
# A worksheet line is named "worksheet line N" and the form's line by its number alone ("line 56",
# "line 57", "T2091 line 2" for the form's line 2 read by the worksheet). A line not completed reads
# "not completed, 0"; line 57 has no such flag.


def worksheet_line_examples() -> list[tuple[object, str]]:
    """Each worksheet and Part 4 line class with an example figure, and its English sentence."""
    return [
        (
            PrincipalResidenceWorksheetLine3(
                RESIDENCE_GAIN, 1, completed=True, line_1=5, line_2=0, result=D("5")
            ),
            "residence_gain: property 1: worksheet line 3 5 = worksheet line 1 5 "
            "plus T2091 line 2 0",
        ),
        (
            PrincipalResidenceWorksheetLine6(
                RESIDENCE_GAIN, 1, completed=True, line_4=12, line_5=0, result=D("12")
            ),
            "residence_gain: property 1: worksheet line 6 12 = worksheet line 4 12 "
            "plus T2091 line 6 0",
        ),
        (
            PrincipalResidenceWorksheetLine16(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_14=D("200000.00"),
                factor=D("1.1"),
                rounding=CENT,
                result=D("220000.00"),
            ),
            "residence_gain: property 1: worksheet line 16 220000 = worksheet line 14 200000 times "
            "1.1 (half-up to 0.01)",
        ),
        (
            PrincipalResidenceWorksheetLine17(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_15=D("230000.00"),
                line_16=D("220000.00"),
                result=D("10000.00"),
            ),
            "residence_gain: property 1: worksheet line 17 10000 = worksheet line 15 230000 less "
            "worksheet line 16 220000, not below 0",
        ),
        (
            PrincipalResidenceWorksheetLine18(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_14=D("200000.00"),
                line_17=D("10000.00"),
                result=D("190000.00"),
            ),
            "residence_gain: property 1: worksheet line 18 190000 = worksheet line 14 200000 less "
            "worksheet line 17 10000",
        ),
        (
            PrincipalResidenceWorksheetLine18(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_14=D("200000.00"),
                line_17=D("280000.00"),
                result=D("-80000.00"),
            ),
            "residence_gain: property 1: worksheet line 18 -80000 = worksheet line 14 200000 less "
            "worksheet line 17 280000",
        ),
        (
            PrincipalResidenceWorksheetLine19(
                RESIDENCE_GAIN,
                1,
                completed=True,
                chart_completed=True,
                line_18=D("190000.00"),
                line_10=D("200000.00"),
                result=D("190000.00"),
            ),
            "residence_gain: property 1: worksheet line 19 190000 = worksheet line 18 190000 "
            "(Chart 1 completed)",
        ),
        (
            PrincipalResidenceWorksheetLine19(
                RESIDENCE_GAIN,
                1,
                completed=True,
                chart_completed=False,
                line_18=D("0"),
                line_10=D("200000.00"),
                result=D("200000.00"),
            ),
            "residence_gain: property 1: worksheet line 19 200000 = worksheet line 10 200000 "
            "(Chart 1 not completed)",
        ),
        (
            PrincipalResidenceWorksheetLine21(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_19=D("190000.00"),
                line_20=D("100000.00"),
                result=D("90000.00"),
            ),
            "residence_gain: property 1: worksheet line 21 90000 = worksheet line 19 190000 less "
            "worksheet line 20 100000",
        ),
        (
            PrincipalResidenceWorksheetLine23(
                RESIDENCE_GAIN, 1, completed=True, line_3=5, plus_one=1, result=D("6")
            ),
            "residence_gain: property 1: worksheet line 23 6 = worksheet line 3 5 plus 1",
        ),
        (
            PrincipalResidenceWorksheetLine24(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_22=D("90000.00"),
                line_23=6,
                result=D("540000.00"),
            ),
            "residence_gain: property 1: worksheet line 24 540000 = worksheet line 22 90000 times "
            "worksheet line 23 6",
        ),
        (
            PrincipalResidenceWorksheetLine26(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_24=D("540000.00"),
                line_25=12,
                rounding=CENT,
                result=D("45000.00"),
            ),
            "residence_gain: property 1: worksheet line 26 45000 = worksheet line 24 "
            "540000 divided by worksheet line 25 12 (half-up to 0.01)",
        ),
        (
            PrincipalResidenceWorksheetLine27(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_21=D("90000.00"),
                line_26=D("45000.00"),
                result=D("45000.00"),
            ),
            "residence_gain: property 1: worksheet line 27 45000 = worksheet line 21 90000 less "
            "worksheet line 26 45000",
        ),
        (
            PrincipalResidenceWorksheetLine59(
                RESIDENCE_GAIN,
                1,
                completed=True,
                part_2_completed=False,
                line_27=D("45000.00"),
                line_58=D("30000.00"),
                result=D("45000.00"),
            ),
            "residence_gain: property 1: worksheet line 59 45000 = worksheet line 27 45000",
        ),
        (
            PrincipalResidenceWorksheetLine61(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_59=D("45000.00"),
                line_60=24,
                result=D("1080000.00"),
            ),
            "residence_gain: property 1: worksheet line 61 1080000 = worksheet line 59 45000 times "
            "worksheet line 60 24",
        ),
        (
            PrincipalResidenceWorksheetLine63(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_61=D("1080000.00"),
                line_62=74,
                rounding=CENT,
                result=D("14594.59"),
            ),
            "residence_gain: property 1: worksheet line 63 14594.59 = worksheet line 61 1080000 "
            "divided by worksheet line 62 74 (half-up to 0.01)",
        ),
        (
            PrincipalResidenceWorksheetLine64(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_59=D("45000.00"),
                line_63=D("14594.59"),
                result=D("30405.41"),
            ),
            "residence_gain: property 1: worksheet line 64 30405.41 = worksheet line 59 45000 less "
            "worksheet line 63 14594.59",
        ),
        (
            PrincipalResidenceWorksheetLine30(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_28=D("240000.00"),
                line_29=D("120000.00"),
                result=D("120000.00"),
            ),
            "residence_gain: property 1: worksheet line 30 120000 = worksheet line 28 240000 less "
            "worksheet line 29 120000",
        ),
        (
            PrincipalResidenceWorksheetLine32(
                RESIDENCE_GAIN, 1, completed=True, line_2=1, plus_one=1, result=D("2")
            ),
            "residence_gain: property 1: worksheet line 32 2 = worksheet line 2 1 plus 1",
        ),
        (
            PrincipalResidenceWorksheetLine33(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_31=D("120000.00"),
                line_32=2,
                result=D("240000.00"),
            ),
            "residence_gain: property 1: worksheet line 33 240000 = worksheet line 31 120000 times "
            "worksheet line 32 2",
        ),
        (
            PrincipalResidenceWorksheetLine35(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_33=D("240000.00"),
                line_34=4,
                rounding=CENT,
                result=D("60000.00"),
            ),
            "residence_gain: property 1: worksheet line 35 60000 = worksheet line 33 240000 "
            "divided by worksheet line 34 4 (half-up to 0.01)",
        ),
        (
            PrincipalResidenceWorksheetLine36(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_30=D("120000.00"),
                line_35=D("60000.00"),
                result=D("60000.00"),
            ),
            "residence_gain: property 1: worksheet line 36 60000 = worksheet line 30 120000 less "
            "worksheet line 35 60000, not below 0",
        ),
        (
            PrincipalResidenceWorksheetLine40(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_38=D("240000.00"),
                line_39=D("6000.00"),
                result=D("246000.00"),
            ),
            "residence_gain: property 1: worksheet line 40 246000 = worksheet line 38 240000 plus "
            "worksheet line 39 6000",
        ),
        (
            PrincipalResidenceWorksheetLine41(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_37=D("300000.00"),
                line_40=D("246000.00"),
                result=D("54000.00"),
            ),
            "residence_gain: property 1: worksheet line 41 54000 = worksheet line 37 300000 less "
            "worksheet line 40 246000",
        ),
        (
            PrincipalResidenceWorksheetLine44(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_42=D("54000.00"),
                line_43=4,
                result=D("216000.00"),
            ),
            "residence_gain: property 1: worksheet line 44 216000 = worksheet line 42 54000 times "
            "worksheet line 43 4",
        ),
        (
            PrincipalResidenceWorksheetLine46(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_44=D("216000.00"),
                line_45=13,
                rounding=CENT,
                result=D("16615.38"),
            ),
            "residence_gain: property 1: worksheet line 46 16615.38 = worksheet line 44 216000 "
            "divided by worksheet line 45 13 (half-up to 0.01)",
        ),
        (
            PrincipalResidenceWorksheetLine47(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_41=D("54000.00"),
                line_46=D("16615.38"),
                result=D("37384.62"),
            ),
            "residence_gain: property 1: worksheet line 47 37384.62 = worksheet line 41 54000 less "
            "worksheet line 46 16615.38, not below 0",
        ),
        (
            PrincipalResidenceWorksheetLine50(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_48=D("360000.00"),
                line_49=D("290000.00"),
                result=D("70000.00"),
            ),
            "residence_gain: property 1: worksheet line 50 70000 = worksheet line 48 360000 less "
            "worksheet line 49 290000, not below 0",
        ),
        (
            PrincipalResidenceWorksheetLine53(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_51=D("60000.00"),
                line_52=D("37384.62"),
                result=D("97384.62"),
            ),
            "residence_gain: property 1: worksheet line 53 97384.62 = worksheet line 51 60000 plus "
            "worksheet line 52 37384.62",
        ),
        (
            PrincipalResidenceWorksheetLine55(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_53=D("97384.62"),
                line_54=D("0"),
                result=D("97384.62"),
            ),
            "residence_gain: property 1: worksheet line 55 97384.62 = worksheet line 53 97384.62 "
            "less worksheet line 54 0, not below 0",
        ),
        (
            PrincipalResidenceWorksheetLine58(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_56=D("58235.29"),
                line_57=D("97384.62"),
                result=D("58235.29"),
            ),
            "residence_gain: property 1: worksheet line 58 58235.29 = lesser of worksheet line 56 "
            "58235.29 and worksheet line 57 97384.62",
        ),
        (
            PrincipalResidenceWorksheetLine66(
                RESIDENCE_GAIN,
                1,
                completed=True,
                line_64=D("30405.41"),
                line_65=D("100000.00"),
                result=D("30405.41"),
            ),
            "residence_gain: property 1: worksheet line 66 30405.41 = lesser of worksheet line 64 "
            "30405.41 and worksheet line 65 100000",
        ),
        (
            PrincipalResidenceLine56(
                RESIDENCE_GAIN, 1, completed=True, line_66=D("30405.41"), result=D("30405.41")
            ),
            "residence_gain: property 1: line 56 30405.41 = worksheet line 66 30405.41",
        ),
        (
            PrincipalResidenceLine57(
                RESIDENCE_GAIN,
                1,
                line_55=D("150000.00"),
                line_56=D("30405.41"),
                result=D("119594.59"),
            ),
            "residence_gain: property 1: line 57 119594.59 = line 55 150000 less line 56 30405.41, "
            "not below 0",
        ),
    ]


WORKSHEET_LINE_EXAMPLES = worksheet_line_examples()


@pytest.mark.parametrize(("line", "text"), WORKSHEET_LINE_EXAMPLES)
def test_renders_each_worksheet_and_part_4_line_in_its_form_words(line: object, text: str) -> None:
    assert render(cast(TraceLine, line)) == text


def test_renders_line_59_as_line_58_when_part_2_is_completed() -> None:
    line = PrincipalResidenceWorksheetLine59(
        RESIDENCE_GAIN,
        1,
        completed=True,
        part_2_completed=True,
        line_27=D("58235.29"),
        line_58=D("10000.00"),
        result=D("10000.00"),
    )

    assert render(line) == (
        "residence_gain: property 1: worksheet line 59 10000 = worksheet line 58 10000 "
        "(Part 2 completed)"
    )


def test_renders_line_59_as_line_27_when_part_2_is_not_completed() -> None:
    line = PrincipalResidenceWorksheetLine59(
        RESIDENCE_GAIN,
        1,
        completed=True,
        part_2_completed=False,
        line_27=D("80666.67"),
        line_58=D("0"),
        result=D("80666.67"),
    )

    assert render(line) == (
        "residence_gain: property 1: worksheet line 59 80666.67 = worksheet line 27 80666.67"
    )


@pytest.mark.parametrize(
    "line",
    [example for example, _text in WORKSHEET_LINE_EXAMPLES if _has_completed_flag(example)],
)
def test_renders_a_worksheet_or_line_56_step_not_completed_as_zero(line: object) -> None:
    skipped = replace(cast(Any, line), completed=False, result=D("0"), position=2)
    name = type(line).__name__
    if name.startswith("PrincipalResidenceWorksheetLine"):
        label = f"worksheet line {name.removeprefix('PrincipalResidenceWorksheetLine')}"
    else:
        label = f"line {name.removeprefix('PrincipalResidenceLine')}"

    assert render(skipped) == f"residence_gain: property 2: {label} not completed, 0"


def test_renders_the_part_2_total_of_the_properties_by_position() -> None:
    line = ItemsTotalLine(RESIDENCE_GAIN, ((1, D("25000.00")), (2, D("0"))), D("25000.00"))

    assert render(line) == "residence_gain: item 1 25000 + item 2 0 = 25000"


# Guide T4002 "You were asking?": "Since your fiscal period is less than 365 days, you have to
# prorate your CCA claim. ... base your CCA claim on the number of days in your fiscal period
# compared to 365 days. In this case, your fiscal period is 214 days. Suppose you calculate your
# CCA to be $3,500. The amount of CCA you can claim is $2,052 ($3,500 × 214 ÷ 365)." A claim line
# and a closing UCC line of a prorated row say so; the claim line's maximum is the prorated one, and
# the unprorated 20% of column 19 (3,500.00) is worked again from column 19 as the capped one is.


def prorated_claim_line(fiscal_period_days: int = 214) -> CcaClaimLine:
    return CcaClaimLine(
        output=CCA_CLAIM,
        position=1,
        class_rate=class_rate("8", "0.20"),
        no_property_left=0,
        column_7=D("17500.00"),
        column_14=D("0"),
        column_15=D("0"),
        column_16=D("0"),
        column_17=D("0"),
        column_18=D("0"),
        column_19=D("17500.00"),
        zero_reason=CcaZeroReason.NONE,
        maximum=D("2052.05"),
        rounding=CENT,
        claim=D("2052.05"),
        fiscal_period_days=fiscal_period_days,
    )


def test_the_claim_line_shows_the_proration_of_a_short_fiscal_period() -> None:
    assert render(prorated_claim_line()) == (
        "cca_claim: item 1 class 8: column 7 17500, column 14 0, column 15 0, column 16 0, "
        "column 17 0, column 18 0, column 19 17500, "
        "maximum 20% of column 19 = 3500 (half-up to 0.01), prorated 214/365 = 2052.05, "
        "claim 2052.05"
    )


def test_the_claim_line_shows_no_proration_for_a_full_year() -> None:
    line = replace(
        prorated_claim_line(365), maximum=D("3500.00"), claim=D("3500.00"), fiscal_period_days=365
    )

    assert render(line) == (
        "cca_claim: item 1 class 8: column 7 17500, column 14 0, column 15 0, column 16 0, "
        "column 17 0, column 18 0, column 19 17500, "
        "maximum 20% of column 19 = 3500 (half-up to 0.01), claim 3500"
    )


def test_the_claim_line_shows_the_proration_of_one_day() -> None:
    line = replace(prorated_claim_line(1), maximum=D("9.59"), claim=D("9.59"))

    assert render(line).endswith(
        "maximum 20% of column 19 = 3500 (half-up to 0.01), prorated 1/365 = 9.59, claim 9.59"
    )


def test_the_claim_line_shows_column_9_and_the_proration() -> None:
    line = replace(prorated_claim_line(), column_9=D("1000"), claim=D("3052.05"))

    assert render(line) == (
        "cca_claim: item 1 class 8: column 7 17500, column 9 1000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 0, column 19 17500, "
        "maximum 20% of column 19 = 3500 (half-up to 0.01), prorated 214/365 = 2052.05, "
        "claim 3052.05"
    )


def prorated_closing_line(fiscal_period_days: int = 214) -> ClosingUccLine:
    return ClosingUccLine(
        CLOSING_UCC,
        1,
        class_rate("8", "0.20"),
        0,
        D("17500.00"),
        CcaZeroReason.NONE,
        D("2052.05"),
        D("15447.95"),
        fiscal_period_days=fiscal_period_days,
    )


def test_the_closing_line_names_the_proration_in_the_claim() -> None:
    assert render(prorated_closing_line()) == (
        "closing_ucc: item 1 class 8: column 7 17500 less claim 2052.05 (prorated 214/365) = "
        "15447.95"
    )


def test_the_closing_line_is_unchanged_for_a_full_year() -> None:
    assert render(prorated_closing_line(365)) == (
        "closing_ucc: item 1 class 8: column 7 17500 less claim 2052.05 = 15447.95"
    )


# T776 Area A Note 9: "you must subtract any remaining personal part of this property's cost from
# the UCC at the end of the year". The closing line names the part after the claim, only when it is
# above 0; the claim line is unchanged. Row P: Class 1 (4%), column 7 60,000, claim 2,400, part
# 5,000: 60,000 - 2,400 - 5,000 = 52,600.


def personal_part_line(
    part: str = "5000", claim: str = "2400", result: str = "52600"
) -> ClosingUccLine:
    return ClosingUccLine(
        CLOSING_UCC,
        1,
        class_rate("1", "0.04"),
        0,
        D("60000"),
        CcaZeroReason.NONE,
        D(claim),
        D(result),
        personal_part_remaining=D(part),
    )


def test_the_closing_line_names_the_remaining_personal_part_after_the_claim() -> None:
    assert render(personal_part_line()) == (
        "closing_ucc: item 1 class 1: column 7 60000 less claim 2400 less personal part 5000 "
        "= 52600"
    )


def test_the_closing_line_names_a_part_with_cents() -> None:
    assert render(personal_part_line("5000.50", "2400", "52599.50")) == (
        "closing_ucc: item 1 class 1: column 7 60000 less claim 2400 less personal part 5000.5 "
        "= 52599.5"
    )


def test_the_closing_line_is_unchanged_when_the_part_is_0() -> None:
    assert render(personal_part_line("0", "2400", "57600")) == (
        "closing_ucc: item 1 class 1: column 7 60000 less claim 2400 = 57600"
    )


def test_the_closing_line_without_a_part_reads_as_one_with_0() -> None:
    without = ClosingUccLine(
        CLOSING_UCC,
        1,
        class_rate("1", "0.04"),
        0,
        D("60000"),
        CcaZeroReason.NONE,
        D("2400"),
        D("57600"),
    )

    assert without == personal_part_line("0", "2400", "57600")
    assert without.personal_part_remaining == D("0")


def test_the_closing_line_names_the_part_after_the_claims_notes() -> None:
    line = replace(
        personal_part_line("1000", "3400", "1600"),
        class_rate=CLASS_8,
        column_7=D("6000"),
        column_9=D("3000"),
        fiscal_period_days=214,
    )

    assert render(line) == (
        "closing_ucc: item 1 class 8: column 7 6000 less claim 3400 (prorated 214/365) "
        "(including column 9 3000) less personal part 1000 = 1600"
    )


def test_a_closing_line_at_zero_does_not_name_a_part() -> None:
    line = replace(
        personal_part_line("0", "0", "0"),
        zero_reason=CcaZeroReason.NO_PROPERTY_LEFT,
        claim=D("0"),
    )

    assert render(line) == "closing_ucc: item 1 class 1: column 7 60000 with no property left: 0"


# A dataset whose full year is 366 days: the line carries it, and a line is prorated when its days
# are not the dataset's.


def test_the_claim_line_of_a_366_day_dataset_unprorated_shows_no_proration() -> None:
    line = replace(
        prorated_claim_line(366), maximum=D("3500.00"), claim=D("3500.00"), full_year_days=366
    )

    assert render(line).endswith("maximum 20% of column 19 = 3500 (half-up to 0.01), claim 3500")


def test_the_claim_line_of_a_366_day_dataset_prorated_at_365_shows_the_proration() -> None:
    line = replace(
        prorated_claim_line(365), maximum=D("3490.44"), claim=D("3490.44"), full_year_days=366
    )

    assert render(line).endswith(
        "maximum 20% of column 19 = 3500 (half-up to 0.01), prorated 365/366 = 3490.44, "
        "claim 3490.44"
    )


def test_the_claim_line_of_a_366_day_dataset_prorated_at_214_shows_its_days() -> None:
    line = replace(
        prorated_claim_line(214), maximum=D("2046.45"), claim=D("2046.45"), full_year_days=366
    )

    assert render(line).endswith("prorated 214/366 = 2046.45, claim 2046.45")


def test_the_closing_line_of_a_366_day_dataset_names_the_proration_against_its_days() -> None:
    prorated = replace(prorated_closing_line(365), full_year_days=366)
    full = replace(prorated_closing_line(366), full_year_days=366)

    assert "less claim 2052.05 (prorated 365/366) =" in render(prorated)
    assert "prorated" not in render(full)


# Guide T4002 "You were asking?": "Since your fiscal period is less than 365 days, you have to
# prorate your CCA claim. ... In this case, your fiscal period is 214 days." `FiscalPeriodDaysLine`
# says the days the caller entered and the days of the fiscal period that the claim is prorated by;
# no days entered is a full year of the dataset's days.
FISCAL_PERIOD_DAYS = ArtifactKind("ex/fiscal_period_days", int)


def test_renders_the_days_entered_as_the_fiscal_period() -> None:
    line = FiscalPeriodDaysLine(FISCAL_PERIOD_DAYS, 214, 214, 365)

    assert render(line) == "fiscal_period_days: entered 214, fiscal period 214 days"


def test_renders_no_days_entered_as_a_full_year() -> None:
    line = FiscalPeriodDaysLine(FISCAL_PERIOD_DAYS, 0, 365, 365)

    assert render(line) == "fiscal_period_days: entered 0, a full year of 365 days"


def test_renders_365_days_entered_as_the_fiscal_period() -> None:
    line = FiscalPeriodDaysLine(FISCAL_PERIOD_DAYS, 365, 365, 365)

    assert render(line) == "fiscal_period_days: entered 365, fiscal period 365 days"


def test_renders_a_full_year_of_a_366_day_dataset() -> None:
    line = FiscalPeriodDaysLine(FISCAL_PERIOD_DAYS, 0, 366, 366)

    assert render(line) == "fiscal_period_days: entered 0, a full year of 366 days"


# T2125 page 1 "Fiscal period From / to, Date (YYYYMMDD)": `FiscalPeriodDaysFromDatesLine` says the
# two dates entered and the days of the period from them; 0 and 0 is no dates entered, a full year.


def test_renders_the_fiscal_period_from_its_dates() -> None:
    line = FiscalPeriodDaysFromDatesLine(FISCAL_PERIOD_DAYS, 20250601, 20251231, 214, 365)

    assert render(line) == "fiscal_period_days: from 20250601 to 20251231, fiscal period 214 days"


def test_renders_365_days_from_its_dates_as_the_fiscal_period() -> None:
    line = FiscalPeriodDaysFromDatesLine(FISCAL_PERIOD_DAYS, 20250101, 20251231, 365, 365)

    assert render(line) == "fiscal_period_days: from 20250101 to 20251231, fiscal period 365 days"


def test_renders_a_leap_year_period_from_its_dates() -> None:
    line = FiscalPeriodDaysFromDatesLine(FISCAL_PERIOD_DAYS, 20240201, 20250131, 366, 365)

    assert render(line) == "fiscal_period_days: from 20240201 to 20250131, fiscal period 366 days"


def test_renders_no_dates_entered_as_a_full_year() -> None:
    line = FiscalPeriodDaysFromDatesLine(FISCAL_PERIOD_DAYS, 0, 0, 365, 365)

    assert render(line) == "fiscal_period_days: no dates entered, a full year of 365 days"


# Income Tax Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation year
# that is less than 51 weeks, its immediate expensing limit for the year is that proportion of its
# immediate expensing limit for the year determined without reference to this paragraph that the
# number of days in the year is of 365". `ProratedByDaysLine` prints the amount with its label and
# value, the days of the fiscal period with their label, the days of a full year and the result,
# and says whether the year was prorated: a year below the 357 days of the figure is prorated, any
# other year is not and its result is the amount.
UNPRORATED_LIMIT = ArtifactKind("ex/unprorated_limit", Decimal)
PRORATED_LIMIT = ArtifactKind("ex/prorated_limit", Decimal)
SHORT_YEAR_DAYS = ArtifactKind("ex/short_year_days", Decimal)


def test_renders_an_amount_prorated_by_the_days_of_the_fiscal_period() -> None:
    line = ProratedByDaysLine(
        PRORATED_LIMIT,
        UNPRORATED_LIMIT,
        D("1500000"),
        FISCAL_PERIOD_DAYS,
        153,
        365,
        SHORT_YEAR_DAYS,
        D("357"),
        D("628767.12"),
    )

    assert render(line) == (
        "prorated_limit: unprorated_limit 1500000 × fiscal_period_days 153 / 365 = 628767.12, "
        "as fiscal_period_days 153 is below 357 days"
    )


def test_renders_the_longest_prorated_year_of_356_days() -> None:
    line = ProratedByDaysLine(
        PRORATED_LIMIT,
        UNPRORATED_LIMIT,
        D("1500000"),
        FISCAL_PERIOD_DAYS,
        356,
        365,
        SHORT_YEAR_DAYS,
        D("357"),
        D("1463013.70"),
    )

    assert render(line) == (
        "prorated_limit: unprorated_limit 1500000 × fiscal_period_days 356 / 365 = 1463013.70, "
        "as fiscal_period_days 356 is below 357 days"
    )


def test_renders_the_days_of_a_full_year_of_a_366_day_dataset() -> None:
    line = ProratedByDaysLine(
        PRORATED_LIMIT,
        UNPRORATED_LIMIT,
        D("1500000"),
        FISCAL_PERIOD_DAYS,
        153,
        366,
        SHORT_YEAR_DAYS,
        D("357"),
        D("627049.18"),
    )

    assert render(line) == (
        "prorated_limit: unprorated_limit 1500000 × fiscal_period_days 153 / 366 = 627049.18, "
        "as fiscal_period_days 153 is below 357 days"
    )


def test_renders_a_full_year_as_not_prorated_with_the_whole_amount() -> None:
    line = ProratedByDaysLine(
        PRORATED_LIMIT,
        UNPRORATED_LIMIT,
        D("600000"),
        FISCAL_PERIOD_DAYS,
        365,
        365,
        SHORT_YEAR_DAYS,
        D("357"),
        D("600000.00"),
    )

    assert render(line) == (
        "prorated_limit: unprorated_limit 600000 = 600000, "
        "not prorated as fiscal_period_days 365 is not below 357 days"
    )


@pytest.mark.parametrize("days", [357, 364])
def test_renders_a_year_of_51_weeks_or_more_as_not_prorated(days: int) -> None:
    line = ProratedByDaysLine(
        PRORATED_LIMIT,
        UNPRORATED_LIMIT,
        D("1500000"),
        FISCAL_PERIOD_DAYS,
        days,
        365,
        SHORT_YEAR_DAYS,
        D("357"),
        D("1500000"),
    )

    assert render(line) == (
        f"prorated_limit: unprorated_limit 1500000 = 1500000, "
        f"not prorated as fiscal_period_days {days} is not below 357 days"
    )


# Form T2043 Chart A amount 8, "Amount 6 multiplied by amount 7." Amount 7 is the days in 2024 over
# the days of the fiscal period, and it is not printed as a number of its own: the line shows the
# amount, the days in 2024 and the fiscal period days, then the result.
CHART_A_AMOUNT_6 = ArtifactKind("ex/chart_a_amount_6", Decimal)
CHART_A_AMOUNT_8 = ArtifactKind("ex/chart_a_amount_8", Decimal)
DAYS_IN_2024 = ArtifactKind("ex/days_in_2024", int)


def test_renders_an_amount_prorated_by_the_days_in_2024_over_the_fiscal_period_days() -> None:
    line = ProratedByDaysInPeriodLine(
        CHART_A_AMOUNT_8,
        CHART_A_AMOUNT_6,
        D("20000"),
        DAYS_IN_2024,
        184,
        FISCAL_PERIOD_DAYS,
        365,
        D("10082.19"),
    )

    assert render(line) == (
        "chart_a_amount_8: chart_a_amount_6 20000 × days_in_2024 184 / fiscal_period_days 365"
        " = 10082.19"
    )


# --- Schedule 12, the multigenerational home renovation credit, per renovation -----------------
#
# Line 3 "Line 1 minus line 2 (maximum $50,000 per qualifying renovation)": "renovation <n>:
# expenditures <e> less reimbursed <r>, at most <maximum> = <result>". Line 6 "Line 4 minus line
# 5": "renovation <n>: maximum <maximum> less claimed by others <c> = <result>". Line 7 "Enter
# whichever is less: amount from line 3 or line 6": "renovation <n>: lesser of line 3 <a> and
# line 6 <b> = <result>". Each total is the items total under its output's label. Every figure
# prints without trailing zeros.

HOME_LINE_3 = ArtifactKind("ex/home_renovation_line_3", Decimal)
HOME_LINE_6 = ArtifactKind("ex/home_renovation_line_6", Decimal)
HOME_LINE_8 = ArtifactKind("ex/home_renovation_line_8", Decimal)


def test_renders_the_first_renovations_line_3_at_the_maximum() -> None:
    line = RenovationLine3(HOME_LINE_3, 1, D("60000"), D("0"), Amount(D("50000")), D("50000"))

    assert render(line) == (
        "home_renovation_line_3: renovation 1: expenditures 60000 less reimbursed 0, at most 50000 "
        "= 50000"
    )


def test_renders_the_second_renovations_line_3_below_the_maximum() -> None:
    line = RenovationLine3(HOME_LINE_3, 2, D("30000"), D("5000"), Amount(D("50000")), D("25000"))

    assert render(line) == (
        "home_renovation_line_3: renovation 2: expenditures 30000 less reimbursed 5000, at most "
        "50000 = 25000"
    )


def test_renders_a_renovations_line_3_without_trailing_zeros() -> None:
    line = RenovationLine3(
        HOME_LINE_3, 2, D("30000.00"), D("5000.00"), Amount(D("50000.00")), D("25000.00")
    )

    assert render(line) == (
        "home_renovation_line_3: renovation 2: expenditures 30000 less reimbursed 5000, at most "
        "50000 = 25000"
    )


def test_renders_the_second_renovations_line_6_after_the_claim_by_others() -> None:
    line = RenovationLine6(HOME_LINE_6, 2, Amount(D("50000")), D("10000"), D("40000"))

    assert render(line) == (
        "home_renovation_line_6: renovation 2: maximum 50000 less claimed by others 10000 = 40000"
    )


def test_renders_the_second_renovations_line_7_as_the_lesser_of_lines_3_and_6() -> None:
    line = RenovationLine7(HOME_LINE_8, 2, D("25000"), D("40000"), D("25000"))

    assert render(line) == (
        "home_renovation_line_8: renovation 2: lesser of line 3 25000 and line 6 40000 = 25000"
    )


def test_renders_the_items_total_of_two_renovations() -> None:
    line = ItemsTotalLine(HOME_LINE_8, ((1, D("50000")), (2, D("25000"))), D("75000"))

    assert render(line) == "home_renovation_line_8: item 1 50000 + item 2 25000 = 75000"


def test_renders_the_items_total_of_no_renovations() -> None:
    assert render(ItemsTotalLine(HOME_LINE_8, (), D("0"))) == (
        "home_renovation_line_8: no items = 0"
    )


# --- the federal logging tax credit, one province at a time (T1 line 133) ---------------------

# One sentence: the output's label, then the province by its position from 1, the two sides of the
# lesser amount (the tax side at the tax rate's percentage, the income side at the income rate's),
# each with its rounding rule in brackets, and the lesser of them. Figures print without trailing
# zeros, as the other per-item lines do.

PROVINCES_LOGGING_TAX_CREDIT = ArtifactKind("ex/provinces_logging_tax_credit", Decimal)


def logging_province(
    position: int,
    tax_paid: str,
    net_income: str,
    tax_share: str,
    income_share: str,
    result: str,
) -> LoggingTaxCreditLine:
    return LoggingTaxCreditLine(
        PROVINCES_LOGGING_TAX_CREDIT,
        position,
        D(tax_paid),
        Rate(D("0.666667")),
        D(tax_share),
        D(net_income),
        Rate(D("0.066667")),
        D(income_share),
        CENT,
        CENT,
        D(result),
    )


def test_renders_one_province_by_position_with_both_sides_and_the_lesser() -> None:
    assert render(logging_province(1, "300", "6000", "200.00", "400.00", "200.00")) == (
        "provinces_logging_tax_credit: province 1: 66.6667% of logging tax paid 300 = 200 "
        "(half-up to 0.01); 6.6667% of net logging income 6000 = 400 (half-up to 0.01); "
        "lesser 200"
    )


def test_renders_the_second_province_when_its_income_side_is_the_lesser() -> None:
    assert render(logging_province(2, "900", "3000", "600.00", "200.00", "200.00")) == (
        "provinces_logging_tax_credit: province 2: 66.6667% of logging tax paid 900 = 600 "
        "(half-up to 0.01); 6.6667% of net logging income 3000 = 200 (half-up to 0.01); "
        "lesser 200"
    )


def test_renders_the_logging_items_total_of_two_provinces() -> None:
    line = ItemsTotalLine(
        PROVINCES_LOGGING_TAX_CREDIT, ((1, D("200.00")), (2, D("200.00"))), D("400.00")
    )

    assert render(line) == "provinces_logging_tax_credit: item 1 200 + item 2 200 = 400"


# --- Form T2043 Chart B row 3, a percentage of one figure over another -------------------------
#
# Row 3 "Percentage (%) of gross income allocated to the designated province. Row 1 divided by row
# 2": "<output>: <dividend> <amount> divided by <divisor> <amount>, times 100 (<rounding>)
# = <result>%".
# A zero divisor adds "(zero divisor, so 0)" after the rounding.

PCT_OUTPUT = ArtifactKind("ex/farm_chart_b_row_3_on", Decimal)
PCT_DIVIDEND = ArtifactKind("ex/farm_chart_b_gross_income_on", Decimal)
PCT_DIVISOR = ArtifactKind("ex/farm_chart_b_total_gross_income", Decimal)
PCT_ROUNDING = RoundTo(D("0.000000000001"), RoundingMode.HALF_UP)


def test_renders_the_figure_printed_for_the_year_a_lease_was_entered_into() -> None:
    line = YearAmountLine(
        ArtifactKind("ex/t777_lease_list_price_limit", Decimal),
        ArtifactKind("ex/t777_lease_year", int),
        2024,
        D("43529"),
    )

    assert render(line) == (
        "t777_lease_list_price_limit: the figure printed for t777_lease_year 2024 = 43529"
    )


def test_renders_a_percentage_of_one_figure_over_another() -> None:
    line = PercentageOfLine(
        PCT_OUTPUT, PCT_DIVIDEND, D("60000"), PCT_DIVISOR, D("100000"), PCT_ROUNDING, D("60")
    )

    assert render(line) == (
        "farm_chart_b_row_3_on: farm_chart_b_gross_income_on 60000 divided by"
        " farm_chart_b_total_gross_income 100000, times 100 (half-up to 0.000000000001) = 60%"
    )


def test_renders_a_zero_divisor_as_zero_percent_with_the_reason() -> None:
    line = PercentageOfLine(
        PCT_OUTPUT, PCT_DIVIDEND, D("5"), PCT_DIVISOR, D("0"), PCT_ROUNDING, D("0")
    )

    assert render(line) == (
        "farm_chart_b_row_3_on: farm_chart_b_gross_income_on 5 divided by"
        " farm_chart_b_total_gross_income 0, times 100 (half-up to 0.000000000001)"
        " (zero divisor, so 0) = 0%"
    )


def test_renders_the_pooled_provincial_credit_with_minimum_tax_line_2_as_the_special_credit() -> (
    None
):
    # One form on the totals: tax paid 150 (100 + 50), line 2 = 150 x 160 / 210 = 114.29, line 3 =
    # 35.71; line 4 = 3300 x 20955.29 / 183300.00 = 377.26.
    line = PooledProvincialForeignTaxCreditLine(
        NON_COMPLIANT_EXPENSES,
        2,
        D("150"),
        D("114.29"),
        D("35.71"),
        D("3300"),
        D("183300.00"),
        D("20955.29"),
        D("200"),
        CENT,
        D("377.26"),
        D("35.71"),
        D("160"),
        ExactFraction(210),
    )

    assert render(line) == (
        "non_compliant_expenses: all 2 sheets pooled, tax paid 150 is not more than 200: "
        "tax paid 150 less minimum tax line 2 114.29 "
        "(150 tax paid x 160 special foreign tax credit / 210 total tax paid plus business tax, "
        "half-up to 0.01) = 35.71; "
        "3300 net foreign income x 20955.29 provincial tax / 183300 net income = 377.26 "
        "(half-up to 0.01); credit 35.71"
    )


def test_renders_the_provincial_credit_worked_once_on_the_totals() -> None:
    line = PooledProvincialForeignTaxCreditLine(
        NON_COMPLIANT_EXPENSES,
        2,
        D("150"),
        D("40.88"),
        D("109.12"),
        D("10100"),
        D("100000"),
        D("5000"),
        D("200"),
        CENT,
        D("505.00"),
        D("109.12"),
    )

    assert render(line) == (
        "non_compliant_expenses: all 2 sheets pooled, tax paid 150 is not more than 200: "
        "tax paid 150 less federal credit 40.88 = 109.12; "
        "10100 net foreign income x 5000 provincial tax / 100000 net income = 505 "
        "(half-up to 0.01); credit 109.12"
    )


# --- the first record's value of a list of records ----------------------------
#
# One item, the first, named by its position 1 with the field's label and its value, then how many
# items the list has. A count prints as a plain whole number.

FIRST_ITEM_COUNT = ArtifactKind("ex/first_item_count", int)


def test_renders_the_first_value_of_a_count_among_two_items() -> None:
    line = FirstRecordCountLine(FIRST_ITEM_COUNT, ITEM_COUNT, 1, 2)

    assert render(line) == "first_item_count: item 1 item_count 1 of 2 items"


def test_renders_the_first_value_of_a_count_of_one_item() -> None:
    line = FirstRecordCountLine(FIRST_ITEM_COUNT, ITEM_COUNT, 0, 1)

    assert render(line) == "first_item_count: item 1 item_count 0 of 1 items"


def test_renders_the_first_value_of_a_count_among_many_items() -> None:
    line = FirstRecordCountLine(FIRST_ITEM_COUNT, ITEM_COUNT, 12, 40)

    assert render(line) == "first_item_count: item 1 item_count 12 of 40 items"
