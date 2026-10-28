"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`).

The T1 lines for CPP that both forms give (`05j_cpp_lines.yaml`): the return carries Schedule 8 or
Form RC381, never both, so one of the two totals is 0 and each of lines 30800 (also ON428 line
58240), 22215 and 44800 is the Schedule 8 total plus the Form RC381 total. Lines 42100, 31000 and
22200 add the Form RC381 total to the sums of Part 4 and Part 5 that `net_tax.py`,
`non_refundable_credits.py` and `deductions.py` hold. The inputs Parts 4 and 5 completed are first
checked by `ca/count_without_records` against the copies of Form RC381, so a return with a copy of
the form cannot count Schedule 8's Part 4 or Part 5 on top of the form's own total. Parts 4 and 5
completed together are alternatives on Schedule 8, so their checked counts are then counted and
refused (an input error) when both are 1. The two inputs are yes or no answers, checked first by
`ca/yes_or_no_count` in `yes_or_no_flag_checks.py`, so a count of 2 or more is refused rather than
counted twice. Part 4 completed with employment earnings (Part 3 line 1, the T4 pensionable earnings
outside Quebec, above 0) is refused too: Part 4 is for a filer with no employment income, so the
count of it with those earnings is counted and refused (an input error) when it is 1.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_calculator.jurisdictions.ca.capabilities.count_without_records import CountWithoutRecords
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_OVERPAYMENT,
    CPP_PART_4_AND_PART_5_BOTH,
    CPP_PART_4_AND_PART_5_BOTH_CHECKED,
    CPP_PART_4_COMPLETED_CHECKED,
    CPP_PART_4_COMPLETED_YES_OR_NO_CHECKED,
    CPP_PART_4_WITH_EMPLOYMENT_EARNINGS,
    CPP_PART_4_WITH_EMPLOYMENT_EARNINGS_CHECKED,
    CPP_PART_5_COMPLETED_CHECKED,
    CPP_PART_5_COMPLETED_YES_OR_NO_CHECKED,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_OVERPAYMENT_ON_RETURN,
    RC381_INSTANCES,
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_OVERPAYMENT,
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
)

INPUTS = frozenset[str]()

OUTPUTS = frozenset(
    {
        "ca/cpp_part_4_and_part_5_both_checked",
        "ca/cpp_part_4_with_employment_earnings_checked",
    }
)

STEPS = {
    # Parts 4 and 5 completed, checked before the T1 lines 42100, 31000 and 22200 read them: each
    # input is refused (an input error) when it is above 0 and the return carries a copy of Form
    # RC381 (`ca/rc381_instances`, which holds one record), and passed on unchanged otherwise.
    CapabilitySelection(
        name="ca/count_without_records",
        params={},
        consumes={
            "count": "ca/cpp_part_4_completed_yes_or_no_checked",
            "records": "ca/rc381_instances",
        },
        produces={"output": "ca/cpp_part_4_completed_checked"},
    ),
    CapabilitySelection(
        name="ca/count_without_records",
        params={},
        consumes={
            "count": "ca/cpp_part_5_completed_yes_or_no_checked",
            "records": "ca/rc381_instances",
        },
        produces={"output": "ca/cpp_part_5_completed_checked"},
    ),
    # Schedule 8 Part 4 and Part 5 completed, each checked above: the count of the two both above 0,
    # 1 when both are completed and 0 otherwise. The two parts are alternatives (Part 4 for
    # self-employment income only, Part 5 for employment income as well), so a count of 1 is
    # refused below, an input error naming both parts, not added. The checked count is read by
    # nothing on the return.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_part_4_and_part_5_both_conditions"},
        consumes={
            "counts": (
                "ca/cpp_part_4_completed_checked",
                "ca/cpp_part_5_completed_checked",
            ),
            "amounts": (),
        },
        produces={"output": "ca/cpp_part_4_and_part_5_both"},
    ),
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/cpp_part_4_and_part_5_both_refused"},
        consumes={"count": "ca/cpp_part_4_and_part_5_both"},
        produces={"output": "ca/cpp_part_4_and_part_5_both_checked"},
    ),
    # Schedule 8 Part 4 completed with employment earnings: Part 4 checked above and Part 3 line 1
    # (the T4 CPP pensionable earnings outside Quebec) above 0, the count of the two, 1 when both
    # hold and 0 otherwise. Part 4 is for a filer with no employment income, so a count of 1 is
    # refused below, an input error naming Part 4 and the form's Part 5 route, not added. Part 5
    # alone is not refused: a T4 with zero box 14 is legitimate. The checked count is read by
    # nothing on the return.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/cpp_part_4_with_employment_earnings_conditions"},
        consumes={
            "counts": ("ca/cpp_part_4_completed_checked",),
            "amounts": ("ca/t4_cpp_pensionable_earnings_outside_quebec",),
        },
        produces={"output": "ca/cpp_part_4_with_employment_earnings"},
    ),
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/cpp_part_4_with_employment_earnings_refused"},
        consumes={"count": "ca/cpp_part_4_with_employment_earnings"},
        produces={"output": "ca/cpp_part_4_with_employment_earnings_checked"},
    ),
    # T1 line 30800 and ON428 line 58240: Schedule 8 line 57 or Form RC381 line 98 (or Part 3a
    # line 70, Part 3b line 81), whichever form the return carries.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/schedule_8_cpp_base_contributions_on_return",
                "ca/rc381_cpp_base_contributions_on_return",
            )
        },
        produces={"output": "ca/cpp_base_contributions_on_return"},
    ),
    # T1 line 22215: Schedule 8 line 69 or Form RC381 line 110, whichever form the return carries.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/schedule_8_cpp_enhanced_contributions_on_return",
                "ca/rc381_cpp_enhanced_contributions_on_return",
            )
        },
        produces={"output": "ca/cpp_enhanced_contributions_on_return"},
    ),
    # T1 line 44800: Schedule 8 line 50 or Form RC381 line 91 (or Part 3a line 29, line 74),
    # whichever form the return carries.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/schedule_8_cpp_overpayment",
                "ca/rc381_cpp_overpayment_on_return",
            )
        },
        produces={"output": "ca/cpp_overpayment"},
    ),
}

WIRING = {
    (
        CountWithoutRecords,
        frozenset({CPP_PART_4_COMPLETED_YES_OR_NO_CHECKED, RC381_INSTANCES}),
        frozenset({CPP_PART_4_COMPLETED_CHECKED}),
    ),
    (
        CountWithoutRecords,
        frozenset({CPP_PART_5_COMPLETED_YES_OR_NO_CHECKED, RC381_INSTANCES}),
        frozenset({CPP_PART_5_COMPLETED_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset({CPP_PART_4_COMPLETED_CHECKED, CPP_PART_5_COMPLETED_CHECKED}),
        frozenset({CPP_PART_4_AND_PART_5_BOTH}),
    ),
    (
        CountRefusedByConditions,
        frozenset({CPP_PART_4_AND_PART_5_BOTH}),
        frozenset({CPP_PART_4_AND_PART_5_BOTH_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset({CPP_PART_4_COMPLETED_CHECKED, T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC}),
        frozenset({CPP_PART_4_WITH_EMPLOYMENT_EARNINGS}),
    ),
    (
        CountRefusedByConditions,
        frozenset({CPP_PART_4_WITH_EMPLOYMENT_EARNINGS}),
        frozenset({CPP_PART_4_WITH_EMPLOYMENT_EARNINGS_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN, RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN}
        ),
        frozenset({CPP_BASE_CONTRIBUTIONS_ON_RETURN}),
    ),
    (
        Sum,
        frozenset(
            {
                SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
                RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
            }
        ),
        frozenset({CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN}),
    ),
    (
        Sum,
        frozenset({SCHEDULE_8_CPP_OVERPAYMENT, RC381_CPP_OVERPAYMENT_ON_RETURN}),
        frozenset({CPP_OVERPAYMENT}),
    ),
}
