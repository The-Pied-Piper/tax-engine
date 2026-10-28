"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`).

Schedule 8 Part 5 lines 70 to 88, "Base CPP contributions through self-employment income and other
earnings" (line 70, T1 line 31000) and "Deduction for CPP enhanced contributions on self-employment
income and other earnings" (line 88, T1 line 22200). The copy lines (76, 78, 79, 81, 82 and 85,
each "Amount from line ...") are steps of no capability: the lines that read them read the line
they copy. Line 88 adds the five lines as printed, so line 84 is counted twice when line 74 is
not negative.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_CONTRIBUTIONS_DIFFERENCE,
    CPP_PART_5_LINE_43,
    CPP_PART_5_LINE_44,
    CPP_PART_5_LINE_45,
    CPP_PART_5_LINE_70,
    CPP_PART_5_LINE_71,
    CPP_PART_5_LINE_72,
    CPP_PART_5_LINE_73,
    CPP_PART_5_LINE_74,
    CPP_PART_5_LINE_75,
    CPP_PART_5_LINE_75_BASE,
    CPP_PART_5_LINE_77,
    CPP_PART_5_LINE_80,
    CPP_PART_5_LINE_83,
    CPP_PART_5_LINE_84,
    CPP_PART_5_LINE_86,
    CPP_PART_5_LINE_87,
    CPP_PART_5_LINE_88,
    CPP_ZERO,
)

INPUTS = frozenset[str]()

# Every line here is read by another line or by a routing step, so nothing is a declared output;
# lines 49, 50, 57 and 69 of the earlier Part 5 steps are read by the routing steps too.
OUTPUTS = frozenset[str]()

FORM_STEPS = {
    # Schedule 8 Part 5 line 70 "Base CPP contributions through self-employment income and other
    # earnings: Line 70: Enter the result of the following calculation (in dollars and cents) on
    # line 31000 of your return. amount from line 43 multiplied by 50% =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/cpp_part_5_line_70_rate"},
        consumes={"base": "ca/cpp_part_5_line_43"},
        produces={"output": "ca/cpp_part_5_line_70"},
    ),
    # Schedule 8 Part 5 line 71 "Amount from line 44 multiplied by 50% =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/cpp_part_5_line_71_rate"},
        consumes={"base": "ca/cpp_part_5_line_44"},
        produces={"output": "ca/cpp_part_5_line_71"},
    ),
    # Schedule 8 Part 5 line 72 "Line 70 plus line 71 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/cpp_part_5_line_70", "ca/cpp_part_5_line_71")},
        produces={"output": "ca/cpp_part_5_line_72"},
    ),
    # Schedule 8 Part 5 line 73 "Enter the amount from line 24 of Part 3 if positive. If not,
    # enter "0".": line 24 of Part 3 less "0", not below zero (line 48 takes the same amount
    # through its own step).
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_contributions_difference", "less": "ca/cpp_zero"},
        produces={"output": "ca/cpp_part_5_line_73"},
    ),
    # Schedule 8 Part 5 line 74 "Line 72 minus line 73 (if negative, show in brackets) =":
    # signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_72", "less": "ca/cpp_part_5_line_73"},
        produces={"output": "ca/cpp_part_5_line_74"},
    ),
    # Schedule 8 Part 5 line 75 "Enter whichever is less: amount from line 72 or line 73 Line
    # A": the lesser of the two, the amount line 75 multiplies and line 77 takes line 76 off.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/cpp_part_5_line_72", "ca/cpp_part_5_line_73")},
        produces={"output": "ca/cpp_part_5_line_75_base"},
    ),
    # Schedule 8 Part 5 line 75 "multiply by 83.1933 =": line A times 83.1933%, the same factor
    # as Part 3 line 9, as a dataset of this line.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/cpp_part_5_line_75_rate"},
        consumes={"base": "ca/cpp_part_5_line_75_base"},
        produces={"output": "ca/cpp_part_5_line_75"},
    ),
    # Schedule 8 Part 5 line 77 "Amount A minus line 76 =": line 76 is "Amount from line 75".
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_75_base", "less": "ca/cpp_part_5_line_75"},
        produces={"output": "ca/cpp_part_5_line_77"},
    ),
    # Schedule 8 Part 5 line 80 "Line 78 minus line 79 =": line 78 is "Amount from line 70" and
    # line 79 "Amount from line 75". Signed: line 75 can be a cent more than line 70 when the
    # amounts are a few dollars or less.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_70", "less": "ca/cpp_part_5_line_75"},
        produces={"output": "ca/cpp_part_5_line_80"},
    ),
    # Schedule 8 Part 5 line 83 "Line 81 minus line 82 =": line 81 is "Amount from line 71" and
    # line 82 "Amount from line 77". Not negative: line 77 never exceeds line 71 (checked for
    # every line 30 from 0 to 67,800.00).
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_71", "less": "ca/cpp_part_5_line_77"},
        produces={"output": "ca/cpp_part_5_line_83"},
    ),
    # Schedule 8 Part 5 line 84 "Amount from line 45 multiplied by 50% =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/cpp_part_5_line_84_rate"},
        consumes={"base": "ca/cpp_part_5_line_45"},
        produces={"output": "ca/cpp_part_5_line_84"},
    ),
    # Schedule 8 Part 5 line 86 "If line 74 is negative, enter it as a positive amount.": "0"
    # less line 74, not below zero (0 when line 74 is positive or "0").
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_zero", "less": "ca/cpp_part_5_line_74"},
        produces={"output": "ca/cpp_part_5_line_86"},
    ),
    # Schedule 8 Part 5 line 87 "Line 85 minus line 86 (if negative, enter "0") =": line 85 is
    # "Amount from line 84".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_84", "less": "ca/cpp_part_5_line_86"},
        produces={"output": "ca/cpp_part_5_line_87"},
    ),
    # Schedule 8 Part 5 line 88 "Deduction for CPP enhanced contributions on self-employment
    # income and other earnings: Add lines 80, 81, 83, 84, and 87. Enter this amount (in dollar
    # and cents) on line 22200 of your return. =": the five as printed (line 81 is "Amount from
    # line 71").
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cpp_part_5_line_80",
                "ca/cpp_part_5_line_71",
                "ca/cpp_part_5_line_83",
                "ca/cpp_part_5_line_84",
                "ca/cpp_part_5_line_87",
            )
        },
        produces={"output": "ca/cpp_part_5_line_88"},
    ),
}

FORM_WIRING = {
    (
        ApplyRate,
        frozenset({CPP_PART_5_LINE_43}),
        frozenset({CPP_PART_5_LINE_70}),
    ),
    (
        ApplyRate,
        frozenset({CPP_PART_5_LINE_44}),
        frozenset({CPP_PART_5_LINE_71}),
    ),
    (
        Sum,
        frozenset({CPP_PART_5_LINE_70, CPP_PART_5_LINE_71}),
        frozenset({CPP_PART_5_LINE_72}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_CONTRIBUTIONS_DIFFERENCE, CPP_ZERO}),
        frozenset({CPP_PART_5_LINE_73}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_72, CPP_PART_5_LINE_73}),
        frozenset({CPP_PART_5_LINE_74}),
    ),
    (
        LesserOf,
        frozenset({CPP_PART_5_LINE_72, CPP_PART_5_LINE_73}),
        frozenset({CPP_PART_5_LINE_75_BASE}),
    ),
    (
        ApplyRate,
        frozenset({CPP_PART_5_LINE_75_BASE}),
        frozenset({CPP_PART_5_LINE_75}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_75_BASE, CPP_PART_5_LINE_75}),
        frozenset({CPP_PART_5_LINE_77}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_70, CPP_PART_5_LINE_75}),
        frozenset({CPP_PART_5_LINE_80}),
    ),
    (
        Subtract,
        frozenset({CPP_PART_5_LINE_71, CPP_PART_5_LINE_77}),
        frozenset({CPP_PART_5_LINE_83}),
    ),
    (
        ApplyRate,
        frozenset({CPP_PART_5_LINE_45}),
        frozenset({CPP_PART_5_LINE_84}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_ZERO, CPP_PART_5_LINE_74}),
        frozenset({CPP_PART_5_LINE_86}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({CPP_PART_5_LINE_84, CPP_PART_5_LINE_86}),
        frozenset({CPP_PART_5_LINE_87}),
    ),
    (
        Sum,
        frozenset(
            {
                CPP_PART_5_LINE_80,
                CPP_PART_5_LINE_71,
                CPP_PART_5_LINE_83,
                CPP_PART_5_LINE_84,
                CPP_PART_5_LINE_87,
            }
        ),
        frozenset({CPP_PART_5_LINE_88}),
    ),
}
