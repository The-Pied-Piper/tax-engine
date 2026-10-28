"""The CA-ON manifest entries of Form Schedule 8 (see `test_manifest.py` and
`test_manifest_schedule_8.py`).

Schedule 8, the Canada Pension Plan contributions and overpayment, is a form of the manifest: its
Part 3, Part 3a, Part 3b and Part 5 selections belong to the form `ca/schedule_8` (`FORM_STEPS`
here and in the three Part 5 modules), run once for the one copy of the form the return carries
(none, with an empty `ca/schedule_8_instances`). Part 4 stays in the return. The record has no
fields: every figure the form reads is a starting amount of the return, or a total of another
form's export. The form exports the lines the return reads, which it totals over the copies
(`STEPS` and `WIRING`, 0 with no copy), and the line 13 of Part 3 that nothing reads.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.amount_by_count import AmountForCount
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.contribution_tier import TieredContribution
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    COMMISSION_INCOME,
    CPP_ACTUAL_BASE_CONTRIBUTIONS,
    CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASE_CONTRIBUTIONS,
    CPP_BASE_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASIC_EXEMPTION,
    CPP_CONTRIBUTIONS_DIFFERENCE,
    CPP_ENHANCED_CONTRIBUTIONS,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE,
    CPP_LINE_16_NOT_NEGATIVE,
    CPP_LINE_16_POSITIVE,
    CPP_LINE_19_NOT_NEGATIVE,
    CPP_LINE_20_POSITIVE,
    CPP_LINE_23_AND_LINE_33_POSITIVE,
    CPP_LINE_23_AND_LINE_40_POSITIVE,
    CPP_LINE_23_NOT_NEGATIVE,
    CPP_LINE_24_POSITIVE,
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_MONTHS,
    CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_PART_3_OVERPAYMENT,
    CPP_PART_3B_LINE_23_LESS_LINE_35,
    CPP_PART_3B_LINE_30,
    CPP_PART_3B_LINE_31,
    CPP_PART_3B_LINE_32,
    CPP_PART_3B_LINE_32_LESSER,
    CPP_PART_3B_LINE_33,
    CPP_PART_3B_LINE_34,
    CPP_PART_3B_LINE_35,
    CPP_PART_3B_LINE_35_LESSER,
    CPP_PART_3B_LINE_36,
    CPP_PART_3B_LINE_37,
    CPP_PART_3B_LINE_38,
    CPP_PART_3B_LINE_39,
    CPP_PART_3B_LINE_39_LESSER,
    CPP_PART_3B_LINE_40,
    CPP_PART_3B_LINE_41,
    CPP_PART_3B_LINE_42,
    CPP_PART_3B_LINE_42_LESSER,
    CPP_PART_3B_LINE_43,
    CPP_PART_3B_LINE_44,
    CPP_PART_3B_LINE_45,
    CPP_PART_3B_LINE_46,
    CPP_PART_3B_LINE_46_LESSER,
    CPP_PART_3B_LINE_47,
    CPP_PART_3B_LINE_48,
    CPP_PART_5_COMPLETED,
    CPP_PART_5_LINE_49,
    CPP_PART_5_LINE_50,
    CPP_PART_5_LINE_57,
    CPP_PART_5_LINE_69,
    CPP_PART_5_LINE_70,
    CPP_PART_5_LINE_88,
    CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
    CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPP_ZERO,
    FARMING_INCOME,
    FISHING_INCOME,
    NET_PARTNERSHIP_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS,
    PROFESSIONAL_INCOME,
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_OVERPAYMENT,
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
)
from tests.jurisdictions.ca_on.manifest_families.t1139 import (
    BUSINESS_INCOME_ON_RETURN_LINES,
    COMMISSION_INCOME_ON_RETURN_LINES,
    FARMING_INCOME_ON_RETURN_LINES,
    FISHING_INCOME_ON_RETURN_LINES,
    PROFESSIONAL_INCOME_ON_RETURN_LINES,
)

BUSINESS_INCOME_PER_STATEMENT = BUSINESS_INCOME_ON_RETURN_LINES
PROFESSIONAL_INCOME_PER_STATEMENT = PROFESSIONAL_INCOME_ON_RETURN_LINES
COMMISSION_INCOME_PER_STATEMENT = COMMISSION_INCOME_ON_RETURN_LINES
FARMING_INCOME_PER_STATEMENT = FARMING_INCOME_ON_RETURN_LINES
FISHING_INCOME_PER_STATEMENT = FISHING_INCOME_ON_RETURN_LINES

INPUTS = frozenset({"ca/schedule_8_instances"})

FORM_EXPORTS = (
    "ca/schedule_8_cpp_base_contributions_on_return",
    "ca/schedule_8_cpp_enhanced_contributions_on_return",
    "ca/schedule_8_cpp_overpayment",
    "ca/cpp_part_5_line_49",
    "ca/cpp_part_5_line_70",
    "ca/cpp_part_5_line_88",
    "ca/cpp_zero",
    "ca/cpp_required_base_and_first_additional_contributions",
)

# The form's exports nothing on the return reads (line 13 of Part 3) are no declared outputs.
OUTPUTS = frozenset[str]()

SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN_PER_INSTANCE = RecordListKind(
    "ca/schedule_8.schedule_8_cpp_base_contributions_on_return",
    fields=(SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,),
)
SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN_PER_INSTANCE = RecordListKind(
    "ca/schedule_8.schedule_8_cpp_enhanced_contributions_on_return",
    fields=(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,),
)
SCHEDULE_8_CPP_OVERPAYMENT_PER_INSTANCE = RecordListKind(
    "ca/schedule_8.schedule_8_cpp_overpayment", fields=(SCHEDULE_8_CPP_OVERPAYMENT,)
)
CPP_PART_5_LINE_49_PER_INSTANCE = RecordListKind(
    "ca/schedule_8.cpp_part_5_line_49", fields=(CPP_PART_5_LINE_49,)
)
CPP_PART_5_LINE_70_PER_INSTANCE = RecordListKind(
    "ca/schedule_8.cpp_part_5_line_70", fields=(CPP_PART_5_LINE_70,)
)
CPP_PART_5_LINE_88_PER_INSTANCE = RecordListKind(
    "ca/schedule_8.cpp_part_5_line_88", fields=(CPP_PART_5_LINE_88,)
)
CPP_ZERO_PER_INSTANCE = RecordListKind("ca/schedule_8.cpp_zero", fields=(CPP_ZERO,))

# The return's totals of the form's lines.
STEPS = {
    # T1 line 30800 and ON428 line 58240, Schedule 8 Part 5 line 57 or the Part 3a or Part 3b
    # amount, for each Schedule 8 the return carries, added.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.schedule_8_cpp_base_contributions_on_return"},
        produces={"output": "ca/schedule_8_cpp_base_contributions_on_return"},
    ),
    # T1 line 22215, Schedule 8 Part 5 line 69 or the Part 3a or Part 3b amount, for each
    # Schedule 8 the return carries, added.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.schedule_8_cpp_enhanced_contributions_on_return"},
        produces={"output": "ca/schedule_8_cpp_enhanced_contributions_on_return"},
    ),
    # T1 line 44800, Schedule 8 Part 5 line 50 or the Part 3a line 29 amount, for each Schedule
    # 8 the return carries, added.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.schedule_8_cpp_overpayment"},
        produces={"output": "ca/schedule_8_cpp_overpayment"},
    ),
    # T1 line 42100, Schedule 8 Part 5 line 49, for each Schedule 8 the return carries, added.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.cpp_part_5_line_49"},
        produces={"output": "ca/cpp_part_5_line_49"},
    ),
    # T1 line 31000, Schedule 8 Part 5 line 70, for each Schedule 8 the return carries, added.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.cpp_part_5_line_70"},
        produces={"output": "ca/cpp_part_5_line_70"},
    ),
    # T1 line 22200, Schedule 8 Part 5 line 88, for each Schedule 8 the return carries, added.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.cpp_part_5_line_88"},
        produces={"output": "ca/cpp_part_5_line_88"},
    ),
    # the zero of Schedule 8 Part 3b and Part 3a, for each Schedule 8 the return carries, added.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.cpp_zero"},
        produces={"output": "ca/cpp_zero"},
    ),
}

WIRING = {
    (
        RecordTotal,
        frozenset({SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN_PER_INSTANCE}),
        frozenset({SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN}),
    ),
    (
        RecordTotal,
        frozenset({SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN_PER_INSTANCE}),
        frozenset({SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN}),
    ),
    (
        RecordTotal,
        frozenset({SCHEDULE_8_CPP_OVERPAYMENT_PER_INSTANCE}),
        frozenset({SCHEDULE_8_CPP_OVERPAYMENT}),
    ),
    (RecordTotal, frozenset({CPP_PART_5_LINE_49_PER_INSTANCE}), frozenset({CPP_PART_5_LINE_49})),
    (RecordTotal, frozenset({CPP_PART_5_LINE_70_PER_INSTANCE}), frozenset({CPP_PART_5_LINE_70})),
    (RecordTotal, frozenset({CPP_PART_5_LINE_88_PER_INSTANCE}), frozenset({CPP_PART_5_LINE_88})),
    (RecordTotal, frozenset({CPP_ZERO_PER_INSTANCE}), frozenset({CPP_ZERO})),
}

# The steps the form holds that were steps of the return: the contributions on employment income
# (Part 3 lines 11 and 12, Part 3a line 28) and the form's copies of the steps the return also needs
# (Part 2 lines B to E, Part 4 line 1 and the net self-employment income it adds), which the
# return keeps.
FORM_STEPS = {
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_first_additional_contribution"},
        consumes={"earnings": "ca/t4_cpp_pensionable_earnings_outside_quebec"},
        produces={"output": "ca/cpp_first_additional_contributions"},
    ),
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_second_additional_contribution"},
        consumes={"earnings": "ca/t4_cpp_pensionable_earnings_outside_quebec"},
        produces={"output": "ca/cpp_second_additional_contributions"},
    ),
    # Schedule 8 Part 3a line 28 "Line 26 plus line 27": the first and second additional
    # contributions together, the T1 line 22215 deduction.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cpp_first_additional_contributions",
                "ca/cpp_second_additional_contributions",
            )
        },
        produces={"output": "ca/cpp_enhanced_contributions"},
    ),
    # Schedule 8 Part 3 line 9 "amount from line 8 multiplied by 83.1933% =", the actual base
    # contributions, of the T4 box 16 total (line 8 and line 50340).
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/cpp_actual_base_share"},
        consumes={"base": "ca/cpp_t4_base_and_first_additional_contributions"},
        produces={"output": "ca/cpp_actual_base_contributions"},
    ),
    # Schedule 8 Part 3 line 10 "Line 8 minus line 9 =", the actual first additional contributions.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_t4_base_and_first_additional_contributions",
            "less": "ca/cpp_actual_base_contributions",
        },
        produces={"output": "ca/cpp_actual_first_additional_contributions"},
    ),
    # Schedule 8 Part 3 line 13 "Line 11 plus line 12 =", the required base and first additional
    # contributions.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cpp_base_contributions",
                "ca/cpp_first_additional_contributions",
            )
        },
        produces={"output": "ca/cpp_required_base_and_first_additional_contributions"},
    ),
    # Schedule 8 Part 3 line 16 "Line 14 minus line 15 (if negative, show in brackets) =", line 14
    # being line 9 and line 15 line 11.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_actual_base_contributions",
            "less": "ca/cpp_base_contributions",
        },
        produces={"output": "ca/cpp_base_contributions_difference"},
    ),
    # Schedule 8 Part 3 line 19 "Line 17 minus line 18 (if negative, show in brackets) =", line 17
    # being line 10 and line 18 line 12.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_actual_first_additional_contributions",
            "less": "ca/cpp_first_additional_contributions",
        },
        produces={"output": "ca/cpp_first_additional_contributions_difference"},
    ),
    # Schedule 8 Part 3 line 20 "Line 16 plus line 19 (if negative, show in brackets) =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cpp_base_contributions_difference",
                "ca/cpp_first_additional_contributions_difference",
            )
        },
        produces={"output": "ca/cpp_base_and_first_additional_contributions_difference"},
    ),
    # Schedule 8 Part 3 line 23 "Line 21 minus line 22 (if negative, show in brackets) =", line 21
    # being the T4 box 16A total (line 21 and line 50341) and line 22 the required second
    # additional contributions.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_t4_second_additional_contributions",
            "less": "ca/cpp_second_additional_contributions",
        },
        produces={"output": "ca/cpp_second_additional_contributions_difference"},
    ),
    # Schedule 8 Part 3 line 24 "Line 20 plus line 23 (if negative, show in brackets) =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cpp_base_and_first_additional_contributions_difference",
                "ca/cpp_second_additional_contributions_difference",
            )
        },
        produces={"output": "ca/cpp_contributions_difference"},
    ),
    # Schedule 8 Part 3b line 32 "If not, enter "0"" (and lines 35, 39, 42 and 46): the form's "0",
    # a dataset claimed whole, which is also the floor of the "as a positive amount" lines 31, 38
    # and 45 and the "0" of the routing on line 24.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/schedule_8_zero"},
        consumes={},
        produces={"output": "ca/cpp_zero"},
    ),
    # Schedule 8 Part 3 (continued) "If your earnings subject to contributions are from employment
    # income only and line 24 is:" "- positive, complete Part 3a below": a count of 1 when line 24
    # is positive, else 0 (the "0" and negative cases complete Part 3b).
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_24_positive_conditions"},
        consumes={"counts": (), "amounts": ("ca/cpp_contributions_difference",)},
        produces={"output": "ca/cpp_line_24_positive"},
    ),
    # Schedule 8 Part 3b line 30 "If line 16 is positive or "0", enter the amount from line 15 at
    # line 30 and line 36, and continue at line 37. If not, enter the amount from line 14 and
    # continue at line 31.": a count of 1 when line 16 is positive or "0".
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_16_not_negative_conditions"},
        consumes={"counts": (), "amounts": ("ca/cpp_base_contributions_difference",)},
        produces={"output": "ca/cpp_line_16_not_negative"},
    ),
    # Schedule 8 Part 3b, the instruction printed under the misprinted heading "Line 36" (it is line
    # 37) "If line 19 is positive or "0", enter the amount from line 18 at line 37 and line 43, and
    # continue at line 44. If not, enter the amount from line 17 and continue at line 38.": a count
    # of 1 when line 19 is positive or "0".
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_19_not_negative_conditions"},
        consumes={"counts": (), "amounts": ("ca/cpp_first_additional_contributions_difference",)},
        produces={"output": "ca/cpp_line_19_not_negative"},
    ),
    # Schedule 8 Part 3b line 44 "If line 23 is positive or "0", enter the amount from line 22 on
    # line 44 and line 47, and continue at line 48. If not, enter the amount from line 21 and
    # continue at line 45.": a count of 1 when line 23 is positive or "0".
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_23_not_negative_conditions"},
        consumes={"counts": (), "amounts": ("ca/cpp_second_additional_contributions_difference",)},
        produces={"output": "ca/cpp_line_23_not_negative"},
    ),
    # Schedule 8 Part 3b line 32 "If line 16 is negative and line 19 is positive, enter whichever is
    # less: amount from line 19 or line 31. If not, enter "0".": a count of 1 when line 16 is
    # negative (the line 30 count is 0) and line 19 is positive.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_16_negative_line_19_positive_conditions"},
        consumes={
            "counts": ("ca/cpp_line_16_not_negative",),
            "amounts": ("ca/cpp_first_additional_contributions_difference",),
        },
        produces={"output": "ca/cpp_line_16_negative_line_19_positive"},
    ),
    # Schedule 8 Part 3b line 35 "If line 23 and line 33 are both positive, enter whichever is less.
    # If not, enter "0".": a count of 1 when both are positive.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_23_and_line_33_positive_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/cpp_second_additional_contributions_difference",
                "ca/cpp_part_3b_line_33",
            ),
        },
        produces={"output": "ca/cpp_line_23_and_line_33_positive"},
    ),
    # Schedule 8 Part 3b line 39 "If line 16 is positive, enter whichever is less: amount from line
    # 16 or line 38. If not, enter "0".": a count of 1 when line 16 is positive.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_16_positive_conditions"},
        consumes={"counts": (), "amounts": ("ca/cpp_base_contributions_difference",)},
        produces={"output": "ca/cpp_line_16_positive"},
    ),
    # Schedule 8 Part 3b line 42 "If line 23 and line 40 are both positive, enter whichever is less:
    # amount from line 40 or the result of line 23 minus line 35. If not, enter "0".": a count of 1
    # when both are positive.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_23_and_line_40_positive_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/cpp_second_additional_contributions_difference",
                "ca/cpp_part_3b_line_40",
            ),
        },
        produces={"output": "ca/cpp_line_23_and_line_40_positive"},
    ),
    # Schedule 8 Part 3b line 46 "If line 20 is positive, enter whichever is less: amount from line
    # 20 or line 45. If not, enter "0".": a count of 1 when line 20 is positive.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_line_20_positive_conditions"},
        consumes={
            "counts": (),
            "amounts": ("ca/cpp_base_and_first_additional_contributions_difference",),
        },
        produces={"output": "ca/cpp_line_20_positive"},
    ),
    # Schedule 8 Part 3b line 30 "If line 16 is positive or "0", enter the amount from line 15 at
    # line 30 and line 36 ... If not, enter the amount from line 14": line 15 is the amount from
    # line 11 and line 14 the amount from line 9.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_16_not_negative",
            "when_none": "ca/cpp_actual_base_contributions",
            "when_any": "ca/cpp_base_contributions",
        },
        produces={"output": "ca/cpp_part_3b_line_30"},
    ),
    # Schedule 8 Part 3b line 31 "If line 16 is negative: Enter the amount from line 16 as a
    # positive amount.": 0 when line 16 is not negative.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_zero", "less": "ca/cpp_base_contributions_difference"},
        produces={"output": "ca/cpp_part_3b_line_31"},
    ),
    # Schedule 8 Part 3b line 32 "enter whichever is less: amount from line 19 or line 31": the
    # lesser of the two, taken when the line 32 count is 1.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cpp_first_additional_contributions_difference",
                "ca/cpp_part_3b_line_31",
            )
        },
        produces={"output": "ca/cpp_part_3b_line_32_lesser"},
    ),
    # Schedule 8 Part 3b line 32 "If line 16 is negative and line 19 is positive, enter whichever is
    # less: amount from line 19 or line 31. If not, enter "0".":
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_16_negative_line_19_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_3b_line_32_lesser",
        },
        produces={"output": "ca/cpp_part_3b_line_32"},
    ),
    # Schedule 8 Part 3b line 33 "Line 31 minus line 32 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_3b_line_31", "less": "ca/cpp_part_3b_line_32"},
        produces={"output": "ca/cpp_part_3b_line_33"},
    ),
    # Schedule 8 Part 3b line 34 "Line 30 plus line 32 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_3b_line_30", "ca/cpp_part_3b_line_32")},
        produces={"output": "ca/cpp_part_3b_line_34"},
    ),
    # Schedule 8 Part 3b line 35 "enter whichever is less": the lesser of line 23 and line 33, taken
    # when the line 35 count is 1.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cpp_second_additional_contributions_difference",
                "ca/cpp_part_3b_line_33",
            )
        },
        produces={"output": "ca/cpp_part_3b_line_35_lesser"},
    ),
    # Schedule 8 Part 3b line 35 "If line 23 and line 33 are both positive, enter whichever is less.
    # If not, enter "0".":
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_23_and_line_33_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_3b_line_35_lesser",
        },
        produces={"output": "ca/cpp_part_3b_line_35"},
    ),
    # Schedule 8 Part 3b line 36 "Line 34 plus line 35. Enter this amount (in dollars and cents) on
    # line 30800 of your return and line 58240 of your Form 428. =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_3b_line_34", "ca/cpp_part_3b_line_35")},
        produces={"output": "ca/cpp_part_3b_line_36"},
    ),
    # Schedule 8 Part 3b line 37 (printed under the heading "Line 36") "If line 19 is positive or
    # "0", enter the amount from line 18 at line 37 ... If not, enter the amount from line 17": line
    # 18 is the amount from line 12 and line 17 the amount from line 10.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_19_not_negative",
            "when_none": "ca/cpp_actual_first_additional_contributions",
            "when_any": "ca/cpp_first_additional_contributions",
        },
        produces={"output": "ca/cpp_part_3b_line_37"},
    ),
    # Schedule 8 Part 3b line 38 "If line 19 is negative: Enter the amount from line 19 as a
    # positive amount.": 0 when line 19 is not negative.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_zero",
            "less": "ca/cpp_first_additional_contributions_difference",
        },
        produces={"output": "ca/cpp_part_3b_line_38"},
    ),
    # Schedule 8 Part 3b line 39 "enter whichever is less: amount from line 16 or line 38": the
    # lesser of the two, taken when the line 39 count is 1.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/cpp_base_contributions_difference", "ca/cpp_part_3b_line_38")},
        produces={"output": "ca/cpp_part_3b_line_39_lesser"},
    ),
    # Schedule 8 Part 3b line 39 "If line 16 is positive, enter whichever is less: amount from line
    # 16 or line 38. If not, enter "0".":
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_16_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_3b_line_39_lesser",
        },
        produces={"output": "ca/cpp_part_3b_line_39"},
    ),
    # Schedule 8 Part 3b line 40 "Line 38 minus line 39 =".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_3b_line_38", "less": "ca/cpp_part_3b_line_39"},
        produces={"output": "ca/cpp_part_3b_line_40"},
    ),
    # Schedule 8 Part 3b line 41 "Line 37 plus line 39 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_3b_line_37", "ca/cpp_part_3b_line_39")},
        produces={"output": "ca/cpp_part_3b_line_41"},
    ),
    # Schedule 8 Part 3b line 42 "the result of line 23 minus line 35", which can be negative (then
    # the line 42 count is 0 or the lesser is that result).
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/cpp_second_additional_contributions_difference",
            "less": "ca/cpp_part_3b_line_35",
        },
        produces={"output": "ca/cpp_part_3b_line_23_less_line_35"},
    ),
    # Schedule 8 Part 3b line 42 "enter whichever is less: amount from line 40 or the result of line
    # 23 minus line 35": the lesser of the two, taken when the line 42 count is 1.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/cpp_part_3b_line_40", "ca/cpp_part_3b_line_23_less_line_35")},
        produces={"output": "ca/cpp_part_3b_line_42_lesser"},
    ),
    # Schedule 8 Part 3b line 42 "If line 23 and line 40 are both positive, enter whichever is less
    # ... If not, enter "0".":
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_23_and_line_40_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_3b_line_42_lesser",
        },
        produces={"output": "ca/cpp_part_3b_line_42"},
    ),
    # Schedule 8 Part 3b line 43 "Line 41 plus line 42 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_3b_line_41", "ca/cpp_part_3b_line_42")},
        produces={"output": "ca/cpp_part_3b_line_43"},
    ),
    # Schedule 8 Part 3b line 44 "If line 23 is positive or "0", enter the amount from line 22 on
    # line 44 and line 47 ... If not, enter the amount from line 21":
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_23_not_negative",
            "when_none": "ca/cpp_t4_second_additional_contributions",
            "when_any": "ca/cpp_second_additional_contributions",
        },
        produces={"output": "ca/cpp_part_3b_line_44"},
    ),
    # Schedule 8 Part 3b line 45 "If line 23 is negative: Enter the amount from line 23 as a
    # positive amount.": 0 when line 23 is not negative.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_zero",
            "less": "ca/cpp_second_additional_contributions_difference",
        },
        produces={"output": "ca/cpp_part_3b_line_45"},
    ),
    # Schedule 8 Part 3b line 46 "enter whichever is less: amount from line 20 or line 45": the
    # lesser of the two, taken when the line 46 count is 1.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cpp_base_and_first_additional_contributions_difference",
                "ca/cpp_part_3b_line_45",
            )
        },
        produces={"output": "ca/cpp_part_3b_line_46_lesser"},
    ),
    # Schedule 8 Part 3b line 46 "If line 20 is positive, enter whichever is less: amount from line
    # 20 or line 45. If not, enter "0".":
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_20_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_part_3b_line_46_lesser",
        },
        produces={"output": "ca/cpp_part_3b_line_46"},
    ),
    # Schedule 8 Part 3b line 47 "Line 44 plus line 46 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_3b_line_44", "ca/cpp_part_3b_line_46")},
        produces={"output": "ca/cpp_part_3b_line_47"},
    ),
    # Schedule 8 Part 3b line 48 "Line 43 plus line 47 Enter this amount (in dollars and cents) on
    # line 22215 of your return. =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_3b_line_43", "ca/cpp_part_3b_line_47")},
        produces={"output": "ca/cpp_part_3b_line_48"},
    ),
    # T1 line 30800 and ON428 line 58240, from Schedule 8 Part 3a line 25 "Enter the amount from
    # line 15." when line 24 is positive (the line 15 amount is line 11), else Part 3b line 36:
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_24_positive",
            "when_none": "ca/cpp_part_3b_line_36",
            "when_any": "ca/cpp_base_contributions",
        },
        produces={"output": "ca/cpp_part_3_base_contributions_on_return"},
    ),
    # T1 line 22215, from Schedule 8 Part 3a line 28 "Line 26 plus line 27" (the existing line 28
    # step) when line 24 is positive, else Part 3b line 48:
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_24_positive",
            "when_none": "ca/cpp_part_3b_line_48",
            "when_any": "ca/cpp_enhanced_contributions",
        },
        produces={"output": "ca/cpp_part_3_enhanced_contributions_on_return"},
    ),
    # T1 line 44800 "CPP overpayment", from Schedule 8 Part 3a line 29 "Enter the amount from line
    # 24." when line 24 is positive, else "0":
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_line_24_positive",
            "when_none": "ca/cpp_zero",
            "when_any": "ca/cpp_contributions_difference",
        },
        produces={"output": "ca/cpp_part_3_overpayment"},
    ),
    # T1 line 30800 (also ON428 line 58240): Schedule 8 Part 5 line 57 when Part 5 is
    # completed (it replaces Part 3a and Part 3b, the filer's choice on the form), else the
    # Part 3a or Part 3b amount.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_part_5_completed",
            "when_none": "ca/cpp_part_3_base_contributions_on_return",
            "when_any": "ca/cpp_part_5_line_57",
        },
        produces={"output": "ca/schedule_8_cpp_base_contributions_on_return"},
    ),
    # T1 line 22215: Schedule 8 Part 5 line 69 when Part 5 is completed, else the Part 3a or
    # Part 3b amount.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_part_5_completed",
            "when_none": "ca/cpp_part_3_enhanced_contributions_on_return",
            "when_any": "ca/cpp_part_5_line_69",
        },
        produces={"output": "ca/schedule_8_cpp_enhanced_contributions_on_return"},
    ),
    # T1 line 44800: Schedule 8 Part 5 line 50 when Part 5 is completed, else the Part 3a line
    # 29 amount or 0.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/cpp_part_5_completed",
            "when_none": "ca/cpp_part_3_overpayment",
            "when_any": "ca/cpp_part_5_line_50",
        },
        produces={"output": "ca/schedule_8_cpp_overpayment"},
    ),
    # Schedule 8 Part 3, each contribution on employment income: line 11 (base, 4.95% of the
    # earnings between the $3,500 exemption and the $71,300 ceiling, lines 2 to 7), line 12
    # (first additional, 1% of the same band) and line 22 (second additional, 4% of the
    # earnings between the $71,300 and $81,200 ceilings, lines 2 to 4).
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_base_contribution"},
        consumes={"earnings": "ca/t4_cpp_pensionable_earnings_outside_quebec"},
        produces={"output": "ca/cpp_base_contributions"},
    ),
    # Schedule 8 Part 2 "Box A: Enter the number of months that CPP applied in 2025." and the
    # "Monthly proration for 2025" table, a row for each number of months (1 to 12): line B
    # (maximum pensionable earnings), line C (maximum amount subject to second additional
    # contributions), line D (additional maximum pensionable earnings) and line E (maximum
    # basic exemption), each the figure of the row for the months in box A.
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/cpp_maximum_pensionable_earnings"},
        consumes={"count": "ca/cpp_months"},
        produces={"output": "ca/cpp_maximum_pensionable_earnings"},
    ),
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/cpp_second_additional_earnings_maximum"},
        consumes={"count": "ca/cpp_months"},
        produces={"output": "ca/cpp_second_additional_earnings_maximum"},
    ),
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/cpp_additional_maximum_pensionable_earnings"},
        consumes={"count": "ca/cpp_months"},
        produces={"output": "ca/cpp_additional_maximum_pensionable_earnings"},
    ),
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/cpp_basic_exemption"},
        consumes={"count": "ca/cpp_months"},
        produces={"output": "ca/cpp_basic_exemption"},
    ),
    # Schedule 8 Part 4 line 1 "amount from line 12200 of your return plus line 27 of your
    # return": the pensionable net self-employment earnings, the net partnership income then
    # the net self-employment income.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/net_partnership_income", "ca/net_self_employment_income")},
        produces={"output": "ca/pensionable_net_self_employment_earnings"},
    ),
    # T1 line 27 "Add lines 22 to 26. Net self-employment income": line 22 (13500) business
    # income, line 23 (13700) professional income, line 24 (13900) commission income, line 25
    # (14100) farming income and line 26 (14300) fishing income, the "Net" box of each, in line
    # order. Line 28 "Line 21 plus line 27" is not a step of its own: total income (line 15000)
    # adds line 27 to the lines 1 to 20, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_income",
                "ca/professional_income",
                "ca/commission_income",
                "ca/farming_income",
                "ca/fishing_income",
            ),
        },
        produces={"output": "ca/net_self_employment_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_business_income_on_return"},
        produces={"output": "ca/business_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_professional_income_on_return"},
        produces={"output": "ca/professional_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_commission_income_on_return"},
        produces={"output": "ca/commission_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_farming_income_on_return"},
        produces={"output": "ca/farming_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_fishing_income_on_return"},
        produces={"output": "ca/fishing_income"},
    ),
}

FORM_WIRING = {
    (
        TieredContribution,
        frozenset({T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC}),
        frozenset({CPP_FIRST_ADDITIONAL_CONTRIBUTIONS}),
    ),
    (
        TieredContribution,
        frozenset({T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC}),
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS}),
    ),
    (
        Sum,
        frozenset({CPP_FIRST_ADDITIONAL_CONTRIBUTIONS, CPP_SECOND_ADDITIONAL_CONTRIBUTIONS}),
        frozenset({CPP_ENHANCED_CONTRIBUTIONS}),
    ),
    (
        ApplyRate,
        frozenset({CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS}),
        frozenset({CPP_ACTUAL_BASE_CONTRIBUTIONS}),
    ),
    (
        Subtract,
        frozenset({CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS, CPP_ACTUAL_BASE_CONTRIBUTIONS}),
        frozenset({CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS}),
    ),
    (
        Sum,
        frozenset({CPP_BASE_CONTRIBUTIONS, CPP_FIRST_ADDITIONAL_CONTRIBUTIONS}),
        frozenset({CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS}),
    ),
    (
        Subtract,
        frozenset({CPP_ACTUAL_BASE_CONTRIBUTIONS, CPP_BASE_CONTRIBUTIONS}),
        frozenset({CPP_BASE_CONTRIBUTIONS_DIFFERENCE}),
    ),
    (
        Subtract,
        frozenset({CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS, CPP_FIRST_ADDITIONAL_CONTRIBUTIONS}),
        frozenset({CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
    ),
    (
        Sum,
        frozenset(
            {CPP_BASE_CONTRIBUTIONS_DIFFERENCE, CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}
        ),
        frozenset({CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
    ),
    (
        Subtract,
        frozenset({CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS, CPP_SECOND_ADDITIONAL_CONTRIBUTIONS}),
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
    ),
    (
        Sum,
        frozenset(
            {
                CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
                CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
            }
        ),
        frozenset({CPP_CONTRIBUTIONS_DIFFERENCE}),
    ),
    (
        CreditAmount,
        frozenset(),
        frozenset({CPP_ZERO}),
    ),
    (
        CountByConditions,
        frozenset({CPP_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_LINE_24_POSITIVE}),
    ),
    (
        CountByConditions,
        frozenset({CPP_BASE_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_LINE_16_NOT_NEGATIVE}),
    ),
    (
        CountByConditions,
        frozenset({CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_LINE_19_NOT_NEGATIVE}),
    ),
    (
        CountByConditions,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_LINE_23_NOT_NEGATIVE}),
    ),
    (
        CountByConditions,
        frozenset({CPP_LINE_16_NOT_NEGATIVE, CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE}),
    ),
    (
        CountByConditions,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_3B_LINE_33}),
        frozenset({CPP_LINE_23_AND_LINE_33_POSITIVE}),
    ),
    (
        CountByConditions,
        frozenset({CPP_BASE_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_LINE_16_POSITIVE}),
    ),
    (
        CountByConditions,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_3B_LINE_40}),
        frozenset({CPP_LINE_23_AND_LINE_40_POSITIVE}),
    ),
    (
        CountByConditions,
        frozenset({CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_LINE_20_POSITIVE}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CPP_LINE_16_NOT_NEGATIVE, CPP_ACTUAL_BASE_CONTRIBUTIONS, CPP_BASE_CONTRIBUTIONS}
        ),
        frozenset({CPP_PART_3B_LINE_30}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_BASE_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_3B_LINE_31}),
    ),
    (
        LesserOf,
        frozenset({CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_3B_LINE_31}),
        frozenset({CPP_PART_3B_LINE_32_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE, CPP_ZERO, CPP_PART_3B_LINE_32_LESSER}),
        frozenset({CPP_PART_3B_LINE_32}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_3B_LINE_31, CPP_PART_3B_LINE_32}),
        frozenset({CPP_PART_3B_LINE_33}),
    ),
    (
        Sum,
        frozenset({CPP_PART_3B_LINE_30, CPP_PART_3B_LINE_32}),
        frozenset({CPP_PART_3B_LINE_34}),
    ),
    (
        LesserOf,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_3B_LINE_33}),
        frozenset({CPP_PART_3B_LINE_35_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_23_AND_LINE_33_POSITIVE, CPP_ZERO, CPP_PART_3B_LINE_35_LESSER}),
        frozenset({CPP_PART_3B_LINE_35}),
    ),
    (
        Sum,
        frozenset({CPP_PART_3B_LINE_34, CPP_PART_3B_LINE_35}),
        frozenset({CPP_PART_3B_LINE_36}),
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
        frozenset({CPP_PART_3B_LINE_37}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_3B_LINE_38}),
    ),
    (
        LesserOf,
        frozenset({CPP_BASE_CONTRIBUTIONS_DIFFERENCE, CPP_PART_3B_LINE_38}),
        frozenset({CPP_PART_3B_LINE_39_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_16_POSITIVE, CPP_ZERO, CPP_PART_3B_LINE_39_LESSER}),
        frozenset({CPP_PART_3B_LINE_39}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_3B_LINE_38, CPP_PART_3B_LINE_39}),
        frozenset({CPP_PART_3B_LINE_40}),
    ),
    (
        Sum,
        frozenset({CPP_PART_3B_LINE_37, CPP_PART_3B_LINE_39}),
        frozenset({CPP_PART_3B_LINE_41}),
    ),
    (
        Subtract,
        frozenset({CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_3B_LINE_35}),
        frozenset({CPP_PART_3B_LINE_23_LESS_LINE_35}),
    ),
    (
        LesserOf,
        frozenset({CPP_PART_3B_LINE_40, CPP_PART_3B_LINE_23_LESS_LINE_35}),
        frozenset({CPP_PART_3B_LINE_42_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_23_AND_LINE_40_POSITIVE, CPP_ZERO, CPP_PART_3B_LINE_42_LESSER}),
        frozenset({CPP_PART_3B_LINE_42}),
    ),
    (
        Sum,
        frozenset({CPP_PART_3B_LINE_41, CPP_PART_3B_LINE_42}),
        frozenset({CPP_PART_3B_LINE_43}),
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
        frozenset({CPP_PART_3B_LINE_44}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_3B_LINE_45}),
    ),
    (
        LesserOf,
        frozenset({CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, CPP_PART_3B_LINE_45}),
        frozenset({CPP_PART_3B_LINE_46_LESSER}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_20_POSITIVE, CPP_ZERO, CPP_PART_3B_LINE_46_LESSER}),
        frozenset({CPP_PART_3B_LINE_46}),
    ),
    (
        Sum,
        frozenset({CPP_PART_3B_LINE_44, CPP_PART_3B_LINE_46}),
        frozenset({CPP_PART_3B_LINE_47}),
    ),
    (
        Sum,
        frozenset({CPP_PART_3B_LINE_43, CPP_PART_3B_LINE_47}),
        frozenset({CPP_PART_3B_LINE_48}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_24_POSITIVE, CPP_PART_3B_LINE_36, CPP_BASE_CONTRIBUTIONS}),
        frozenset({CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_24_POSITIVE, CPP_PART_3B_LINE_48, CPP_ENHANCED_CONTRIBUTIONS}),
        frozenset({CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_LINE_24_POSITIVE, CPP_ZERO, CPP_CONTRIBUTIONS_DIFFERENCE}),
        frozenset({CPP_PART_3_OVERPAYMENT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CPP_PART_5_COMPLETED, CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN, CPP_PART_5_LINE_57}
        ),
        frozenset({SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN}),
    ),
    (
        ChooseByCount,
        frozenset(
            {CPP_PART_5_COMPLETED, CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN, CPP_PART_5_LINE_69}
        ),
        frozenset({SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN}),
    ),
    (
        ChooseByCount,
        frozenset({CPP_PART_5_COMPLETED, CPP_PART_3_OVERPAYMENT, CPP_PART_5_LINE_50}),
        frozenset({SCHEDULE_8_CPP_OVERPAYMENT}),
    ),
    (
        TieredContribution,
        frozenset({T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC}),
        frozenset({CPP_BASE_CONTRIBUTIONS}),
    ),
    (
        AmountForCount,
        frozenset({CPP_MONTHS}),
        frozenset({CPP_MAXIMUM_PENSIONABLE_EARNINGS}),
    ),
    (
        AmountForCount,
        frozenset({CPP_MONTHS}),
        frozenset({CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM}),
    ),
    (
        AmountForCount,
        frozenset({CPP_MONTHS}),
        frozenset({CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS}),
    ),
    (
        AmountForCount,
        frozenset({CPP_MONTHS}),
        frozenset({CPP_BASIC_EXEMPTION}),
    ),
    (
        Sum,
        frozenset({NET_PARTNERSHIP_INCOME, NET_SELF_EMPLOYMENT_INCOME}),
        frozenset({PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_INCOME,
                PROFESSIONAL_INCOME,
                COMMISSION_INCOME,
                FARMING_INCOME,
                FISHING_INCOME,
            }
        ),
        frozenset({NET_SELF_EMPLOYMENT_INCOME}),
    ),
    (RecordTotal, frozenset({BUSINESS_INCOME_PER_STATEMENT}), frozenset({BUSINESS_INCOME})),
    (RecordTotal, frozenset({PROFESSIONAL_INCOME_PER_STATEMENT}), frozenset({PROFESSIONAL_INCOME})),
    (RecordTotal, frozenset({COMMISSION_INCOME_PER_STATEMENT}), frozenset({COMMISSION_INCOME})),
    (RecordTotal, frozenset({FARMING_INCOME_PER_STATEMENT}), frozenset({FARMING_INCOME})),
    (RecordTotal, frozenset({FISHING_INCOME_PER_STATEMENT}), frozenset({FISHING_INCOME})),
}
