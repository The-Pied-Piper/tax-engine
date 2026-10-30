"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`).

Schedule 8 Part 5 lines 1 to 42, "Contributions on self-employment income and other earnings when
you also have employment income", and Part 3 line 2. The copy lines (Part 5 lines 5, 11, 17, 18,
23, 24, 26, 27, 31, 34, 37, 38 and 40) are steps of no capability: each reads the kind it copies.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.divided_by_rate import DividedByRate
from tax_engine.jurisdictions.ca.catalog import (
    CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASIC_EXEMPTION,
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_PART_3_LINE_2,
    CPP_PART_5_LINE_4,
    CPP_PART_5_LINE_6,
    CPP_PART_5_LINE_7,
    CPP_PART_5_LINE_8,
    CPP_PART_5_LINE_9,
    CPP_PART_5_LINE_9_LESSER,
    CPP_PART_5_LINE_10,
    CPP_PART_5_LINE_12,
    CPP_PART_5_LINE_13,
    CPP_PART_5_LINE_14,
    CPP_PART_5_LINE_15,
    CPP_PART_5_LINE_15_LESSER,
    CPP_PART_5_LINE_16,
    CPP_PART_5_LINE_19,
    CPP_PART_5_LINE_20,
    CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE,
    CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE,
    CPP_PART_5_LINE_21,
    CPP_PART_5_LINE_22,
    CPP_PART_5_LINE_25,
    CPP_PART_5_LINE_28,
    CPP_PART_5_LINE_29,
    CPP_PART_5_LINE_30,
    CPP_PART_5_LINE_33,
    CPP_PART_5_LINE_33_MORE_THAN_LINE_17,
    CPP_PART_5_LINE_35,
    CPP_PART_5_LINE_36,
    CPP_PART_5_LINE_39,
    CPP_PART_5_LINE_41,
    CPP_PART_5_LINE_42,
    CPP_PART_5_LINE_42_LESSER,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
    CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPP_ZERO,
    CPT20_EARNINGS,
    CPT20_T4_EARNINGS,
    PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS,
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
)

INPUTS = frozenset({"ca/cpt20_t4_earnings"})

# Part 5 line 30 and line 42: nothing on the return reads them yet (the lines that route them to
# lines 30800, 22215, 31000, 22200, 42100 and 44800 follow), so they are declared outputs.
OUTPUTS = frozenset[str]()

FORM_STEPS = {
    # Schedule 8 Part 3 line 2 "Enter whichever is less: amount from line D of Part 2 or line
    # 1.": line 1 is the employment income. Part 5 line 32 is "Amount from line 2 of Part 3".
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cpp_additional_maximum_pensionable_earnings",
                "ca/t4_cpp_pensionable_earnings_outside_quebec",
            )
        },
        produces={"output": "ca/cpp_part_3_line_2"},
    ),
    # Schedule 8 Part 5 line 1 "amount from line 12200 of your return plus line 27 of your
    # return" (the pensionable net self-employment earnings, as Part 4 line 1), line 2 and line
    # 50373 "Employment earnings not shown on a T4 slip that you are electing to pay additional
    # CPP contributions on (complete Form CPT20)", line 3 and line 50399 "Employment earnings
    # shown on a T4 slip that you are electing to pay additional CPP contributions on (complete
    # Form CPT20)" and line 4 "Add lines 1 to 3.": no floor is printed, so a loss on line 1
    # stays negative.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/pensionable_net_self_employment_earnings",
                "ca/cpt20_earnings",
                "ca/cpt20_t4_earnings",
            )
        },
        produces={"output": "ca/cpp_part_5_line_4"},
    ),
    # Schedule 8 Part 5 line 6 "Enter the amount from line 20 of Part 3 if positive. If not,
    # enter "0".": line 20 of Part 3 less "0", not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_base_and_first_additional_contributions_difference",
            "less": "ca/cpp_zero",
        },
        produces={"output": "ca/cpp_part_5_line_6"},
    ),
    # Schedule 8 Part 5 line 5 "Total actual base and first additional contributions from line 8
    # of Part 3" and line 7 "Line 5 minus line 6 =": line 5 is the T4 box 16 total.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_t4_base_and_first_additional_contributions",
            "less": "ca/cpp_part_5_line_6",
        },
        produces={"output": "ca/cpp_part_5_line_7"},
    ),
    # Schedule 8 Part 5 line 8 "Enter the amount from line 20 of Part 3 as a positive amount.":
    # "0" less line 20 of Part 3, not below zero (0 when line 20 is not negative).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_zero",
            "less": "ca/cpp_base_and_first_additional_contributions_difference",
        },
        produces={"output": "ca/cpp_part_5_line_8"},
    ),
    # Schedule 8 Part 5 "If the amount from line 20 of Part 3 is negative and line 23 of Part 3
    # is positive, complete lines 8 and 9. If not, enter "0" on line 9 and continue at line
    # 10.": counts 1 when line 8 (line 20 as a positive amount) and line 23 of Part 3 are both
    # more than 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_part_5_line_20_negative_line_23_positive_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/cpp_part_5_line_8",
                "ca/cpp_second_additional_contributions_difference",
            ),
        },
        produces={"output": "ca/cpp_part_5_line_20_negative_line_23_positive"},
    ),
    # Schedule 8 Part 5 line 9 "Enter whichever is less: amount from line 23 of Part 3 or line
    # 8.": the lesser of the two, a candidate that line 9 takes only when the count applies.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/cpp_second_additional_contributions_difference", "ca/cpp_part_5_line_8")
        },
        produces={"output": "ca/cpp_part_5_line_9_lesser"},
    ),
    # Schedule 8 Part 5 line 9 "If not, enter "0" on line 9": the lesser when lines 8 and 9 are
    # completed, else "0".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_part_5_line_20_negative_line_23_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_5_line_9_lesser",
        },
        produces={"output": "ca/cpp_part_5_line_9"},
    ),
    # Schedule 8 Part 5 line 10 "Line 7 plus line 9 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_7", "ca/cpp_part_5_line_9")},
        produces={"output": "ca/cpp_part_5_line_10"},
    ),
    # Schedule 8 Part 5 line 12 "Enter the amount from line 23 of Part 3 if positive. If not,
    # enter "0".": line 23 of Part 3 less "0", not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_second_additional_contributions_difference",
            "less": "ca/cpp_zero",
        },
        produces={"output": "ca/cpp_part_5_line_12"},
    ),
    # Schedule 8 Part 5 line 11 "Total actual second additional contributions from line 21 of
    # Part 3" and line 13 "Line 11 minus line 12 =": line 11 is the T4 box 16A total.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_t4_second_additional_contributions",
            "less": "ca/cpp_part_5_line_12",
        },
        produces={"output": "ca/cpp_part_5_line_13"},
    ),
    # Schedule 8 Part 5 line 14 "Enter the amount from line 23 of Part 3 as a positive amount.":
    # "0" less line 23 of Part 3, not below zero (0 when line 23 is not negative).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_zero",
            "less": "ca/cpp_second_additional_contributions_difference",
        },
        produces={"output": "ca/cpp_part_5_line_14"},
    ),
    # Schedule 8 Part 5 "If the amount from line 20 of Part 3 is positive and line 23 of Part 3
    # is negative, complete lines 14 and 15. If not, enter "0" on line 15 and continue at line
    # 16.": counts 1 when line 20 of Part 3 and line 14 (line 23 as a positive amount) are both
    # more than 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_part_5_line_20_positive_line_23_negative_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/cpp_base_and_first_additional_contributions_difference",
                "ca/cpp_part_5_line_14",
            ),
        },
        produces={"output": "ca/cpp_part_5_line_20_positive_line_23_negative"},
    ),
    # Schedule 8 Part 5 line 15 "Enter whichever is less: amount from line 20 of Part 3 or line
    # 14.": the lesser of the two, a candidate that line 15 takes only when the count applies.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cpp_base_and_first_additional_contributions_difference",
                "ca/cpp_part_5_line_14",
            )
        },
        produces={"output": "ca/cpp_part_5_line_15_lesser"},
    ),
    # Schedule 8 Part 5 line 15 "If not, enter "0" on line 15": the lesser when lines 14 and 15
    # are completed, else "0".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_part_5_line_20_positive_line_23_negative",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_5_line_15_lesser",
        },
        produces={"output": "ca/cpp_part_5_line_15"},
    ),
    # Schedule 8 Part 5 line 16 "Line 13 plus line 15 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_13", "ca/cpp_part_5_line_15")},
        produces={"output": "ca/cpp_part_5_line_16"},
    ),
    # Schedule 8 Part 5 line 17 "Amount from line B of Part 2", line 18 "Amount from line E of
    # Part 2" and line 19 "Line 17 minus line 18 (if negative, enter "0") (maximum $67,800) =":
    # the maximum pensionable earnings less the basic exemption, which is the $67,800 for a full
    # year.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_maximum_pensionable_earnings",
            "less": "ca/cpp_basic_exemption",
        },
        produces={"output": "ca/cpp_part_5_line_19"},
    ),
    # Schedule 8 Part 5 line 20 "Amount from line 10 multiplied by 16.80672 =": 16.80672 is more
    # than 1, so it is a fraction dataset, not a rate.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/cpp_part_5_line_20_multiplier"},
        consumes={"base": "ca/cpp_part_5_line_10"},
        produces={"output": "ca/cpp_part_5_line_20"},
    ),
    # Schedule 8 Part 5 line 21 "Line 19 minus line 20 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_19", "less": "ca/cpp_part_5_line_20"},
        produces={"output": "ca/cpp_part_5_line_21"},
    ),
    # Schedule 8 Part 5 line 22 "Enter whichever is less: amount from line 4 or line 21."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/cpp_part_5_line_4", "ca/cpp_part_5_line_21")},
        produces={"output": "ca/cpp_part_5_line_22"},
    ),
    # Schedule 8 Part 5 line 23 "Amount from line 18", line 24 "Amount from line 1 of Part 3"
    # (the employment income) and line 25 "Line 23 minus line 24 (if negative, enter "0" on
    # lines 25 and 29, and continue at line 30) =": the exemption less the employment income,
    # not below zero. The form's "If the amount from line 1 of Part 3 is less than line 18,
    # complete lines 23 to 29. If not, enter "0" on line 29" holds without a count: line 25 is 0
    # otherwise, so line 29 is.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_basic_exemption",
            "less": "ca/t4_cpp_pensionable_earnings_outside_quebec",
        },
        produces={"output": "ca/cpp_part_5_line_25"},
    ),
    # Schedule 8 Part 5 line 26 "Amount from line 4", line 27 "Amount from line 19" and line 28
    # "Line 26 minus line 27 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_4", "less": "ca/cpp_part_5_line_19"},
        produces={"output": "ca/cpp_part_5_line_28"},
    ),
    # Schedule 8 Part 5 line 29 "Line 25 minus line 28 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_25", "less": "ca/cpp_part_5_line_28"},
        produces={"output": "ca/cpp_part_5_line_29"},
    ),
    # Schedule 8 Part 5 line 30 "Self-employment income and other earnings subject to base and
    # first additional contributions: Line 22 minus line 29 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_22", "less": "ca/cpp_part_5_line_29"},
        produces={"output": "ca/cpp_part_5_line_30"},
    ),
    # Schedule 8 Part 5 line 31 "Amount from line 4", line 32 "Amount from line 2 of Part 3" and
    # line 33 "Line 31 plus line 32 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_4", "ca/cpp_part_3_line_2")},
        produces={"output": "ca/cpp_part_5_line_33"},
    ),
    # Schedule 8 Part 5 "If the amount from line 33 is more than line 17, complete lines 34 to
    # 42. If not, enter "0" on line 42 and continue at line 43.": counts 1 when line 33 is more
    # than line 17.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_part_5_line_33_more_than_line_17_conditions"},
        consumes={
            "counts": (),
            "amounts": ("ca/cpp_part_5_line_33", "ca/cpp_maximum_pensionable_earnings"),
        },
        produces={"output": "ca/cpp_part_5_line_33_more_than_line_17"},
    ),
    # Schedule 8 Part 5 line 35 "Amount from line 16 divided by 4% =".
    CapabilitySelection(
        name="ca/divided_by_rate",
        params={"rate": "ca/cpp_part_5_line_35_rate"},
        consumes={"dividend": "ca/cpp_part_5_line_16"},
        produces={"output": "ca/cpp_part_5_line_35"},
    ),
    # Schedule 8 Part 5 line 34 "Amount from line C of Part 2" and line 36 "Line 34 minus line
    # 35 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_second_additional_earnings_maximum",
            "less": "ca/cpp_part_5_line_35",
        },
        produces={"output": "ca/cpp_part_5_line_36"},
    ),
    # Schedule 8 Part 5 line 37 "Amount from line 4", line 38 "Amount from line 25 (if any)" and
    # line 39 "Line 37 minus line 38 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_4", "less": "ca/cpp_part_5_line_25"},
        produces={"output": "ca/cpp_part_5_line_39"},
    ),
    # Schedule 8 Part 5 line 40 "Amount from line 30" and line 41 "Line 39 minus line 40 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_39", "less": "ca/cpp_part_5_line_30"},
        produces={"output": "ca/cpp_part_5_line_41"},
    ),
    # Schedule 8 Part 5 line 42 "Enter whichever is less: amount from line 36 or line 41.": the
    # lesser of the two, a candidate that line 42 takes only when the count of line 33 more than
    # line 17 applies.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/cpp_part_5_line_36", "ca/cpp_part_5_line_41")},
        produces={"output": "ca/cpp_part_5_line_42_lesser"},
    ),
    # Schedule 8 Part 5 line 42 "Self-employment income and other earnings subject to second
    # additional contributions" and "If not, enter "0" on line 42": the lesser when line 33 is
    # more than line 17, else "0".
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_part_5_line_33_more_than_line_17",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_5_line_42_lesser",
        },
        produces={"output": "ca/cpp_part_5_line_42"},
    ),
}

FORM_WIRING = {
    (
        LesserOf,
        frozenset(
            {
                CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
                T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
            }
        ),
        frozenset({CPP_PART_3_LINE_2}),
    ),
    (
        Sum,
        frozenset({PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS, CPT20_EARNINGS, CPT20_T4_EARNINGS}),
        frozenset({CPP_PART_5_LINE_4}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_ZERO}),
        frozenset({CPP_PART_5_LINE_6}),
    ),
    (
        Subtract,
        frozenset({CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS, CPP_PART_5_LINE_6}),
        frozenset({CPP_PART_5_LINE_7}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_5_LINE_8}),
    ),
    (
        CountByConditions,
        frozenset({CPP_PART_5_LINE_8, CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE}),
    ),
    (
        LesserOf,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_8}),
        frozenset({CPP_PART_5_LINE_9_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE, CPP_ZERO, CPP_PART_5_LINE_9_LESSER}
        ),
        frozenset({CPP_PART_5_LINE_9}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_7, CPP_PART_5_LINE_9}),
        frozenset({CPP_PART_5_LINE_10}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_ZERO}),
        frozenset({CPP_PART_5_LINE_12}),
    ),
    (
        Subtract,
        frozenset({CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS, CPP_PART_5_LINE_12}),
        frozenset({CPP_PART_5_LINE_13}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_5_LINE_14}),
    ),
    (
        CountByConditions,
        frozenset({CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_14}),
        frozenset({CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE}),
    ),
    (
        LesserOf,
        frozenset({CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_5_LINE_14}),
        frozenset({CPP_PART_5_LINE_15_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE, CPP_ZERO, CPP_PART_5_LINE_15_LESSER}
        ),
        frozenset({CPP_PART_5_LINE_15}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_13, CPP_PART_5_LINE_15}),
        frozenset({CPP_PART_5_LINE_16}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_MAXIMUM_PENSIONABLE_EARNINGS, CPP_BASIC_EXEMPTION}),
        frozenset({CPP_PART_5_LINE_19}),
    ),
    (
        ApplyFraction,
        frozenset({CPP_PART_5_LINE_10}),
        frozenset({CPP_PART_5_LINE_20}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_PART_5_LINE_19, CPP_PART_5_LINE_20}),
        frozenset({CPP_PART_5_LINE_21}),
    ),
    (
        LesserOf,
        frozenset({CPP_PART_5_LINE_4, CPP_PART_5_LINE_21}),
        frozenset({CPP_PART_5_LINE_22}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_BASIC_EXEMPTION, T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC}),
        frozenset({CPP_PART_5_LINE_25}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_PART_5_LINE_4, CPP_PART_5_LINE_19}),
        frozenset({CPP_PART_5_LINE_28}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_PART_5_LINE_25, CPP_PART_5_LINE_28}),
        frozenset({CPP_PART_5_LINE_29}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_PART_5_LINE_22, CPP_PART_5_LINE_29}),
        frozenset({CPP_PART_5_LINE_30}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_4, CPP_PART_3_LINE_2}),
        frozenset({CPP_PART_5_LINE_33}),
    ),
    (
        CountByConditions,
        frozenset({CPP_PART_5_LINE_33, CPP_MAXIMUM_PENSIONABLE_EARNINGS}),
        frozenset({CPP_PART_5_LINE_33_MORE_THAN_LINE_17}),
    ),
    (
        DividedByRate,
        frozenset({CPP_PART_5_LINE_16}),
        frozenset({CPP_PART_5_LINE_35}),
    ),
    (
        Subtract,
        frozenset({CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM, CPP_PART_5_LINE_35}),
        frozenset({CPP_PART_5_LINE_36}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_4, CPP_PART_5_LINE_25}),
        frozenset({CPP_PART_5_LINE_39}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_39, CPP_PART_5_LINE_30}),
        frozenset({CPP_PART_5_LINE_41}),
    ),
    (
        LesserOf,
        frozenset({CPP_PART_5_LINE_36, CPP_PART_5_LINE_41}),
        frozenset({CPP_PART_5_LINE_42_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_PART_5_LINE_33_MORE_THAN_LINE_17, CPP_ZERO, CPP_PART_5_LINE_42_LESSER}),
        frozenset({CPP_PART_5_LINE_42}),
    ),
}
