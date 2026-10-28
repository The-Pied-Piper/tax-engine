"""Unit tests for the structured trace: one frozen line class per fact, with made-up values.

Each line records what happened with the domain objects involved (`ArtifactKind`, `Rate`,
`Credit`, `Amount`, `ContributionTier`, `Taper`, `Factor`, `Fraction`, `RateTableRow`,
`RoundingRule`), never text; its `amount` is the figure the line is about. A count is an `int`
artifact kind and its `int` value; a chosen rate is a `Rate` artifact kind and its `Rate` value.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal
from fractions import Fraction as ExactFraction
from functools import partial
from typing import Any, cast

import pytest

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.parameters.claim_reduction import ClaimReduction
from tax_calculator.domain.parameters.class_rates import (
    ClassRate,
    HalfYearRule,
    HalfYearRuleOnSale,
    RecaptureAndTerminalLoss,
)
from tax_calculator.domain.parameters.contribution_tier import ContributionTier
from tax_calculator.domain.parameters.credit import Credit
from tax_calculator.domain.parameters.factor import Factor
from tax_calculator.domain.parameters.fraction import Fraction
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rate_table import RateTableRow
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_calculator.domain.parameters.taper import Taper
from tax_calculator.domain.parameters.threshold_rate import ThresholdRate
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.domain.trace import (
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
from tax_calculator.jurisdictions.ca.trace import (
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
from tax_calculator.jurisdictions.ca_on.trace import (
    CaregiverClaimLessClaimedLine,
    PlacementCreditLine,
    PooledProvincialForeignTaxCreditLine,
    ProvincialForeignTaxCreditLine,
)

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
BASE = ArtifactKind("ex/base", Decimal)
TAX = ArtifactKind("ex/tax", Decimal)
PART_ONE = ArtifactKind("ex/part_one", Decimal)
PART_TWO = ArtifactKind("ex/part_two", Decimal)
TOTAL = ArtifactKind("ex/total", Decimal)
RATED = ArtifactKind("ex/rated", Decimal)
RATED_RATE = ArtifactKind("ex/rated", Rate)
GROSS = ArtifactKind("ex/gross", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)
NET = ArtifactKind("ex/net", Decimal)
PERSONAL = ArtifactKind("ex/personal_amount", Decimal)
CAPPED = ArtifactKind("ex/capped", Decimal)
LESSER = ArtifactKind("ex/lesser", Decimal)
GREATER = ArtifactKind("ex/greater", Decimal)
EARNINGS = ArtifactKind("ex/earnings", Decimal)
CONTRIBUTION = ArtifactKind("ex/contribution", Decimal)
TIER = ContributionTier(Rate(D("0.05")), D(3000), D(50000), D(2350))
SURCHARGE = ArtifactKind("ex/surcharge", Decimal)
INCOME = ArtifactKind("ex/income", Decimal)
TAPER = Taper(D(1000), D(500), D(20000), D(10000))
CHILDREN = ArtifactKind("ex/child_count", int)
CHILD_AMOUNT = ArtifactKind("ex/child_amount", Decimal)
CLAIMED = ArtifactKind("ex/claimed_amount", Decimal)
LIMIT = ArtifactKind("ex/claim_limit", Decimal)
ALLOWED = ArtifactKind("ex/allowed_amount", Decimal)
EARNED = ArtifactKind("ex/earned_income", Decimal)
PORTION = ArtifactKind("ex/earned_portion", Decimal)
EACH = ArtifactKind("ex/amount_each", Decimal)
PERSONS = ArtifactKind("ex/person_count", int)
CLAIMED_FOR_ALL = ArtifactKind("ex/amount_claimed", Decimal)
DEPENDANTS = ArtifactKind("ex/dependant_count", int)
ALONE = ArtifactKind("ex/amount_alone", Decimal)
WITH_FAMILY = ArtifactKind("ex/amount_with_family", Decimal)
CHOSEN = ArtifactKind("ex/amount_chosen", Decimal)
TAX_PAYABLE = ArtifactKind("ex/tax_payable", Decimal)
FOREIGN_INCOME = ArtifactKind("ex/foreign_income", Decimal)
WORLD_INCOME = ArtifactKind("ex/worldwide_income", Decimal)
CREDIT_SHARE = ArtifactKind("ex/credit_share", Decimal)
PERCENTAGE = ArtifactKind("ex/allocated_percentage", Decimal)
ITEM_AMOUNT = ArtifactKind("ex/item_amount", Decimal)
GATED = ArtifactKind("ex/gated_amount", Decimal)
GATE = ArtifactKind("ex/gate_amount", Decimal)
TESTED = ArtifactKind("ex/amount_tested", Decimal)
IN_THE_FIRST_RANGE = ArtifactKind("ex/amount_in_the_first_range", Decimal)
IN_THE_SECOND_RANGE = ArtifactKind("ex/amount_in_the_second_range", Decimal)
FAMILY_INCOME = ArtifactKind("ex/family_income", Decimal)
BAND_RATE = ArtifactKind("ex/band_rate", Rate)
BAND = RateTableRow(D(45000), D(50000), Rate(D("0.55")))
TOP_BAND = RateTableRow(D(150000), None, Rate(D(0)))
CARE_EXPENSES = ArtifactKind("ex/care_expenses", Decimal)
CARE_CREDIT = ArtifactKind("ex/care_credit", Decimal)
CAREGIVER = ArtifactKind("ex/caregiver_amount", Decimal)
APPRENTICESHIP = ArtifactKind("ex/apprenticeship_wages_total", Decimal)
MEDICAL = ArtifactKind("ex/dependants_medical", Decimal)
RENOVATION_3 = ArtifactKind("ex/home_renovation_line_3", Decimal)
RENOVATION_6 = ArtifactKind("ex/home_renovation_line_6", Decimal)
RENOVATION_8 = ArtifactKind("ex/home_renovation_line_8", Decimal)
MEDICAL_REDUCTION = ClaimReduction(Rate(D("0.03")), D("2834"), D("15551"))
LIMITED = ArtifactKind("ex/limited_amount", Decimal)
DIVIDED = ArtifactKind("ex/divided_amount", Decimal)
THRESHOLD_LIMIT = ThresholdRate(Rate(D("0.0505")), D("52886"))
NON_COMPLIANT = ArtifactKind("ex/non_compliant_expenses", Decimal)
NON_COMPLIANT_CCA_TOTAL = ArtifactKind("ex/non_compliant_cca", Decimal)
NON_COMPLIANT_CCA_BY_CLASS = RecordListKind(
    "ex/non_compliant_cca_by_class", fields=(ArtifactKind("ex/column_22", Decimal),)
)
RENTAL_ADDITION_TOTAL = ArtifactKind("ex/rental_additions_total", Decimal)
TRANSFERRED = ArtifactKind("ex/transferred_amount", Decimal)
RESIDENCE_GAIN = ArtifactKind("ex/residence_gain", Decimal)
DISPOSITION_GAIN = ArtifactKind("ex/disposition_gain", Decimal)
COUNT_GATE = ArtifactKind("ex/gate", int)
FLAG = ArtifactKind("ex/flag", int)
REDUCTION_BASE = ArtifactKind("ex/reduction_base", Decimal)
OTHER_BASE = ArtifactKind("ex/other_base", Decimal)
MONTHS = ArtifactKind("ex/month_count", int)
MONTHLY = ArtifactKind("ex/monthly_amount", Decimal)


def column_line() -> BracketColumnLine:
    return BracketColumnLine(D(100), D("0.20"), D(150), D("10.00"), D("40.00"))


def total_line() -> RoundedTotalLine:
    return RoundedTotalLine(TAX, BASE, D(250), CENT, D("40.00"))


def sum_line() -> SumLine:
    return SumLine(TOTAL, ((PART_ONE, D("1.25")), (PART_TWO, D(2))), D("3.25"))


def sum_not_below_zero_line() -> SumNotBelowZeroLine:
    return SumNotBelowZeroLine(TOTAL, ((PART_ONE, D("1.25")), (PART_TWO, D("-2"))), D(0))


def rate_applied_line() -> RateAppliedLine:
    return RateAppliedLine(RATED, BASE, D("200.01"), Rate(D("0.5")), CENT, D("100.01"))


def divided_by_rate_line() -> DividedByRateLine:
    return DividedByRateLine(RATED, BASE, D("3795"), Rate(D("0.145")), CENT, D("26172.41"))


def sign_chosen_difference_line() -> SignChosenDifferenceLine:
    return SignChosenDifferenceLine(
        NET, GROSS, D("-100"), REDUCTION, D("30"), BASE, D("130"), D("-30")
    )


def subtracted_line() -> SubtractedLine:
    return SubtractedLine(NET, GROSS, D("100.25"), REDUCTION, D(40), D("60.25"))


def subtracted_not_below_zero_line() -> SubtractedNotBelowZeroLine:
    return SubtractedNotBelowZeroLine(NET, GROSS, D(10), REDUCTION, D("25.5"), D(0))


def credit_amount_line() -> CreditAmountLine:
    return CreditAmountLine(PERSONAL, Credit(D("1000.005")), CENT, D("1000.01"))


def capped_amount_line() -> CappedAmountLine:
    return CappedAmountLine(CAPPED, GROSS, D("1500.25"), Amount(D(1000)), CENT, D("1000.00"))


def threshold_gate_line() -> ThresholdGateLine:
    return ThresholdGateLine(
        GATED, GROSS, D("1500.25"), GATE, D("4390"), Amount(D("4390")), CENT, D("1500.25")
    )


def amount_or_divided_by_rate_line() -> AmountOrDividedByRateLine:
    return AmountOrDividedByRateLine(
        LIMITED, TESTED, D("60000"), DIVIDED, D("3321.67"), THRESHOLD_LIMIT, CENT, D("65775.64")
    )


def lesser_of_with_maximum_line() -> LesserOfWithMaximumLine:
    return LesserOfWithMaximumLine(
        LESSER, ((PART_ONE, D("2500")), (PART_TWO, D("3000"))), Amount(D(2000)), CENT, D("2000.00")
    )


def greater_of_line() -> GreaterOfLine:
    return GreaterOfLine(GREATER, ((PART_ONE, D("100.25")), (PART_TWO, D(40))), D("100.25"))


def lesser_of_line() -> LesserOfLine:
    return LesserOfLine(LESSER, ((PART_ONE, D("100.25")), (PART_TWO, D(40))), D(40))


def contribution_tier_line() -> ContributionTierLine:
    return ContributionTierLine(
        CONTRIBUTION, EARNINGS, D("23000.10"), TIER, CENT, D("20000.10"), D("1000.01")
    )


def surcharge_tier_line() -> SurchargeTierLine:
    return SurchargeTierLine(SURCHARGE, TAX, D("400.25"), D(300), Rate(D("0.25")), CENT, D("25.06"))


def capped_surcharge_tier_line() -> SurchargeTierLine:
    return SurchargeTierLine(
        SURCHARGE, TAX, D("400.25"), D(300), Rate(D("0.25")), CENT, D("25.06"), D(30)
    )


def tapered_amount_line() -> TaperedAmountLine:
    return TaperedAmountLine(
        PERSONAL, INCOME, D("22000.5"), TAPER, CENT, ExactFraction("100.025"), D("1399.98")
    )


def per_unit_amount_line() -> PerUnitAmountLine:
    return PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 2, Amount(D(544)), CENT, D(1088))


def multiple_over_line() -> MultipleOverLine:
    return MultipleOverLine(
        REDUCTION, TOTAL, D(294), Factor(D(2)), TAX, D("100.25"), CENT, D("487.75")
    )


def at_most_line() -> AtMostLine:
    return AtMostLine(ALLOWED, CLAIMED, D("1500.25"), LIMIT, D(1926))


def fraction_applied_line() -> FractionAppliedLine:
    return FractionAppliedLine(PORTION, EARNED, D(50000), Fraction(2, 3), CENT, D("33333.33"))


def times_count_line() -> TimesCountLine:
    return TimesCountLine(CLAIMED_FOR_ALL, EACH, D("16129.50"), PERSONS, 2, D("32259.00"))


def chosen_by_count_line() -> ChosenByCountLine:
    return ChosenByCountLine(CHOSEN, DEPENDANTS, 1, WITH_FAMILY, D("2813.00"))


def ratio_applied_line() -> RatioAppliedLine:
    return RatioAppliedLine(
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


def percentage_applied_line() -> PercentageAppliedLine:
    return PercentageAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("1000"),
        PERCENTAGE,
        D("50"),
        CENT,
        D("500"),
    )


def amount_by_count_line() -> AmountByCountLine:
    return AmountByCountLine(MONTHLY, MONTHS, 4, D("400.255"), CENT, D("400.26"))


def record_total_line() -> RecordTotalLine:
    return RecordTotalLine(TOTAL, ITEM_AMOUNT, (D("6000"), D("4000.50")), D("10000.50"))


def record_positive_total_line() -> RecordPositiveTotalLine:
    return RecordPositiveTotalLine(TOTAL, ITEM_AMOUNT, (D("6000"), D("-4000.50")), D("6000"))


def chosen_by_range_line() -> ChosenByRangeLine:
    return ChosenByRangeLine(CHOSEN, TESTED, D("1000.00"), IN_THE_SECOND_RANGE, D("625.01"))


def rate_by_income_band_line() -> RateByIncomeBandLine:
    return RateByIncomeBandLine(BAND_RATE, FAMILY_INCOME, D("45500.25"), BAND, Rate(D("0.55")))


def chosen_rate_applied_line() -> ChosenRateAppliedLine:
    return ChosenRateAppliedLine(
        CARE_CREDIT, CARE_EXPENSES, D("5000.01"), BAND_RATE, Rate(D("0.55")), CENT, D("2750.01")
    )


def caregiver_claim_line() -> CaregiverClaimLine:
    return CaregiverClaimLine(
        CAREGIVER,
        2,
        Amount(D("28798.00")),
        D("25000"),
        Amount(D("8601")),
        CENT,
        D("3798.00"),
    )


def renovation_line_3() -> RenovationLine3:
    return RenovationLine3(
        RENOVATION_3,
        2,
        D("60000"),
        D("5000"),
        Amount(D("50000")),
        D("50000"),
    )


def renovation_line_6() -> RenovationLine6:
    return RenovationLine6(RENOVATION_6, 2, Amount(D("50000")), D("10000"), D("40000"))


def renovation_line_7() -> RenovationLine7:
    return RenovationLine7(RENOVATION_8, 2, D("50000"), D("40000"), D("40000"))


def apprentice_wages_line() -> ApprenticeWagesLine:
    return ApprenticeWagesLine(
        APPRENTICESHIP, 2, D("25000"), Amount(D("20000")), CENT, D("20000.00")
    )


def other_dependant_medical_line() -> OtherDependantMedicalLine:
    return OtherDependantMedicalLine(
        MEDICAL,
        2,
        D("3000.00"),
        D("10000"),
        MEDICAL_REDUCTION,
        CENT,
        D("2700.00"),
    )


def short_term_rental_non_compliant_line() -> ShortTermRentalNonCompliantLine:
    return ShortTermRentalNonCompliantLine(NON_COMPLIANT, 2, D("900.00"), 30, 90, CENT, D("300.00"))


def short_term_rental_non_compliant_cca_line() -> ShortTermRentalNonCompliantCcaLine:
    return ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA_TOTAL, 2, D("10.1"), D("900.00"), 30, 90, CENT, D("300.00")
    )


def short_term_rental_non_compliant_cca_by_class_line() -> (
    ShortTermRentalNonCompliantCcaByClassLine
):
    return ShortTermRentalNonCompliantCcaByClassLine(
        NON_COMPLIANT_CCA_BY_CLASS, 2, D("10.1"), (D("300.00"), D("33.33")), D("333.33")
    )


def rental_addition_line() -> RentalAdditionLine:
    return RentalAdditionLine(
        RENTAL_ADDITION_TOTAL, 2, D("8"), D("1000.00"), D("250.00"), D("750.00")
    )


def foreign_property_tax_line() -> ForeignPropertyTaxLine:
    return ForeignPropertyTaxLine(
        NON_COMPLIANT, 2, D("6000"), D("20000"), D("0.15"), CENT, D("3000.00"), D("3000.00")
    )


def foreign_tax_credit_line() -> ForeignTaxCreditLine:
    return ForeignTaxCreditLine(
        NON_COMPLIANT,
        2,
        D("1500"),
        D("10000"),
        D("100000"),
        D("14000"),
        CENT,
        D("1400.00"),
        D("1400.00"),
    )


def pooled_foreign_tax_credit_line() -> PooledForeignTaxCreditLine:
    return PooledForeignTaxCreditLine(
        NON_COMPLIANT,
        2,
        D("200"),
        D("10100"),
        D("100000"),
        D("14000"),
        D("250"),
        D("200"),
        CENT,
        D("1414.00"),
        D("200"),
    )


def foreign_business_line_4() -> ForeignBusinessLine4:
    return ForeignBusinessLine4(NON_COMPLIANT, 2, D("400"), D("50"), D("450"))


def foreign_business_line_5() -> ForeignBusinessLine5:
    return ForeignBusinessLine5(
        NON_COMPLIANT, 2, D("6000"), D("100000"), D("14500"), CENT, D("870.00")
    )


def foreign_business_line_7() -> ForeignBusinessLine7:
    return ForeignBusinessLine7(NON_COMPLIANT, 2, D("870.00"), D("100"), D("970.00"))


def foreign_business_line_8() -> ForeignBusinessLine8:
    return ForeignBusinessLine8(NON_COMPLIANT, 2, D("14500"), D("100"), D("14600"))


def foreign_business_line_10() -> ForeignBusinessLine10:
    return ForeignBusinessLine10(NON_COMPLIANT, 2, D("14600"), D("1400"), D("13200"))


def foreign_business_line_11() -> ForeignBusinessLine11:
    return ForeignBusinessLine11(NON_COMPLIANT, 2, D("450"), D("970.00"), D("13200"), D("450"))


def provincial_foreign_tax_credit_line() -> ProvincialForeignTaxCreditLine:
    return ProvincialForeignTaxCreditLine(
        NON_COMPLIANT,
        2,
        D("1500"),
        D("1400.00"),
        D("100.00"),
        D("10000"),
        D("100000"),
        D("5000"),
        CENT,
        D("500.00"),
        D("100.00"),
    )


def pooled_provincial_foreign_tax_credit_line() -> PooledProvincialForeignTaxCreditLine:
    return PooledProvincialForeignTaxCreditLine(
        NON_COMPLIANT,
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


def pooled_provincial_foreign_tax_credit_minimum_tax_line() -> PooledProvincialForeignTaxCreditLine:
    # One form on the totals with minimum tax: line 2 = 150 x 160 / 210 = 114.29 (the special
    # credit 160 and the divisor 150 + 60 = 210 are the minimum tax figures of the line).
    return PooledProvincialForeignTaxCreditLine(
        NON_COMPLIANT,
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


def caregiver_claim_less_claimed_line() -> CaregiverClaimLessClaimedLine:
    return CaregiverClaimLessClaimedLine(
        CAREGIVER,
        2,
        Amount(D("26562.00")),
        D("5000"),
        Amount(D("6008")),
        D("6008.00"),
        D("2500.00"),
        CENT,
        D("3508.00"),
    )


def disability_transfer_line() -> DisabilityTransferLine:
    return DisabilityTransferLine(
        TRANSFERRED,
        2,
        Amount(D("10138.00")),
        Amount(D("5914.00")),
        Amount(D("3464.00")),
        Amount(D("16052")),
        1,
        D("5000"),
        D("1536.00"),
        D("4378.00"),
        D("4378.00"),
        D("14516.00"),
        D("1000"),
        D("15516.00"),
        D("2000"),
        D("13516.00"),
        CENT,
        D("13516.00"),
    )


def disposition_gain_line() -> DispositionGainLine:
    return DispositionGainLine(
        DISPOSITION_GAIN, 2, D("800.00"), D("1000.00"), D("30.00"), D("-230.00")
    )


def disposition_gain_only_line() -> DispositionGainOnlyLine:
    return DispositionGainOnlyLine(
        DISPOSITION_GAIN, 2, D("800.00"), D("1000.00"), D("30.00"), D("-230.00"), D("0")
    )


def depreciable_property_gain_line() -> DepreciablePropertyGainLine:
    return DepreciablePropertyGainLine(
        output=DISPOSITION_GAIN,
        position=2,
        proceeds=D("800.00"),
        adjusted_cost_base=D("1000.00"),
        outlays=D("30.00"),
        farm_loss_property_taxes=D("0"),
        farm_loss_interest=D("0"),
        farm_loss_applied=D("0"),
        depreciable=1,
        gain=D("-230.00"),
        result=D("0"),
    )


def qffp_gain_line() -> QffpGainLine:
    return QffpGainLine(
        output=DISPOSITION_GAIN,
        position=2,
        proceeds=D("200000"),
        adjusted_cost_base=D("160000"),
        outlays=D("0"),
        farm_loss_property_taxes=D("5000"),
        farm_loss_interest=D("5000"),
        farm_loss_applied=D("10000"),
        result=D("30000"),
    )


def farm_loss_applied_line() -> FarmLossAppliedLine:
    return FarmLossAppliedLine(
        output=DISPOSITION_GAIN,
        position=2,
        property_taxes=D("5000"),
        interest=D("5000"),
        result=D("10000"),
    )


def personal_use_property_gain_line() -> PersonalUsePropertyGainLine:
    return PersonalUsePropertyGainLine(
        output=DISPOSITION_GAIN,
        position=2,
        proceeds=D("800.00"),
        adjusted_cost_base=D("1000.00"),
        outlays=D("30.00"),
        minimum=D("1000"),
        proceeds_used=D("1000"),
        cost_base_used=D("1000"),
        gain=D("-30.00"),
        result=D("0"),
    )


def disposition_proceeds_line() -> DispositionProceedsLine:
    return DispositionProceedsLine(DISPOSITION_GAIN, 2, D("800.00"))


def principal_residence_gain_line() -> PrincipalResidenceGainLine:
    return PrincipalResidenceGainLine(
        output=RESIDENCE_GAIN,
        position=2,
        years_designated_after_1981=6,
        years_designated_1972_to_1981=0,
        designated=6,
        years_owned_after_1981=10,
        years_owned_1972_to_1981=0,
        owned=10,
        plus_one=1,
        proceeds=D("400000.00"),
        adjusted_cost_base=D("95000.00"),
        outlays=D("5000.00"),
        gain=D("300000.00"),
        line_20=7,
        line_21=D("2100000.00"),
        rounding=CENT,
        exempt=D("210000.00"),
        part_2_applies=0,
        line_53=D("0"),
        line_24=D("90000.00"),
        result=D("90000.00"),
    )


def items_total_line() -> ItemsTotalLine:
    return ItemsTotalLine(CAREGIVER, ((1, D("750.00")), (3, D("800"))), D("1550.00"))


def condition_line() -> ConditionLine:
    return ConditionLine(
        COUNT_GATE,
        2,
        "There is an amount on line 72",
        ((REDUCTION_BASE, D("120.00")),),
        True,
    )


def conditions_count_line() -> ConditionsCountLine:
    return ConditionsCountLine(COUNT_GATE, (2, 3), 0)


def item_sum_line() -> ItemSumLine:
    return ItemSumLine(TOTAL, 2, ((PART_ONE, D("400.00")), (PART_TWO, D("500"))), D("900.00"))


def item_lesser_of_line() -> ItemLesserOfLine:
    return ItemLesserOfLine(TOTAL, 1, ((PART_ONE, D("1500")), (PART_TWO, D("750.50"))), D("750.50"))


def count_at_least_line() -> CountAtLeastLine:
    return CountAtLeastLine(PERSONS, CHILDREN, 3, DEPENDANTS, 2)


def more_than_per_unit_line() -> MoreThanPerUnitLine:
    return MoreThanPerUnitLine(
        output=TOTAL,
        total_kind=PART_ONE,
        total=D("201"),
        count_kind=CHILDREN,
        count=2,
        per_unit=Amount(D("100.00")),
        rounding=CENT,
        minimum_total=D("200.00"),
    )


def claim_at_most_line() -> ClaimAtMostLine:
    return ClaimAtMostLine(ALLOWED, CLAIMED, D("1500.25"), LIMIT, D(1926))


def count_at_most_line() -> CountAtMostLine:
    return CountAtMostLine(PERSONS, CHILDREN, 3, DEPENDANTS, 4)


def yes_or_no_count_line() -> YesOrNoCountLine:
    return YesOrNoCountLine(PERSONS, CHILDREN, 1)


def count_without_records_line() -> CountWithoutRecordsLine:
    return CountWithoutRecordsLine(PERSONS, CHILDREN, 1, ITEMS, 0)


def count_not_refused_line() -> CountNotRefusedLine:
    return CountNotRefusedLine(PERSONS, CHILDREN, 2)


def ratio_truncated_line() -> RatioTruncatedLine:
    return RatioTruncatedLine(
        RATED_RATE,
        BASE,
        D("30000"),
        TOTAL,
        D("70000"),
        RoundTo(D("0.00001"), RoundingMode.DOWN),
        False,
        D("0.42857"),
    )


def positive_part_of_negation_line() -> PositivePartOfNegationLine:
    return PositivePartOfNegationLine(RATED, NET, D("-12.50"), D("12.50"))


def lesser_of_when_positive_line() -> LesserOfWhenPositiveLine:
    return LesserOfWhenPositiveLine(
        TOTAL, ((PART_ONE, D("1500")), (PART_TWO, D("750.50"))), True, True, D("-750.50")
    )


def amount_when_more_line() -> AmountWhenMoreLine:
    return AmountWhenMoreLine(
        ALLOWED, CLAIMED, D("1500.25"), TESTED, D("70000.01"), LIMIT, D(70000), D("1500.25")
    )


def chosen_by_sign_line() -> ChosenBySignLine:
    return ChosenBySignLine(CHOSEN, GATE, D("-3"), ALONE, D("1633.00"))


ALL_LINES = [
    column_line,
    total_line,
    sum_line,
    sum_not_below_zero_line,
    rate_applied_line,
    divided_by_rate_line,
    sign_chosen_difference_line,
    subtracted_line,
    subtracted_not_below_zero_line,
    credit_amount_line,
    capped_amount_line,
    threshold_gate_line,
    amount_or_divided_by_rate_line,
    lesser_of_line,
    lesser_of_with_maximum_line,
    greater_of_line,
    contribution_tier_line,
    surcharge_tier_line,
    tapered_amount_line,
    per_unit_amount_line,
    multiple_over_line,
    at_most_line,
    fraction_applied_line,
    times_count_line,
    chosen_by_count_line,
    ratio_applied_line,
    percentage_applied_line,
    amount_by_count_line,
    record_total_line,
    record_positive_total_line,
    chosen_by_range_line,
    rate_by_income_band_line,
    chosen_rate_applied_line,
    caregiver_claim_line,
    renovation_line_3,
    renovation_line_6,
    renovation_line_7,
    caregiver_claim_less_claimed_line,
    disability_transfer_line,
    principal_residence_gain_line,
    item_sum_line,
    item_lesser_of_line,
    disposition_gain_line,
    foreign_property_tax_line,
    foreign_tax_credit_line,
    pooled_foreign_tax_credit_line,
    foreign_business_line_4,
    foreign_business_line_5,
    foreign_business_line_7,
    foreign_business_line_8,
    foreign_business_line_10,
    foreign_business_line_11,
    disposition_gain_only_line,
    items_total_line,
    other_dependant_medical_line,
    short_term_rental_non_compliant_line,
    short_term_rental_non_compliant_cca_line,
    short_term_rental_non_compliant_cca_by_class_line,
    rental_addition_line,
    condition_line,
    conditions_count_line,
    count_at_least_line,
    more_than_per_unit_line,
    count_at_most_line,
    yes_or_no_count_line,
    count_not_refused_line,
    count_without_records_line,
    ratio_truncated_line,
    positive_part_of_negation_line,
    lesser_of_when_positive_line,
    chosen_by_sign_line,
    amount_when_more_line,
]


def test_the_base_line_cannot_be_built() -> None:
    with pytest.raises(TypeError):
        cast(Any, TraceLine)()


@pytest.mark.parametrize("make", ALL_LINES)
def test_every_line_is_a_trace_line(make: Any) -> None:
    assert isinstance(make(), TraceLine)


@pytest.mark.parametrize("make", ALL_LINES)
def test_lines_are_equal_by_value(make: Any) -> None:
    assert make() == make()
    assert make() is not make()


@pytest.mark.parametrize("make", ALL_LINES)
def test_lines_are_frozen(make: Any) -> None:
    line = make()
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_bracket_column_line_fields_in_order() -> None:
    line = column_line()

    assert line == BracketColumnLine(
        lower=D(100), rate=D("0.20"), excess=D(150), tax_at_start=D("10.00"), tax=D("40.00")
    )
    assert [f.name for f in fields(line)] == ["lower", "rate", "excess", "tax_at_start", "tax"]
    assert (line.lower, line.rate, line.excess, line.tax_at_start, line.tax) == (
        D(100),
        D("0.20"),
        D(150),
        D("10.00"),
        D("40.00"),
    )
    assert line.amount == D("40.00")


def test_bracket_column_line_has_no_upper_bound() -> None:
    assert "upper" not in [f.name for f in fields(BracketColumnLine)]


def test_bracket_column_lines_differ_by_any_field() -> None:
    line = column_line()

    assert line != BracketColumnLine(D(0), D("0.20"), D(150), D("10.00"), D("40.00"))
    assert line != BracketColumnLine(D(100), D("0.25"), D(150), D("10.00"), D("40.00"))
    assert line != BracketColumnLine(D(100), D("0.20"), D(140), D("10.00"), D("40.00"))
    assert line != BracketColumnLine(D(100), D("0.20"), D(150), D("10.01"), D("40.00"))
    assert line != BracketColumnLine(D(100), D("0.20"), D(150), D("10.00"), D("40.01"))


def test_rounded_total_line_fields_in_order() -> None:
    line = total_line()

    assert line == RoundedTotalLine(
        output=TAX, base=BASE, base_amount=D(250), rounding=CENT, total=D("40.00")
    )
    assert line.output is TAX
    assert line.base is BASE
    assert line.base_amount == D(250)
    assert line.rounding == CENT
    assert line.total == D("40.00")
    assert line.amount == D("40.00")


def test_rounded_total_lines_differ_by_rounding() -> None:
    assert total_line() != RoundedTotalLine(TAX, BASE, D(250), NO_ROUNDING, D("40.00"))


def test_sum_line_fields_in_order() -> None:
    line = sum_line()

    assert line == SumLine(
        output=TOTAL, parts=((PART_ONE, D("1.25")), (PART_TWO, D(2))), total=D("3.25")
    )
    assert [f.name for f in fields(line)] == ["output", "parts", "total"]
    assert line.output is TOTAL
    assert line.parts == ((PART_ONE, D("1.25")), (PART_TWO, D(2)))
    assert line.total == D("3.25")
    assert line.amount == D("3.25")


def test_sum_line_may_have_no_parts() -> None:
    line = SumLine(TOTAL, (), D(0))

    assert line.parts == ()
    assert line.amount == D(0)


def test_sum_lines_differ_by_the_order_of_their_parts() -> None:
    assert sum_line() != SumLine(TOTAL, ((PART_TWO, D(2)), (PART_ONE, D("1.25"))), D("3.25"))


def test_sum_lines_are_hashable() -> None:
    assert hash(sum_line()) == hash(sum_line())


def test_sum_not_below_zero_line_fields_in_order() -> None:
    line = sum_not_below_zero_line()

    assert line == SumNotBelowZeroLine(
        output=TOTAL, parts=((PART_ONE, D("1.25")), (PART_TWO, D("-2"))), total=D(0)
    )
    assert [f.name for f in fields(line)] == ["output", "parts", "total"]
    assert line.output is TOTAL
    assert line.parts == ((PART_ONE, D("1.25")), (PART_TWO, D("-2")))
    assert line.total == D(0)
    assert line.amount == D(0)


def test_sum_not_below_zero_line_may_hold_a_positive_total() -> None:
    line = SumNotBelowZeroLine(TOTAL, ((PART_ONE, D("1.25")), (PART_TWO, D(2))), D("3.25"))

    assert line.total == D("3.25")
    assert line.amount == D("3.25")


def test_sum_not_below_zero_line_may_have_no_parts() -> None:
    line = SumNotBelowZeroLine(TOTAL, (), D(0))

    assert line.parts == ()
    assert line.amount == D(0)


def test_sum_not_below_zero_lines_differ_by_the_order_of_their_parts() -> None:
    assert sum_not_below_zero_line() != SumNotBelowZeroLine(
        TOTAL, ((PART_TWO, D("-2")), (PART_ONE, D("1.25"))), D(0)
    )


def test_sum_not_below_zero_lines_are_hashable() -> None:
    assert hash(sum_not_below_zero_line()) == hash(sum_not_below_zero_line())


def test_a_floored_sum_is_not_a_plain_sum_line() -> None:
    # The class says the floor applied, so the same fields in the two classes are not equal.
    floored = SumNotBelowZeroLine(TOTAL, ((PART_ONE, D("1.25")), (PART_TWO, D(2))), D("3.25"))

    assert not isinstance(floored, SumLine)
    assert cast(Any, floored) != SumLine(
        TOTAL, ((PART_ONE, D("1.25")), (PART_TWO, D(2))), D("3.25")
    )


def test_rate_applied_line_fields_in_order() -> None:
    line = rate_applied_line()

    assert line == RateAppliedLine(
        output=RATED,
        base=BASE,
        base_amount=D("200.01"),
        rate=Rate(D("0.5")),
        rounding=CENT,
        result=D("100.01"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "base",
        "base_amount",
        "rate",
        "rounding",
        "result",
    ]
    assert line.output is RATED
    assert line.base is BASE
    assert line.base_amount == D("200.01")
    assert line.rate == Rate(D("0.5"))
    assert line.rounding == CENT
    assert line.result == D("100.01")
    assert line.amount == D("100.01")


def test_rate_applied_lines_differ_by_rounding() -> None:
    assert rate_applied_line() != RateAppliedLine(
        RATED, BASE, D("200.01"), Rate(D("0.5")), NO_ROUNDING, D("100.01")
    )


def test_rate_applied_lines_are_hashable() -> None:
    assert hash(rate_applied_line()) == hash(rate_applied_line())


def test_divided_by_rate_line_fields_in_order() -> None:
    line = divided_by_rate_line()

    assert line == DividedByRateLine(
        output=RATED,
        dividend=BASE,
        dividend_amount=D("3795"),
        rate=Rate(D("0.145")),
        rounding=CENT,
        result=D("26172.41"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "dividend",
        "dividend_amount",
        "rate",
        "rounding",
        "result",
    ]
    assert line.output is RATED
    assert line.dividend is BASE
    assert line.dividend_amount == D("3795")
    assert line.rate == Rate(D("0.145"))
    assert line.rounding == CENT
    assert line.result == D("26172.41")
    assert line.amount == D("26172.41")


def test_divided_by_rate_lines_differ_by_rounding() -> None:
    assert divided_by_rate_line() != DividedByRateLine(
        RATED, BASE, D("3795"), Rate(D("0.145")), NO_ROUNDING, D("26172.41")
    )


def test_divided_by_rate_lines_are_hashable() -> None:
    assert hash(divided_by_rate_line()) == hash(divided_by_rate_line())


def test_a_divided_by_rate_line_is_not_a_rate_applied_line() -> None:
    assert not isinstance(divided_by_rate_line(), RateAppliedLine)


def test_sign_chosen_difference_line_fields_in_order() -> None:
    line = sign_chosen_difference_line()

    assert line == SignChosenDifferenceLine(
        output=NET,
        sign=GROSS,
        sign_amount=D("-100"),
        reference=REDUCTION,
        reference_amount=D("30"),
        difference=BASE,
        difference_amount=D("130"),
        result=D("-30"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "sign",
        "sign_amount",
        "reference",
        "reference_amount",
        "difference",
        "difference_amount",
        "result",
    ]
    assert line.output is NET
    assert line.sign is GROSS
    assert line.sign_amount == D("-100")
    assert line.reference is REDUCTION
    assert line.reference_amount == D("30")
    assert line.difference is BASE
    assert line.difference_amount == D("130")
    assert line.result == D("-30")
    assert line.amount == D("-30")


def test_sign_chosen_difference_lines_differ_by_result() -> None:
    assert sign_chosen_difference_line() != SignChosenDifferenceLine(
        NET, GROSS, D("-100"), REDUCTION, D("30"), BASE, D("130"), D("30")
    )


def test_sign_chosen_difference_lines_differ_by_sign_amount() -> None:
    assert sign_chosen_difference_line() != SignChosenDifferenceLine(
        NET, GROSS, D("100"), REDUCTION, D("30"), BASE, D("130"), D("-30")
    )


def test_sign_chosen_difference_lines_are_hashable() -> None:
    assert hash(sign_chosen_difference_line()) == hash(sign_chosen_difference_line())


def test_a_sign_chosen_difference_line_is_not_a_subtracted_line() -> None:
    assert not isinstance(sign_chosen_difference_line(), SubtractedLine)


def test_subtracted_line_fields_in_order() -> None:
    line = subtracted_line()

    assert line == SubtractedLine(
        output=NET,
        minuend=GROSS,
        minuend_amount=D("100.25"),
        subtrahend=REDUCTION,
        subtrahend_amount=D(40),
        result=D("60.25"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "minuend",
        "minuend_amount",
        "subtrahend",
        "subtrahend_amount",
        "result",
    ]
    assert line.output is NET
    assert line.minuend is GROSS
    assert line.minuend_amount == D("100.25")
    assert line.subtrahend is REDUCTION
    assert line.subtrahend_amount == D(40)
    assert line.result == D("60.25")
    assert line.amount == D("60.25")


def test_subtracted_line_may_hold_a_negative_result() -> None:
    line = SubtractedLine(NET, GROSS, D(10), REDUCTION, D("25.5"), D("-15.5"))

    assert line.result == D("-15.5")
    assert line.amount == D("-15.5")


def test_subtracted_lines_differ_by_which_kind_is_taken_off() -> None:
    assert subtracted_line() != SubtractedLine(
        NET, REDUCTION, D("100.25"), GROSS, D(40), D("60.25")
    )


def test_subtracted_lines_are_hashable() -> None:
    assert hash(subtracted_line()) == hash(subtracted_line())


def test_subtracted_not_below_zero_line_fields_in_order() -> None:
    line = subtracted_not_below_zero_line()

    assert line == SubtractedNotBelowZeroLine(
        output=NET,
        minuend=GROSS,
        minuend_amount=D(10),
        subtrahend=REDUCTION,
        subtrahend_amount=D("25.5"),
        result=D(0),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "minuend",
        "minuend_amount",
        "subtrahend",
        "subtrahend_amount",
        "result",
    ]
    assert line.output is NET
    assert line.minuend is GROSS
    assert line.minuend_amount == D(10)
    assert line.subtrahend is REDUCTION
    assert line.subtrahend_amount == D("25.5")
    assert line.result == D(0)
    assert line.amount == D(0)


def test_subtracted_not_below_zero_line_may_hold_a_positive_result() -> None:
    line = SubtractedNotBelowZeroLine(NET, GROSS, D("100.25"), REDUCTION, D(40), D("60.25"))

    assert line.result == D("60.25")
    assert line.amount == D("60.25")


def test_subtracted_not_below_zero_lines_differ_by_which_kind_is_taken_off() -> None:
    assert subtracted_not_below_zero_line() != SubtractedNotBelowZeroLine(
        NET, REDUCTION, D(10), GROSS, D("25.5"), D(0)
    )


def test_subtracted_not_below_zero_lines_are_hashable() -> None:
    assert hash(subtracted_not_below_zero_line()) == hash(subtracted_not_below_zero_line())


def test_a_floored_subtraction_is_not_a_plain_subtracted_line() -> None:
    # The class says the floor applied, so the same fields in the two classes are not equal.
    floored = SubtractedNotBelowZeroLine(NET, GROSS, D("100.25"), REDUCTION, D(40), D("60.25"))

    assert cast(Any, floored) != subtracted_line()


def test_credit_amount_line_fields_in_order() -> None:
    line = credit_amount_line()

    assert line == CreditAmountLine(
        output=PERSONAL, basis=Credit(D("1000.005")), rounding=CENT, value=D("1000.01")
    )
    assert [f.name for f in fields(line)] == ["output", "basis", "rounding", "value"]
    assert line.output is PERSONAL
    assert line.basis == Credit(D("1000.005"))
    assert line.rounding == CENT
    # Settled: `value` is the rounded amount, not the dataset's; the inherited `amount` returns it.
    assert line.value == D("1000.01")
    assert line.amount == line.value


def test_credit_amount_line_may_hold_an_unrounded_amount() -> None:
    line = CreditAmountLine(PERSONAL, Credit(D("1000.005")), NO_ROUNDING, D("1000.005"))

    assert line.rounding == NO_ROUNDING
    assert line.value == D("1000.005")
    assert line.amount == line.value


def test_credit_amount_lines_differ_by_rounding() -> None:
    assert credit_amount_line() != CreditAmountLine(
        PERSONAL, Credit(D("1000.005")), NO_ROUNDING, D("1000.01")
    )


def test_credit_amount_lines_differ_by_value() -> None:
    assert credit_amount_line() != CreditAmountLine(
        PERSONAL, Credit(D("1000.005")), CENT, D("1000.00")
    )


def test_credit_amount_lines_are_hashable() -> None:
    assert hash(credit_amount_line()) == hash(credit_amount_line())


def test_a_credit_amount_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(credit_amount_line())]


def test_capped_amount_line_fields_in_order() -> None:
    line = capped_amount_line()

    assert line == CappedAmountLine(
        output=CAPPED,
        base=GROSS,
        base_amount=D("1500.25"),
        cap=Amount(D(1000)),
        rounding=CENT,
        result=D("1000.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "base",
        "base_amount",
        "cap",
        "rounding",
        "result",
    ]
    assert line.output is CAPPED
    assert line.base is GROSS
    assert line.base_amount == D("1500.25")
    assert line.cap == Amount(D(1000))
    assert line.rounding == CENT
    assert line.result == D("1000.00")
    assert line.amount == D("1000.00")


def test_capped_amount_line_may_hold_a_base_below_the_cap() -> None:
    line = CappedAmountLine(CAPPED, GROSS, D("400.25"), Amount(D(1000)), NO_ROUNDING, D("400.25"))

    assert line.result == D("400.25")
    assert line.amount == D("400.25")


def test_capped_amount_lines_differ_by_cap() -> None:
    assert capped_amount_line() != CappedAmountLine(
        CAPPED, GROSS, D("1500.25"), Amount(D(1200)), CENT, D("1000.00")
    )


def test_capped_amount_lines_differ_by_rounding() -> None:
    assert capped_amount_line() != CappedAmountLine(
        CAPPED, GROSS, D("1500.25"), Amount(D(1000)), NO_ROUNDING, D("1000.00")
    )


def test_capped_amount_lines_are_hashable() -> None:
    assert hash(capped_amount_line()) == hash(capped_amount_line())


def test_lesser_of_line_fields_in_order() -> None:
    line = lesser_of_line()

    assert line == LesserOfLine(
        output=LESSER, parts=((PART_ONE, D("100.25")), (PART_TWO, D(40))), result=D(40)
    )
    assert [f.name for f in fields(line)] == ["output", "parts", "result"]
    assert line.output is LESSER
    assert line.parts == ((PART_ONE, D("100.25")), (PART_TWO, D(40)))
    assert line.result == D(40)
    assert line.amount == D(40)


def test_lesser_of_with_maximum_line_fields_in_order() -> None:
    line = lesser_of_with_maximum_line()

    assert line == LesserOfWithMaximumLine(
        output=LESSER,
        parts=((PART_ONE, D("2500")), (PART_TWO, D("3000"))),
        maximum=Amount(D(2000)),
        rounding=CENT,
        result=D("2000.00"),
    )
    assert [f.name for f in fields(line)] == ["output", "parts", "maximum", "rounding", "result"]
    assert line.output is LESSER
    assert line.parts == ((PART_ONE, D("2500")), (PART_TWO, D("3000")))
    assert line.maximum == Amount(D(2000))
    assert line.rounding == CENT
    assert line.result == D("2000.00")
    assert line.amount == D("2000.00")


def test_lesser_of_with_maximum_lines_differ_by_maximum_rounding_and_the_order_of_parts() -> None:
    parts = ((PART_ONE, D("2500")), (PART_TWO, D("3000")))
    assert lesser_of_with_maximum_line() != LesserOfWithMaximumLine(
        LESSER, parts, Amount(D(1000)), CENT, D("2000.00")
    )
    assert lesser_of_with_maximum_line() != LesserOfWithMaximumLine(
        LESSER, parts, Amount(D(2000)), NO_ROUNDING, D("2000.00")
    )
    assert lesser_of_with_maximum_line() != LesserOfWithMaximumLine(
        LESSER, parts[::-1], Amount(D(2000)), CENT, D("2000.00")
    )


def test_lesser_of_with_maximum_lines_are_hashable() -> None:
    assert hash(lesser_of_with_maximum_line()) == hash(lesser_of_with_maximum_line())


def test_a_lesser_of_with_maximum_line_is_not_a_lesser_of_or_capped_amount_line() -> None:
    line = lesser_of_with_maximum_line()

    assert not isinstance(line, LesserOfLine)
    assert not isinstance(line, CappedAmountLine)
    assert not isinstance(lesser_of_line(), LesserOfWithMaximumLine)


def test_lesser_of_line_may_have_one_part() -> None:
    line = LesserOfLine(LESSER, ((PART_ONE, D("1.25")),), D("1.25"))

    assert line.parts == ((PART_ONE, D("1.25")),)
    assert line.amount == D("1.25")


def test_lesser_of_lines_differ_by_the_order_of_their_parts() -> None:
    assert lesser_of_line() != LesserOfLine(
        LESSER, ((PART_TWO, D(40)), (PART_ONE, D("100.25"))), D(40)
    )


def test_lesser_of_lines_differ_by_result() -> None:
    assert lesser_of_line() != LesserOfLine(
        LESSER, ((PART_ONE, D("100.25")), (PART_TWO, D(40))), D("100.25")
    )


def test_lesser_of_lines_are_hashable() -> None:
    assert hash(lesser_of_line()) == hash(lesser_of_line())


def test_a_lesser_of_line_is_not_a_sum_line_nor_a_capped_amount_line() -> None:
    assert not isinstance(lesser_of_line(), SumLine)
    assert not isinstance(lesser_of_line(), CappedAmountLine)
    assert cast(Any, lesser_of_line()) != SumLine(
        LESSER, ((PART_ONE, D("100.25")), (PART_TWO, D(40))), D(40)
    )


def test_greater_of_line_fields_in_order() -> None:
    line = greater_of_line()

    assert line == GreaterOfLine(
        output=GREATER, parts=((PART_ONE, D("100.25")), (PART_TWO, D(40))), result=D("100.25")
    )
    assert [f.name for f in fields(line)] == ["output", "parts", "result"]
    assert line.output is GREATER
    assert line.parts == ((PART_ONE, D("100.25")), (PART_TWO, D(40)))
    assert line.result == D("100.25")
    assert line.amount == D("100.25")


def test_greater_of_line_may_have_one_part() -> None:
    line = GreaterOfLine(GREATER, ((PART_ONE, D("1.25")),), D("1.25"))

    assert line.parts == ((PART_ONE, D("1.25")),)
    assert line.amount == D("1.25")


def test_greater_of_lines_differ_by_the_order_of_their_parts() -> None:
    assert greater_of_line() != GreaterOfLine(
        GREATER, ((PART_TWO, D(40)), (PART_ONE, D("100.25"))), D("100.25")
    )


def test_greater_of_lines_differ_by_result() -> None:
    assert greater_of_line() != GreaterOfLine(
        GREATER, ((PART_ONE, D("100.25")), (PART_TWO, D(40))), D(40)
    )


def test_greater_of_lines_are_hashable() -> None:
    assert hash(greater_of_line()) == hash(greater_of_line())


def test_a_greater_of_line_is_not_a_lesser_of_line() -> None:
    assert not isinstance(greater_of_line(), LesserOfLine)
    assert cast(Any, greater_of_line()) != LesserOfLine(
        GREATER, ((PART_ONE, D("100.25")), (PART_TWO, D(40))), D("100.25")
    )


def test_contribution_tier_line_fields_in_order() -> None:
    line = contribution_tier_line()

    assert line == ContributionTierLine(
        output=CONTRIBUTION,
        earnings=EARNINGS,
        earnings_amount=D("23000.10"),
        tier=TIER,
        rounding=CENT,
        contributory=D("20000.10"),
        result=D("1000.01"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "earnings",
        "earnings_amount",
        "tier",
        "rounding",
        "contributory",
        "result",
    ]
    assert line.output is CONTRIBUTION
    assert line.earnings is EARNINGS
    assert line.earnings_amount == D("23000.10")
    assert line.tier == TIER
    assert line.rounding == CENT
    assert line.contributory == D("20000.10")
    assert line.result == D("1000.01")
    assert line.amount == D("1000.01")


def test_contribution_tier_line_may_hold_zero_contributory_earnings() -> None:
    line = ContributionTierLine(CONTRIBUTION, EARNINGS, D("-500"), TIER, NO_ROUNDING, D(0), D(0))

    assert line.earnings_amount == D("-500")
    assert line.contributory == D(0)
    assert line.amount == D(0)


def test_contribution_tier_lines_differ_by_tier() -> None:
    other = ContributionTier(Rate(D("0.05")), D(3000), D(50000), D(2000))

    assert contribution_tier_line() != ContributionTierLine(
        CONTRIBUTION, EARNINGS, D("23000.10"), other, CENT, D("20000.10"), D("1000.01")
    )


def test_contribution_tier_lines_differ_by_rounding() -> None:
    assert contribution_tier_line() != ContributionTierLine(
        CONTRIBUTION, EARNINGS, D("23000.10"), TIER, NO_ROUNDING, D("20000.10"), D("1000.01")
    )


def test_contribution_tier_lines_differ_by_contributory_earnings() -> None:
    assert contribution_tier_line() != ContributionTierLine(
        CONTRIBUTION, EARNINGS, D("23000.10"), TIER, CENT, D("20000"), D("1000.01")
    )


def test_contribution_tier_lines_are_hashable() -> None:
    assert hash(contribution_tier_line()) == hash(contribution_tier_line())


def test_a_contribution_tier_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(contribution_tier_line())]


def test_a_contribution_tier_line_is_not_a_rate_applied_or_capped_amount_line() -> None:
    line = contribution_tier_line()

    assert not isinstance(line, RateAppliedLine)
    assert not isinstance(line, CappedAmountLine)


def test_surcharge_tier_line_fields_in_order() -> None:
    line = surcharge_tier_line()

    assert line == SurchargeTierLine(
        output=SURCHARGE,
        base=TAX,
        base_amount=D("400.25"),
        threshold=D(300),
        rate=Rate(D("0.25")),
        rounding=CENT,
        part=D("25.06"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "base",
        "base_amount",
        "threshold",
        "rate",
        "rounding",
        "part",
        "maximum",
    ]
    assert line.output is SURCHARGE
    assert line.base is TAX
    # `base_amount` is the whole base, not the part of it over the threshold.
    assert line.base_amount == D("400.25")
    assert line.threshold == D(300)
    assert line.rate == Rate(D("0.25"))
    assert line.rounding == CENT
    assert line.part == D("25.06")
    assert line.amount == D("25.06")


def test_surcharge_tier_line_may_hold_a_zero_part() -> None:
    # A base that does not reach the threshold still gets its tier's line, with nothing charged.
    line = SurchargeTierLine(SURCHARGE, TAX, D(200), D(300), Rate(D("0.25")), NO_ROUNDING, D(0))

    assert line.part == D(0)
    assert line.amount == D(0)


def test_surcharge_tier_line_has_no_maximum_by_default() -> None:
    assert surcharge_tier_line().maximum is None


def test_surcharge_tier_line_holds_its_tiers_maximum() -> None:
    line = SurchargeTierLine(
        SURCHARGE, TAX, D("400.25"), D(300), Rate(D("0.25")), CENT, D("20"), D("20")
    )

    assert line.maximum == D("20")
    # The capped part is still the line's amount.
    assert line.amount == D("20")


def test_surcharge_tier_line_takes_its_maximum_by_keyword() -> None:
    line = SurchargeTierLine(
        output=SURCHARGE,
        base=TAX,
        base_amount=D("400.25"),
        threshold=D(300),
        rate=Rate(D("0.25")),
        rounding=CENT,
        part=D("0"),
        maximum=D(0),
    )

    assert line.maximum == D(0)


def test_surcharge_tier_lines_differ_by_maximum() -> None:
    assert surcharge_tier_line() != capped_surcharge_tier_line()
    assert capped_surcharge_tier_line() != SurchargeTierLine(
        SURCHARGE, TAX, D("400.25"), D(300), Rate(D("0.25")), CENT, D("25.06"), D(40)
    )


def test_surcharge_tier_lines_with_a_maximum_are_hashable() -> None:
    assert hash(capped_surcharge_tier_line()) == hash(capped_surcharge_tier_line())


def test_surcharge_tier_lines_differ_by_threshold() -> None:
    assert surcharge_tier_line() != SurchargeTierLine(
        SURCHARGE, TAX, D("400.25"), D(100), Rate(D("0.25")), CENT, D("25.06")
    )


def test_surcharge_tier_lines_differ_by_rounding() -> None:
    assert surcharge_tier_line() != SurchargeTierLine(
        SURCHARGE, TAX, D("400.25"), D(300), Rate(D("0.25")), NO_ROUNDING, D("25.06")
    )


def test_surcharge_tier_lines_are_hashable() -> None:
    assert hash(surcharge_tier_line()) == hash(surcharge_tier_line())


def test_a_surcharge_tier_line_is_not_a_rate_applied_line() -> None:
    assert not isinstance(surcharge_tier_line(), RateAppliedLine)


def test_tapered_amount_line_fields_in_order() -> None:
    line = tapered_amount_line()

    assert line == TaperedAmountLine(
        output=PERSONAL,
        base=INCOME,
        base_amount=D("22000.5"),
        taper=TAPER,
        rounding=CENT,
        reduction=ExactFraction("100.025"),
        result=D("1399.98"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "base",
        "base_amount",
        "taper",
        "rounding",
        "reduction",
        "result",
    ]
    assert line.output is PERSONAL
    assert line.base is INCOME
    assert line.base_amount == D("22000.5")
    assert line.taper == TAPER
    assert line.rounding == CENT
    assert line.reduction == ExactFraction(4001, 40)
    assert isinstance(line.reduction, ExactFraction)
    assert line.result == D("1399.98")
    assert line.amount == D("1399.98")


def test_tapered_amount_line_may_hold_a_zero_reduction() -> None:
    # A base at or below the threshold reduces nothing: the full amount.
    line = TaperedAmountLine(
        PERSONAL, INCOME, D(15000), TAPER, NO_ROUNDING, ExactFraction(0), D(1500)
    )

    assert line.reduction == ExactFraction(0)
    assert line.amount == D(1500)


def test_tapered_amount_line_may_hold_a_reduction_above_the_supplement() -> None:
    # The reduction is recorded before the floor at zero; the result is the base amount.
    line = TaperedAmountLine(
        PERSONAL, INCOME, D(80000), TAPER, NO_ROUNDING, ExactFraction(3000), D(1000)
    )

    assert line.reduction == ExactFraction(3000)
    assert line.amount == D(1000)


def test_tapered_amount_lines_differ_by_taper() -> None:
    other = Taper(D(1000), D(500), D(20000), D(5000))

    assert tapered_amount_line() != TaperedAmountLine(
        PERSONAL, INCOME, D("22000.5"), other, CENT, ExactFraction("100.025"), D("1399.98")
    )


def test_tapered_amount_lines_differ_by_rounding() -> None:
    assert tapered_amount_line() != TaperedAmountLine(
        PERSONAL, INCOME, D("22000.5"), TAPER, NO_ROUNDING, ExactFraction("100.025"), D("1399.98")
    )


def test_tapered_amount_lines_differ_by_reduction() -> None:
    assert tapered_amount_line() != TaperedAmountLine(
        PERSONAL, INCOME, D("22000.5"), TAPER, CENT, ExactFraction(100), D("1399.98")
    )


def test_tapered_amount_lines_are_hashable() -> None:
    assert hash(tapered_amount_line()) == hash(tapered_amount_line())


def test_a_tapered_amount_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(tapered_amount_line())]


def test_a_tapered_amount_line_is_not_a_contribution_tier_or_subtracted_line() -> None:
    line = tapered_amount_line()

    assert not isinstance(line, ContributionTierLine)
    assert not isinstance(line, SubtractedNotBelowZeroLine)


def test_per_unit_amount_line_fields_in_order() -> None:
    line = per_unit_amount_line()

    assert line == PerUnitAmountLine(
        output=CHILD_AMOUNT,
        count_kind=CHILDREN,
        count=2,
        per_unit=Amount(D(544)),
        rounding=CENT,
        result=D(1088),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "count_kind",
        "count",
        "per_unit",
        "rounding",
        "result",
    ]
    assert line.output is CHILD_AMOUNT
    assert line.count_kind is CHILDREN
    assert line.count == 2
    assert type(line.count) is int
    assert line.per_unit == Amount(D(544))
    assert line.rounding == CENT
    assert line.result == D(1088)
    assert line.amount == D(1088)


def test_per_unit_amount_line_may_hold_a_count_of_zero() -> None:
    line = PerUnitAmountLine(CHILD_AMOUNT, CHILDREN, 0, Amount(D(544)), NO_ROUNDING, D(0))

    assert line.count == 0
    assert line.amount == D(0)


def test_per_unit_amount_lines_differ_by_count() -> None:
    assert per_unit_amount_line() != PerUnitAmountLine(
        CHILD_AMOUNT, CHILDREN, 3, Amount(D(544)), CENT, D(1088)
    )


def test_per_unit_amount_lines_differ_by_per_unit_amount() -> None:
    assert per_unit_amount_line() != PerUnitAmountLine(
        CHILD_AMOUNT, CHILDREN, 2, Amount(D(545)), CENT, D(1088)
    )


def test_per_unit_amount_lines_differ_by_rounding() -> None:
    assert per_unit_amount_line() != PerUnitAmountLine(
        CHILD_AMOUNT, CHILDREN, 2, Amount(D(544)), NO_ROUNDING, D(1088)
    )


def test_per_unit_amount_lines_differ_by_count_kind() -> None:
    other = ArtifactKind("ex/dependant_count", int)

    assert per_unit_amount_line() != PerUnitAmountLine(
        CHILD_AMOUNT, other, 2, Amount(D(544)), CENT, D(1088)
    )


def test_per_unit_amount_lines_are_hashable() -> None:
    assert hash(per_unit_amount_line()) == hash(per_unit_amount_line())


def test_a_per_unit_amount_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(per_unit_amount_line())]


def test_a_per_unit_amount_line_is_not_a_credit_amount_or_capped_amount_line() -> None:
    line = per_unit_amount_line()

    assert not isinstance(line, CreditAmountLine)
    assert not isinstance(line, CappedAmountLine)


def test_multiple_over_line_fields_in_order() -> None:
    line = multiple_over_line()

    assert line == MultipleOverLine(
        output=REDUCTION,
        base=TOTAL,
        base_amount=D(294),
        factor=Factor(D(2)),
        less=TAX,
        less_amount=D("100.25"),
        rounding=CENT,
        result=D("487.75"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "base",
        "base_amount",
        "factor",
        "less",
        "less_amount",
        "rounding",
        "result",
    ]
    assert line.output is REDUCTION
    assert line.base is TOTAL
    assert line.base_amount == D(294)
    assert line.factor == Factor(D(2))
    assert line.less is TAX
    assert line.less_amount == D("100.25")
    assert line.rounding == CENT
    assert line.result == D("487.75")
    assert line.amount == D("487.75")


def test_multiple_over_line_may_hold_a_floored_zero() -> None:
    # The multiple is below the figure taken off: the result is 0.
    line = MultipleOverLine(
        REDUCTION, TOTAL, D(294), Factor(D(2)), TAX, D("8195.7644476"), NO_ROUNDING, D(0)
    )

    assert line.result == D(0)
    assert line.amount == D(0)


def test_multiple_over_lines_differ_by_factor() -> None:
    assert multiple_over_line() != MultipleOverLine(
        REDUCTION, TOTAL, D(294), Factor(D(3)), TAX, D("100.25"), CENT, D("487.75")
    )


def test_multiple_over_lines_differ_by_rounding() -> None:
    assert multiple_over_line() != MultipleOverLine(
        REDUCTION, TOTAL, D(294), Factor(D(2)), TAX, D("100.25"), NO_ROUNDING, D("487.75")
    )


def test_multiple_over_lines_differ_by_the_figure_taken_off() -> None:
    assert multiple_over_line() != MultipleOverLine(
        REDUCTION, TOTAL, D(294), Factor(D(2)), TAX, D("100.5"), CENT, D("487.75")
    )


def test_multiple_over_lines_are_hashable() -> None:
    assert hash(multiple_over_line()) == hash(multiple_over_line())


def test_a_multiple_over_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(multiple_over_line())]


def test_a_multiple_over_line_is_not_a_subtracted_or_rate_applied_line() -> None:
    line = multiple_over_line()

    assert not isinstance(line, SubtractedNotBelowZeroLine)
    assert not isinstance(line, SubtractedLine)
    assert not isinstance(line, RateAppliedLine)


def test_at_most_line_fields_in_order() -> None:
    line = at_most_line()

    assert line == AtMostLine(
        output=ALLOWED,
        amount_kind=CLAIMED,
        amount_value=D("1500.25"),
        bound=LIMIT,
        bound_value=D(1926),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "bound",
        "bound_value",
    ]
    assert line.output is ALLOWED
    assert line.amount_kind is CLAIMED
    assert line.amount_value == D("1500.25")
    assert line.bound is LIMIT
    assert line.bound_value == D(1926)
    assert line.amount == D("1500.25")


def test_at_most_line_may_hold_an_amount_equal_to_its_bound() -> None:
    line = AtMostLine(ALLOWED, CLAIMED, D(1926), LIMIT, D(1926))

    assert line.amount == D(1926)


def test_at_most_line_may_hold_a_zero_amount() -> None:
    line = AtMostLine(ALLOWED, CLAIMED, D(0), LIMIT, D(0))

    assert line.amount == D(0)


def test_at_most_lines_differ_by_amount() -> None:
    assert at_most_line() != AtMostLine(ALLOWED, CLAIMED, D("1500.5"), LIMIT, D(1926))


def test_at_most_lines_differ_by_bound() -> None:
    assert at_most_line() != AtMostLine(ALLOWED, CLAIMED, D("1500.25"), LIMIT, D(2000))


def test_at_most_lines_differ_by_the_bounds_kind() -> None:
    other = ArtifactKind("ex/other_limit", Decimal)

    assert at_most_line() != AtMostLine(ALLOWED, CLAIMED, D("1500.25"), other, D(1926))


def test_at_most_lines_are_hashable() -> None:
    assert hash(at_most_line()) == hash(at_most_line())


def test_an_at_most_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(at_most_line())]


def test_an_at_most_line_is_not_a_lesser_of_or_capped_amount_line() -> None:
    line = at_most_line()

    assert not isinstance(line, LesserOfLine)
    assert not isinstance(line, CappedAmountLine)


def test_fraction_applied_line_fields_in_order() -> None:
    line = fraction_applied_line()

    assert line == FractionAppliedLine(
        output=PORTION,
        base=EARNED,
        base_amount=D(50000),
        fraction=Fraction(2, 3),
        rounding=CENT,
        result=D("33333.33"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "base",
        "base_amount",
        "fraction",
        "rounding",
        "result",
    ]
    assert line.output is PORTION
    assert line.base is EARNED
    assert line.base_amount == D(50000)
    assert line.fraction == Fraction(2, 3)
    assert line.rounding == CENT
    assert line.result == D("33333.33")
    assert line.amount == D("33333.33")


def test_fraction_applied_line_may_hold_an_unrounded_exact_amount() -> None:
    line = FractionAppliedLine(PORTION, EARNED, D(60000), Fraction(2, 3), NO_ROUNDING, D("40000"))

    assert line.amount == D("40000")


def test_fraction_applied_lines_differ_by_fraction() -> None:
    assert fraction_applied_line() != FractionAppliedLine(
        PORTION, EARNED, D(50000), Fraction(1, 3), CENT, D("33333.33")
    )


def test_fraction_applied_lines_differ_by_rounding() -> None:
    assert fraction_applied_line() != FractionAppliedLine(
        PORTION, EARNED, D(50000), Fraction(2, 3), NO_ROUNDING, D("33333.33")
    )


def test_fraction_applied_lines_are_hashable() -> None:
    assert hash(fraction_applied_line()) == hash(fraction_applied_line())


def test_a_fraction_applied_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(fraction_applied_line())]


def test_a_fraction_applied_line_is_not_a_rate_applied_line() -> None:
    assert not isinstance(fraction_applied_line(), RateAppliedLine)


def test_times_count_line_fields_in_order() -> None:
    line = times_count_line()

    assert line == TimesCountLine(
        output=CLAIMED_FOR_ALL,
        amount_kind=EACH,
        amount_value=D("16129.50"),
        count_kind=PERSONS,
        count=2,
        result=D("32259.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "count_kind",
        "count",
        "result",
    ]
    assert line.output is CLAIMED_FOR_ALL
    assert line.amount_kind is EACH
    assert line.amount_value == D("16129.50")
    assert line.count_kind is PERSONS
    assert line.count == 2
    assert type(line.count) is int
    assert line.result == D("32259.00")
    assert line.amount == D("32259.00")


def test_times_count_line_may_hold_a_count_of_zero() -> None:
    line = TimesCountLine(CLAIMED_FOR_ALL, EACH, D("16129.50"), PERSONS, 0, D(0))

    assert line.count == 0
    assert line.amount == D(0)


def test_times_count_lines_differ_by_count() -> None:
    assert times_count_line() != TimesCountLine(
        CLAIMED_FOR_ALL, EACH, D("16129.50"), PERSONS, 3, D("32259.00")
    )


def test_times_count_lines_differ_by_amount() -> None:
    assert times_count_line() != TimesCountLine(
        CLAIMED_FOR_ALL, EACH, D("16129.75"), PERSONS, 2, D("32259.00")
    )


def test_times_count_lines_differ_by_the_amounts_kind() -> None:
    other = ArtifactKind("ex/other_amount", Decimal)

    assert times_count_line() != TimesCountLine(
        CLAIMED_FOR_ALL, other, D("16129.50"), PERSONS, 2, D("32259.00")
    )


def test_times_count_lines_differ_by_count_kind() -> None:
    other = ArtifactKind("ex/dependant_count", int)

    assert times_count_line() != TimesCountLine(
        CLAIMED_FOR_ALL, EACH, D("16129.50"), other, 2, D("32259.00")
    )


def test_times_count_lines_are_hashable() -> None:
    assert hash(times_count_line()) == hash(times_count_line())


def test_a_times_count_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(times_count_line())]


def test_a_times_count_line_is_not_a_per_unit_amount_line() -> None:
    assert not isinstance(times_count_line(), PerUnitAmountLine)


def test_chosen_by_count_line_fields_in_order() -> None:
    line = chosen_by_count_line()

    assert line == ChosenByCountLine(
        output=CHOSEN,
        count_kind=DEPENDANTS,
        count=1,
        chosen_kind=WITH_FAMILY,
        chosen_value=D("2813.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "count_kind",
        "count",
        "chosen_kind",
        "chosen_value",
    ]
    assert line.output is CHOSEN
    assert line.count_kind is DEPENDANTS
    assert line.count == 1
    assert type(line.count) is int
    assert line.chosen_kind is WITH_FAMILY
    assert line.chosen_value == D("2813.00")
    assert line.amount == D("2813.00")
    assert str(line.amount) == "2813.00"


def test_chosen_by_count_line_may_hold_a_count_of_zero() -> None:
    line = ChosenByCountLine(CHOSEN, DEPENDANTS, 0, ALONE, D("1633"))

    assert line.count == 0
    assert line.chosen_kind is ALONE
    assert line.amount == D("1633")


def test_chosen_by_count_lines_differ_by_count() -> None:
    assert chosen_by_count_line() != ChosenByCountLine(
        CHOSEN, DEPENDANTS, 2, WITH_FAMILY, D("2813.00")
    )


def test_chosen_by_count_lines_differ_by_the_chosen_kind() -> None:
    assert chosen_by_count_line() != ChosenByCountLine(CHOSEN, DEPENDANTS, 1, ALONE, D("2813.00"))


def test_chosen_by_count_lines_differ_by_the_chosen_value() -> None:
    assert chosen_by_count_line() != ChosenByCountLine(
        CHOSEN, DEPENDANTS, 1, WITH_FAMILY, D("2813.01")
    )


def test_chosen_by_count_lines_differ_by_count_kind() -> None:
    other = ArtifactKind("ex/spouse_count", int)

    assert chosen_by_count_line() != ChosenByCountLine(CHOSEN, other, 1, WITH_FAMILY, D("2813.00"))


def test_chosen_by_count_lines_differ_by_output() -> None:
    other = ArtifactKind("ex/other_amount", Decimal)

    assert chosen_by_count_line() != ChosenByCountLine(
        other, DEPENDANTS, 1, WITH_FAMILY, D("2813.00")
    )


def test_chosen_by_count_lines_are_hashable() -> None:
    assert hash(chosen_by_count_line()) == hash(chosen_by_count_line())


def test_a_chosen_by_count_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(chosen_by_count_line())]


def test_a_chosen_by_count_line_is_not_a_times_count_line() -> None:
    assert not isinstance(chosen_by_count_line(), TimesCountLine)


def test_amount_by_count_line_fields_in_order() -> None:
    line = amount_by_count_line()

    assert line == AmountByCountLine(
        output=MONTHLY,
        count_kind=MONTHS,
        count=4,
        row=D("400.255"),
        rounding=CENT,
        result=D("400.26"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "count_kind",
        "count",
        "row",
        "rounding",
        "result",
    ]
    assert line.output is MONTHLY
    assert line.count_kind is MONTHS
    assert line.count == 4
    assert type(line.count) is int
    assert line.row == D("400.255")
    assert line.rounding == CENT
    assert line.result == D("400.26")
    assert line.amount == D("400.26")


def test_amount_by_count_line_may_hold_a_count_of_zero() -> None:
    line = AmountByCountLine(MONTHLY, MONTHS, 0, D("0"), NO_ROUNDING, D("0"))

    assert line.count == 0
    assert line.amount == D("0")


def test_amount_by_count_lines_differ_by_count() -> None:
    assert amount_by_count_line() != AmountByCountLine(
        MONTHLY, MONTHS, 3, D("400.255"), CENT, D("400.26")
    )


def test_amount_by_count_lines_differ_by_row() -> None:
    assert amount_by_count_line() != AmountByCountLine(
        MONTHLY, MONTHS, 4, D("400.256"), CENT, D("400.26")
    )


def test_amount_by_count_lines_differ_by_rounding() -> None:
    assert amount_by_count_line() != AmountByCountLine(
        MONTHLY, MONTHS, 4, D("400.255"), NO_ROUNDING, D("400.26")
    )


def test_amount_by_count_lines_differ_by_result() -> None:
    assert amount_by_count_line() != AmountByCountLine(
        MONTHLY, MONTHS, 4, D("400.255"), CENT, D("400.27")
    )


def test_amount_by_count_lines_differ_by_count_kind() -> None:
    other = ArtifactKind("ex/week_count", int)

    assert amount_by_count_line() != AmountByCountLine(
        MONTHLY, other, 4, D("400.255"), CENT, D("400.26")
    )


def test_amount_by_count_lines_are_hashable() -> None:
    assert hash(amount_by_count_line()) == hash(amount_by_count_line())


def test_an_amount_by_count_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(amount_by_count_line())]


def test_an_amount_by_count_line_is_not_a_per_unit_or_chosen_by_count_line() -> None:
    line = amount_by_count_line()

    assert not isinstance(line, PerUnitAmountLine)
    assert not isinstance(line, ChosenByCountLine)
    assert not isinstance(line, TimesCountLine)


def test_record_total_line_fields_in_order() -> None:
    line = record_total_line()

    assert line == RecordTotalLine(
        output=TOTAL, field=ITEM_AMOUNT, amounts=(D("6000"), D("4000.50")), total=D("10000.50")
    )
    assert [f.name for f in fields(line)] == ["output", "field", "amounts", "total"]
    assert line.output is TOTAL
    assert line.field is ITEM_AMOUNT
    assert line.amounts == (D("6000"), D("4000.50"))
    assert isinstance(line.amounts, tuple)
    assert line.total == D("10000.50")
    assert line.amount == D("10000.50")
    assert str(line.amount) == "10000.50"


def test_record_total_line_may_have_no_amounts() -> None:
    line = RecordTotalLine(TOTAL, ITEM_AMOUNT, (), D(0))

    assert line.amounts == ()
    assert line.amount == D(0)


def test_record_total_lines_differ_by_the_order_of_their_amounts() -> None:
    assert record_total_line() != RecordTotalLine(
        TOTAL, ITEM_AMOUNT, (D("4000.50"), D("6000")), D("10000.50")
    )


def test_record_total_lines_differ_by_the_amounts() -> None:
    assert record_total_line() != RecordTotalLine(
        TOTAL, ITEM_AMOUNT, (D("6000"), D("4000.51")), D("10000.50")
    )


def test_record_total_lines_differ_by_the_total() -> None:
    assert record_total_line() != RecordTotalLine(
        TOTAL, ITEM_AMOUNT, (D("6000"), D("4000.50")), D("10000.51")
    )


def test_record_total_lines_differ_by_the_field() -> None:
    other = ArtifactKind("ex/other_item_amount", Decimal)

    assert record_total_line() != RecordTotalLine(
        TOTAL, other, (D("6000"), D("4000.50")), D("10000.50")
    )


def test_record_total_lines_differ_by_the_output() -> None:
    other = ArtifactKind("ex/other_total", Decimal)

    assert record_total_line() != RecordTotalLine(
        other, ITEM_AMOUNT, (D("6000"), D("4000.50")), D("10000.50")
    )


def test_record_total_lines_are_hashable() -> None:
    assert hash(record_total_line()) == hash(record_total_line())


def test_a_record_total_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(record_total_line())]


def test_a_record_total_line_is_not_a_sum_line() -> None:
    assert not isinstance(record_total_line(), SumLine)
    assert cast(Any, record_total_line()) != SumLine(
        TOTAL, ((ITEM_AMOUNT, D("6000")), (ITEM_AMOUNT, D("4000.50"))), D("10000.50")
    )


def test_record_positive_total_line_fields_in_order() -> None:
    line = record_positive_total_line()

    assert line == RecordPositiveTotalLine(
        output=TOTAL, field=ITEM_AMOUNT, amounts=(D("6000"), D("-4000.50")), total=D("6000")
    )
    assert [f.name for f in fields(line)] == ["output", "field", "amounts", "total"]
    assert line.output is TOTAL
    assert line.field is ITEM_AMOUNT
    assert line.amounts == (D("6000"), D("-4000.50"))
    assert isinstance(line.amounts, tuple)
    assert line.total == D("6000")
    assert line.amount == D("6000")
    assert str(line.amount) == "6000"


def test_record_positive_total_line_may_have_no_amounts() -> None:
    line = RecordPositiveTotalLine(TOTAL, ITEM_AMOUNT, (), D(0))

    assert line.amounts == ()
    assert line.amount == D(0)


def test_record_positive_total_lines_differ_by_the_order_of_their_amounts() -> None:
    assert record_positive_total_line() != RecordPositiveTotalLine(
        TOTAL, ITEM_AMOUNT, (D("-4000.50"), D("6000")), D("6000")
    )


def test_record_positive_total_lines_differ_by_the_amounts() -> None:
    assert record_positive_total_line() != RecordPositiveTotalLine(
        TOTAL, ITEM_AMOUNT, (D("6000"), D("-4000.51")), D("6000")
    )


def test_record_positive_total_lines_differ_by_the_total() -> None:
    assert record_positive_total_line() != RecordPositiveTotalLine(
        TOTAL, ITEM_AMOUNT, (D("6000"), D("-4000.50")), D("6000.01")
    )


def test_record_positive_total_lines_differ_by_the_field() -> None:
    other = ArtifactKind("ex/other_item_amount", Decimal)

    assert record_positive_total_line() != RecordPositiveTotalLine(
        TOTAL, other, (D("6000"), D("-4000.50")), D("6000")
    )


def test_record_positive_total_lines_differ_by_the_output() -> None:
    other = ArtifactKind("ex/other_total", Decimal)

    assert record_positive_total_line() != RecordPositiveTotalLine(
        other, ITEM_AMOUNT, (D("6000"), D("-4000.50")), D("6000")
    )


def test_record_positive_total_lines_are_hashable() -> None:
    assert hash(record_positive_total_line()) == hash(record_positive_total_line())


def test_a_record_positive_total_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(record_positive_total_line())]


def test_a_record_positive_total_line_is_not_a_sum_line() -> None:
    assert not isinstance(record_positive_total_line(), SumLine)
    assert cast(Any, record_positive_total_line()) != SumLine(
        TOTAL, ((ITEM_AMOUNT, D("6000")), (ITEM_AMOUNT, D("-4000.50"))), D("6000")
    )


def test_a_record_positive_total_line_is_not_a_record_total_line() -> None:
    assert not isinstance(record_positive_total_line(), RecordTotalLine)


def test_chosen_by_range_line_fields_in_order() -> None:
    line = chosen_by_range_line()

    assert line == ChosenByRangeLine(
        output=CHOSEN,
        tested_kind=TESTED,
        tested_value=D("1000.00"),
        chosen_kind=IN_THE_SECOND_RANGE,
        chosen_value=D("625.01"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "tested_kind",
        "tested_value",
        "chosen_kind",
        "chosen_value",
    ]
    assert line.output is CHOSEN
    assert line.tested_kind is TESTED
    assert line.tested_value == D("1000.00")
    assert str(line.tested_value) == "1000.00"
    assert line.chosen_kind is IN_THE_SECOND_RANGE
    assert line.chosen_value == D("625.01")
    assert line.amount == D("625.01")
    assert str(line.amount) == "625.01"


def test_chosen_by_range_lines_differ_by_the_tested_value() -> None:
    assert chosen_by_range_line() != ChosenByRangeLine(
        CHOSEN, TESTED, D("1000.01"), IN_THE_SECOND_RANGE, D("625.01")
    )


def test_chosen_by_range_lines_differ_by_the_tested_kind() -> None:
    other = ArtifactKind("ex/other_tested", Decimal)

    assert chosen_by_range_line() != ChosenByRangeLine(
        CHOSEN, other, D("1000.00"), IN_THE_SECOND_RANGE, D("625.01")
    )


def test_chosen_by_range_lines_differ_by_the_chosen_kind() -> None:
    assert chosen_by_range_line() != ChosenByRangeLine(
        CHOSEN, TESTED, D("1000.00"), IN_THE_FIRST_RANGE, D("625.01")
    )


def test_chosen_by_range_lines_differ_by_the_chosen_value() -> None:
    assert chosen_by_range_line() != ChosenByRangeLine(
        CHOSEN, TESTED, D("1000.00"), IN_THE_SECOND_RANGE, D("625.02")
    )


def test_chosen_by_range_lines_differ_by_output() -> None:
    other = ArtifactKind("ex/other_amount", Decimal)

    assert chosen_by_range_line() != ChosenByRangeLine(
        other, TESTED, D("1000.00"), IN_THE_SECOND_RANGE, D("625.01")
    )


def test_chosen_by_range_lines_are_hashable() -> None:
    assert hash(chosen_by_range_line()) == hash(chosen_by_range_line())


def test_a_chosen_by_range_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(chosen_by_range_line())]


def test_a_chosen_by_range_line_is_not_a_chosen_by_count_line() -> None:
    assert not isinstance(chosen_by_range_line(), ChosenByCountLine)


def test_rate_by_income_band_line_fields_in_order() -> None:
    line = rate_by_income_band_line()

    assert line == RateByIncomeBandLine(
        output=BAND_RATE,
        income=FAMILY_INCOME,
        income_amount=D("45500.25"),
        row=BAND,
        rate=Rate(D("0.55")),
    )
    assert [f.name for f in fields(line)] == ["output", "income", "income_amount", "row", "rate"]
    assert line.output is BAND_RATE
    assert line.income is FAMILY_INCOME
    assert line.income_amount == D("45500.25")
    assert line.row == BAND
    assert line.rate == Rate(D("0.55"))


def test_a_rate_by_income_band_lines_amount_is_the_rates_value() -> None:
    line = rate_by_income_band_line()

    assert line.amount == D("0.55")
    assert type(line.amount) is Decimal


def test_rate_by_income_band_line_may_hold_the_unbounded_last_row() -> None:
    line = RateByIncomeBandLine(BAND_RATE, FAMILY_INCOME, D(150001), TOP_BAND, Rate(D(0)))

    assert line.row == TOP_BAND
    assert line.amount == D(0)


def test_rate_by_income_band_line_holds_no_row_for_the_rate_at_zero() -> None:
    # A figure of exactly zero takes the table's rate at zero, which is no row's.
    line = RateByIncomeBandLine(BAND_RATE, FAMILY_INCOME, D(0), None, Rate(D("0.75")))

    assert line.row is None
    assert line.amount == D("0.75")


def test_rate_by_income_band_lines_differ_by_row() -> None:
    assert rate_by_income_band_line() != RateByIncomeBandLine(
        BAND_RATE,
        FAMILY_INCOME,
        D("45500.25"),
        RateTableRow(D(40000), D(45000), Rate(D("0.55"))),
        Rate(D("0.55")),
    )


def test_rate_by_income_band_lines_differ_by_rate() -> None:
    assert rate_by_income_band_line() != RateByIncomeBandLine(
        BAND_RATE, FAMILY_INCOME, D("45500.25"), BAND, Rate(D("0.57"))
    )


def test_rate_by_income_band_lines_differ_by_income() -> None:
    assert rate_by_income_band_line() != RateByIncomeBandLine(
        BAND_RATE, FAMILY_INCOME, D("45500.26"), BAND, Rate(D("0.55"))
    )


def test_rate_by_income_band_lines_differ_by_output() -> None:
    other = ArtifactKind("ex/other_rate", Rate)

    assert rate_by_income_band_line() != RateByIncomeBandLine(
        other, FAMILY_INCOME, D("45500.25"), BAND, Rate(D("0.55"))
    )


def test_rate_by_income_band_lines_are_hashable() -> None:
    assert hash(rate_by_income_band_line()) == hash(rate_by_income_band_line())


def test_a_rate_by_income_band_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(rate_by_income_band_line())]


def test_a_rate_by_income_band_line_is_not_a_bracket_column_or_surcharge_tier_line() -> None:
    line = rate_by_income_band_line()

    assert not isinstance(line, BracketColumnLine)
    assert not isinstance(line, SurchargeTierLine)


def test_chosen_rate_applied_line_fields_in_order() -> None:
    line = chosen_rate_applied_line()

    assert line == ChosenRateAppliedLine(
        output=CARE_CREDIT,
        base=CARE_EXPENSES,
        base_amount=D("5000.01"),
        rate_kind=BAND_RATE,
        rate=Rate(D("0.55")),
        rounding=CENT,
        result=D("2750.01"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "base",
        "base_amount",
        "rate_kind",
        "rate",
        "rounding",
        "result",
    ]
    assert line.output is CARE_CREDIT
    assert line.base is CARE_EXPENSES
    assert line.base_amount == D("5000.01")
    assert line.rate_kind is BAND_RATE
    assert line.rate == Rate(D("0.55"))
    assert line.rounding == CENT
    assert line.result == D("2750.01")
    assert line.amount == D("2750.01")


def test_chosen_rate_applied_line_may_hold_an_unrounded_amount() -> None:
    line = ChosenRateAppliedLine(
        CARE_CREDIT,
        CARE_EXPENSES,
        D("5000.01"),
        BAND_RATE,
        Rate(D("0.55")),
        NO_ROUNDING,
        D("2750.0055"),
    )

    assert line.amount == D("2750.0055")


def test_chosen_rate_applied_lines_differ_by_rate() -> None:
    assert chosen_rate_applied_line() != ChosenRateAppliedLine(
        CARE_CREDIT, CARE_EXPENSES, D("5000.01"), BAND_RATE, Rate(D("0.53")), CENT, D("2750.01")
    )


def test_chosen_rate_applied_lines_differ_by_the_rates_kind() -> None:
    other = ArtifactKind("ex/other_rate", Rate)

    assert chosen_rate_applied_line() != ChosenRateAppliedLine(
        CARE_CREDIT, CARE_EXPENSES, D("5000.01"), other, Rate(D("0.55")), CENT, D("2750.01")
    )


def test_chosen_rate_applied_lines_differ_by_rounding() -> None:
    assert chosen_rate_applied_line() != ChosenRateAppliedLine(
        CARE_CREDIT,
        CARE_EXPENSES,
        D("5000.01"),
        BAND_RATE,
        Rate(D("0.55")),
        NO_ROUNDING,
        D("2750.01"),
    )


def test_chosen_rate_applied_lines_are_hashable() -> None:
    assert hash(chosen_rate_applied_line()) == hash(chosen_rate_applied_line())


def test_a_chosen_rate_applied_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(chosen_rate_applied_line())]


def test_a_chosen_rate_applied_line_is_not_a_rate_applied_line() -> None:
    assert not isinstance(chosen_rate_applied_line(), RateAppliedLine)


def test_apprentice_wages_line_fields_in_order() -> None:
    line = apprentice_wages_line()

    assert line == ApprenticeWagesLine(
        output=APPRENTICESHIP,
        position=2,
        salary_and_wages=D("25000"),
        maximum=Amount(D("20000")),
        rounding=CENT,
        result=D("20000.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "salary_and_wages",
        "maximum",
        "rounding",
        "result",
    ]
    assert line.amount == D("20000.00")


def test_apprentice_wages_lines_differ_by_each_field() -> None:
    line = apprentice_wages_line()

    assert line != ApprenticeWagesLine(
        APPRENTICESHIP, 1, line.salary_and_wages, line.maximum, CENT, line.result
    )
    assert line != ApprenticeWagesLine(
        APPRENTICESHIP, 2, D("15000"), line.maximum, CENT, line.result
    )
    assert line != ApprenticeWagesLine(
        APPRENTICESHIP, 2, line.salary_and_wages, Amount(D("21000")), CENT, line.result
    )
    assert line != ApprenticeWagesLine(
        APPRENTICESHIP, 2, line.salary_and_wages, line.maximum, CENT, D("19999.99")
    )


def test_caregiver_claim_line_fields_in_order() -> None:
    line = caregiver_claim_line()

    assert line == CaregiverClaimLine(
        output=CAREGIVER,
        position=2,
        base=Amount(D("28798.00")),
        net_income=D("25000"),
        maximum=Amount(D("8601")),
        rounding=CENT,
        result=D("3798.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "base",
        "net_income",
        "maximum",
        "rounding",
        "result",
    ]
    assert line.output is CAREGIVER
    assert line.position == 2
    assert line.base == Amount(D("28798.00"))
    assert line.net_income == D("25000")
    assert line.maximum == Amount(D("8601"))
    assert line.rounding == CENT
    assert line.result == D("3798.00")


def test_caregiver_claim_line_amount_is_the_result() -> None:
    line = caregiver_claim_line()

    assert line.amount == D("3798.00")
    assert str(line.amount) == "3798.00"
    assert "amount" not in [f.name for f in fields(line)]


def test_caregiver_claim_lines_differ_by_each_field() -> None:
    line = caregiver_claim_line()

    assert line != CaregiverClaimLine(
        CAREGIVER, 1, line.base, line.net_income, line.maximum, CENT, line.result
    )
    assert line != CaregiverClaimLine(
        CAREGIVER, 2, Amount(D("28799.00")), line.net_income, line.maximum, CENT, line.result
    )
    assert line != CaregiverClaimLine(
        CAREGIVER, 2, line.base, D("25001"), line.maximum, CENT, line.result
    )
    assert line != CaregiverClaimLine(
        CAREGIVER, 2, line.base, line.net_income, Amount(D("8602")), CENT, line.result
    )
    assert line != CaregiverClaimLine(
        CAREGIVER, 2, line.base, line.net_income, line.maximum, NO_ROUNDING, line.result
    )
    assert line != CaregiverClaimLine(
        CAREGIVER, 2, line.base, line.net_income, line.maximum, CENT, D("3798.01")
    )


def test_caregiver_claim_lines_are_hashable() -> None:
    assert hash(caregiver_claim_line()) == hash(caregiver_claim_line())


def test_renovation_line_3_fields_in_order() -> None:
    line = renovation_line_3()

    assert line == RenovationLine3(
        output=RENOVATION_3,
        position=2,
        expenditures=D("60000"),
        reimbursed=D("5000"),
        maximum=Amount(D("50000")),
        result=D("50000"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "expenditures",
        "reimbursed",
        "maximum",
        "result",
    ]
    assert line.amount == D("50000")
    assert "amount" not in [f.name for f in fields(line)]


def test_renovation_line_6_fields_in_order() -> None:
    line = renovation_line_6()

    assert line == RenovationLine6(
        output=RENOVATION_6,
        position=2,
        maximum=Amount(D("50000")),
        claimed_by_others=D("10000"),
        result=D("40000"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "maximum",
        "claimed_by_others",
        "result",
    ]
    assert line.amount == D("40000")


def test_renovation_line_7_fields_in_order() -> None:
    line = renovation_line_7()

    assert line == RenovationLine7(
        output=RENOVATION_8,
        position=2,
        line_3=D("50000"),
        line_6=D("40000"),
        result=D("40000"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "line_3",
        "line_6",
        "result",
    ]
    assert line.amount == D("40000")


def test_renovation_lines_differ_by_each_field() -> None:
    line = renovation_line_3()

    assert line != RenovationLine3(
        RENOVATION_3, 1, D("60000"), D("5000"), Amount(D("50000")), D("50000")
    )
    assert line != RenovationLine3(
        RENOVATION_3, 2, D("60001"), D("5000"), Amount(D("50000")), D("50000")
    )
    assert line != RenovationLine3(
        RENOVATION_3, 2, D("60000"), D("5001"), Amount(D("50000")), D("50000")
    )
    assert line != RenovationLine3(
        RENOVATION_3, 2, D("60000"), D("5000"), Amount(D("40000")), D("50000")
    )
    assert line != RenovationLine3(
        RENOVATION_3, 2, D("60000"), D("5000"), Amount(D("50000")), D("50001")
    )


def test_renovation_lines_are_hashable() -> None:
    assert hash(renovation_line_3()) == hash(renovation_line_3())
    assert hash(renovation_line_6()) == hash(renovation_line_6())
    assert hash(renovation_line_7()) == hash(renovation_line_7())


def test_other_dependant_medical_line_fields_in_order() -> None:
    line = other_dependant_medical_line()

    assert line == OtherDependantMedicalLine(
        output=MEDICAL,
        position=2,
        expenses=D("3000.00"),
        net_income=D("10000"),
        reduction=MEDICAL_REDUCTION,
        rounding=CENT,
        result=D("2700.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "expenses",
        "net_income",
        "reduction",
        "rounding",
        "result",
    ]
    assert line.output is MEDICAL
    assert line.position == 2
    assert line.expenses == D("3000.00")
    assert line.net_income == D("10000")
    assert line.reduction == MEDICAL_REDUCTION
    assert line.rounding == CENT
    assert line.result == D("2700.00")


def test_other_dependant_medical_line_amount_is_the_result() -> None:
    line = other_dependant_medical_line()

    assert line.amount == D("2700.00")
    assert str(line.amount) == "2700.00"
    assert "amount" not in [f.name for f in fields(line)]


def test_other_dependant_medical_line_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, other_dependant_medical_line()).result = D("1")


def test_other_dependant_medical_lines_differ_by_each_field() -> None:
    line = other_dependant_medical_line()
    other = ClaimReduction(Rate(D("0.03")), D("2834"), None)

    assert line != OtherDependantMedicalLine(
        MEDICAL, 1, line.expenses, line.net_income, line.reduction, CENT, line.result
    )
    assert line != OtherDependantMedicalLine(
        MEDICAL, 2, D("3001"), line.net_income, line.reduction, CENT, line.result
    )
    assert line != OtherDependantMedicalLine(
        MEDICAL, 2, line.expenses, D("10001"), line.reduction, CENT, line.result
    )
    assert line != OtherDependantMedicalLine(
        MEDICAL, 2, line.expenses, line.net_income, other, CENT, line.result
    )
    assert line != OtherDependantMedicalLine(
        MEDICAL, 2, line.expenses, line.net_income, line.reduction, NO_ROUNDING, line.result
    )
    assert line != OtherDependantMedicalLine(
        MEDICAL, 2, line.expenses, line.net_income, line.reduction, CENT, D("2700.01")
    )


def test_other_dependant_medical_lines_are_hashable() -> None:
    assert hash(other_dependant_medical_line()) == hash(other_dependant_medical_line())


def test_an_other_dependant_medical_line_is_not_a_caregiver_claim_line() -> None:
    assert not isinstance(other_dependant_medical_line(), CaregiverClaimLine)


def test_short_term_rental_non_compliant_line_fields_in_order() -> None:
    line = short_term_rental_non_compliant_line()

    assert line == ShortTermRentalNonCompliantLine(
        output=NON_COMPLIANT,
        position=2,
        related_expenses=D("900.00"),
        non_compliant_days=30,
        days=90,
        rounding=CENT,
        result=D("300.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "related_expenses",
        "non_compliant_days",
        "days",
        "rounding",
        "result",
    ]
    assert line.output is NON_COMPLIANT
    assert line.position == 2
    assert line.related_expenses == D("900.00")
    assert line.non_compliant_days == 30
    assert line.days == 90
    assert line.rounding == CENT
    assert line.result == D("300.00")


def test_short_term_rental_non_compliant_line_amount_is_the_result() -> None:
    line = short_term_rental_non_compliant_line()

    assert line.amount == D("300.00")
    assert str(line.amount) == "300.00"
    assert "amount" not in [f.name for f in fields(line)]


def test_short_term_rental_non_compliant_line_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, short_term_rental_non_compliant_line()).result = D("1")


def test_short_term_rental_non_compliant_lines_differ_by_each_field() -> None:
    line = short_term_rental_non_compliant_line()
    other_output = ArtifactKind("ex/other_expenses", Decimal)

    assert line != ShortTermRentalNonCompliantLine(
        other_output, 2, D("900.00"), 30, 90, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantLine(
        NON_COMPLIANT, 1, D("900.00"), 30, 90, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantLine(
        NON_COMPLIANT, 2, D("901.00"), 30, 90, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantLine(
        NON_COMPLIANT, 2, D("900.00"), 31, 90, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantLine(
        NON_COMPLIANT, 2, D("900.00"), 30, 91, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantLine(
        NON_COMPLIANT, 2, D("900.00"), 30, 90, NO_ROUNDING, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantLine(
        NON_COMPLIANT, 2, D("900.00"), 30, 90, CENT, D("300.01")
    )


def test_short_term_rental_non_compliant_lines_are_hashable() -> None:
    assert hash(short_term_rental_non_compliant_line()) == hash(
        short_term_rental_non_compliant_line()
    )


def test_a_short_term_rental_non_compliant_line_is_not_an_other_dependant_medical_line() -> None:
    assert not isinstance(short_term_rental_non_compliant_line(), OtherDependantMedicalLine)


def test_short_term_rental_non_compliant_cca_line_fields_in_order() -> None:
    line = short_term_rental_non_compliant_cca_line()

    assert line == ShortTermRentalNonCompliantCcaLine(
        output=NON_COMPLIANT_CCA_TOTAL,
        position=2,
        class_number=D("10.1"),
        related_cca=D("900.00"),
        non_compliant_days=30,
        days=90,
        rounding=CENT,
        result=D("300.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "class_number",
        "related_cca",
        "non_compliant_days",
        "days",
        "rounding",
        "result",
    ]
    assert line.amount == D("300.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_short_term_rental_non_compliant_cca_line_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, short_term_rental_non_compliant_cca_line()).result = D("1")


def test_short_term_rental_non_compliant_cca_lines_differ_by_each_field() -> None:
    line = short_term_rental_non_compliant_cca_line()

    assert line != ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA_TOTAL, 1, D("10.1"), D("900.00"), 30, 90, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA_TOTAL, 2, D("10"), D("900.00"), 30, 90, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA_TOTAL, 2, D("10.1"), D("901.00"), 30, 90, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA_TOTAL, 2, D("10.1"), D("900.00"), 31, 90, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA_TOTAL, 2, D("10.1"), D("900.00"), 30, 91, CENT, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA_TOTAL, 2, D("10.1"), D("900.00"), 30, 90, NO_ROUNDING, D("300.00")
    )
    assert line != ShortTermRentalNonCompliantCcaLine(
        NON_COMPLIANT_CCA_TOTAL, 2, D("10.1"), D("900.00"), 30, 90, CENT, D("300.01")
    )


def test_short_term_rental_non_compliant_cca_lines_are_hashable() -> None:
    assert hash(short_term_rental_non_compliant_cca_line()) == hash(
        short_term_rental_non_compliant_cca_line()
    )


def test_short_term_rental_non_compliant_cca_by_class_line_fields_in_order() -> None:
    line = short_term_rental_non_compliant_cca_by_class_line()

    assert line == ShortTermRentalNonCompliantCcaByClassLine(
        output=NON_COMPLIANT_CCA_BY_CLASS,
        position=2,
        class_number=D("10.1"),
        amounts=(D("300.00"), D("33.33")),
        result=D("333.33"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "class_number",
        "amounts",
        "result",
    ]
    assert line.amount == D("333.33")
    assert "amount" not in [f.name for f in fields(line)]


def test_short_term_rental_non_compliant_cca_by_class_line_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, short_term_rental_non_compliant_cca_by_class_line()).result = D("1")


def test_short_term_rental_non_compliant_cca_by_class_lines_differ_by_each_field() -> None:
    line = short_term_rental_non_compliant_cca_by_class_line()
    kind = NON_COMPLIANT_CCA_BY_CLASS

    assert line != ShortTermRentalNonCompliantCcaByClassLine(
        kind, 1, D("10.1"), (D("300.00"), D("33.33")), D("333.33")
    )
    assert line != ShortTermRentalNonCompliantCcaByClassLine(
        kind, 2, D("10"), (D("300.00"), D("33.33")), D("333.33")
    )
    assert line != ShortTermRentalNonCompliantCcaByClassLine(
        kind, 2, D("10.1"), (D("300.00"),), D("333.33")
    )
    assert line != ShortTermRentalNonCompliantCcaByClassLine(
        kind, 2, D("10.1"), (D("300.00"), D("33.33")), D("333.34")
    )


def test_short_term_rental_non_compliant_cca_by_class_lines_are_hashable() -> None:
    assert hash(short_term_rental_non_compliant_cca_by_class_line()) == hash(
        short_term_rental_non_compliant_cca_by_class_line()
    )


def test_rental_addition_line_fields_in_order() -> None:
    line = rental_addition_line()

    assert line == RentalAdditionLine(
        output=RENTAL_ADDITION_TOTAL,
        position=2,
        class_number=D("8"),
        total_cost=D("1000.00"),
        personal_portion=D("250.00"),
        result=D("750.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "class_number",
        "total_cost",
        "personal_portion",
        "result",
    ]
    assert line.output is RENTAL_ADDITION_TOTAL
    assert line.position == 2
    assert line.class_number == D("8")
    assert line.total_cost == D("1000.00")
    assert line.personal_portion == D("250.00")
    assert line.result == D("750.00")


def test_rental_addition_line_amount_is_the_result() -> None:
    line = rental_addition_line()

    assert line.amount == D("750.00")
    assert str(line.amount) == "750.00"
    assert "amount" not in [f.name for f in fields(line)]


def test_rental_addition_line_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, rental_addition_line()).result = D("1")


def test_rental_addition_lines_differ_by_each_field() -> None:
    line = rental_addition_line()
    other_output = ArtifactKind("ex/other_additions", Decimal)

    assert line != RentalAdditionLine(
        other_output, 2, D("8"), D("1000.00"), D("250.00"), D("750.00")
    )
    assert line != RentalAdditionLine(
        RENTAL_ADDITION_TOTAL, 1, D("8"), D("1000.00"), D("250.00"), D("750.00")
    )
    assert line != RentalAdditionLine(
        RENTAL_ADDITION_TOTAL, 2, D("50"), D("1000.00"), D("250.00"), D("750.00")
    )
    assert line != RentalAdditionLine(
        RENTAL_ADDITION_TOTAL, 2, D("8"), D("1001.00"), D("250.00"), D("750.00")
    )
    assert line != RentalAdditionLine(
        RENTAL_ADDITION_TOTAL, 2, D("8"), D("1000.00"), D("251.00"), D("750.00")
    )
    assert line != RentalAdditionLine(
        RENTAL_ADDITION_TOTAL, 2, D("8"), D("1000.00"), D("250.00"), D("750.01")
    )


def test_rental_addition_lines_are_hashable() -> None:
    assert hash(rental_addition_line()) == hash(rental_addition_line())


def test_foreign_property_tax_line_fields_in_order() -> None:
    line = foreign_property_tax_line()

    assert line == ForeignPropertyTaxLine(
        output=NON_COMPLIANT,
        position=2,
        tax_paid=D("6000"),
        income=D("20000"),
        rate=D("0.15"),
        rounding=CENT,
        limit=D("3000.00"),
        result=D("3000.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "tax_paid",
        "income",
        "rate",
        "rounding",
        "limit",
        "result",
    ]


def test_foreign_property_tax_line_amount_is_the_result() -> None:
    line = foreign_property_tax_line()

    assert line.amount == D("3000.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_foreign_property_tax_line_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, foreign_property_tax_line()).result = D("1")


def test_foreign_property_tax_lines_differ_by_each_field() -> None:
    line = foreign_property_tax_line()
    other_output = ArtifactKind("ex/other_expenses", Decimal)
    base: list[Any] = [
        NON_COMPLIANT,
        2,
        D("6000"),
        D("20000"),
        D("0.15"),
        CENT,
        D("3000.00"),
        D("3000.00"),
    ]
    varied = [
        other_output,
        1,
        D("6001"),
        D("20001"),
        D("0.16"),
        NO_ROUNDING,
        D("3000.01"),
        D("3000.01"),
    ]
    for index, value in enumerate(varied):
        args = list(base)
        args[index] = value
        assert line != ForeignPropertyTaxLine(*args)


def test_foreign_property_tax_lines_are_hashable() -> None:
    assert hash(foreign_property_tax_line()) == hash(foreign_property_tax_line())


def test_foreign_tax_credit_line_fields_in_order() -> None:
    line = foreign_tax_credit_line()

    assert line == ForeignTaxCreditLine(
        output=NON_COMPLIANT,
        position=2,
        tax_paid=D("1500"),
        income=D("10000"),
        net_income=D("100000"),
        basic_federal_tax=D("14000"),
        rounding=CENT,
        line_2=D("1400.00"),
        result=D("1400.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "tax_paid",
        "income",
        "net_income",
        "basic_federal_tax",
        "rounding",
        "line_2",
        "result",
    ]
    assert line.output is NON_COMPLIANT
    assert line.position == 2
    assert line.rounding == CENT


def test_foreign_tax_credit_line_amount_is_the_result() -> None:
    line = foreign_tax_credit_line()

    assert line.amount == D("1400.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_foreign_tax_credit_lines_differ_by_each_field() -> None:
    line = foreign_tax_credit_line()
    other_output = ArtifactKind("ex/other_expenses", Decimal)
    args: list[Any] = [
        NON_COMPLIANT,
        2,
        D("1500"),
        D("10000"),
        D("100000"),
        D("14000"),
        CENT,
        D("1400.00"),
        D("1400.00"),
    ]
    changes: list[Any] = [
        other_output,
        1,
        D("1501"),
        D("10001"),
        D("100001"),
        D("14001"),
        NO_ROUNDING,
        D("1400.01"),
        D("1400.01"),
    ]
    for index, changed in enumerate(changes):
        varied = [*args[:index], changed, *args[index + 1 :]]
        assert line != ForeignTaxCreditLine(*varied)


def test_foreign_tax_credit_lines_are_hashable() -> None:
    assert hash(foreign_tax_credit_line()) == hash(foreign_tax_credit_line())


def test_pooled_foreign_tax_credit_line_fields_in_order() -> None:
    line = pooled_foreign_tax_credit_line()

    assert line == PooledForeignTaxCreditLine(
        output=NON_COMPLIANT,
        countries=2,
        tax_paid=D("200"),
        income=D("10100"),
        net_income=D("100000"),
        basic_federal_tax=D("14000"),
        total_foreign_taxes=D("250"),
        threshold=D("200"),
        rounding=CENT,
        line_2=D("1414.00"),
        result=D("200"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "countries",
        "tax_paid",
        "income",
        "net_income",
        "basic_federal_tax",
        "total_foreign_taxes",
        "threshold",
        "rounding",
        "line_2",
        "result",
    ]
    assert line.countries == 2
    assert type(line.countries) is int


def test_pooled_foreign_tax_credit_line_amount_is_the_result() -> None:
    line = pooled_foreign_tax_credit_line()

    assert line.amount == D("200")
    assert "amount" not in [f.name for f in fields(line)]


def test_pooled_foreign_tax_credit_lines_differ_by_each_field() -> None:
    line = pooled_foreign_tax_credit_line()
    other_output = ArtifactKind("ex/other_expenses", Decimal)
    args: list[Any] = [
        NON_COMPLIANT,
        2,
        D("200"),
        D("10100"),
        D("100000"),
        D("14000"),
        D("250"),
        D("200"),
        CENT,
        D("1414.00"),
        D("200"),
    ]
    changes: list[Any] = [
        other_output,
        3,
        D("201"),
        D("10101"),
        D("100001"),
        D("14001"),
        D("251"),
        D("250"),
        NO_ROUNDING,
        D("1414.01"),
        D("199"),
    ]
    for index, changed in enumerate(changes):
        varied = [*args[:index], changed, *args[index + 1 :]]
        assert line != PooledForeignTaxCreditLine(*varied)


# (class, factory, field names after output and position, the value of each, the result)
BUSINESS_LINES: list[tuple[type, Any, list[str], list[Any]]] = [
    (
        ForeignBusinessLine4,
        foreign_business_line_4,
        ["tax_paid", "unused_credits", "result"],
        [D("400"), D("50"), D("450")],
    ),
    (
        ForeignBusinessLine5,
        foreign_business_line_5,
        ["income", "net_income", "basic_federal_tax", "rounding", "result"],
        [D("6000"), D("100000"), D("14500"), CENT, D("870.00")],
    ),
    (
        ForeignBusinessLine7,
        foreign_business_line_7,
        ["line_5", "line_6", "result"],
        [D("870.00"), D("100"), D("970.00")],
    ),
    (
        ForeignBusinessLine8,
        foreign_business_line_8,
        ["basic_federal_tax", "line_6", "result"],
        [D("14500"), D("100"), D("14600")],
    ),
    (
        ForeignBusinessLine10,
        foreign_business_line_10,
        ["line_8", "line_3", "result"],
        [D("14600"), D("1400"), D("13200")],
    ),
    (
        ForeignBusinessLine11,
        foreign_business_line_11,
        ["line_4", "line_7", "line_10", "result"],
        [D("450"), D("970.00"), D("13200"), D("450")],
    ),
]
BUSINESS_IDS = [cls.__name__ for cls, *_ in BUSINESS_LINES]


@pytest.mark.parametrize(("cls", "make", "names", "values"), BUSINESS_LINES, ids=BUSINESS_IDS)
def test_foreign_business_lines_have_their_fields_in_order(
    cls: type, make: Any, names: list[str], values: list[Any]
) -> None:
    line = make()

    assert [f.name for f in fields(line)] == ["output", "position", *names]
    assert line == cls(NON_COMPLIANT, 2, *values)
    assert line.output is NON_COMPLIANT
    assert line.position == 2
    assert type(line.position) is int


@pytest.mark.parametrize(("cls", "make", "names", "values"), BUSINESS_LINES, ids=BUSINESS_IDS)
def test_foreign_business_line_amount_is_the_result(
    cls: type, make: Any, names: list[str], values: list[Any]
) -> None:
    line = make()

    assert line.amount == values[-1]
    assert "amount" not in [f.name for f in fields(line)]


@pytest.mark.parametrize(("cls", "make", "names", "values"), BUSINESS_LINES, ids=BUSINESS_IDS)
def test_foreign_business_lines_differ_by_each_field(
    cls: type, make: Any, names: list[str], values: list[Any]
) -> None:
    line = make()
    args: list[Any] = [NON_COMPLIANT, 2, *values]
    for index in range(len(args)):
        changed: Any
        if index == 0:
            changed = ArtifactKind("ex/other_expenses", Decimal)
        elif index == 1:
            changed = 3
        elif args[index] == CENT:
            changed = NO_ROUNDING
        else:
            changed = args[index] + D("1")
        varied = [*args[:index], changed, *args[index + 1 :]]
        assert line != cls(*varied)


def test_the_foreign_business_lines_are_not_each_other() -> None:
    classes = [cls for cls, *_ in BUSINESS_LINES]
    for cls, make, *_ in BUSINESS_LINES:
        for other in classes:
            assert isinstance(make(), other) is (other is cls)


def test_a_pooled_foreign_tax_credit_line_is_not_a_foreign_tax_credit_line() -> None:
    assert not isinstance(pooled_foreign_tax_credit_line(), ForeignTaxCreditLine)
    assert not isinstance(foreign_tax_credit_line(), PooledForeignTaxCreditLine)


def test_provincial_foreign_tax_credit_line_fields_in_order() -> None:
    line = provincial_foreign_tax_credit_line()

    assert line == ProvincialForeignTaxCreditLine(
        output=NON_COMPLIANT,
        position=2,
        tax_paid=D("1500"),
        federal_credit=D("1400.00"),
        line_3=D("100.00"),
        income=D("10000"),
        net_income=D("100000"),
        provincial_tax=D("5000"),
        rounding=CENT,
        line_4=D("500.00"),
        result=D("100.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "tax_paid",
        "federal_credit",
        "line_3",
        "income",
        "net_income",
        "provincial_tax",
        "rounding",
        "line_4",
        "result",
        "special_credit",
        "divisor",
        "separate_sheet",
    ]
    assert line.output is NON_COMPLIANT
    assert line.position == 2
    assert type(line.position) is int
    assert line.rounding == CENT
    # Line 2 is the sheet's T2209 line 3 unless minimum tax is payable: the three fields default.
    assert line.special_credit is None
    assert line.divisor is None
    assert line.separate_sheet is False


def provincial_foreign_tax_credit_minimum_tax_line() -> ProvincialForeignTaxCreditLine:
    return ProvincialForeignTaxCreditLine(
        NON_COMPLIANT,
        2,
        D("300"),
        D("187.50"),
        D("112.50"),
        D("10000"),
        D("100000"),
        D("5000"),
        CENT,
        D("500.00"),
        D("112.50"),
        D("250"),
        ExactFraction(1000),
        True,
    )


def test_provincial_foreign_tax_credit_line_minimum_tax_fields() -> None:
    line = provincial_foreign_tax_credit_minimum_tax_line()

    assert line.special_credit == D("250")
    assert line.divisor == ExactFraction(1000)
    assert line.separate_sheet is True
    assert line.federal_credit == D("187.50")
    assert line.amount == D("112.50")


def test_provincial_foreign_tax_credit_minimum_tax_lines_differ_by_each_new_field() -> None:
    line = provincial_foreign_tax_credit_minimum_tax_line()

    assert line != replace(line, special_credit=D("251"))
    assert line != replace(line, special_credit=None)
    assert line != replace(line, divisor=ExactFraction(1001))
    assert line != replace(line, divisor=None)
    assert line != replace(line, separate_sheet=False)
    assert hash(line) == hash(provincial_foreign_tax_credit_minimum_tax_line())


def test_provincial_foreign_tax_credit_line_amount_is_the_result() -> None:
    line = provincial_foreign_tax_credit_line()

    assert line.amount == D("100.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_provincial_foreign_tax_credit_lines_differ_by_each_field() -> None:
    line = provincial_foreign_tax_credit_line()
    other_output = ArtifactKind("ex/other_expenses", Decimal)
    args: list[Any] = [
        NON_COMPLIANT,
        2,
        D("1500"),
        D("1400.00"),
        D("100.00"),
        D("10000"),
        D("100000"),
        D("5000"),
        CENT,
        D("500.00"),
        D("100.00"),
    ]
    changes: list[Any] = [
        other_output,
        1,
        D("1501"),
        D("1400.01"),
        D("100.01"),
        D("10001"),
        D("100001"),
        D("5001"),
        NO_ROUNDING,
        D("500.01"),
        D("99.00"),
    ]
    for index, changed in enumerate(changes):
        varied = [*args[:index], changed, *args[index + 1 :]]
        assert line != ProvincialForeignTaxCreditLine(*varied)


def test_provincial_foreign_tax_credit_lines_are_frozen_and_hashable() -> None:
    line = provincial_foreign_tax_credit_line()

    assert hash(line) == hash(provincial_foreign_tax_credit_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, "result", D(1))  # noqa: B010


def test_a_provincial_foreign_tax_credit_line_is_not_a_federal_foreign_tax_credit_line() -> None:
    assert not isinstance(provincial_foreign_tax_credit_line(), ForeignTaxCreditLine)
    assert not isinstance(provincial_foreign_tax_credit_line(), PooledForeignTaxCreditLine)


def test_caregiver_claim_less_claimed_line_fields_in_order() -> None:
    line = caregiver_claim_less_claimed_line()

    assert line == CaregiverClaimLessClaimedLine(
        output=CAREGIVER,
        position=2,
        base=Amount(D("26562.00")),
        net_income=D("5000"),
        maximum=Amount(D("6008")),
        allowable_before_claimed=D("6008.00"),
        claimed=D("2500.00"),
        rounding=CENT,
        result=D("3508.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "base",
        "net_income",
        "maximum",
        "allowable_before_claimed",
        "claimed",
        "rounding",
        "result",
    ]
    assert line.output is CAREGIVER
    assert line.position == 2
    assert line.base == Amount(D("26562.00"))
    assert line.net_income == D("5000")
    assert line.maximum == Amount(D("6008"))
    assert line.allowable_before_claimed == D("6008.00")
    assert line.claimed == D("2500.00")
    assert line.rounding == CENT
    assert line.result == D("3508.00")


def test_caregiver_claim_less_claimed_line_amount_is_the_result() -> None:
    line = caregiver_claim_less_claimed_line()

    assert line.amount == D("3508.00")
    assert str(line.amount) == "3508.00"
    assert "amount" not in [f.name for f in fields(line)]


def test_caregiver_claim_less_claimed_lines_differ_by_each_field() -> None:
    line = caregiver_claim_less_claimed_line()
    other = CaregiverClaimLessClaimedLine

    assert line != other(
        CAREGIVER,
        1,
        line.base,
        D("5000"),
        line.maximum,
        D("6008.00"),
        D("2500.00"),
        CENT,
        D("3508.00"),
    )
    assert line != other(
        CAREGIVER,
        2,
        Amount(D("26563.00")),
        D("5000"),
        line.maximum,
        D("6008.00"),
        D("2500.00"),
        CENT,
        D("3508.00"),
    )
    assert line != other(
        CAREGIVER,
        2,
        line.base,
        D("5001"),
        line.maximum,
        D("6008.00"),
        D("2500.00"),
        CENT,
        D("3508.00"),
    )
    assert line != other(
        CAREGIVER,
        2,
        line.base,
        D("5000"),
        Amount(D("6009")),
        D("6008.00"),
        D("2500.00"),
        CENT,
        D("3508.00"),
    )
    assert line != other(
        CAREGIVER,
        2,
        line.base,
        D("5000"),
        line.maximum,
        D("6007.00"),
        D("2500.00"),
        CENT,
        D("3508.00"),
    )
    assert line != other(
        CAREGIVER,
        2,
        line.base,
        D("5000"),
        line.maximum,
        D("6008.00"),
        D("2501.00"),
        CENT,
        D("3508.00"),
    )
    assert line != other(
        CAREGIVER,
        2,
        line.base,
        D("5000"),
        line.maximum,
        D("6008.00"),
        D("2500.00"),
        NO_ROUNDING,
        D("3508.00"),
    )
    assert line != other(
        CAREGIVER,
        2,
        line.base,
        D("5000"),
        line.maximum,
        D("6008.00"),
        D("2500.00"),
        CENT,
        D("3508.01"),
    )


def test_caregiver_claim_less_claimed_lines_are_hashable() -> None:
    assert hash(caregiver_claim_less_claimed_line()) == hash(caregiver_claim_less_claimed_line())


def test_a_caregiver_claim_less_claimed_line_is_not_a_caregiver_claim_line() -> None:
    assert not isinstance(caregiver_claim_less_claimed_line(), CaregiverClaimLine)


def test_disability_transfer_line_fields_in_order() -> None:
    line = disability_transfer_line()

    assert line == DisabilityTransferLine(
        output=TRANSFERRED,
        position=2,
        base=Amount(D("10138.00")),
        supplement=Amount(D("5914.00")),
        threshold=Amount(D("3464.00")),
        maximum=Amount(D("16052")),
        under_18=1,
        care_expenses=D("5000"),
        line_5=D("1536.00"),
        line_6=D("4378.00"),
        line_7=D("4378.00"),
        line_8=D("14516.00"),
        credit_amounts=D("1000"),
        line_10=D("15516.00"),
        taxable_income=D("2000"),
        line_12=D("13516.00"),
        rounding=CENT,
        result=D("13516.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "base",
        "supplement",
        "threshold",
        "maximum",
        "under_18",
        "care_expenses",
        "line_5",
        "line_6",
        "line_7",
        "line_8",
        "credit_amounts",
        "line_10",
        "taxable_income",
        "line_12",
        "rounding",
        "result",
    ]
    assert line.output is TRANSFERRED
    assert line.position == 2
    assert line.base == Amount(D("10138.00"))
    assert line.supplement == Amount(D("5914.00"))
    assert line.threshold == Amount(D("3464.00"))
    assert line.maximum == Amount(D("16052"))
    assert line.under_18 == 1
    assert line.care_expenses == D("5000")
    assert line.line_5 == D("1536.00")
    assert line.line_6 == D("4378.00")
    assert line.line_7 == D("4378.00")
    assert line.line_8 == D("14516.00")
    assert line.credit_amounts == D("1000")
    assert line.line_10 == D("15516.00")
    assert line.taxable_income == D("2000")
    assert line.line_12 == D("13516.00")
    assert line.rounding == CENT
    assert line.result == D("13516.00")


def test_disability_transfer_line_amount_is_the_result() -> None:
    line = disability_transfer_line()

    assert line.amount == D("13516.00")
    assert str(line.amount) == "13516.00"
    assert "amount" not in [f.name for f in fields(line)]


def test_disability_transfer_lines_differ_by_each_field() -> None:
    line = disability_transfer_line()
    same = dict(
        zip(
            [f.name for f in fields(line)],
            [getattr(line, f.name) for f in fields(line)],
            strict=True,
        )
    )
    changed: dict[str, Any] = {
        "position": 1,
        "base": Amount(D("10139.00")),
        "supplement": Amount(D("5915.00")),
        "threshold": Amount(D("3465.00")),
        "maximum": Amount(D("16053")),
        "under_18": 0,
        "care_expenses": D("5001"),
        "line_5": D("1537.00"),
        "line_6": D("4379.00"),
        "line_7": D("4379.00"),
        "line_8": D("14517.00"),
        "credit_amounts": D("1001"),
        "line_10": D("15517.00"),
        "taxable_income": D("2001"),
        "line_12": D("13517.00"),
        "rounding": NO_ROUNDING,
        "result": D("13516.01"),
    }

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != DisabilityTransferLine(**{**same, name: value}), name
    assert line != DisabilityTransferLine(**{**same, "output": CAREGIVER})


def test_disability_transfer_lines_are_hashable() -> None:
    assert hash(disability_transfer_line()) == hash(disability_transfer_line())


def test_a_disability_transfer_line_is_not_a_caregiver_claim_line() -> None:
    assert not isinstance(disability_transfer_line(), CaregiverClaimLine)


def test_principal_residence_gain_line_fields_in_order() -> None:
    line = principal_residence_gain_line()

    assert line == PrincipalResidenceGainLine(
        output=RESIDENCE_GAIN,
        position=2,
        years_designated_after_1981=6,
        years_designated_1972_to_1981=0,
        designated=6,
        years_owned_after_1981=10,
        years_owned_1972_to_1981=0,
        owned=10,
        plus_one=1,
        proceeds=D("400000.00"),
        adjusted_cost_base=D("95000.00"),
        outlays=D("5000.00"),
        gain=D("300000.00"),
        line_20=7,
        line_21=D("2100000.00"),
        rounding=CENT,
        exempt=D("210000.00"),
        part_2_applies=0,
        line_53=D("0"),
        line_24=D("90000.00"),
        result=D("90000.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "years_designated_after_1981",
        "years_designated_1972_to_1981",
        "designated",
        "years_owned_after_1981",
        "years_owned_1972_to_1981",
        "owned",
        "plus_one",
        "proceeds",
        "adjusted_cost_base",
        "outlays",
        "gain",
        "line_20",
        "line_21",
        "rounding",
        "exempt",
        "part_2_applies",
        "line_53",
        "line_24",
        "result",
    ]
    assert line.output is RESIDENCE_GAIN
    assert line.position == 2
    assert line.designated == 6
    assert line.owned == 10
    assert line.plus_one == 1
    assert line.gain == D("300000.00")
    assert line.line_20 == 7
    assert line.line_21 == D("2100000.00")
    assert line.rounding == CENT
    assert line.exempt == D("210000.00")
    assert line.part_2_applies == 0
    assert line.line_53 == D("0")
    assert line.line_24 == D("90000.00")
    assert line.result == D("90000.00")


def test_principal_residence_gain_line_amount_is_the_result() -> None:
    line = principal_residence_gain_line()

    assert line.amount == D("90000.00")
    assert str(line.amount) == "90000.00"
    assert "amount" not in [f.name for f in fields(line)]


def test_principal_residence_gain_lines_differ_by_each_field() -> None:
    line = principal_residence_gain_line()
    same = dict(
        zip(
            [f.name for f in fields(line)],
            [getattr(line, f.name) for f in fields(line)],
            strict=True,
        )
    )
    changed: dict[str, Any] = {
        "position": 1,
        "years_designated_after_1981": 5,
        "years_designated_1972_to_1981": 1,
        "designated": 5,
        "years_owned_after_1981": 9,
        "years_owned_1972_to_1981": 1,
        "owned": 9,
        "plus_one": 0,
        "proceeds": D("400000.01"),
        "adjusted_cost_base": D("95000.01"),
        "outlays": D("5000.01"),
        "gain": D("300000.01"),
        "line_20": 6,
        "line_21": D("2100000.01"),
        "rounding": NO_ROUNDING,
        "exempt": D("210000.01"),
        "part_2_applies": 1,
        "line_53": D("0.01"),
        "line_24": D("90000.02"),
        "result": D("90000.01"),
    }

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != PrincipalResidenceGainLine(**{**same, name: value}), name
    assert line != PrincipalResidenceGainLine(**{**same, "output": CAREGIVER})


def test_principal_residence_gain_lines_are_hashable() -> None:
    assert hash(principal_residence_gain_line()) == hash(principal_residence_gain_line())


def test_a_principal_residence_gain_line_is_not_a_disability_transfer_line() -> None:
    assert not isinstance(principal_residence_gain_line(), DisabilityTransferLine)


# --- Form T2091(IND) Part 2: one line per computed line, 27 to 53 ---------------------------------
#
# Each records one property's figures for its line, named after the form lines it takes, then
# `result`, the line's figure. The areas the form says not to complete carry `completed` False.

PART_2_LINES: list[tuple[type, list[str], list[Any]]] = [
    (
        PrincipalResidenceLine27,
        ["completed", "line_12", "line_11", "result"],
        [True, D("90000.00"), D("40000.00"), D("50000.00")],
    ),
    (
        PrincipalResidenceLine29,
        ["completed", "line_2", "plus_one", "result"],
        [True, 1, 1, D("2")],
    ),
    (
        PrincipalResidenceLine30,
        ["completed", "line_27", "line_29", "result"],
        [True, D("50000.00"), D("2"), D("100000.00")],
    ),
    (
        PrincipalResidenceLine32,
        ["completed", "line_30", "line_6", "rounding", "result"],
        [True, D("100000.00"), 4, CENT, D("25000.00")],
    ),
    (
        PrincipalResidenceLine33,
        ["completed", "line_27", "line_32", "result"],
        [True, D("50000.00"), D("25000.00"), D("25000.00")],
    ),
    (
        PrincipalResidenceLine38,
        ["completed", "line_12", "line_13", "line_9", "result"],
        [True, D("90000.00"), D("10000.00"), D("5000.00"), D("105000.00")],
    ),
    (
        PrincipalResidenceLine39,
        ["completed", "line_8", "line_38", "result"],
        [True, D("300000.00"), D("105000.00"), D("195000.00")],
    ),
    (
        PrincipalResidenceLine42,
        ["completed", "line_39", "line_1", "result"],
        [True, D("195000.00"), 6, D("1170000.00")],
    ),
    (
        PrincipalResidenceLine44,
        ["completed", "line_42", "line_5", "rounding", "result"],
        [True, D("1170000.00"), 10, CENT, D("117000.00")],
    ),
    (
        PrincipalResidenceLine45,
        ["completed", "line_39", "line_44", "result"],
        [True, D("195000.00"), D("117000.00"), D("78000.00")],
    ),
    (
        PrincipalResidenceLine48,
        ["completed", "line_12", "line_8", "result"],
        [True, D("90000.00"), D("300000.00"), D("0")],
    ),
    (
        PrincipalResidenceLine51,
        ["completed", "line_33", "line_45", "result"],
        [True, D("25000.00"), D("78000.00"), D("103000.00")],
    ),
    (
        PrincipalResidenceLine53,
        ["completed", "line_51", "line_48", "result"],
        [True, D("103000.00"), D("0"), D("103000.00")],
    ),
]
PART_2_IDS = [cls.__name__ for cls, *_ in PART_2_LINES]
ALL_LINES.extend(partial(cls, RESIDENCE_GAIN, 2, *values) for cls, _, values in PART_2_LINES)


@pytest.mark.parametrize(("cls", "names", "values"), PART_2_LINES, ids=PART_2_IDS)
def test_part_2_lines_have_their_fields_in_order(
    cls: type, names: list[str], values: list[Any]
) -> None:
    line = cls(RESIDENCE_GAIN, 2, *values)

    assert [f.name for f in fields(line)] == ["output", "position", *names]
    assert line.output is RESIDENCE_GAIN
    assert line.position == 2
    assert type(line.position) is int
    for name, value in zip(names, values, strict=True):
        assert getattr(line, name) == value, name


@pytest.mark.parametrize(("cls", "names", "values"), PART_2_LINES, ids=PART_2_IDS)
def test_part_2_line_amount_is_the_result(cls: type, names: list[str], values: list[Any]) -> None:
    line = cls(RESIDENCE_GAIN, 2, *values)

    assert line.amount == values[-1]
    assert "amount" not in [f.name for f in fields(line)]


@pytest.mark.parametrize(("cls", "names", "values"), PART_2_LINES, ids=PART_2_IDS)
def test_part_2_lines_differ_by_each_field(cls: type, names: list[str], values: list[Any]) -> None:
    line = cls(RESIDENCE_GAIN, 2, *values)
    args = [RESIDENCE_GAIN, 2, *values]
    for name, value in zip(["output", "position", *names], args, strict=True):
        changed: Any
        if name == "output":
            changed = ArtifactKind("ex/other_residence_line", Decimal)
        elif name == "position":
            changed = 3
        elif isinstance(value, bool):
            changed = not value
        elif value == CENT:
            changed = NO_ROUNDING
        elif isinstance(value, int):
            changed = value + 1
        else:
            changed = value + D("1")
        assert line != replace(line, **{name: changed}), name


@pytest.mark.parametrize(("cls", "names", "values"), PART_2_LINES, ids=PART_2_IDS)
def test_part_2_lines_are_hashable(cls: type, names: list[str], values: list[Any]) -> None:
    assert hash(cls(RESIDENCE_GAIN, 2, *values)) == hash(cls(RESIDENCE_GAIN, 2, *values))


def test_part_2_lines_are_not_each_other_nor_the_gain_line() -> None:
    classes = [cls for cls, *_ in PART_2_LINES]
    for cls, _names, values in PART_2_LINES:
        made = cls(RESIDENCE_GAIN, 2, *values)
        for other in [*classes, PrincipalResidenceGainLine]:
            assert isinstance(made, other) is (other is cls), (cls.__name__, other.__name__)
        assert not isinstance(made, DisabilityTransferLine)


# --- Form T2091(IND)-WS and Part 4: one line per worksheet line that Part 4 reads, and 56 and 57
#
# Each records one property's figures for its line, named after the form's lines (a worksheet
# line is named `line_N` with N the worksheet's number, and a line of the form, T2091(IND), by its
# own number), then `result`. A worksheet line is `completed` when the election was filed (lines 16
# to 18 also need Chart 1); line 57 has no flag, since the form has none for it.

WORKSHEET_LINES: list[tuple[type, list[str], list[Any]]] = [
    (
        PrincipalResidenceWorksheetLine3,
        ["completed", "line_1", "line_2", "result"],
        [True, 5, 0, D("5")],
    ),
    (
        PrincipalResidenceWorksheetLine6,
        ["completed", "line_4", "line_5", "result"],
        [True, 12, 0, D("12")],
    ),
    (
        PrincipalResidenceWorksheetLine16,
        ["completed", "line_14", "factor", "rounding", "result"],
        [True, D("200000.00"), D("1.1"), CENT, D("220000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine17,
        ["completed", "line_15", "line_16", "result"],
        [True, D("230000.00"), D("220000.00"), D("10000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine18,
        ["completed", "line_14", "line_17", "result"],
        [True, D("200000.00"), D("10000.00"), D("190000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine19,
        ["completed", "chart_completed", "line_18", "line_10", "result"],
        [True, True, D("190000.00"), D("200000.00"), D("190000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine21,
        ["completed", "line_19", "line_20", "result"],
        [True, D("190000.00"), D("100000.00"), D("90000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine23,
        ["completed", "line_3", "plus_one", "result"],
        [True, 5, 1, D("6")],
    ),
    (
        PrincipalResidenceWorksheetLine24,
        ["completed", "line_22", "line_23", "result"],
        [True, D("90000.00"), 6, D("540000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine26,
        ["completed", "line_24", "line_25", "rounding", "result"],
        [True, D("540000.00"), 12, CENT, D("45000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine27,
        ["completed", "line_21", "line_26", "result"],
        [True, D("90000.00"), D("45000.00"), D("45000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine59,
        ["completed", "part_2_completed", "line_27", "line_58", "result"],
        [True, True, D("45000.00"), D("30000.00"), D("30000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine61,
        ["completed", "line_59", "line_60", "result"],
        [True, D("45000.00"), 24, D("1080000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine63,
        ["completed", "line_61", "line_62", "rounding", "result"],
        [True, D("1080000.00"), 74, CENT, D("14594.59")],
    ),
    (
        PrincipalResidenceWorksheetLine64,
        ["completed", "line_59", "line_63", "result"],
        [True, D("45000.00"), D("14594.59"), D("30405.41")],
    ),
    (
        PrincipalResidenceWorksheetLine66,
        ["completed", "line_64", "line_65", "result"],
        [True, D("30405.41"), D("100000.00"), D("30405.41")],
    ),
    # Form T2091(IND)-WS Part 2, lines 30 to 58: each calculated line records its own figures;
    # `completed` is True when the line is completed (the election filed, Part 2 applying and the
    # area the line is in not skipped). The figures of an area's lines are the lines the form reads.
    (
        PrincipalResidenceWorksheetLine30,
        ["completed", "line_28", "line_29", "result"],
        [True, D("240000.00"), D("120000.00"), D("120000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine32,
        ["completed", "line_2", "plus_one", "result"],
        [True, 1, 1, D("2")],
    ),
    (
        PrincipalResidenceWorksheetLine33,
        ["completed", "line_31", "line_32", "result"],
        [True, D("120000.00"), 2, D("240000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine35,
        ["completed", "line_33", "line_34", "rounding", "result"],
        [True, D("240000.00"), 4, CENT, D("60000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine36,
        ["completed", "line_30", "line_35", "result"],
        [True, D("120000.00"), D("60000.00"), D("60000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine40,
        ["completed", "line_38", "line_39", "result"],
        [True, D("240000.00"), D("6000.00"), D("246000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine41,
        ["completed", "line_37", "line_40", "result"],
        [True, D("300000.00"), D("246000.00"), D("54000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine44,
        ["completed", "line_42", "line_43", "result"],
        [True, D("54000.00"), 4, D("216000.00")],
    ),
    (
        PrincipalResidenceWorksheetLine46,
        ["completed", "line_44", "line_45", "rounding", "result"],
        [True, D("216000.00"), 13, CENT, D("16615.38")],
    ),
    (
        PrincipalResidenceWorksheetLine47,
        ["completed", "line_41", "line_46", "result"],
        [True, D("54000.00"), D("16615.38"), D("37384.62")],
    ),
    (
        PrincipalResidenceWorksheetLine50,
        ["completed", "line_48", "line_49", "result"],
        [True, D("240000.00"), D("300000.00"), D("0")],
    ),
    (
        PrincipalResidenceWorksheetLine53,
        ["completed", "line_51", "line_52", "result"],
        [True, D("60000.00"), D("37384.62"), D("97384.62")],
    ),
    (
        PrincipalResidenceWorksheetLine55,
        ["completed", "line_53", "line_54", "result"],
        [True, D("97384.62"), D("0"), D("97384.62")],
    ),
    (
        PrincipalResidenceWorksheetLine58,
        ["completed", "line_56", "line_57", "result"],
        [True, D("58235.29"), D("97384.62"), D("58235.29")],
    ),
    (
        PrincipalResidenceLine56,
        ["completed", "line_66", "result"],
        [True, D("30405.41"), D("30405.41")],
    ),
    (
        PrincipalResidenceLine57,
        ["line_55", "line_56", "result"],
        [D("150000.00"), D("30405.41"), D("119594.59")],
    ),
]
WORKSHEET_IDS = [cls.__name__ for cls, *_ in WORKSHEET_LINES]
ALL_LINES.extend(partial(cls, RESIDENCE_GAIN, 2, *values) for cls, _, values in WORKSHEET_LINES)


@pytest.mark.parametrize(("cls", "names", "values"), WORKSHEET_LINES, ids=WORKSHEET_IDS)
def test_worksheet_lines_have_their_fields_in_order(
    cls: type, names: list[str], values: list[Any]
) -> None:
    line = cls(RESIDENCE_GAIN, 2, *values)

    assert [f.name for f in fields(line)] == ["output", "position", *names]
    assert line.output is RESIDENCE_GAIN
    assert line.position == 2
    for name, value in zip(names, values, strict=True):
        assert getattr(line, name) == value, name


@pytest.mark.parametrize(("cls", "names", "values"), WORKSHEET_LINES, ids=WORKSHEET_IDS)
def test_worksheet_line_amount_is_the_result(
    cls: type, names: list[str], values: list[Any]
) -> None:
    line = cls(RESIDENCE_GAIN, 2, *values)

    assert line.amount == values[-1]
    assert "amount" not in [f.name for f in fields(line)]


@pytest.mark.parametrize(("cls", "names", "values"), WORKSHEET_LINES, ids=WORKSHEET_IDS)
def test_worksheet_lines_differ_by_each_field(
    cls: type, names: list[str], values: list[Any]
) -> None:
    line = cls(RESIDENCE_GAIN, 2, *values)
    args = [RESIDENCE_GAIN, 2, *values]
    for name, value in zip(["output", "position", *names], args, strict=True):
        changed: Any
        if name == "output":
            changed = ArtifactKind("ex/other_residence_line", Decimal)
        elif name == "position":
            changed = 3
        elif isinstance(value, bool):
            changed = not value
        elif value == CENT:
            changed = NO_ROUNDING
        elif isinstance(value, int):
            changed = value + 1
        else:
            changed = value + D("1")
        assert line != replace(line, **{name: changed}), name


@pytest.mark.parametrize(("cls", "names", "values"), WORKSHEET_LINES, ids=WORKSHEET_IDS)
def test_worksheet_lines_are_hashable(cls: type, names: list[str], values: list[Any]) -> None:
    assert hash(cls(RESIDENCE_GAIN, 2, *values)) == hash(cls(RESIDENCE_GAIN, 2, *values))


def test_worksheet_lines_are_not_each_other_nor_the_part_2_or_gain_lines() -> None:
    classes = [cls for cls, *_ in WORKSHEET_LINES]
    for cls, _names, values in WORKSHEET_LINES:
        made = cls(RESIDENCE_GAIN, 2, *values)
        for other in [*classes, PrincipalResidenceGainLine, PrincipalResidenceLine53]:
            assert isinstance(made, other) is (other is cls), (cls.__name__, other.__name__)
        assert not isinstance(made, DisabilityTransferLine)


def test_line_57_has_no_completed_flag() -> None:
    assert [f.name for f in fields(PrincipalResidenceLine57)] == [
        "output",
        "position",
        "line_55",
        "line_56",
        "result",
    ]


def test_item_sum_line_fields_in_order() -> None:
    line = item_sum_line()

    assert line == ItemSumLine(
        output=TOTAL,
        position=2,
        parts=((PART_ONE, D("400.00")), (PART_TWO, D("500"))),
        total=D("900.00"),
    )
    assert [f.name for f in fields(line)] == ["output", "position", "parts", "total"]
    assert line.output is TOTAL
    assert line.position == 2
    assert line.parts == ((PART_ONE, D("400.00")), (PART_TWO, D("500")))
    assert line.total == D("900.00")
    assert str(line.amount) == "900.00"


def test_item_sum_line_amount_is_the_total() -> None:
    line = item_sum_line()

    assert line.amount == D("900.00")
    assert str(line.amount) == "900.00"
    assert "amount" not in [f.name for f in fields(line)]


def test_item_sum_line_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, item_sum_line()).total = D("1")


def test_item_sum_lines_are_hashable() -> None:
    assert hash(item_sum_line()) == hash(item_sum_line())


def test_item_sum_lines_differ_by_position_parts_and_total() -> None:
    line = item_sum_line()
    parts = ((PART_ONE, D("400.00")), (PART_TWO, D("500")))

    assert line != ItemSumLine(TOTAL, 3, parts, D("900.00"))
    assert line != ItemSumLine(TOTAL, 2, ((PART_TWO, D("400.00")), (PART_ONE, D("500"))), D("900"))
    assert line != ItemSumLine(TOTAL, 2, parts, D("901.00"))
    assert line != ItemSumLine(BASE, 2, parts, D("900.00"))


def test_item_lesser_of_line_fields_in_order() -> None:
    line = item_lesser_of_line()

    assert line == ItemLesserOfLine(
        output=TOTAL,
        position=1,
        parts=((PART_ONE, D("1500")), (PART_TWO, D("750.50"))),
        result=D("750.50"),
    )
    assert [f.name for f in fields(line)] == ["output", "position", "parts", "result"]
    assert line.position == 1
    assert line.result == D("750.50")
    assert line.amount == D("750.50")


def test_item_lesser_of_line_amount_is_the_result() -> None:
    line = item_lesser_of_line()

    assert str(line.amount) == "750.50"
    assert "amount" not in [f.name for f in fields(line)]


def test_item_lesser_of_line_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, item_lesser_of_line()).result = D("1")


def test_item_lesser_of_lines_are_hashable() -> None:
    assert hash(item_lesser_of_line()) == hash(item_lesser_of_line())


def test_item_lesser_of_lines_differ_by_position_and_result() -> None:
    parts = ((PART_ONE, D("1500")), (PART_TWO, D("750.50")))

    assert item_lesser_of_line() != ItemLesserOfLine(TOTAL, 2, parts, D("750.50"))
    assert item_lesser_of_line() != ItemLesserOfLine(TOTAL, 1, parts, D("750.51"))


def test_items_total_line_fields_in_order() -> None:
    line = items_total_line()

    assert line == ItemsTotalLine(
        output=CAREGIVER, items=((1, D("750.00")), (3, D("800"))), total=D("1550.00")
    )
    assert [f.name for f in fields(line)] == ["output", "items", "total"]
    assert line.items == ((1, D("750.00")), (3, D("800")))
    assert line.total == D("1550.00")
    assert str(line.amount) == "1550.00"


def test_an_items_total_line_may_hold_no_items() -> None:
    line = ItemsTotalLine(CAREGIVER, (), D("0"))

    assert line.items == ()
    assert line.amount == D("0")


def test_items_total_lines_differ_by_items_and_total() -> None:
    assert items_total_line() != ItemsTotalLine(CAREGIVER, ((1, D("750.00")),), D("1550.00"))
    assert items_total_line() != ItemsTotalLine(
        CAREGIVER, ((2, D("750.00")), (3, D("800"))), D("1550.00")
    )
    assert items_total_line() != ItemsTotalLine(
        CAREGIVER, ((1, D("750.00")), (3, D("800"))), D("1551.00")
    )


def test_condition_line_fields_in_order() -> None:
    line = condition_line()

    assert line == ConditionLine(
        output=COUNT_GATE,
        position=2,
        text="There is an amount on line 72",
        reads=((REDUCTION_BASE, D("120.00")),),
        applies=True,
    )
    assert [f.name for f in fields(line)] == ["output", "position", "text", "reads", "applies"]
    assert line.output is COUNT_GATE
    assert line.position == 2
    assert line.text == "There is an amount on line 72"
    assert line.reads == ((REDUCTION_BASE, D("120.00")),)
    assert line.applies is True


def test_a_condition_line_amount_is_1_when_it_applies_and_0_when_it_does_not() -> None:
    applies = condition_line()
    does_not = ConditionLine(
        COUNT_GATE, 2, "There is an amount on line 72", ((REDUCTION_BASE, D(0)),), False
    )

    assert applies.amount == D(1)
    assert does_not.amount == D(0)
    assert type(applies.amount) is Decimal


def test_a_condition_line_reads_counts_and_amounts_in_the_order_read() -> None:
    line = ConditionLine(
        COUNT_GATE,
        1,
        "first",
        ((FLAG, 1), (REDUCTION_BASE, D("82125.50")), (OTHER_BASE, D("0"))),
        True,
    )

    assert [kind for kind, _value in line.reads] == [FLAG, REDUCTION_BASE, OTHER_BASE]
    assert line.reads[0][1] == 1
    assert type(line.reads[0][1]) is int
    assert type(line.reads[1][1]) is Decimal


def test_condition_lines_differ_by_each_field() -> None:
    base = condition_line()

    assert base != ConditionLine(FLAG, 2, base.text, base.reads, True)
    assert base != ConditionLine(COUNT_GATE, 3, base.text, base.reads, True)
    assert base != ConditionLine(COUNT_GATE, 2, "There is an amount on line 73", base.reads, True)
    assert base != ConditionLine(COUNT_GATE, 2, base.text, ((REDUCTION_BASE, D("0")),), True)
    assert base != ConditionLine(COUNT_GATE, 2, base.text, ((OTHER_BASE, D("120.00")),), True)
    assert base != ConditionLine(COUNT_GATE, 2, base.text, base.reads, False)


def test_condition_lines_are_hashable() -> None:
    assert hash(condition_line()) == hash(condition_line())


def test_a_condition_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(condition_line())]


def test_conditions_count_line_fields_in_order() -> None:
    line = conditions_count_line()

    assert line == ConditionsCountLine(output=COUNT_GATE, applied=(2, 3), count=0)
    assert [f.name for f in fields(line)] == ["output", "applied", "count"]
    assert line.output is COUNT_GATE
    assert line.applied == (2, 3)
    assert line.count == 0


def test_a_conditions_count_line_amount_is_the_count() -> None:
    assert conditions_count_line().amount == D(0)
    assert ConditionsCountLine(COUNT_GATE, (), 1).amount == D(1)
    assert type(conditions_count_line().amount) is Decimal


def test_a_conditions_count_line_may_name_no_position() -> None:
    line = ConditionsCountLine(COUNT_GATE, (), 1)

    assert line.applied == ()
    assert line.count == 1


def test_conditions_count_lines_differ_by_each_field() -> None:
    base = conditions_count_line()

    assert base != ConditionsCountLine(FLAG, (2, 3), 0)
    assert base != ConditionsCountLine(COUNT_GATE, (2,), 0)
    assert base != ConditionsCountLine(COUNT_GATE, (2, 3), 1)


def test_conditions_count_lines_are_hashable() -> None:
    assert hash(conditions_count_line()) == hash(conditions_count_line())


def test_a_conditions_count_line_is_not_an_items_total_line() -> None:
    assert not isinstance(conditions_count_line(), ItemsTotalLine)


def test_ratio_applied_line_fields_in_order() -> None:
    line = ratio_applied_line()

    assert line == RatioAppliedLine(
        output=CREDIT_SHARE,
        amount_kind=TAX_PAYABLE,
        amount_value=D("1000"),
        numerator_kind=FOREIGN_INCOME,
        numerator_value=D("1"),
        denominator_kind=WORLD_INCOME,
        denominator_value=D("3"),
        rounding=CENT,
        result=D("333.33"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "numerator_kind",
        "numerator_value",
        "denominator_kind",
        "denominator_value",
        "rounding",
        "result",
    ]
    assert line.output is CREDIT_SHARE
    assert line.amount_kind is TAX_PAYABLE
    assert line.amount_value == D("1000")
    assert line.numerator_kind is FOREIGN_INCOME
    assert line.numerator_value == D("1")
    assert line.denominator_kind is WORLD_INCOME
    assert line.denominator_value == D("3")
    assert line.rounding == CENT
    assert line.result == D("333.33")
    assert line.amount == D("333.33")


def test_ratio_applied_line_may_hold_an_unrounded_exact_amount() -> None:
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

    assert line.amount == D("1400")


def test_ratio_applied_lines_differ_by_amount_value() -> None:
    assert ratio_applied_line() != RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("1001"),
        FOREIGN_INCOME,
        D("1"),
        WORLD_INCOME,
        D("3"),
        CENT,
        D("333.33"),
    )


def test_ratio_applied_lines_differ_by_numerator_value() -> None:
    assert ratio_applied_line() != RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("1000"),
        FOREIGN_INCOME,
        D("2"),
        WORLD_INCOME,
        D("3"),
        CENT,
        D("333.33"),
    )


def test_ratio_applied_lines_differ_by_denominator_value() -> None:
    assert ratio_applied_line() != RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("1000"),
        FOREIGN_INCOME,
        D("1"),
        WORLD_INCOME,
        D("4"),
        CENT,
        D("333.33"),
    )


def test_ratio_applied_lines_differ_by_kind() -> None:
    other = ArtifactKind("ex/other_amount", Decimal)

    assert ratio_applied_line() != RatioAppliedLine(
        CREDIT_SHARE,
        other,
        D("1000"),
        FOREIGN_INCOME,
        D("1"),
        WORLD_INCOME,
        D("3"),
        CENT,
        D("333.33"),
    )
    assert ratio_applied_line() != RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("1000"),
        other,
        D("1"),
        WORLD_INCOME,
        D("3"),
        CENT,
        D("333.33"),
    )
    assert ratio_applied_line() != RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("1000"),
        FOREIGN_INCOME,
        D("1"),
        other,
        D("3"),
        CENT,
        D("333.33"),
    )


def test_ratio_applied_lines_differ_by_rounding() -> None:
    assert ratio_applied_line() != RatioAppliedLine(
        CREDIT_SHARE,
        TAX_PAYABLE,
        D("1000"),
        FOREIGN_INCOME,
        D("1"),
        WORLD_INCOME,
        D("3"),
        NO_ROUNDING,
        D("333.33"),
    )


def test_ratio_applied_lines_are_hashable() -> None:
    assert hash(ratio_applied_line()) == hash(ratio_applied_line())


def test_a_ratio_applied_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(ratio_applied_line())]


def test_a_ratio_applied_line_is_not_a_fraction_applied_line() -> None:
    assert not isinstance(ratio_applied_line(), FractionAppliedLine)
    assert not isinstance(ratio_applied_line(), RateAppliedLine)


def test_the_item_lines_are_not_their_whole_list_counterparts() -> None:
    assert not isinstance(item_sum_line(), SumLine)
    assert not isinstance(item_lesser_of_line(), LesserOfLine)


def test_lines_of_different_classes_are_not_equal() -> None:
    assert cast(Any, SumLine(TOTAL, (), D(10))) != BracketColumnLine(
        D(0), D("0.10"), D(100), D(0), D(10)
    )


DIVIDEND = ArtifactKind("ex/dividend_amount", Decimal)


DIVISOR = ArtifactKind("ex/divisor_amount", Decimal)


QUOTIENT = ArtifactKind("ex/quotient_amount", Decimal)


ITEM_COUNT = ArtifactKind("ex/item_count", int)


ITEMS = RecordListKind("ex/items", fields=(ITEM_AMOUNT,))


SHARE = ArtifactKind("ex/remaining_share", Decimal)


def quotient_line() -> QuotientLine:
    return QuotientLine(QUOTIENT, DIVIDEND, D("100000.00"), DIVISOR, D("200000.00"), D("0.5"))


def record_count_line() -> RecordCountLine:
    return RecordCountLine(ITEM_COUNT, ITEMS, 2)


def placement_credit_line() -> PlacementCreditLine:
    return PlacementCreditLine(
        output=TOTAL,
        position=1,
        field=ITEM_AMOUNT,
        expenditure=D("8000"),
        line_1=D("2000.00"),
        line_3=D("400.00"),
        line_12=D("200.000"),
        line_13=D("2200.00"),
        remaining_share=SHARE,
        remaining_share_amount=D("0.5"),
        expenditure_rate=Rate(D("0.25")),
        supplement_rate=Rate(D("0.05")),
        maximum=Amount(D("3000")),
        rounding=CENT,
    )


def test_quotient_line_fields_in_order() -> None:
    line = quotient_line()

    assert line == QuotientLine(
        output=QUOTIENT,
        dividend=DIVIDEND,
        dividend_amount=D("100000.00"),
        divisor=DIVISOR,
        divisor_amount=D("200000.00"),
        result=D("0.5"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "dividend",
        "dividend_amount",
        "divisor",
        "divisor_amount",
        "result",
    ]
    assert line.output is QUOTIENT
    assert line.dividend is DIVIDEND
    assert line.dividend_amount == D("100000.00")
    assert line.divisor is DIVISOR
    assert line.divisor_amount == D("200000.00")
    assert line.result == D("0.5")
    assert line.amount == D("0.5")


def test_quotient_lines_differ_by_the_dividend_and_the_divisor() -> None:
    other = ArtifactKind("ex/other_amount", Decimal)

    assert quotient_line() != QuotientLine(
        QUOTIENT, other, D("100000.00"), DIVISOR, D("200000.00"), D("0.5")
    )
    assert quotient_line() != QuotientLine(
        QUOTIENT, DIVIDEND, D("100000.00"), other, D("200000.00"), D("0.5")
    )
    assert quotient_line() != QuotientLine(
        QUOTIENT, DIVIDEND, D("100000.01"), DIVISOR, D("200000.00"), D("0.5")
    )
    assert quotient_line() != QuotientLine(
        QUOTIENT, DIVIDEND, D("100000.00"), DIVISOR, D("200000.01"), D("0.5")
    )


def test_quotient_lines_differ_by_the_result_and_the_output() -> None:
    other = ArtifactKind("ex/other_quotient", Decimal)

    assert quotient_line() != QuotientLine(
        QUOTIENT, DIVIDEND, D("100000.00"), DIVISOR, D("200000.00"), D("0.6")
    )
    assert quotient_line() != QuotientLine(
        other, DIVIDEND, D("100000.00"), DIVISOR, D("200000.00"), D("0.5")
    )


def test_quotient_lines_are_hashable() -> None:
    assert hash(quotient_line()) == hash(quotient_line())


def test_a_quotient_line_is_not_a_subtracted_line() -> None:
    assert not isinstance(quotient_line(), SubtractedLine)


def test_record_count_line_fields_in_order() -> None:
    line = record_count_line()

    assert line == RecordCountLine(output=ITEM_COUNT, records=ITEMS, count=2)
    assert [f.name for f in fields(line)] == ["output", "records", "count"]
    assert line.output is ITEM_COUNT
    assert line.records is ITEMS
    assert line.count == 2
    assert type(line.count) is int
    assert line.amount == D(2)


def test_record_count_line_may_count_no_records() -> None:
    line = RecordCountLine(ITEM_COUNT, ITEMS, 0)

    assert line.count == 0
    assert line.amount == D(0)


def test_record_count_lines_differ_by_the_count_the_list_and_the_output() -> None:
    other_list = RecordListKind("ex/other_items", fields=(ITEM_AMOUNT,))
    other_count = ArtifactKind("ex/other_count", int)

    assert record_count_line() != RecordCountLine(ITEM_COUNT, ITEMS, 3)
    assert record_count_line() != RecordCountLine(ITEM_COUNT, other_list, 2)
    assert record_count_line() != RecordCountLine(other_count, ITEMS, 2)


def test_record_count_lines_are_hashable() -> None:
    assert hash(record_count_line()) == hash(record_count_line())


FIRST_ITEM_COUNT = ArtifactKind("ex/first_item_count", int)


def first_record_count_line() -> FirstRecordCountLine:
    return FirstRecordCountLine(FIRST_ITEM_COUNT, ITEM_COUNT, 4, 3)


def test_first_record_count_line_fields_in_order() -> None:
    line = first_record_count_line()

    assert line == FirstRecordCountLine(
        output=FIRST_ITEM_COUNT, field=ITEM_COUNT, value=4, record_count=3
    )
    assert [f.name for f in fields(line)] == ["output", "field", "value", "record_count"]
    assert line.output is FIRST_ITEM_COUNT
    assert line.field is ITEM_COUNT
    assert line.value == 4
    assert type(line.value) is int
    assert line.record_count == 3
    assert line.amount == D(4)


def test_first_record_count_lines_differ_by_the_value_the_record_count_and_the_kinds() -> None:
    other_count = ArtifactKind("ex/other_count", int)
    other_output = ArtifactKind("ex/other_first", int)

    assert first_record_count_line() != FirstRecordCountLine(FIRST_ITEM_COUNT, ITEM_COUNT, 5, 3)
    assert first_record_count_line() != FirstRecordCountLine(FIRST_ITEM_COUNT, ITEM_COUNT, 4, 2)
    assert first_record_count_line() != FirstRecordCountLine(FIRST_ITEM_COUNT, other_count, 4, 3)
    assert first_record_count_line() != FirstRecordCountLine(other_output, ITEM_COUNT, 4, 3)


def test_first_record_count_lines_are_hashable() -> None:
    assert hash(first_record_count_line()) == hash(first_record_count_line())


def test_a_first_record_count_line_is_neither_a_record_total_line_nor_a_record_count_line() -> None:
    assert not isinstance(first_record_count_line(), RecordTotalLine)
    assert not isinstance(first_record_count_line(), RecordCountLine)


def test_placement_credit_line_fields_in_order() -> None:
    line = placement_credit_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "field",
        "expenditure",
        "line_1",
        "line_3",
        "line_12",
        "line_13",
        "remaining_share",
        "remaining_share_amount",
        "expenditure_rate",
        "supplement_rate",
        "maximum",
        "rounding",
    ]
    assert line.output is TOTAL
    assert line.position == 1
    assert line.field is ITEM_AMOUNT
    assert line.expenditure == D("8000")
    assert line.line_1 == D("2000.00")
    assert line.line_3 == D("400.00")
    assert line.line_12 == D("200.000")
    assert line.line_13 == D("2200.00")
    assert line.remaining_share is SHARE
    assert line.remaining_share_amount == D("0.5")
    assert line.expenditure_rate == Rate(D("0.25"))
    assert line.supplement_rate == Rate(D("0.05"))
    assert line.maximum == Amount(D("3000"))
    assert line.rounding == CENT


def test_a_placement_credit_lines_amount_is_its_line_13() -> None:
    assert placement_credit_line().amount == D("2200.00")
    assert "amount" not in [f.name for f in fields(placement_credit_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": ArtifactKind("ex/other_total", Decimal)},
        {"position": 2},
        {"field": ArtifactKind("ex/other_item_amount", Decimal)},
        {"expenditure": D("8000.01")},
        {"line_1": D("2000.01")},
        {"line_3": D("400.01")},
        {"line_12": D("200.01")},
        {"line_13": D("2200.01")},
        {"remaining_share": ArtifactKind("ex/other_share", Decimal)},
        {"remaining_share_amount": D("0.6")},
        {"expenditure_rate": Rate(D("0.30"))},
        {"supplement_rate": Rate(D("0.06"))},
        {"maximum": Amount(D("3001"))},
        {"rounding": NO_ROUNDING},
    ],
)
def test_placement_credit_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = placement_credit_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != PlacementCreditLine(**values)


def test_placement_credit_lines_are_hashable() -> None:
    assert hash(placement_credit_line()) == hash(placement_credit_line())


def test_a_placement_credit_line_is_not_a_record_total_line() -> None:
    assert not isinstance(placement_credit_line(), RecordTotalLine)


def test_threshold_gate_line_fields_in_order() -> None:
    line = threshold_gate_line()

    assert line == ThresholdGateLine(
        output=GATED,
        amount_kind=GROSS,
        amount_value=D("1500.25"),
        gate_kind=GATE,
        gate_value=D("4390"),
        threshold=Amount(D("4390")),
        rounding=CENT,
        result=D("1500.25"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "gate_kind",
        "gate_value",
        "threshold",
        "rounding",
        "result",
    ]
    assert line.output is GATED
    assert line.amount_kind is GROSS
    assert line.amount_value == D("1500.25")
    assert line.gate_kind is GATE
    assert line.gate_value == D("4390")
    assert line.threshold == Amount(D("4390"))
    assert line.rounding == CENT
    assert line.result == D("1500.25")
    assert line.amount == D("1500.25")


def test_a_threshold_gate_line_may_hold_a_gate_below_the_threshold() -> None:
    line = ThresholdGateLine(
        GATED, GROSS, D("1500.25"), GATE, D("4389.99"), Amount(D("4390")), NO_ROUNDING, D("0")
    )

    assert line.result == D("0")
    assert line.amount == D("0")


@pytest.mark.parametrize(
    "change",
    [
        {"output": CAPPED},
        {"amount_kind": CLAIMED},
        {"amount_value": D("1500.5")},
        {"gate_kind": LIMIT},
        {"gate_value": D("4389.99")},
        {"threshold": Amount(D("5000"))},
        {"rounding": NO_ROUNDING},
        {"result": D("0")},
    ],
)
def test_threshold_gate_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = threshold_gate_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != ThresholdGateLine(**values)


def test_threshold_gate_lines_are_hashable() -> None:
    assert hash(threshold_gate_line()) == hash(threshold_gate_line())


def test_a_threshold_gate_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(threshold_gate_line())]


def test_a_threshold_gate_line_is_not_a_capped_amount_or_at_most_line() -> None:
    line = threshold_gate_line()

    assert not isinstance(line, CappedAmountLine)
    assert not isinstance(line, AtMostLine)


def test_amount_or_divided_by_rate_line_fields_in_order() -> None:
    line = amount_or_divided_by_rate_line()

    assert line == AmountOrDividedByRateLine(
        output=LIMITED,
        amount_kind=TESTED,
        amount_value=D("60000"),
        dividend_kind=DIVIDED,
        dividend_value=D("3321.67"),
        limit=THRESHOLD_LIMIT,
        rounding=CENT,
        result=D("65775.64"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "dividend_kind",
        "dividend_value",
        "limit",
        "rounding",
        "result",
    ]
    assert line.output is LIMITED
    assert line.amount_kind is TESTED
    assert line.amount_value == D("60000")
    assert line.dividend_kind is DIVIDED
    assert line.dividend_value == D("3321.67")
    assert line.limit == THRESHOLD_LIMIT
    assert line.rounding == CENT
    assert line.result == D("65775.64")
    assert line.amount == D("65775.64")


def test_an_amount_or_divided_by_rate_line_may_hold_an_amount_at_the_threshold() -> None:
    line = AmountOrDividedByRateLine(
        LIMITED, TESTED, D("52886"), DIVIDED, D("3321.67"), THRESHOLD_LIMIT, NO_ROUNDING, D("52886")
    )

    assert line.result == D("52886")
    assert line.amount == D("52886")


@pytest.mark.parametrize(
    "change",
    [
        {"output": CAPPED},
        {"amount_kind": CLAIMED},
        {"amount_value": D("60001")},
        {"dividend_kind": LIMIT},
        {"dividend_value": D("3321.68")},
        {"limit": ThresholdRate(Rate(D("0.0505")), D("57375"))},
        {"limit": ThresholdRate(Rate(D("0.145")), D("52886"))},
        {"rounding": NO_ROUNDING},
        {"result": D("65775.65")},
    ],
)
def test_amount_or_divided_by_rate_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = amount_or_divided_by_rate_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != AmountOrDividedByRateLine(**values)


def test_amount_or_divided_by_rate_lines_are_hashable() -> None:
    assert hash(amount_or_divided_by_rate_line()) == hash(amount_or_divided_by_rate_line())


def test_an_amount_or_divided_by_rate_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(amount_or_divided_by_rate_line())]


def test_an_amount_or_divided_by_rate_line_is_not_a_threshold_gate_line() -> None:
    line = amount_or_divided_by_rate_line()

    assert not isinstance(line, ThresholdGateLine)
    assert not isinstance(line, CappedAmountLine)
    assert not isinstance(line, AtMostLine)


# --- the capital cost allowance table, one line per class ---------------------------------------

CLASS = ClassRate(
    D("43.1"),
    Rate(D("0.30")),
    HalfYearRule.APPLIES,
    RecaptureAndTerminalLoss.APPLIES,
    Fraction(3, 2),
    Fraction(7, 3),
    HalfYearRuleOnSale.DOES_NOT_APPLY,
)
OTHER_CLASS = ClassRate(
    D("10.1"),
    Rate(D("0.30")),
    HalfYearRule.APPLIES,
    RecaptureAndTerminalLoss.EXCLUDED,
    Fraction(0, 1),
    Fraction(1, 2),
    HalfYearRuleOnSale.DOES_NOT_APPLY,
)
CCA = ArtifactKind("ex/cca_claim", Decimal)
RECAPTURE = ArtifactKind("ex/recaptured_cca", Decimal)
TERMINAL_LOSS = ArtifactKind("ex/terminal_loss", Decimal)
CLOSING_UCC = RecordListKind("ex/closing_ucc", fields=(ArtifactKind("ex/ucc_at_end", Decimal),))


def cca_claim_line() -> CcaClaimLine:
    return CcaClaimLine(
        output=CCA,
        position=2,
        class_rate=CLASS,
        no_property_left=0,
        column_7=D("6000.00"),
        column_14=D("400.00"),
        column_15=D("900.00"),
        column_16=D("0"),
        column_17=D("0"),
        column_18=D("0"),
        column_19=D("6900.00"),
        zero_reason=CcaZeroReason.NONE,
        maximum=D("2070.00"),
        rounding=CENT,
        claim=D("2000.00"),
    )


def recaptured_cca_line() -> RecapturedCcaLine:
    return RecapturedCcaLine(
        RECAPTURE, 1, CLASS, D("-3000.00"), CcaZeroReason.COLUMN_7_NEGATIVE, D("3000.00")
    )


def terminal_loss_line() -> TerminalLossLine:
    return TerminalLossLine(
        TERMINAL_LOSS, 1, CLASS, 1, D("5000.00"), CcaZeroReason.NO_PROPERTY_LEFT, True, D("5000.00")
    )


def closing_ucc_line() -> ClosingUccLine:
    return ClosingUccLine(
        CLOSING_UCC, 2, CLASS, 0, D("6000.00"), CcaZeroReason.NONE, D("2000.00"), D("4000.00")
    )


CCA_LINES = [cca_claim_line, recaptured_cca_line, terminal_loss_line, closing_ucc_line]


@pytest.mark.parametrize("make", CCA_LINES)
def test_every_cca_line_is_a_frozen_trace_line_equal_by_value(make: Any) -> None:
    line = make()

    assert isinstance(line, TraceLine)
    assert line == make()
    assert line is not make()
    assert hash(line) == hash(make())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_the_cca_lines_are_classes_of_their_own() -> None:
    lines = [make() for make in CCA_LINES]

    assert len({type(line) for line in lines}) == 4
    for line in lines:
        assert not isinstance(
            line, ItemsTotalLine | PlacementCreditLine | OtherDependantMedicalLine
        )


def test_cca_claim_line_fields_in_order() -> None:
    line = cca_claim_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "class_rate",
        "no_property_left",
        "column_7",
        "column_14",
        "column_15",
        "column_16",
        "column_17",
        "column_18",
        "column_19",
        "zero_reason",
        "maximum",
        "rounding",
        "claim",
        "column_9",
        "half_year_rule_on_sale",
        "fiscal_period_days",
        "full_year_days",
    ]
    assert line == CcaClaimLine(
        CCA,
        2,
        CLASS,
        0,
        D("6000.00"),
        D("400.00"),
        D("900.00"),
        D("0"),
        D("0"),
        D("0"),
        D("6900.00"),
        CcaZeroReason.NONE,
        D("2070.00"),
        CENT,
        D("2000.00"),
    )
    assert line.output is CCA
    assert line.zero_reason is CcaZeroReason.NONE
    assert line.class_rate == CLASS
    assert line.maximum == D("2070.00")
    assert line.claim == D("2000.00")


def test_a_cca_claim_lines_amount_is_the_claim() -> None:
    assert cca_claim_line().amount == D("2000.00")
    assert str(cca_claim_line().amount) == "2000.00"
    assert "amount" not in [f.name for f in fields(cca_claim_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": ArtifactKind("ex/other_cca_claim", Decimal)},
        {"position": 1},
        {"class_rate": OTHER_CLASS},
        {"no_property_left": 1},
        {"column_7": D("6000.01")},
        {"column_14": D("400.01")},
        {"column_15": D("900.01")},
        {"column_16": D("0.01")},
        {"column_17": D("0.01")},
        {"column_18": D("0.01")},
        {"column_19": D("6900.01")},
        {"zero_reason": CcaZeroReason.NO_PROPERTY_LEFT},
        {"maximum": D("2070.01")},
        {"rounding": NO_ROUNDING},
        {"claim": D("2000.01")},
        {"column_9": D("1000")},
        {"half_year_rule_on_sale": True},
        {"fiscal_period_days": 214},
        {"full_year_days": 366},
    ],
)
def test_cca_claim_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_claim_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaClaimLine(**values)


def test_recaptured_cca_line_fields_in_order() -> None:
    line = recaptured_cca_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "class_rate",
        "column_7",
        "zero_reason",
        "result",
        "has_diep",
    ]
    assert line == RecapturedCcaLine(
        output=RECAPTURE,
        position=1,
        class_rate=CLASS,
        column_7=D("-3000.00"),
        zero_reason=CcaZeroReason.COLUMN_7_NEGATIVE,
        result=D("3000.00"),
    )


def test_a_recaptured_cca_lines_amount_is_the_result() -> None:
    assert recaptured_cca_line().amount == D("3000.00")
    assert "amount" not in [f.name for f in fields(recaptured_cca_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": ArtifactKind("ex/other_recapture", Decimal)},
        {"position": 2},
        {"class_rate": OTHER_CLASS},
        {"column_7": D("-3000.01")},
        {"zero_reason": CcaZeroReason.NONE},
        {"result": D("0")},
    ],
)
def test_recaptured_cca_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = recaptured_cca_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != RecapturedCcaLine(**values)


def test_terminal_loss_line_fields_in_order() -> None:
    line = terminal_loss_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "class_rate",
        "no_property_left",
        "column_7",
        "zero_reason",
        "column_7_positive",
        "result",
        "has_diep",
        "column_9",
        "half_year_rule_on_sale",
    ]
    assert line == TerminalLossLine(
        output=TERMINAL_LOSS,
        position=1,
        class_rate=CLASS,
        no_property_left=1,
        column_7=D("5000.00"),
        zero_reason=CcaZeroReason.NO_PROPERTY_LEFT,
        column_7_positive=True,
        result=D("5000.00"),
    )


def test_a_terminal_loss_lines_amount_is_the_result() -> None:
    assert terminal_loss_line().amount == D("5000.00")
    assert "amount" not in [f.name for f in fields(terminal_loss_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": ArtifactKind("ex/other_terminal_loss", Decimal)},
        {"position": 2},
        {"class_rate": OTHER_CLASS},
        {"no_property_left": 0},
        {"column_7": D("5000.01")},
        {"zero_reason": CcaZeroReason.NONE},
        {"column_7_positive": False},
        {"result": D("0")},
        {"column_9": D("1000")},
        {"half_year_rule_on_sale": True},
    ],
)
def test_terminal_loss_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = terminal_loss_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != TerminalLossLine(**values)


def test_closing_ucc_line_fields_in_order() -> None:
    line = closing_ucc_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "class_rate",
        "no_property_left",
        "column_7",
        "zero_reason",
        "claim",
        "result",
        "column_9",
        "half_year_rule_on_sale",
        "fiscal_period_days",
        "full_year_days",
        "personal_part_remaining",
    ]
    assert line == ClosingUccLine(
        output=CLOSING_UCC,
        position=2,
        class_rate=CLASS,
        no_property_left=0,
        column_7=D("6000.00"),
        zero_reason=CcaZeroReason.NONE,
        claim=D("2000.00"),
        result=D("4000.00"),
    )
    assert line.output is CLOSING_UCC


def test_a_closing_ucc_line_has_no_remaining_personal_part_unless_it_says_so() -> None:
    # T776 Area A Note 9: the part is subtracted from column 24; 0 by default, and the last field.
    line = closing_ucc_line()

    assert line.personal_part_remaining == D("0")
    assert [f.name for f in fields(line)][-1] == "personal_part_remaining"
    with_part = replace(line, personal_part_remaining=D("5000"), result=D("-1000"))
    assert with_part.personal_part_remaining == D("5000")
    assert with_part.amount == D("-1000")


def test_a_closing_ucc_lines_amount_is_the_classs_ucc_at_the_end_of_the_year() -> None:
    assert closing_ucc_line().amount == D("4000.00")
    assert "amount" not in [f.name for f in fields(closing_ucc_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": RecordListKind("ex/other_closing_ucc", fields=(ITEM_AMOUNT,))},
        {"position": 1},
        {"class_rate": OTHER_CLASS},
        {"no_property_left": 1},
        {"column_7": D("6000.01")},
        {"zero_reason": CcaZeroReason.COLUMN_7_NEGATIVE},
        {"claim": D("2000.01")},
        {"result": D("3999.99")},
        {"column_9": D("1000")},
        {"half_year_rule_on_sale": True},
        {"fiscal_period_days": 214},
        {"full_year_days": 366},
        {"personal_part_remaining": D("5000")},
    ],
)
def test_closing_ucc_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = closing_ucc_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != ClosingUccLine(**values)


def cca_vehicle_proceeds_line() -> CcaVehicleProceedsLine:
    # Area A endnote 2: proceeds of 40,000 times the prescribed amount 42,940 over the actual cost
    # 56,500 (a factor of 0.76) are 30,400; no DIEP proceeds.
    return CcaVehicleProceedsLine(
        CLOSING_UCC,
        2,
        True,
        D("42940.00"),
        D("56500.00"),
        D("40000"),
        D("30400.00"),
        D("0"),
        D("0"),
    )


def test_cca_vehicle_proceeds_line_fields_in_order() -> None:
    line = cca_vehicle_proceeds_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "applied",
        "prescribed_amount",
        "actual_cost",
        "proceeds",
        "adjusted_proceeds",
        "diep_proceeds",
        "adjusted_diep_proceeds",
    ]
    assert line == CcaVehicleProceedsLine(
        output=CLOSING_UCC,
        position=2,
        applied=True,
        prescribed_amount=D("42940.00"),
        actual_cost=D("56500.00"),
        proceeds=D("40000"),
        adjusted_proceeds=D("30400.00"),
        diep_proceeds=D("0"),
        adjusted_diep_proceeds=D("0"),
    )
    assert line.output is CLOSING_UCC
    assert line.applied is True


def test_a_cca_vehicle_proceeds_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_vehicle_proceeds_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaVehicleProceedsLine"
    assert line == cca_vehicle_proceeds_line()
    assert line is not cca_vehicle_proceeds_line()
    assert hash(line) == hash(cca_vehicle_proceeds_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_vehicle_proceeds_lines_amount_is_the_adjusted_proceeds() -> None:
    assert cca_vehicle_proceeds_line().amount == D("30400.00")
    assert "amount" not in [f.name for f in fields(cca_vehicle_proceeds_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": RecordListKind("ex/other_closing_ucc", fields=(ITEM_AMOUNT,))},
        {"position": 1},
        {"applied": False},
        {"prescribed_amount": D("42940.01")},
        {"actual_cost": D("56500.01")},
        {"proceeds": D("40000.01")},
        {"adjusted_proceeds": D("30399.99")},
        {"diep_proceeds": D("100")},
        {"adjusted_diep_proceeds": D("76")},
    ],
)
def test_cca_vehicle_proceeds_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_vehicle_proceeds_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaVehicleProceedsLine(**values)


def cca_part_b_check_line() -> CcaPartBCheckLine:
    # Part B row 2: a Class 10.1 vehicle owned from the previous year (UCC 20,000) and sold in the
    # year for 12,000 (the tick is entered with proceeds).
    return CcaPartBCheckLine(CLOSING_UCC, 2, D("20000.00"), D("0"), D("12000.00"), True)


def test_cca_part_b_check_line_fields_in_order() -> None:
    line = cca_part_b_check_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "ucc_at_start",
        "additions",
        "proceeds",
        "sold_in_year",
    ]
    assert line == CcaPartBCheckLine(
        output=CLOSING_UCC,
        position=2,
        ucc_at_start=D("20000.00"),
        additions=D("0"),
        proceeds=D("12000.00"),
        sold_in_year=True,
    )
    assert line.output is CLOSING_UCC
    assert line.sold_in_year is True


def test_a_cca_part_b_check_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_part_b_check_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaPartBCheckLine"
    assert line == cca_part_b_check_line()
    assert line is not cca_part_b_check_line()
    assert hash(line) == hash(cca_part_b_check_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_part_b_check_lines_amount_is_the_proceeds() -> None:
    assert cca_part_b_check_line().amount == D("12000.00")
    assert "amount" not in [f.name for f in fields(cca_part_b_check_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": RecordListKind("ex/other_closing_ucc", fields=(ITEM_AMOUNT,))},
        {"position": 1},
        {"ucc_at_start": D("20000.01")},
        {"additions": D("1")},
        {"proceeds": D("12000.01")},
        {"sold_in_year": False},
    ],
)
def test_cca_part_b_check_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_part_b_check_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaPartBCheckLine(**values)


CHECKED_CLASSES = RecordListKind("ex/business_cca_classes_checked", fields=(ITEM_AMOUNT,))


def cca_vehicle_additions_check_line() -> CcaVehicleAdditionsCheckLine:
    # Row 1: a Class 10.1 vehicle bought in the year, its additions at the limit with tax (checked).
    return CcaVehicleAdditionsCheckLine(CHECKED_CLASSES, 1, True, D("42940.00"), D("42940.00"))


def test_cca_vehicle_additions_check_line_fields_in_order() -> None:
    line = cca_vehicle_additions_check_line()

    assert [f.name for f in fields(line)] == [
        "output_kind",
        "position",
        "applied",
        "additions",
        "limit",
    ]
    assert line == CcaVehicleAdditionsCheckLine(
        output_kind=CHECKED_CLASSES,
        position=1,
        applied=True,
        additions=D("42940.00"),
        limit=D("42940.00"),
    )
    assert line.output_kind is CHECKED_CLASSES
    assert line.applied is True


def test_a_cca_vehicle_additions_check_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_vehicle_additions_check_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaVehicleAdditionsCheckLine"
    assert line == cca_vehicle_additions_check_line()
    assert line is not cca_vehicle_additions_check_line()
    assert hash(line) == hash(cca_vehicle_additions_check_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_vehicle_additions_check_lines_amount_is_the_additions() -> None:
    # The figure the line is about is the cost of additions as entered, not the limit.
    assert cca_vehicle_additions_check_line().amount == D("42940.00")
    assert "amount" not in [f.name for f in fields(cca_vehicle_additions_check_line())]


def test_a_row_not_checked_has_no_limit_of_its_own() -> None:
    line = CcaVehicleAdditionsCheckLine(CHECKED_CLASSES, 2, False, D("31640.00"), D("0"))

    assert line.applied is False
    assert line.limit == D("0")


@pytest.mark.parametrize(
    "change",
    [
        {"output_kind": RecordListKind("ex/other_checked_classes", fields=(ITEM_AMOUNT,))},
        {"position": 2},
        {"applied": False},
        {"additions": D("42940.01")},
        {"limit": D("42941.00")},
    ],
)
def test_cca_vehicle_additions_check_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_vehicle_additions_check_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaVehicleAdditionsCheckLine(**values)


def cca_vehicle_class_check_line() -> CcaVehicleClassCheckLine:
    # Row 1: a Class 10.1 vehicle acquired in 2025 at a cost just above the minimum (checked).
    return CcaVehicleClassCheckLine(CHECKED_CLASSES, 1, True, 2025, D("38000.01"), D("38000"))


def test_cca_vehicle_class_check_line_fields_in_order() -> None:
    line = cca_vehicle_class_check_line()

    assert [f.name for f in fields(line)] == [
        "output_kind",
        "position",
        "applied",
        "year",
        "cost",
        "minimum",
    ]
    assert line == CcaVehicleClassCheckLine(
        output_kind=CHECKED_CLASSES,
        position=1,
        applied=True,
        year=2025,
        cost=D("38000.01"),
        minimum=D("38000"),
    )
    assert line.output_kind is CHECKED_CLASSES
    assert line.applied is True


def test_a_cca_vehicle_class_check_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_vehicle_class_check_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaVehicleClassCheckLine"
    assert line == cca_vehicle_class_check_line()
    assert line is not cca_vehicle_class_check_line()
    assert hash(line) == hash(cca_vehicle_class_check_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_vehicle_class_check_lines_amount_is_the_cost() -> None:
    # The figure the line is about is the cost of vehicle as entered, not the minimum.
    assert cca_vehicle_class_check_line().amount == D("38000.01")
    assert "amount" not in [f.name for f in fields(cca_vehicle_class_check_line())]


def test_a_row_not_checked_has_no_minimum_of_its_own() -> None:
    line = CcaVehicleClassCheckLine(CHECKED_CLASSES, 2, False, 0, D("0"), D("0"))

    assert line.applied is False
    assert line.minimum == D("0")


@pytest.mark.parametrize(
    "change",
    [
        {"output_kind": RecordListKind("ex/other_checked_classes", fields=(ITEM_AMOUNT,))},
        {"position": 2},
        {"applied": False},
        {"year": 2024},
        {"cost": D("38000.02")},
        {"minimum": D("37000")},
    ],
)
def test_cca_vehicle_class_check_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_vehicle_class_check_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaVehicleClassCheckLine(**values)


def cca_vehicle_non_arms_length_check_line() -> CcaVehicleNonArmsLengthCheckLine:
    # Row 1: a Class 10.1 vehicle bought from a non-arm's-length person, whose additions are the
    # limit with tax, the least of the three amounts (checked).
    return CcaVehicleNonArmsLengthCheckLine(
        CHECKED_CLASSES,
        1,
        True,
        D("42940.00"),
        D("50000"),
        D("42940.00"),
        D("60000"),
        D("42940.00"),
    )


def test_cca_vehicle_non_arms_length_check_line_fields_in_order() -> None:
    line = cca_vehicle_non_arms_length_check_line()

    assert [f.name for f in fields(line)] == [
        "output_kind",
        "position",
        "applied",
        "additions",
        "fair_market_value",
        "limit",
        "seller_cost",
        "capital_cost",
    ]
    assert line == CcaVehicleNonArmsLengthCheckLine(
        output_kind=CHECKED_CLASSES,
        position=1,
        applied=True,
        additions=D("42940.00"),
        fair_market_value=D("50000"),
        limit=D("42940.00"),
        seller_cost=D("60000"),
        capital_cost=D("42940.00"),
    )
    assert line.output_kind is CHECKED_CLASSES
    assert line.applied is True
    assert line.capital_cost == D("42940.00")


def test_a_non_arms_length_row_not_checked_has_no_figures_of_its_own() -> None:
    line = CcaVehicleNonArmsLengthCheckLine(
        CHECKED_CLASSES, 2, False, D("5"), D("0"), D("0"), D("0"), D("0")
    )

    assert line.applied is False
    assert (line.fair_market_value, line.limit, line.seller_cost, line.capital_cost) == (
        D("0"),
        D("0"),
        D("0"),
        D("0"),
    )


def test_a_cca_vehicle_non_arms_length_check_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_vehicle_non_arms_length_check_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaVehicleNonArmsLengthCheckLine"
    assert line == cca_vehicle_non_arms_length_check_line()
    assert line is not cca_vehicle_non_arms_length_check_line()
    assert hash(line) == hash(cca_vehicle_non_arms_length_check_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_vehicle_non_arms_length_check_lines_amount_is_the_additions() -> None:
    assert cca_vehicle_non_arms_length_check_line().amount == D("42940.00")
    assert "amount" not in [f.name for f in fields(cca_vehicle_non_arms_length_check_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output_kind": RecordListKind("ex/other_checked_classes", fields=(ITEM_AMOUNT,))},
        {"position": 2},
        {"applied": False},
        {"additions": D("1")},
        {"fair_market_value": D("1")},
        {"limit": D("1")},
        {"seller_cost": D("1")},
        {"capital_cost": D("1")},
    ],
)
def test_cca_vehicle_non_arms_length_check_lines_differ_by_each_field(
    change: dict[str, Any],
) -> None:
    line = cca_vehicle_non_arms_length_check_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaVehicleNonArmsLengthCheckLine(**values)


def cca_vehicle_change_in_use_check_line() -> CcaVehicleChangeInUseCheckLine:
    # Row 1: a Class 10.1 vehicle with a change in use whose additions are its fair market value
    # (the Guide's car worth $11,000 when it started being used for employment).
    return CcaVehicleChangeInUseCheckLine(CHECKED_CLASSES, 1, True, D("11000"), D("11000"))


def test_cca_vehicle_change_in_use_check_line_fields_in_order() -> None:
    line = cca_vehicle_change_in_use_check_line()

    assert [f.name for f in fields(line)] == [
        "output_kind",
        "position",
        "applied",
        "additions",
        "fair_market_value",
    ]
    assert line == CcaVehicleChangeInUseCheckLine(
        output_kind=CHECKED_CLASSES,
        position=1,
        applied=True,
        additions=D("11000"),
        fair_market_value=D("11000"),
    )
    assert line.output_kind is CHECKED_CLASSES
    assert line.applied is True


def test_a_change_in_use_row_not_checked_has_no_fair_market_value_of_its_own() -> None:
    line = CcaVehicleChangeInUseCheckLine(CHECKED_CLASSES, 2, False, D("19000"), D("0"))

    assert line.applied is False
    assert line.fair_market_value == D("0")


def test_a_cca_vehicle_change_in_use_check_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_vehicle_change_in_use_check_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaVehicleChangeInUseCheckLine"
    assert line == cca_vehicle_change_in_use_check_line()
    assert line is not cca_vehicle_change_in_use_check_line()
    assert hash(line) == hash(cca_vehicle_change_in_use_check_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_vehicle_change_in_use_check_lines_amount_is_the_additions() -> None:
    assert cca_vehicle_change_in_use_check_line().amount == D("11000")
    assert "amount" not in [f.name for f in fields(cca_vehicle_change_in_use_check_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output_kind": RecordListKind("ex/other_checked_classes", fields=(ITEM_AMOUNT,))},
        {"position": 2},
        {"applied": False},
        {"additions": D("1")},
        {"fair_market_value": D("1")},
    ],
)
def test_cca_vehicle_change_in_use_check_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_vehicle_change_in_use_check_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaVehicleChangeInUseCheckLine(**values)


def cca_change_in_use_check_line() -> CcaChangeInUseCheckLine:
    # Row 1: a Part A row with a change in use whose additions are its fair market value (the
    # Guide's car worth $11,000 when it started being used for employment).
    return CcaChangeInUseCheckLine(CHECKED_CLASSES, 1, True, D("11000"), D("11000"))


def test_cca_change_in_use_check_line_fields_in_order() -> None:
    line = cca_change_in_use_check_line()

    assert [f.name for f in fields(line)] == [
        "output_kind",
        "position",
        "applied",
        "additions",
        "fair_market_value",
    ]
    assert line == CcaChangeInUseCheckLine(
        output_kind=CHECKED_CLASSES,
        position=1,
        applied=True,
        additions=D("11000"),
        fair_market_value=D("11000"),
    )
    assert line.output_kind is CHECKED_CLASSES
    assert line.applied is True


def test_a_part_a_change_in_use_row_not_checked_has_no_fair_market_value_of_its_own() -> None:
    line = CcaChangeInUseCheckLine(CHECKED_CLASSES, 2, False, D("19000"), D("0"))

    assert line.applied is False
    assert line.fair_market_value == D("0")


def test_a_cca_change_in_use_check_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_change_in_use_check_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaChangeInUseCheckLine"
    assert line == cca_change_in_use_check_line()
    assert line is not cca_change_in_use_check_line()
    assert hash(line) == hash(cca_change_in_use_check_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_change_in_use_check_lines_amount_is_the_additions() -> None:
    assert cca_change_in_use_check_line().amount == D("11000")
    assert "amount" not in [f.name for f in fields(cca_change_in_use_check_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output_kind": RecordListKind("ex/other_checked_classes", fields=(ITEM_AMOUNT,))},
        {"position": 2},
        {"applied": False},
        {"additions": D("1")},
        {"fair_market_value": D("1")},
    ],
)
def test_cca_change_in_use_check_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_change_in_use_check_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaChangeInUseCheckLine(**values)


def cca_part_a_check_line() -> CcaPartACheckLine:
    # Part A row 2: a Class 8 row, the second row of the Class 8 list, with no amount of its own.
    return CcaPartACheckLine(CLOSING_UCC, 2, D("8"))


def test_cca_part_a_check_line_fields_in_order() -> None:
    line = cca_part_a_check_line()

    assert [f.name for f in fields(line)] == ["output", "position", "class_number"]
    assert line == CcaPartACheckLine(output=CLOSING_UCC, position=2, class_number=D("8"))
    assert line.output is CLOSING_UCC
    assert line.class_number == D("8")


def test_a_cca_part_a_check_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_part_a_check_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaPartACheckLine"
    assert line == cca_part_a_check_line()
    assert line is not cca_part_a_check_line()
    assert hash(line) == hash(cca_part_a_check_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_part_a_check_lines_amount_is_zero_as_it_is_not_about_one_figure() -> None:
    assert cca_part_a_check_line().amount == D("0")
    assert "amount" not in [f.name for f in fields(cca_part_a_check_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": RecordListKind("ex/other_closing_ucc", fields=(ITEM_AMOUNT,))},
        {"position": 1},
        {"class_number": D("54")},
    ],
)
def test_cca_part_a_check_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_part_a_check_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaPartACheckLine(**values)


def cca_zepv_proceeds_line() -> CcaZepvProceedsLine:
    # Guide T4036 "Class 54 (30%)": 30,000 x (61,000 / 65,000) is 28,153.85 to the cent; the first
    # vehicle of the second row, no DIEP proceeds.
    return CcaZepvProceedsLine(
        CLOSING_UCC,
        2,
        1,
        True,
        D("61000.00"),
        D("65000.00"),
        D("30000"),
        D("28153.85"),
        D("0"),
        D("0"),
    )


def test_cca_zepv_proceeds_line_fields_in_order() -> None:
    line = cca_zepv_proceeds_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "vehicle",
        "applied",
        "prescribed_amount",
        "actual_cost",
        "proceeds",
        "adjusted_proceeds",
        "diep_proceeds",
        "adjusted_diep_proceeds",
    ]
    assert line == CcaZepvProceedsLine(
        output=CLOSING_UCC,
        position=2,
        vehicle=1,
        applied=True,
        prescribed_amount=D("61000.00"),
        actual_cost=D("65000.00"),
        proceeds=D("30000"),
        adjusted_proceeds=D("28153.85"),
        diep_proceeds=D("0"),
        adjusted_diep_proceeds=D("0"),
    )
    assert line.output is CLOSING_UCC
    assert line.applied is True


def test_a_cca_zepv_proceeds_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = cca_zepv_proceeds_line()

    assert isinstance(line, TraceLine)
    assert type(line).__name__ == "CcaZepvProceedsLine"
    assert line == cca_zepv_proceeds_line()
    assert line is not cca_zepv_proceeds_line()
    assert hash(line) == hash(cca_zepv_proceeds_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, fields(line)[0].name, D(1))


def test_a_cca_zepv_proceeds_line_is_not_a_cca_vehicle_proceeds_line() -> None:
    assert not isinstance(cca_zepv_proceeds_line(), CcaVehicleProceedsLine)


def test_a_cca_zepv_proceeds_lines_amount_is_the_adjusted_proceeds() -> None:
    assert cca_zepv_proceeds_line().amount == D("28153.85")
    assert "amount" not in [f.name for f in fields(cca_zepv_proceeds_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": RecordListKind("ex/other_closing_ucc", fields=(ITEM_AMOUNT,))},
        {"position": 1},
        {"vehicle": 2},
        {"applied": False},
        {"prescribed_amount": D("61000.01")},
        {"actual_cost": D("65000.01")},
        {"proceeds": D("30000.01")},
        {"adjusted_proceeds": D("28153.86")},
        {"diep_proceeds": D("100")},
        {"adjusted_diep_proceeds": D("76")},
    ],
)
def test_cca_zepv_proceeds_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = cca_zepv_proceeds_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != CcaZepvProceedsLine(**values)


@pytest.mark.parametrize("make", [cca_claim_line, terminal_loss_line, closing_ucc_line])
def test_a_cca_line_does_not_use_the_half_year_rule_on_sale_unless_it_says_so(make: Any) -> None:
    assert make().half_year_rule_on_sale is False


@pytest.mark.parametrize("make", [cca_claim_line, closing_ucc_line])
def test_a_cca_line_is_not_prorated_unless_it_says_so(make: Any) -> None:
    # Guide T4002 "You were asking?": a fiscal period of less than 365 days prorates the claim; the
    # default is a full year of 365 days, which is no proration.
    assert make().fiscal_period_days == 365


@pytest.mark.parametrize("make", [cca_claim_line, closing_ucc_line])
def test_a_cca_line_holds_the_days_of_its_fiscal_period(make: Any) -> None:
    line = replace(make(), fiscal_period_days=214)

    assert line.fiscal_period_days == 214
    assert line != make()


@pytest.mark.parametrize("make", [cca_claim_line, closing_ucc_line])
def test_a_cca_line_holds_the_days_in_a_full_year_of_its_dataset(make: Any) -> None:
    assert make().full_year_days == 365
    assert replace(make(), full_year_days=366).full_year_days == 366
    assert replace(make(), full_year_days=366) != make()


FISCAL_PERIOD_DAYS = ArtifactKind("ex/fiscal_period_days", int)


def fiscal_period_days_line() -> FiscalPeriodDaysLine:
    return FiscalPeriodDaysLine(FISCAL_PERIOD_DAYS, 0, 365, 365)


def test_fiscal_period_days_line_fields_in_order() -> None:
    # Guide T4002 "You were asking?": the days of the fiscal period (214 in the guide's example),
    # compared to the 365 of a full year; the days entered are 0 when the caller entered none.
    line = fiscal_period_days_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "entered",
        "fiscal_period_days",
        "full_year_days",
    ]
    assert line == FiscalPeriodDaysLine(FISCAL_PERIOD_DAYS, 0, 365, 365)


def test_a_fiscal_period_days_lines_amount_is_the_days_of_the_fiscal_period() -> None:
    line = FiscalPeriodDaysLine(FISCAL_PERIOD_DAYS, 214, 214, 365)

    assert line.amount == D("214")
    assert isinstance(line.amount, Decimal)
    assert "amount" not in [f.name for f in fields(line)]


@pytest.mark.parametrize(
    "change",
    [
        {"output": ArtifactKind("ex/other_fiscal_period_days", int)},
        {"entered": 214},
        {"fiscal_period_days": 214},
        {"full_year_days": 366},
    ],
)
def test_fiscal_period_days_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = fiscal_period_days_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != FiscalPeriodDaysLine(**values)


def fiscal_period_days_from_dates_line() -> FiscalPeriodDaysFromDatesLine:
    return FiscalPeriodDaysFromDatesLine(FISCAL_PERIOD_DAYS, 0, 0, 365, 365)


def test_fiscal_period_days_from_dates_line_fields_in_order() -> None:
    # T2125 page 1 "Fiscal period From / to, Date (YYYYMMDD)": the two dates the caller enters (0
    # and 0 when none are), the days of the period from them, and the 365 of a full year.
    line = fiscal_period_days_from_dates_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "from_date",
        "to_date",
        "fiscal_period_days",
        "full_year_days",
    ]
    assert line == FiscalPeriodDaysFromDatesLine(FISCAL_PERIOD_DAYS, 0, 0, 365, 365)


def test_a_fiscal_period_days_from_dates_lines_amount_is_the_days_of_the_fiscal_period() -> None:
    # 1 June to 31 December 2025 is 214 days, the guide's example.
    line = FiscalPeriodDaysFromDatesLine(FISCAL_PERIOD_DAYS, 20250601, 20251231, 214, 365)

    assert line.amount == D("214")
    assert isinstance(line.amount, Decimal)
    assert "amount" not in [f.name for f in fields(line)]


@pytest.mark.parametrize(
    "change",
    [
        {"output": ArtifactKind("ex/other_fiscal_period_days", int)},
        {"from_date": 20250601},
        {"to_date": 20251231},
        {"fiscal_period_days": 214},
        {"full_year_days": 366},
    ],
)
def test_fiscal_period_days_from_dates_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = fiscal_period_days_from_dates_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != FiscalPeriodDaysFromDatesLine(**values)


def test_a_fiscal_period_days_from_dates_line_is_not_a_fiscal_period_days_line() -> None:
    assert not isinstance(fiscal_period_days_from_dates_line(), FiscalPeriodDaysLine)
    assert not isinstance(fiscal_period_days_line(), FiscalPeriodDaysFromDatesLine)


LIMIT_PRORATED = ArtifactKind("ex/limit_prorated", Decimal)
UNPRORATED_LIMIT = ArtifactKind("ex/unprorated_limit", Decimal)
SHORT_YEAR_DAYS = ArtifactKind("ex/short_year_days", Decimal)


def prorated_by_days_line() -> ProratedByDaysLine:
    return ProratedByDaysLine(
        LIMIT_PRORATED,
        UNPRORATED_LIMIT,
        D("1500000"),
        FISCAL_PERIOD_DAYS,
        153,
        365,
        SHORT_YEAR_DAYS,
        D("357"),
        D("628767.12"),
    )


def test_prorated_by_days_line_fields_in_order() -> None:
    # Income Tax Regulations 1104(3.5)(b): a year of less than 51 weeks (357 days in 2025) has the
    # limit times its days over 365. 1500000 x 153 / 365 = 628767.12 to the cent.
    line = prorated_by_days_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "days_kind",
        "fiscal_period_days",
        "full_year_days",
        "short_year_days_kind",
        "short_year_days",
        "result",
    ]
    assert line == ProratedByDaysLine(
        output=LIMIT_PRORATED,
        amount_kind=UNPRORATED_LIMIT,
        amount_value=D("1500000"),
        days_kind=FISCAL_PERIOD_DAYS,
        fiscal_period_days=153,
        full_year_days=365,
        short_year_days_kind=SHORT_YEAR_DAYS,
        short_year_days=D("357"),
        result=D("628767.12"),
    )
    assert line.output is LIMIT_PRORATED
    assert line.amount_kind is UNPRORATED_LIMIT
    assert line.amount_value == D("1500000")
    assert line.days_kind is FISCAL_PERIOD_DAYS
    assert line.fiscal_period_days == 153
    assert line.full_year_days == 365
    assert line.short_year_days_kind is SHORT_YEAR_DAYS
    assert line.short_year_days == D("357")
    assert line.result == D("628767.12")


def test_a_prorated_by_days_lines_amount_is_its_result_not_one_of_its_fields() -> None:
    line = prorated_by_days_line()

    assert line.amount == D("628767.12")
    assert isinstance(line.amount, Decimal)
    assert "amount" not in [f.name for f in fields(line)]


def test_prorated_by_days_lines_are_hashable() -> None:
    assert hash(prorated_by_days_line()) == hash(prorated_by_days_line())


def test_prorated_by_days_lines_differ_by_each_field() -> None:
    line = prorated_by_days_line()

    assert line != replace(line, output=ArtifactKind("ex/other_limit_prorated", Decimal))
    assert line != replace(line, amount_kind=ArtifactKind("ex/other_unprorated_limit", Decimal))
    assert line != replace(line, amount_value=D("600000"))
    assert line != replace(line, days_kind=ArtifactKind("ex/other_fiscal_period_days", int))
    assert line != replace(line, fiscal_period_days=154)
    assert line != replace(line, full_year_days=366)
    assert line != replace(
        line, short_year_days_kind=ArtifactKind("ex/other_short_year_days", Decimal)
    )
    assert line != replace(line, short_year_days=D("356"))
    assert line != replace(line, result=D("628767.13"))


def test_a_prorated_by_days_line_is_not_a_fiscal_period_days_line() -> None:
    assert not isinstance(prorated_by_days_line(), FiscalPeriodDaysLine)
    assert not isinstance(fiscal_period_days_line(), ProratedByDaysLine)


DAYS_IN_2024 = ArtifactKind("ex/days_in_2024", int)


def prorated_by_days_in_period_line() -> ProratedByDaysInPeriodLine:
    # Chart A amount 8: amount 6 of 20000 times 184 days in 2024 over 365 days of the period, which
    # is 10082.19 to the cent.
    return ProratedByDaysInPeriodLine(
        LIMIT_PRORATED,
        UNPRORATED_LIMIT,
        D("20000"),
        DAYS_IN_2024,
        184,
        FISCAL_PERIOD_DAYS,
        365,
        D("10082.19"),
    )


def test_prorated_by_days_in_period_line_fields_in_order() -> None:
    line = prorated_by_days_in_period_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "days_kind",
        "days",
        "period_days_kind",
        "period_days",
        "result",
    ]
    assert line == ProratedByDaysInPeriodLine(
        output=LIMIT_PRORATED,
        amount_kind=UNPRORATED_LIMIT,
        amount_value=D("20000"),
        days_kind=DAYS_IN_2024,
        days=184,
        period_days_kind=FISCAL_PERIOD_DAYS,
        period_days=365,
        result=D("10082.19"),
    )
    assert line.output is LIMIT_PRORATED
    assert line.amount_kind is UNPRORATED_LIMIT
    assert line.amount_value == D("20000")
    assert line.days_kind is DAYS_IN_2024
    assert line.days == 184
    assert line.period_days_kind is FISCAL_PERIOD_DAYS
    assert line.period_days == 365
    assert line.result == D("10082.19")


def test_a_prorated_by_days_in_period_lines_amount_is_its_result_not_one_of_its_fields() -> None:
    line = prorated_by_days_in_period_line()

    assert line.amount == D("10082.19")
    assert isinstance(line.amount, Decimal)
    assert "amount" not in [f.name for f in fields(line)]


def test_prorated_by_days_in_period_lines_are_hashable() -> None:
    assert hash(prorated_by_days_in_period_line()) == hash(prorated_by_days_in_period_line())


def test_prorated_by_days_in_period_lines_differ_by_each_field() -> None:
    line = prorated_by_days_in_period_line()

    assert line != replace(line, output=ArtifactKind("ex/other_prorated", Decimal))
    assert line != replace(line, amount_kind=ArtifactKind("ex/other_amount", Decimal))
    assert line != replace(line, amount_value=D("25000"))
    assert line != replace(line, days_kind=ArtifactKind("ex/other_days", int))
    assert line != replace(line, days=183)
    assert line != replace(line, period_days_kind=ArtifactKind("ex/other_period_days", int))
    assert line != replace(line, period_days=366)
    assert line != replace(line, result=D("10082.20"))


def test_a_prorated_by_days_in_period_line_is_not_a_prorated_by_days_line() -> None:
    assert not isinstance(prorated_by_days_in_period_line(), ProratedByDaysLine)
    assert not isinstance(prorated_by_days_line(), ProratedByDaysInPeriodLine)


@pytest.mark.parametrize("make", [recaptured_cca_line, terminal_loss_line])
def test_recaptured_cca_and_terminal_loss_lines_have_no_fiscal_period_days(make: Any) -> None:
    assert "fiscal_period_days" not in [f.name for f in fields(make())]


def test_a_recaptured_cca_line_has_no_half_year_rule_on_sale() -> None:
    assert "half_year_rule_on_sale" not in [f.name for f in fields(recaptured_cca_line())]


def test_the_reasons_a_cca_row_closes_at_zero() -> None:
    # T4036 "Column 7": "You cannot claim CCA when the amount in column 7 is: negative ...
    # positive and you do not have any property left in that class ... In either case, enter
    # "0" in column 24". The line records which, so no reader re-derives it.
    assert [reason.value for reason in CcaZeroReason] == [
        "none",
        "column_7_negative",
        "no_property_left",
    ]


def test_disposition_gain_line_fields_in_order() -> None:
    line = disposition_gain_line()

    assert line == DispositionGainLine(
        output=DISPOSITION_GAIN,
        position=2,
        proceeds=D("800.00"),
        adjusted_cost_base=D("1000.00"),
        outlays=D("30.00"),
        result=D("-230.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "proceeds",
        "adjusted_cost_base",
        "outlays",
        "result",
    ]
    assert line.output is DISPOSITION_GAIN
    assert line.position == 2


def test_disposition_gain_line_amount_is_the_signed_result() -> None:
    line = disposition_gain_line()

    assert line.amount == D("-230.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_disposition_gain_lines_differ_by_each_field() -> None:
    line = disposition_gain_line()
    same = {f.name: getattr(line, f.name) for f in fields(line)}
    changed: dict[str, Any] = {
        "position": 1,
        "proceeds": D("800.01"),
        "adjusted_cost_base": D("1000.01"),
        "outlays": D("30.01"),
        "result": D("-230.01"),
    }

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != DispositionGainLine(**{**same, name: value}), name
    assert line != DispositionGainLine(**{**same, "output": CAREGIVER})


def test_disposition_gain_only_line_fields_in_order() -> None:
    line = disposition_gain_only_line()

    assert line == DispositionGainOnlyLine(
        output=DISPOSITION_GAIN,
        position=2,
        proceeds=D("800.00"),
        adjusted_cost_base=D("1000.00"),
        outlays=D("30.00"),
        gain=D("-230.00"),
        result=D("0"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "proceeds",
        "adjusted_cost_base",
        "outlays",
        "gain",
        "result",
    ]


def test_disposition_gain_only_line_amount_is_the_result_not_the_gain() -> None:
    line = disposition_gain_only_line()

    assert line.amount == D("0")
    assert line.gain == D("-230.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_disposition_gain_only_lines_differ_by_each_field() -> None:
    line = disposition_gain_only_line()
    same = {f.name: getattr(line, f.name) for f in fields(line)}
    changed: dict[str, Any] = {
        "position": 1,
        "proceeds": D("800.01"),
        "adjusted_cost_base": D("1000.01"),
        "outlays": D("30.01"),
        "gain": D("-230.01"),
        "result": D("0.01"),
    }

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != DispositionGainOnlyLine(**{**same, name: value}), name
    assert line != DispositionGainOnlyLine(**{**same, "output": CAREGIVER})


def test_depreciable_property_gain_line_fields_in_order() -> None:
    line = depreciable_property_gain_line()

    assert line == DepreciablePropertyGainLine(
        output=DISPOSITION_GAIN,
        position=2,
        proceeds=D("800.00"),
        adjusted_cost_base=D("1000.00"),
        outlays=D("30.00"),
        farm_loss_property_taxes=D("0"),
        farm_loss_interest=D("0"),
        farm_loss_applied=D("0"),
        depreciable=1,
        gain=D("-230.00"),
        result=D("0"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "proceeds",
        "adjusted_cost_base",
        "outlays",
        "farm_loss_property_taxes",
        "farm_loss_interest",
        "farm_loss_applied",
        "depreciable",
        "gain",
        "result",
    ]


def test_depreciable_property_gain_line_amount_is_the_result_not_the_gain() -> None:
    line = depreciable_property_gain_line()

    assert line.amount == D("0")
    assert line.gain == D("-230.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_depreciable_property_gain_lines_differ_by_each_field() -> None:
    line = depreciable_property_gain_line()
    same = {f.name: getattr(line, f.name) for f in fields(line)}
    changed: dict[str, Any] = {
        "position": 1,
        "proceeds": D("800.01"),
        "adjusted_cost_base": D("1000.01"),
        "outlays": D("30.01"),
        "farm_loss_property_taxes": D("0.01"),
        "farm_loss_interest": D("0.01"),
        "farm_loss_applied": D("0.01"),
        "depreciable": 0,
        "gain": D("-230.01"),
        "result": D("0.01"),
    }

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != DepreciablePropertyGainLine(**{**same, name: value}), name
    assert line != DepreciablePropertyGainLine(**{**same, "output": CAREGIVER})


def test_qffp_gain_line_fields_in_order() -> None:
    line = qffp_gain_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "proceeds",
        "adjusted_cost_base",
        "outlays",
        "farm_loss_property_taxes",
        "farm_loss_interest",
        "farm_loss_applied",
        "result",
    ]


def test_qffp_gain_line_amount_is_the_signed_result() -> None:
    line = qffp_gain_line()

    assert line.amount == D("30000")
    assert QffpGainLine(**{**vars(line), "result": D("-230")}).amount == D("-230")
    assert "amount" not in [f.name for f in fields(line)]


def test_qffp_gain_lines_differ_by_each_field() -> None:
    line = qffp_gain_line()
    same = {f.name: getattr(line, f.name) for f in fields(line)}
    changed: dict[str, Any] = {
        "position": 1,
        "proceeds": D("200000.01"),
        "adjusted_cost_base": D("160000.01"),
        "outlays": D("0.01"),
        "farm_loss_property_taxes": D("5000.01"),
        "farm_loss_interest": D("5000.01"),
        "farm_loss_applied": D("10000.01"),
        "result": D("30000.01"),
    }

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != QffpGainLine(**{**same, name: value}), name
    assert line != QffpGainLine(**{**same, "output": CAREGIVER})


def test_the_qffp_gain_line_is_a_class_of_its_own() -> None:
    assert not isinstance(qffp_gain_line(), DispositionGainLine)
    assert not isinstance(disposition_gain_line(), QffpGainLine)
    assert not isinstance(qffp_gain_line(), ItemsTotalLine)


def test_farm_loss_applied_line_fields_in_order() -> None:
    assert [f.name for f in fields(farm_loss_applied_line())] == [
        "output",
        "position",
        "property_taxes",
        "interest",
        "result",
    ]


def test_farm_loss_applied_line_amount_is_the_result() -> None:
    line = farm_loss_applied_line()

    assert line.amount == D("10000")
    assert FarmLossAppliedLine(**{**vars(line), "result": D("0")}).amount == D("0")
    assert "amount" not in [f.name for f in fields(line)]


def test_farm_loss_applied_lines_differ_by_each_field() -> None:
    line = farm_loss_applied_line()
    same = {f.name: getattr(line, f.name) for f in fields(line)}
    changed: dict[str, Any] = {
        "position": 1,
        "property_taxes": D("5000.01"),
        "interest": D("5000.01"),
        "result": D("10000.01"),
    }

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != FarmLossAppliedLine(**{**same, name: value}), name
    assert line != FarmLossAppliedLine(**{**same, "output": CAREGIVER})


def test_the_farm_loss_applied_line_is_a_class_of_its_own() -> None:
    assert not isinstance(farm_loss_applied_line(), QffpGainLine)
    assert not isinstance(farm_loss_applied_line(), DispositionGainLine)
    assert not isinstance(farm_loss_applied_line(), ItemsTotalLine)


def test_the_depreciable_property_gain_line_is_a_class_of_its_own() -> None:
    assert not isinstance(depreciable_property_gain_line(), DispositionGainOnlyLine)
    assert not isinstance(depreciable_property_gain_line(), DispositionGainLine)
    assert not isinstance(disposition_gain_only_line(), DepreciablePropertyGainLine)
    assert not isinstance(disposition_gain_line(), DepreciablePropertyGainLine)
    assert not isinstance(depreciable_property_gain_line(), ItemsTotalLine)


def test_disposition_proceeds_line_fields_in_order() -> None:
    line = disposition_proceeds_line()

    assert line == DispositionProceedsLine(
        output=DISPOSITION_GAIN, position=2, proceeds=D("800.00")
    )
    assert [f.name for f in fields(line)] == ["output", "position", "proceeds"]


def test_disposition_proceeds_line_amount_is_the_proceeds() -> None:
    line = disposition_proceeds_line()

    assert line.amount == D("800.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_disposition_proceeds_lines_differ_by_each_field() -> None:
    line = disposition_proceeds_line()
    same = {f.name: getattr(line, f.name) for f in fields(line)}
    changed: dict[str, Any] = {"position": 1, "proceeds": D("800.01")}

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != DispositionProceedsLine(**{**same, name: value}), name
    assert line != DispositionProceedsLine(**{**same, "output": CAREGIVER})


def test_the_disposition_proceeds_line_is_a_class_of_its_own() -> None:
    assert not isinstance(disposition_proceeds_line(), DispositionGainLine)
    assert not isinstance(disposition_proceeds_line(), DispositionGainOnlyLine)
    assert not isinstance(disposition_gain_line(), DispositionProceedsLine)


def test_the_two_disposition_lines_are_classes_of_their_own() -> None:
    assert not isinstance(disposition_gain_line(), DispositionGainOnlyLine)
    assert not isinstance(disposition_gain_only_line(), DispositionGainLine)
    assert not isinstance(disposition_gain_line(), ItemsTotalLine)


def test_personal_use_property_gain_line_fields_in_order() -> None:
    line = personal_use_property_gain_line()

    assert line == PersonalUsePropertyGainLine(
        output=DISPOSITION_GAIN,
        position=2,
        proceeds=D("800.00"),
        adjusted_cost_base=D("1000.00"),
        outlays=D("30.00"),
        minimum=D("1000"),
        proceeds_used=D("1000"),
        cost_base_used=D("1000"),
        gain=D("-30.00"),
        result=D("0"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "proceeds",
        "adjusted_cost_base",
        "outlays",
        "minimum",
        "proceeds_used",
        "cost_base_used",
        "gain",
        "result",
    ]


def test_personal_use_property_gain_line_amount_is_the_result_not_the_gain() -> None:
    line = personal_use_property_gain_line()

    assert line.amount == D("0")
    assert line.gain == D("-30.00")
    assert "amount" not in [f.name for f in fields(line)]


def test_personal_use_property_gain_lines_differ_by_each_field() -> None:
    line = personal_use_property_gain_line()
    same = {f.name: getattr(line, f.name) for f in fields(line)}
    changed: dict[str, Any] = {
        "position": 1,
        "proceeds": D("800.01"),
        "adjusted_cost_base": D("1000.01"),
        "outlays": D("30.01"),
        "minimum": D("1000.01"),
        "proceeds_used": D("1000.01"),
        "cost_base_used": D("1000.01"),
        "gain": D("-30.01"),
        "result": D("0.01"),
    }

    assert set(changed) == set(same) - {"output"}
    for name, value in changed.items():
        assert line != PersonalUsePropertyGainLine(**{**same, name: value}), name
    assert line != PersonalUsePropertyGainLine(**{**same, "output": CAREGIVER})


def test_the_personal_use_property_gain_line_is_a_class_of_its_own() -> None:
    assert not isinstance(personal_use_property_gain_line(), DispositionGainOnlyLine)
    assert not isinstance(personal_use_property_gain_line(), DispositionGainLine)
    assert not isinstance(disposition_gain_only_line(), PersonalUsePropertyGainLine)
    assert not isinstance(personal_use_property_gain_line(), ItemsTotalLine)


def test_percentage_applied_line_fields_in_order() -> None:
    line = percentage_applied_line()

    assert line == PercentageAppliedLine(
        output=CREDIT_SHARE,
        amount_kind=TAX_PAYABLE,
        amount_value=D("1000"),
        percentage_kind=PERCENTAGE,
        percentage_value=D("50"),
        rounding=CENT,
        result=D("500"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "percentage_kind",
        "percentage_value",
        "rounding",
        "result",
    ]
    assert line.output is CREDIT_SHARE
    assert line.amount_kind is TAX_PAYABLE
    assert line.amount_value == D("1000")
    assert line.percentage_kind is PERCENTAGE
    assert line.percentage_value == D("50")
    assert line.rounding == CENT
    assert line.result == D("500")
    assert line.amount == D("500")


def test_a_percentage_applied_lines_amount_is_not_one_of_its_fields() -> None:
    assert "amount" not in [f.name for f in fields(percentage_applied_line())]


def test_percentage_applied_lines_are_hashable() -> None:
    assert hash(percentage_applied_line()) == hash(percentage_applied_line())


def test_percentage_applied_lines_differ_by_amount_value() -> None:
    assert percentage_applied_line() != PercentageAppliedLine(
        CREDIT_SHARE, TAX_PAYABLE, D("1001"), PERCENTAGE, D("50"), CENT, D("500")
    )


def test_percentage_applied_lines_differ_by_percentage_value() -> None:
    assert percentage_applied_line() != PercentageAppliedLine(
        CREDIT_SHARE, TAX_PAYABLE, D("1000"), PERCENTAGE, D("51"), CENT, D("500")
    )


def test_percentage_applied_lines_differ_by_kind() -> None:
    other = ArtifactKind("ex/other_percentage", Decimal)

    assert percentage_applied_line() != PercentageAppliedLine(
        CREDIT_SHARE, TAX_PAYABLE, D("1000"), other, D("50"), CENT, D("500")
    )


def test_percentage_applied_lines_differ_by_rounding() -> None:
    assert percentage_applied_line() != PercentageAppliedLine(
        CREDIT_SHARE, TAX_PAYABLE, D("1000"), PERCENTAGE, D("50"), NO_ROUNDING, D("500")
    )


def test_a_percentage_applied_line_is_not_a_ratio_or_rate_applied_line() -> None:
    assert not isinstance(percentage_applied_line(), RatioAppliedLine)
    assert not isinstance(percentage_applied_line(), RateAppliedLine)


# --- lines for the engine capabilities of Form RC381 ----------------------------------------------


def test_count_at_least_line_fields_in_order() -> None:
    line = count_at_least_line()

    assert line == CountAtLeastLine(
        output=PERSONS, count_kind=CHILDREN, count=3, minimum_kind=DEPENDANTS, minimum=2
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "count_kind",
        "count",
        "minimum_kind",
        "minimum",
    ]
    assert line.output is PERSONS
    assert line.count_kind is CHILDREN
    assert line.count == 3
    assert line.minimum_kind is DEPENDANTS
    assert line.minimum == 2
    assert line.amount == D(3)


def test_count_at_least_lines_differ_by_count_and_minimum() -> None:
    assert count_at_least_line() != CountAtLeastLine(PERSONS, CHILDREN, 4, DEPENDANTS, 2)
    assert count_at_least_line() != CountAtLeastLine(PERSONS, CHILDREN, 3, DEPENDANTS, 3)


def test_count_at_least_lines_are_hashable() -> None:
    assert hash(count_at_least_line()) == hash(count_at_least_line())


def test_a_count_at_least_line_is_not_an_at_most_line() -> None:
    assert not isinstance(count_at_least_line(), AtMostLine)


# --- more than per unit (`ca/more_than_per_unit`): one line, the total checked against the count
# times the per-unit amount, rounded once


def test_more_than_per_unit_line_fields_in_order() -> None:
    line = more_than_per_unit_line()

    assert line == MoreThanPerUnitLine(
        output=TOTAL,
        total_kind=PART_ONE,
        total=D("201"),
        count_kind=CHILDREN,
        count=2,
        per_unit=Amount(D("100.00")),
        rounding=CENT,
        minimum_total=D("200.00"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "total_kind",
        "total",
        "count_kind",
        "count",
        "per_unit",
        "rounding",
        "minimum_total",
    ]
    assert line.output is TOTAL
    assert line.total_kind is PART_ONE
    assert line.total == D("201")
    assert line.count_kind is CHILDREN
    assert line.count == 2
    assert line.per_unit == Amount(D("100.00"))
    assert line.rounding == CENT
    assert line.minimum_total == D("200.00")


def test_more_than_per_unit_line_amount_is_the_total() -> None:
    assert more_than_per_unit_line().amount == D("201")


def test_more_than_per_unit_lines_differ_by_total_count_and_minimum() -> None:
    base = more_than_per_unit_line()

    assert base != MoreThanPerUnitLine(
        output=TOTAL,
        total_kind=PART_ONE,
        total=D("202"),
        count_kind=CHILDREN,
        count=2,
        per_unit=Amount(D("100.00")),
        rounding=CENT,
        minimum_total=D("200.00"),
    )
    assert base != MoreThanPerUnitLine(
        output=TOTAL,
        total_kind=PART_ONE,
        total=D("201"),
        count_kind=CHILDREN,
        count=3,
        per_unit=Amount(D("100.00")),
        rounding=CENT,
        minimum_total=D("300.00"),
    )


def test_more_than_per_unit_lines_are_hashable() -> None:
    assert hash(more_than_per_unit_line()) == hash(more_than_per_unit_line())


def test_a_more_than_per_unit_line_is_not_a_count_at_least_line() -> None:
    assert not isinstance(more_than_per_unit_line(), CountAtLeastLine)


def test_a_more_than_per_unit_line_is_not_a_per_unit_amount_line() -> None:
    assert not isinstance(more_than_per_unit_line(), PerUnitAmountLine)


# --- claim at most (`ca/claim_at_most`): one line, the claim and the signed maximum it was checked


def test_claim_at_most_line_fields_in_order() -> None:
    line = claim_at_most_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "claim_kind",
        "claim_value",
        "maximum_kind",
        "maximum_value",
    ]
    assert line.output is ALLOWED
    assert line.claim_kind is CLAIMED
    assert line.claim_value == D("1500.25")
    assert line.maximum_kind is LIMIT
    assert line.maximum_value == D(1926)
    assert line.amount == D("1500.25")


def test_claim_at_most_lines_differ_by_claim_and_maximum() -> None:
    assert claim_at_most_line() != ClaimAtMostLine(ALLOWED, CLAIMED, D(0), LIMIT, D(1926))
    assert claim_at_most_line() != ClaimAtMostLine(ALLOWED, CLAIMED, D("1500.25"), LIMIT, D(-1))


def test_claim_at_most_lines_are_hashable() -> None:
    assert hash(claim_at_most_line()) == hash(claim_at_most_line())


def test_a_claim_at_most_line_is_not_an_at_most_line() -> None:
    assert not isinstance(claim_at_most_line(), AtMostLine)
    assert not isinstance(at_most_line(), ClaimAtMostLine)


# --- count at most (`ca/count_at_most`): one line, the count and the maximum it was checked against


def test_count_at_most_line_fields_in_order() -> None:
    line = count_at_most_line()

    assert line == CountAtMostLine(
        output=PERSONS, count_kind=CHILDREN, count=3, maximum_kind=DEPENDANTS, maximum=4
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "count_kind",
        "count",
        "maximum_kind",
        "maximum",
    ]
    assert line.output is PERSONS
    assert line.count_kind is CHILDREN
    assert line.count == 3
    assert line.maximum_kind is DEPENDANTS
    assert line.maximum == 4
    assert line.amount == D(3)


def test_count_at_most_lines_differ_by_count_and_maximum() -> None:
    assert count_at_most_line() != CountAtMostLine(PERSONS, CHILDREN, 4, DEPENDANTS, 4)
    assert count_at_most_line() != CountAtMostLine(PERSONS, CHILDREN, 3, DEPENDANTS, 3)


def test_count_at_most_lines_are_hashable() -> None:
    assert hash(count_at_most_line()) == hash(count_at_most_line())


def test_a_count_at_most_line_is_not_a_count_at_least_line() -> None:
    assert not isinstance(count_at_most_line(), CountAtLeastLine)
    assert not isinstance(count_at_least_line(), CountAtMostLine)


# --- yes or no count (`ca/yes_or_no_count`): one line, the count and the kind it was checked as ---


def test_yes_or_no_count_line_fields_in_order() -> None:
    line = yes_or_no_count_line()

    assert line == YesOrNoCountLine(output=PERSONS, count_kind=CHILDREN, count=1)
    assert [f.name for f in fields(line)] == ["output", "count_kind", "count"]
    assert line.output is PERSONS
    assert line.count_kind is CHILDREN
    assert line.count == 1
    assert line.amount == D(1)


def test_yes_or_no_count_lines_differ_by_count() -> None:
    assert yes_or_no_count_line() != YesOrNoCountLine(PERSONS, CHILDREN, 0)
    assert yes_or_no_count_line() == YesOrNoCountLine(PERSONS, CHILDREN, 1)


def test_yes_or_no_count_lines_are_hashable() -> None:
    assert hash(yes_or_no_count_line()) == hash(yes_or_no_count_line())


def test_a_yes_or_no_count_line_is_not_a_count_at_least_line() -> None:
    assert not isinstance(yes_or_no_count_line(), CountAtLeastLine)
    assert not isinstance(yes_or_no_count_line(), AtMostLine)


# --- count without records (`ca/count_without_records`): one line, the count and the record list
# it was checked against, with the number of its records ---


def test_count_without_records_line_fields_in_order() -> None:
    line = count_without_records_line()

    assert line == CountWithoutRecordsLine(
        output=PERSONS, count_kind=CHILDREN, count=1, records_kind=ITEMS, record_count=0
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "count_kind",
        "count",
        "records_kind",
        "record_count",
    ]
    assert line.output is PERSONS
    assert line.count_kind is CHILDREN
    assert line.count == 1
    assert line.records_kind is ITEMS
    assert line.record_count == 0
    assert line.amount == D(1)


def test_count_without_records_line_amount_is_the_count_not_the_record_count() -> None:
    line = CountWithoutRecordsLine(PERSONS, CHILDREN, 0, ITEMS, 2)

    assert line.count == 0
    assert line.record_count == 2
    assert line.amount == D(0)


def test_count_without_records_lines_differ_by_count_records_and_output() -> None:
    other_list = RecordListKind("ex/other_records", fields=(ITEM_AMOUNT,))

    assert count_without_records_line() != CountWithoutRecordsLine(PERSONS, CHILDREN, 2, ITEMS, 0)
    assert count_without_records_line() != CountWithoutRecordsLine(PERSONS, CHILDREN, 1, ITEMS, 1)
    assert count_without_records_line() != CountWithoutRecordsLine(
        PERSONS, CHILDREN, 1, other_list, 0
    )
    assert count_without_records_line() != CountWithoutRecordsLine(
        DEPENDANTS, CHILDREN, 1, ITEMS, 0
    )


def test_count_without_records_lines_are_hashable() -> None:
    assert hash(count_without_records_line()) == hash(count_without_records_line())


def test_a_count_without_records_line_is_not_a_count_at_least_or_yes_or_no_line() -> None:
    assert not isinstance(count_without_records_line(), CountAtLeastLine)
    assert not isinstance(count_without_records_line(), YesOrNoCountLine)
    assert not isinstance(count_without_records_line(), AtMostLine)


# --- count not refused (`ca/count_refused_by_conditions`): the count and the kind checked ---


def test_count_not_refused_line_fields_in_order() -> None:
    line = count_not_refused_line()

    assert line == CountNotRefusedLine(output=PERSONS, count_kind=CHILDREN, count=2)
    assert [f.name for f in fields(line)] == ["output", "count_kind", "count"]
    assert line.output is PERSONS
    assert line.count_kind is CHILDREN
    assert line.count == 2
    assert line.amount == D(2)


def test_count_not_refused_lines_differ_by_count() -> None:
    assert count_not_refused_line() != CountNotRefusedLine(PERSONS, CHILDREN, 3)
    assert count_not_refused_line() == CountNotRefusedLine(PERSONS, CHILDREN, 2)


def test_count_not_refused_lines_are_hashable() -> None:
    assert hash(count_not_refused_line()) == hash(count_not_refused_line())


def test_a_count_not_refused_line_is_not_a_yes_or_no_count_line() -> None:
    assert not isinstance(count_not_refused_line(), YesOrNoCountLine)
    assert not isinstance(yes_or_no_count_line(), CountNotRefusedLine)


def test_ratio_truncated_line_fields_in_order() -> None:
    line = ratio_truncated_line()
    five_decimals_down = RoundTo(D("0.00001"), RoundingMode.DOWN)

    assert line == RatioTruncatedLine(
        output=RATED_RATE,
        dividend=BASE,
        dividend_amount=D("30000"),
        divisor=TOTAL,
        divisor_amount=D("70000"),
        rounding=five_decimals_down,
        cap_at_one=False,
        result=D("0.42857"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "dividend",
        "dividend_amount",
        "divisor",
        "divisor_amount",
        "rounding",
        "cap_at_one",
        "result",
    ]
    assert line.output is RATED_RATE
    assert line.dividend is BASE
    assert line.divisor is TOTAL
    assert line.rounding == five_decimals_down
    assert line.cap_at_one is False
    assert line.amount == D("0.42857")


def test_ratio_truncated_lines_differ_by_cap_and_rounding() -> None:
    line = ratio_truncated_line()
    five_decimals_down = RoundTo(D("0.00001"), RoundingMode.DOWN)

    assert line != RatioTruncatedLine(
        RATED_RATE, BASE, D("30000"), TOTAL, D("70000"), five_decimals_down, True, D("0.42857")
    )
    assert line != RatioTruncatedLine(
        RATED_RATE, BASE, D("30000"), TOTAL, D("70000"), NO_ROUNDING, False, D("0.42857")
    )


def test_ratio_truncated_lines_are_hashable() -> None:
    assert hash(ratio_truncated_line()) == hash(ratio_truncated_line())


def test_a_ratio_truncated_line_is_not_a_quotient_line() -> None:
    assert not isinstance(ratio_truncated_line(), QuotientLine)


def test_positive_part_of_negation_line_fields_in_order() -> None:
    line = positive_part_of_negation_line()

    assert line == PositivePartOfNegationLine(
        output=RATED, amount_kind=NET, amount_value=D("-12.50"), result=D("12.50")
    )
    assert [f.name for f in fields(line)] == ["output", "amount_kind", "amount_value", "result"]
    assert line.output is RATED
    assert line.amount_kind is NET
    assert line.amount_value == D("-12.50")
    assert line.amount == D("12.50")


def test_positive_part_of_negation_lines_differ_by_value() -> None:
    assert positive_part_of_negation_line() != PositivePartOfNegationLine(
        RATED, NET, D("-13"), D("12.50")
    )


def test_positive_part_of_negation_lines_are_hashable() -> None:
    assert hash(positive_part_of_negation_line()) == hash(positive_part_of_negation_line())


def test_lesser_of_when_positive_line_fields_in_order() -> None:
    line = lesser_of_when_positive_line()

    assert line == LesserOfWhenPositiveLine(
        output=TOTAL,
        parts=((PART_ONE, D("1500")), (PART_TWO, D("750.50"))),
        all_positive=True,
        bracket=True,
        result=D("-750.50"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "parts",
        "all_positive",
        "bracket",
        "result",
    ]
    assert line.output is TOTAL
    assert line.parts == ((PART_ONE, D("1500")), (PART_TWO, D("750.50")))
    assert line.all_positive is True
    assert line.bracket is True
    assert line.amount == D("-750.50")


def test_lesser_of_when_positive_lines_differ_by_condition_bracket_and_result() -> None:
    parts = ((PART_ONE, D("1500")), (PART_TWO, D("750.50")))

    assert lesser_of_when_positive_line() != LesserOfWhenPositiveLine(
        TOTAL, parts, False, True, D("-750.50")
    )
    assert lesser_of_when_positive_line() != LesserOfWhenPositiveLine(
        TOTAL, parts, True, False, D("-750.50")
    )
    assert lesser_of_when_positive_line() != LesserOfWhenPositiveLine(
        TOTAL, parts, True, True, D("750.50")
    )


def test_lesser_of_when_positive_lines_are_hashable() -> None:
    assert hash(lesser_of_when_positive_line()) == hash(lesser_of_when_positive_line())


def test_a_lesser_of_when_positive_line_is_not_a_lesser_of_line() -> None:
    assert not isinstance(lesser_of_when_positive_line(), LesserOfLine)


def test_chosen_by_sign_line_fields_in_order() -> None:
    line = chosen_by_sign_line()

    assert line == ChosenBySignLine(
        output=CHOSEN, sign_kind=GATE, sign=D("-3"), chosen_kind=ALONE, chosen_value=D("1633.00")
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "sign_kind",
        "sign",
        "chosen_kind",
        "chosen_value",
    ]
    assert line.output is CHOSEN
    assert line.sign_kind is GATE
    assert line.sign == D("-3")
    assert line.chosen_kind is ALONE
    assert line.amount == D("1633.00")


def test_a_chosen_by_sign_line_for_an_omitted_branch_names_no_kind() -> None:
    line = ChosenBySignLine(CHOSEN, GATE, D("0"), None, D("0"))

    assert line.chosen_kind is None
    assert line.amount == D("0")


def test_chosen_by_sign_lines_differ_by_sign_and_chosen_kind() -> None:
    assert chosen_by_sign_line() != ChosenBySignLine(CHOSEN, GATE, D("3"), ALONE, D("1633.00"))
    assert chosen_by_sign_line() != ChosenBySignLine(
        CHOSEN, GATE, D("-3"), WITH_FAMILY, D("1633.00")
    )


def test_chosen_by_sign_lines_are_hashable() -> None:
    assert hash(chosen_by_sign_line()) == hash(chosen_by_sign_line())


def test_a_chosen_by_sign_line_is_not_a_chosen_by_count_line() -> None:
    assert not isinstance(chosen_by_sign_line(), ChosenByCountLine)


def test_amount_when_more_line_fields_in_order() -> None:
    line = amount_when_more_line()

    assert line == AmountWhenMoreLine(
        output=ALLOWED,
        amount_kind=CLAIMED,
        amount_value=D("1500.25"),
        more_kind=TESTED,
        more_value=D("70000.01"),
        than_kind=LIMIT,
        than_value=D(70000),
        result=D("1500.25"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "amount_kind",
        "amount_value",
        "more_kind",
        "more_value",
        "than_kind",
        "than_value",
        "result",
    ]
    assert line.output is ALLOWED
    assert line.amount_kind is CLAIMED
    assert line.more_kind is TESTED
    assert line.than_kind is LIMIT
    assert line.amount == D("1500.25")


def test_amount_when_more_lines_differ_by_values_and_result() -> None:
    line = amount_when_more_line()

    assert line != AmountWhenMoreLine(
        ALLOWED, CLAIMED, D("1500.25"), TESTED, D(70000), LIMIT, D(70000), D(0)
    )
    assert line != AmountWhenMoreLine(
        ALLOWED, CLAIMED, D("1500.25"), TESTED, D("70000.01"), LIMIT, D(60000), D("1500.25")
    )


def test_amount_when_more_lines_are_hashable() -> None:
    assert hash(amount_when_more_line()) == hash(amount_when_more_line())


def test_an_amount_when_more_line_is_not_a_threshold_gate_line() -> None:
    assert not isinstance(amount_when_more_line(), ThresholdGateLine)


# --- a vehicle of Form T2125 Charts A to C ------------------------------------------------------

MOTOR_VEHICLE_EXPENSES = ArtifactKind("ex/motor_vehicle_expenses", Decimal)


def business_vehicle_line() -> BusinessVehicleLine:
    return BusinessVehicleLine(
        MOTOR_VEHICLE_EXPENSES,
        1,
        D("5000.00"),
        D("2500.00"),
        D("400.00"),
        D("2147.00"),
        D("2500.00"),
    )


def test_business_vehicle_line_is_a_frozen_trace_line_equal_by_value() -> None:
    line = business_vehicle_line()

    assert isinstance(line, TraceLine)
    assert line == business_vehicle_line()
    assert line is not business_vehicle_line()
    assert hash(line) == hash(business_vehicle_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, "line_16", D(1))  # noqa: B010


def test_business_vehicle_line_fields_in_order() -> None:
    line = business_vehicle_line()

    assert [f.name for f in fields(line)] == [
        "output",
        "position",
        "line_12",
        "line_13",
        "line_19",
        "line_28",
        "line_16",
    ]
    assert line == BusinessVehicleLine(
        output=MOTOR_VEHICLE_EXPENSES,
        position=1,
        line_12=D("5000.00"),
        line_13=D("2500.00"),
        line_19=D("400.00"),
        line_28=D("2147.00"),
        line_16=D("2500.00"),
    )


def test_a_business_vehicle_lines_amount_is_line_16() -> None:
    assert business_vehicle_line().amount == D("2500.00")
    assert "amount" not in [f.name for f in fields(business_vehicle_line())]


@pytest.mark.parametrize(
    "change",
    [
        {"output": ArtifactKind("ex/other_vehicle_expenses", Decimal)},
        {"position": 2},
        {"line_12": D("5000.01")},
        {"line_13": D("2500.01")},
        {"line_19": D("400.01")},
        {"line_28": D("2147.01")},
        {"line_16": D("2600.00")},
    ],
)
def test_business_vehicle_lines_differ_by_each_field(change: dict[str, Any]) -> None:
    line = business_vehicle_line()
    values = {f.name: getattr(line, f.name) for f in fields(line)}
    values.update(change)

    assert line != BusinessVehicleLine(**values)


def test_a_business_vehicle_line_is_not_an_items_total_line() -> None:
    assert not isinstance(business_vehicle_line(), ItemsTotalLine)


# --- YearAmountLine (Guide T4044 "Eligible leasing costs" footnotes) ------------------------------


def year_amount_line() -> YearAmountLine:
    return YearAmountLine(
        ArtifactKind("ex/lease_list_price_limit", Decimal),
        ArtifactKind("ex/lease_year", int),
        2024,
        D("43529"),
    )


def test_year_amount_line_fields_in_order() -> None:
    assert [f.name for f in fields(year_amount_line())] == [
        "output",
        "year_kind",
        "year_value",
        "result",
    ]


def test_a_year_amount_line_amount_is_its_result() -> None:
    assert year_amount_line().amount == D("43529")
    assert "amount" not in [f.name for f in fields(year_amount_line())]


def test_year_amount_lines_differ_by_each_field() -> None:
    line = year_amount_line()

    assert hash(line) == hash(year_amount_line())
    assert line != replace(line, output=ArtifactKind("ex/other", Decimal))
    assert line != replace(line, year_kind=ArtifactKind("ex/other_year", int))
    assert line != replace(line, year_value=2023)
    assert line != replace(line, result=D("42353"))


# --- PercentageOfLine (Form T2043 Chart B rows 3 and 6) ------------------------------------------

PCT_OUTPUT = ArtifactKind("ex/farm_chart_b_row_3_on", Decimal)
PCT_DIVIDEND = ArtifactKind("ex/farm_chart_b_gross_income_on", Decimal)
PCT_DIVISOR = ArtifactKind("ex/farm_chart_b_total_gross_income", Decimal)
PCT_ROUNDING = RoundTo(D("0.0001"), RoundingMode.HALF_UP)


def percentage_of_line() -> PercentageOfLine:
    # Row 3: 60,000 of 100,000 is 60%.
    return PercentageOfLine(
        PCT_OUTPUT,
        PCT_DIVIDEND,
        D("60000"),
        PCT_DIVISOR,
        D("100000"),
        PCT_ROUNDING,
        D("60"),
    )


def test_percentage_of_line_fields_in_order() -> None:
    assert [f.name for f in fields(percentage_of_line())] == [
        "output",
        "dividend",
        "dividend_amount",
        "divisor",
        "divisor_amount",
        "rounding",
        "result",
    ]
    assert percentage_of_line() == PercentageOfLine(
        output=PCT_OUTPUT,
        dividend=PCT_DIVIDEND,
        dividend_amount=D("60000"),
        divisor=PCT_DIVISOR,
        divisor_amount=D("100000"),
        rounding=PCT_ROUNDING,
        result=D("60"),
    )


def test_a_percentage_of_line_amount_is_its_result_not_one_of_its_fields() -> None:
    line = percentage_of_line()

    assert line.amount == D("60")
    assert isinstance(line.amount, Decimal)
    assert "amount" not in [f.name for f in fields(line)]


def test_percentage_of_lines_are_hashable() -> None:
    assert hash(percentage_of_line()) == hash(percentage_of_line())


def test_percentage_of_lines_differ_by_each_field() -> None:
    line = percentage_of_line()

    assert line != replace(line, output=ArtifactKind("ex/other_percent", Decimal))
    assert line != replace(line, dividend=ArtifactKind("ex/other_dividend", Decimal))
    assert line != replace(line, dividend_amount=D("60001"))
    assert line != replace(line, divisor=ArtifactKind("ex/other_divisor", Decimal))
    assert line != replace(line, divisor_amount=D("100001"))
    assert line != replace(line, rounding=RoundTo(D("0.01"), RoundingMode.HALF_UP))
    assert line != replace(line, result=D("60.0001"))


def test_pooled_provincial_foreign_tax_credit_line_fields_in_order() -> None:
    line = pooled_provincial_foreign_tax_credit_line()

    assert line == PooledProvincialForeignTaxCreditLine(
        output=NON_COMPLIANT,
        sheets=2,
        tax_paid=D("150"),
        federal_credit=D("40.88"),
        line_3=D("109.12"),
        income=D("10100"),
        net_income=D("100000"),
        provincial_tax=D("5000"),
        threshold=D("200"),
        rounding=CENT,
        line_4=D("505.00"),
        result=D("109.12"),
    )
    assert [f.name for f in fields(line)] == [
        "output",
        "sheets",
        "tax_paid",
        "federal_credit",
        "line_3",
        "income",
        "net_income",
        "provincial_tax",
        "threshold",
        "rounding",
        "line_4",
        "result",
        "special_credit",
        "divisor",
    ]
    assert line.output is NON_COMPLIANT
    assert type(line.sheets) is int
    assert line.rounding == CENT


def test_a_pooled_provincial_foreign_tax_credit_lines_amount_is_its_result() -> None:
    assert pooled_provincial_foreign_tax_credit_line().amount == D("109.12")


def test_pooled_provincial_foreign_tax_credit_lines_differ_by_each_field() -> None:
    line = pooled_provincial_foreign_tax_credit_line()
    other_output = ArtifactKind("ex/other_expenses", Decimal)
    args: list[Any] = [
        NON_COMPLIANT,
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
    ]
    changes: list[Any] = [
        other_output,
        3,
        D("151"),
        D("40.89"),
        D("109.13"),
        D("10101"),
        D("100001"),
        D("5001"),
        D("201"),
        NO_ROUNDING,
        D("505.01"),
        D("99.00"),
    ]
    for index, changed in enumerate(changes):
        varied = [*args[:index], changed, *args[index + 1 :]]
        assert line != PooledProvincialForeignTaxCreditLine(*varied)


def test_pooled_provincial_foreign_tax_credit_lines_are_frozen_and_hashable() -> None:
    line = pooled_provincial_foreign_tax_credit_line()

    assert hash(line) == hash(pooled_provincial_foreign_tax_credit_line())
    with pytest.raises(FrozenInstanceError):
        setattr(line, "result", D(1))  # noqa: B010


def test_a_pooled_provincial_line_is_not_a_provincial_sheet_line() -> None:
    assert not isinstance(
        pooled_provincial_foreign_tax_credit_line(), ProvincialForeignTaxCreditLine
    )
    assert not isinstance(pooled_provincial_foreign_tax_credit_line(), PooledForeignTaxCreditLine)


def test_pooled_provincial_foreign_tax_credit_line_minimum_tax_fields_default_to_none() -> None:
    # Without minimum tax (the count 0) the pooled line keeps the two new fields at None.
    line = pooled_provincial_foreign_tax_credit_line()

    assert line.special_credit is None
    assert line.divisor is None


def test_pooled_provincial_foreign_tax_credit_minimum_tax_line_carries_its_fields() -> None:
    line = pooled_provincial_foreign_tax_credit_minimum_tax_line()

    assert line.special_credit == D("160")
    assert line.divisor == ExactFraction(210)
    assert line.federal_credit == D("114.29")
    assert line.amount == D("35.71")


def test_a_pooled_provincial_minimum_tax_line_differs_by_each_new_field() -> None:
    line = pooled_provincial_foreign_tax_credit_minimum_tax_line()

    assert line != replace(line, special_credit=D("161"))
    assert line != replace(line, special_credit=None)
    assert line != replace(line, divisor=ExactFraction(211))
    assert line != replace(line, divisor=None)
    assert hash(line) == hash(pooled_provincial_foreign_tax_credit_minimum_tax_line())


def test_a_pooled_provincial_line_with_and_without_minimum_tax_fields_is_unequal() -> None:
    plain = pooled_provincial_foreign_tax_credit_line()
    minimum = pooled_provincial_foreign_tax_credit_minimum_tax_line()

    assert plain != minimum
