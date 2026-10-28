"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`).

Schedule 8 Part 5 lines 43 to 69, "Tax credit, deduction and overpayment for CPP contributions
through employment income, self-employment income, and other earnings". Lines 51 to 69 repeat Part
3b lines 30 to 48 with the same formulas, but each Part 5 line is its own step. Every line here
computes something, so there are no copy lines.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.contribution_tier import TieredContribution
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_ACTUAL_BASE_CONTRIBUTIONS,
    CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASE_CONTRIBUTIONS,
    CPP_BASE_CONTRIBUTIONS_DIFFERENCE,
    CPP_CONTRIBUTIONS_DIFFERENCE,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE,
    CPP_LINE_16_NOT_NEGATIVE,
    CPP_LINE_16_POSITIVE,
    CPP_LINE_19_NOT_NEGATIVE,
    CPP_LINE_20_POSITIVE,
    CPP_LINE_23_NOT_NEGATIVE,
    CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE,
    CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE,
    CPP_PART_5_LINE_23_LESS_LINE_56,
    CPP_PART_5_LINE_30,
    CPP_PART_5_LINE_42,
    CPP_PART_5_LINE_43,
    CPP_PART_5_LINE_44,
    CPP_PART_5_LINE_45,
    CPP_PART_5_LINE_46,
    CPP_PART_5_LINE_47,
    CPP_PART_5_LINE_48,
    CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE,
    CPP_PART_5_LINE_49,
    CPP_PART_5_LINE_50,
    CPP_PART_5_LINE_50_LINE_49_POSITIVE,
    CPP_PART_5_LINE_51,
    CPP_PART_5_LINE_52,
    CPP_PART_5_LINE_53,
    CPP_PART_5_LINE_53_LESSER,
    CPP_PART_5_LINE_54,
    CPP_PART_5_LINE_55,
    CPP_PART_5_LINE_56,
    CPP_PART_5_LINE_56_LESSER,
    CPP_PART_5_LINE_57,
    CPP_PART_5_LINE_58,
    CPP_PART_5_LINE_59,
    CPP_PART_5_LINE_60,
    CPP_PART_5_LINE_60_LESSER,
    CPP_PART_5_LINE_61,
    CPP_PART_5_LINE_62,
    CPP_PART_5_LINE_63,
    CPP_PART_5_LINE_63_LESSER,
    CPP_PART_5_LINE_64,
    CPP_PART_5_LINE_65,
    CPP_PART_5_LINE_66,
    CPP_PART_5_LINE_67,
    CPP_PART_5_LINE_67_LESSER,
    CPP_PART_5_LINE_68,
    CPP_PART_5_LINE_69,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPP_ZERO,
)

INPUTS = frozenset[str]()

# Part 5 line 49 (42100), line 50 (44800), line 57 (30800) and line 69 (22215) are read by the
# routing steps (see `deductions_schedule_8_part_5_other_earnings.py` for lines 70 to 88), so
# nothing here is a declared output.
OUTPUTS = frozenset[str]()

FORM_STEPS = {
    # Schedule 8 Part 5 line 43 "Required base contributions on CPP pensionable earnings: Line
    # 43: amount from line 30 multiplied by 9.9% (maximum $6,712.20) =": the tier of Part 4 line
    # 10 on line 30, which is the earnings of Part 4 line 9 here.
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_self_employed_base_contribution"},
        consumes={"earnings": "ca/cpp_part_5_line_30"},
        produces={"output": "ca/cpp_part_5_line_43"},
    ),
    # Schedule 8 Part 5 line 44 "Required first additional contributions on CPP pensionable
    # earnings: Line 44: amount from line 30 multiplied by 2% (maximum $1,356.00) =".
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_self_employed_first_additional_contribution"},
        consumes={"earnings": "ca/cpp_part_5_line_30"},
        produces={"output": "ca/cpp_part_5_line_44"},
    ),
    # Schedule 8 Part 5 line 45 "Required second additional contributions on CPP pensionable
    # earnings: Line 45: amount from line 42 multiplied by 8% (maximum $792.00) =": line 42
    # prints no floor and is negative for a loss with employment income above $71,300, which the
    # tier floors to a band of 0 (so line 45 is 0).
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_self_employed_second_additional_contribution"},
        consumes={"earnings": "ca/cpp_part_5_line_42"},
        produces={"output": "ca/cpp_part_5_line_45"},
    ),
    # Schedule 8 Part 5 line 46 "Line 44 plus line 45 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_44", "ca/cpp_part_5_line_45")},
        produces={"output": "ca/cpp_part_5_line_46"},
    ),
    # Schedule 8 Part 5 line 47 "Line 43 plus line 46 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_43", "ca/cpp_part_5_line_46")},
        produces={"output": "ca/cpp_part_5_line_47"},
    ),
    # Schedule 8 Part 5 line 48 "Amount from line 24 of Part 3 (if positive) multiplied by 2 =":
    # the amount from line 24 of Part 3 if positive, line 24 less "0", not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_contributions_difference", "less": "ca/cpp_zero"},
        produces={"output": "ca/cpp_part_5_line_48_line_24_if_positive"},
    ),
    # Schedule 8 Part 5 line 48 "multiplied by 2 =": 2 is more than 1, so it is a fraction
    # dataset, not a rate (as the 138% of the eligible dividend gross-up).
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/cpp_part_5_line_48_multiplier"},
        consumes={"base": "ca/cpp_part_5_line_48_line_24_if_positive"},
        produces={"output": "ca/cpp_part_5_line_48"},
    ),
    # Schedule 8 Part 5 line 49 "CPP contributions payable on self-employment income and other
    # earnings: Line 47 minus line 48. If positive, enter the amount (in dollars and cents) on
    # line 42100 of your return and continue at line 51. If negative, show in brackets and
    # continue at line 50. =": signed, negative in brackets when line 48 is more than line 47.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_47", "less": "ca/cpp_part_5_line_48"},
        produces={"output": "ca/cpp_part_5_line_49"},
    ),
    # Schedule 8 Part 5 line 50 "amount from line 49 entered as a positive amount": "0" less
    # line 49, not below zero (0 when line 49 is positive or "0").
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_zero", "less": "ca/cpp_part_5_line_49"},
        produces={"output": "ca/cpp_part_5_line_50_line_49_positive"},
    ),
    # Schedule 8 Part 5 line 50 "CPP overpayment: Enter the result of the following calculation
    # (in dollars and cents) on line 44800 of your return: amount from line 49 entered as a
    # positive amount multiplied by 50% =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/cpp_part_5_line_50_rate"},
        consumes={"base": "ca/cpp_part_5_line_50_line_49_positive"},
        produces={"output": "ca/cpp_part_5_line_50"},
    ),
    # Schedule 8 Part 5 line 51 "If line 16 of Part 3 is positive or "0", enter the amount from
    # line 11 of Part 3 at lines 51 and 57, and continue at line 58. If not, enter the amount
    # from line 9 of Part 3 and continue at line 52.": line 11 (the required base contributions)
    # when line 16 is not negative, else line 9 (the actual base contributions), as Part 3b line
    # 30.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_16_not_negative",
            "when_none": "ca/cpp_actual_base_contributions",
            "when_any": "ca/cpp_base_contributions",
        },
        produces={"output": "ca/cpp_part_5_line_51"},
    ),
    # Schedule 8 Part 5 line 52 "If line 16 of Part 3 is negative: Enter the amount from line 16
    # of Part 3 as a positive amount.": "0" less line 16 of Part 3, not below zero (0 when line
    # 16 is positive or "0"), as Part 3b line 31.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_zero", "less": "ca/cpp_base_contributions_difference"},
        produces={"output": "ca/cpp_part_5_line_52"},
    ),
    # Schedule 8 Part 5 line 53 "If line 16 of Part 3 is negative and line 19 of Part 3 is
    # positive, enter whichever is less: amount from line 19 of Part 3 or line 52.": the lesser
    # of the two, a candidate that line 53 takes only when line 16 is negative and line 19
    # positive, as Part 3b line 32.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/cpp_first_additional_contributions_difference", "ca/cpp_part_5_line_52")
        },
        produces={"output": "ca/cpp_part_5_line_53_lesser"},
    ),
    # Schedule 8 Part 5 line 53 "If not, enter "0".": the lesser when line 16 of Part 3 is
    # negative and line 19 of Part 3 is positive, else "0".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_16_negative_line_19_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_5_line_53_lesser",
        },
        produces={"output": "ca/cpp_part_5_line_53"},
    ),
    # Schedule 8 Part 5 line 54 "Line 52 minus line 53 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_52", "less": "ca/cpp_part_5_line_53"},
        produces={"output": "ca/cpp_part_5_line_54"},
    ),
    # Schedule 8 Part 5 line 55 "Line 51 plus line 53 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_51", "ca/cpp_part_5_line_53")},
        produces={"output": "ca/cpp_part_5_line_55"},
    ),
    # Schedule 8 Part 5 line 56 "If line 23 of Part 3 and line 54 are both positive, enter
    # whichever is less. If not, enter "0".": counts 1 when line 23 of Part 3 and line 54 are
    # both more than 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_part_5_line_23_and_line_54_positive_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/cpp_second_additional_contributions_difference",
                "ca/cpp_part_5_line_54",
            ),
        },
        produces={"output": "ca/cpp_part_5_line_23_and_line_54_positive"},
    ),
    # Schedule 8 Part 5 line 56 "enter whichever is less": the lesser of line 23 of Part 3 and
    # line 54, a candidate that line 56 takes only when both are positive.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cpp_second_additional_contributions_difference",
                "ca/cpp_part_5_line_54",
            )
        },
        produces={"output": "ca/cpp_part_5_line_56_lesser"},
    ),
    # Schedule 8 Part 5 line 56 "If not, enter "0".": the lesser when line 23 of Part 3 and line
    # 54 are both positive, else "0".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_part_5_line_23_and_line_54_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_5_line_56_lesser",
        },
        produces={"output": "ca/cpp_part_5_line_56"},
    ),
    # Schedule 8 Part 5 line 57 "Base CPP contributions through employment income: Line 55 plus
    # line 56 Enter this amount (in dollars and cents) on line 30800 of your return. =": the Part 5
    # amount that the T1 line 30800 choice takes when Part 5 is completed.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_55", "ca/cpp_part_5_line_56")},
        produces={"output": "ca/cpp_part_5_line_57"},
    ),
    # Schedule 8 Part 5 line 58 "If line 19 of Part 3 is positive or "0", enter the amount from
    # line 12 of Part 3 at line 58 and line 64, and continue at line 65. If not, enter the
    # amount from line 10 of Part 3 and continue at line 59.": line 12 (the required first
    # additional contributions) when line 19 is not negative, else line 10 (the actual first
    # additional contributions).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_19_not_negative",
            "when_none": "ca/cpp_actual_first_additional_contributions",
            "when_any": "ca/cpp_first_additional_contributions",
        },
        produces={"output": "ca/cpp_part_5_line_58"},
    ),
    # Schedule 8 Part 5 line 59 "If line 19 of Part 3 is negative: Enter the amount from line 19
    # of Part 3 as a positive amount.": "0" less line 19 of Part 3, not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_zero",
            "less": "ca/cpp_first_additional_contributions_difference",
        },
        produces={"output": "ca/cpp_part_5_line_59"},
    ),
    # Schedule 8 Part 5 line 60 "If line 16 of Part 3 is positive, enter whichever is less:
    # amount from line 16 of Part 3 or line 59.": the lesser of the two, a candidate that line
    # 60 takes only when line 16 is positive.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/cpp_base_contributions_difference", "ca/cpp_part_5_line_59")},
        produces={"output": "ca/cpp_part_5_line_60_lesser"},
    ),
    # Schedule 8 Part 5 line 60 "If not, enter "0".": the lesser when line 16 of Part 3 is
    # positive, else "0".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_16_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_5_line_60_lesser",
        },
        produces={"output": "ca/cpp_part_5_line_60"},
    ),
    # Schedule 8 Part 5 line 61 "Line 59 minus line 60 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_59", "less": "ca/cpp_part_5_line_60"},
        produces={"output": "ca/cpp_part_5_line_61"},
    ),
    # Schedule 8 Part 5 line 62 "Line 58 plus line 60 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_58", "ca/cpp_part_5_line_60")},
        produces={"output": "ca/cpp_part_5_line_62"},
    ),
    # Schedule 8 Part 5 line 63 "the result of line 23 of Part 3 minus line 56": line 23 less
    # line 56, signed, the comparison amount of the line 63 candidate.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_second_additional_contributions_difference",
            "less": "ca/cpp_part_5_line_56",
        },
        produces={"output": "ca/cpp_part_5_line_23_less_line_56"},
    ),
    # Schedule 8 Part 5 line 63 "If line 23 of Part 3 and line 61 are both positive, enter
    # whichever is less": counts 1 when line 23 of Part 3 and line 61 are both more than 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_part_5_line_23_and_line_61_positive_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/cpp_second_additional_contributions_difference",
                "ca/cpp_part_5_line_61",
            ),
        },
        produces={"output": "ca/cpp_part_5_line_23_and_line_61_positive"},
    ),
    # Schedule 8 Part 5 line 63 "amount from line 61 or the result of line 23 of Part 3 minus
    # line 56": the lesser of the two, a candidate that line 63 takes only when both are
    # positive.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/cpp_part_5_line_61", "ca/cpp_part_5_line_23_less_line_56")},
        produces={"output": "ca/cpp_part_5_line_63_lesser"},
    ),
    # Schedule 8 Part 5 line 63 "If not, enter "0".": the lesser when line 23 of Part 3 and line
    # 61 are both positive, else "0".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_part_5_line_23_and_line_61_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_5_line_63_lesser",
        },
        produces={"output": "ca/cpp_part_5_line_63"},
    ),
    # Schedule 8 Part 5 line 64 "Line 62 plus line 63 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_62", "ca/cpp_part_5_line_63")},
        produces={"output": "ca/cpp_part_5_line_64"},
    ),
    # Schedule 8 Part 5 line 65 "If line 23 of Part 3 is positive or "0", enter the amount from
    # line 22 of Part 3 on line 65 and line 68, and continue at line 69. If not, enter the
    # amount from line 21 of Part 3 and continue at line 66.": line 22 (the required second
    # additional contributions) when line 23 is not negative, else line 21 (the T4 box 16A
    # total).
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_23_not_negative",
            "when_none": "ca/cpp_t4_second_additional_contributions",
            "when_any": "ca/cpp_second_additional_contributions",
        },
        produces={"output": "ca/cpp_part_5_line_65"},
    ),
    # Schedule 8 Part 5 line 66 "If line 23 of Part 3 is negative: Enter the amount from line 23
    # of Part 3 as a positive amount.": "0" less line 23 of Part 3, not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_zero",
            "less": "ca/cpp_second_additional_contributions_difference",
        },
        produces={"output": "ca/cpp_part_5_line_66"},
    ),
    # Schedule 8 Part 5 line 67 "If line 20 of Part 3 is positive, enter whichever is less:
    # amount from line 20 of Part 3 or line 66.": the lesser of the two, a candidate that line
    # 67 takes only when line 20 is positive.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cpp_base_and_first_additional_contributions_difference",
                "ca/cpp_part_5_line_66",
            )
        },
        produces={"output": "ca/cpp_part_5_line_67_lesser"},
    ),
    # Schedule 8 Part 5 line 67 "If not, enter "0".": the lesser when line 20 of Part 3 is
    # positive, else "0".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_20_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_5_line_67_lesser",
        },
        produces={"output": "ca/cpp_part_5_line_67"},
    ),
    # Schedule 8 Part 5 line 68 "Line 65 plus line 67 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_65", "ca/cpp_part_5_line_67")},
        produces={"output": "ca/cpp_part_5_line_68"},
    ),
    # Schedule 8 Part 5 line 69 "Deduction for CPP enhanced contributions on employment income:
    # Line 64 plus line 68 Enter this amount (in dollars and cents) on line 22215 of your
    # return. =": the Part 5 amount that the T1 line 22215 choice takes when Part 5 is completed.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_64", "ca/cpp_part_5_line_68")},
        produces={"output": "ca/cpp_part_5_line_69"},
    ),
}

FORM_WIRING = {
    (
        TieredContribution,
        frozenset({CPP_PART_5_LINE_30}),
        frozenset({CPP_PART_5_LINE_43}),
    ),
    (
        TieredContribution,
        frozenset({CPP_PART_5_LINE_30}),
        frozenset({CPP_PART_5_LINE_44}),
    ),
    (
        TieredContribution,
        frozenset({CPP_PART_5_LINE_42}),
        frozenset({CPP_PART_5_LINE_45}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_44, CPP_PART_5_LINE_45}),
        frozenset({CPP_PART_5_LINE_46}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_43, CPP_PART_5_LINE_46}),
        frozenset({CPP_PART_5_LINE_47}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_CONTRIBUTIONS_DIFFERENCE, CPP_ZERO}),
        frozenset({CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE}),
    ),
    (
        ApplyFraction,
        frozenset({CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE}),
        frozenset({CPP_PART_5_LINE_48}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_47, CPP_PART_5_LINE_48}),
        frozenset({CPP_PART_5_LINE_49}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_PART_5_LINE_49}),
        frozenset({CPP_PART_5_LINE_50_LINE_49_POSITIVE}),
    ),
    (
        ApplyRate,
        frozenset({CPP_PART_5_LINE_50_LINE_49_POSITIVE}),
        frozenset({CPP_PART_5_LINE_50}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CPP_LINE_16_NOT_NEGATIVE, CPP_ACTUAL_BASE_CONTRIBUTIONS, CPP_BASE_CONTRIBUTIONS}
        ),
        frozenset({CPP_PART_5_LINE_51}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_BASE_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_5_LINE_52}),
    ),
    (
        LesserOf,
        frozenset({CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_52}),
        frozenset({CPP_PART_5_LINE_53_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE, CPP_ZERO, CPP_PART_5_LINE_53_LESSER}),
        frozenset({CPP_PART_5_LINE_53}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_52, CPP_PART_5_LINE_53}),
        frozenset({CPP_PART_5_LINE_54}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_51, CPP_PART_5_LINE_53}),
        frozenset({CPP_PART_5_LINE_55}),
    ),
    (
        CountByConditions,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_54}),
        frozenset({CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE}),
    ),
    (
        LesserOf,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_54}),
        frozenset({CPP_PART_5_LINE_56_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE, CPP_ZERO, CPP_PART_5_LINE_56_LESSER}),
        frozenset({CPP_PART_5_LINE_56}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_55, CPP_PART_5_LINE_56}),
        frozenset({CPP_PART_5_LINE_57}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CPP_LINE_19_NOT_NEGATIVE,
                CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS,
                CPP_FIRST_ADDITIONAL_CONTRIBUTIONS,
            }
        ),
        frozenset({CPP_PART_5_LINE_58}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_5_LINE_59}),
    ),
    (
        LesserOf,
        frozenset({CPP_BASE_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_59}),
        frozenset({CPP_PART_5_LINE_60_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_16_POSITIVE, CPP_ZERO, CPP_PART_5_LINE_60_LESSER}),
        frozenset({CPP_PART_5_LINE_60}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_59, CPP_PART_5_LINE_60}),
        frozenset({CPP_PART_5_LINE_61}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_58, CPP_PART_5_LINE_60}),
        frozenset({CPP_PART_5_LINE_62}),
    ),
    (
        Subtract,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_56}),
        frozenset({CPP_PART_5_LINE_23_LESS_LINE_56}),
    ),
    (
        CountByConditions,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_61}),
        frozenset({CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE}),
    ),
    (
        LesserOf,
        frozenset({CPP_PART_5_LINE_61, CPP_PART_5_LINE_23_LESS_LINE_56}),
        frozenset({CPP_PART_5_LINE_63_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE, CPP_ZERO, CPP_PART_5_LINE_63_LESSER}),
        frozenset({CPP_PART_5_LINE_63}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_62, CPP_PART_5_LINE_63}),
        frozenset({CPP_PART_5_LINE_64}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                CPP_LINE_23_NOT_NEGATIVE,
                CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS,
                CPP_SECOND_ADDITIONAL_CONTRIBUTIONS,
            }
        ),
        frozenset({CPP_PART_5_LINE_65}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_5_LINE_66}),
    ),
    (
        LesserOf,
        frozenset({CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_66}),
        frozenset({CPP_PART_5_LINE_67_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_20_POSITIVE, CPP_ZERO, CPP_PART_5_LINE_67_LESSER}),
        frozenset({CPP_PART_5_LINE_67}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_65, CPP_PART_5_LINE_67}),
        frozenset({CPP_PART_5_LINE_68}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_64, CPP_PART_5_LINE_68}),
        frozenset({CPP_PART_5_LINE_69}),
    ),
}
