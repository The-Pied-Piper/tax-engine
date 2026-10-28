"""The CA-ON manifest entries of Form T2205 "Amounts from a Spousal or Common-law Partner RRSP,
RRIF, or SPP to Include in Income" (see `test_manifest_t2205.py`).

The form `ca/t2205` runs once (it has no instances): the twelve amounts the filer enters (lines 1,
2, 4, 6, 7, 12, 13, 14, 17, 18 and 20 and the part of line 11 that relates to SPP withdrawals), the
checks that a part is not above its whole (lines 4, 7, 14 and 18 and the SPP part of line 11), and
the printed sums, differences and "whichever is less" lines. Its exports are the RRSP part of line
11, the SPP part of line 11, line 22 (the amounts the filer reports) and line 10 and line 21 (the
spouse's amounts, shown and exported, never read into this return).

The form cannot read the age of the filer (`ca/born_in_1960_or_earlier_checked` is a figure of the
return), so the return part `03v_t2205_routing.yaml` totals the exports and sends them to T1 line
11500 (65 or older at the end of the year) or 13000, the RRSP part to line 12900. Those steps are
the return's own and are listed here as STEPS and WIRING; the sums of total income that add the
three amounts are listed with their families (`income`, `t929`, `refund`).
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign
from tax_calculator.jurisdictions.ca.catalog import (
    BORN_IN_1960_OR_EARLIER_CHECKED,
    T2205_LINE_1,
    T2205_LINE_2,
    T2205_LINE_3,
    T2205_LINE_4,
    T2205_LINE_4_CHECKED,
    T2205_LINE_5,
    T2205_LINE_6,
    T2205_LINE_7,
    T2205_LINE_7_CHECKED,
    T2205_LINE_8,
    T2205_LINE_10,
    T2205_LINE_11,
    T2205_LINE_11_RRSP_PART,
    T2205_LINE_11_SPP_PART,
    T2205_LINE_11_SPP_PART_CHECKED,
    T2205_LINE_12,
    T2205_LINE_13,
    T2205_LINE_14,
    T2205_LINE_14_CHECKED,
    T2205_LINE_15,
    T2205_LINE_16,
    T2205_LINE_17,
    T2205_LINE_17_USED,
    T2205_LINE_18,
    T2205_LINE_18_CHECKED,
    T2205_LINE_18_FROM_PART_1,
    T2205_LINE_18_USED,
    T2205_LINE_19,
    T2205_LINE_20,
    T2205_LINE_21,
    T2205_LINE_22,
    T2205_LINE_22_ON_LINE_11500,
    T2205_LINE_22_ON_LINE_13000,
    T2205_LINE_22_TOTAL,
    T2205_ON_LINE_11500,
    T2205_ON_LINE_12900,
    T2205_ON_LINE_13000,
    T2205_SPP_PART_ON_LINE_11500,
    T2205_SPP_PART_ON_LINE_13000,
    T2205_SPP_PART_TOTAL,
)

FORM = "ca/t2205"

# The record lists of one record that the engine derives from the form's exports the return reads.
T2205_LINE_11_RRSP_PART_PER_FORM = RecordListKind(
    "ca/t2205.t2205_line_11_rrsp_part", fields=(T2205_LINE_11_RRSP_PART,)
)
T2205_LINE_11_SPP_PART_CHECKED_PER_FORM = RecordListKind(
    "ca/t2205.t2205_line_11_spp_part_checked", fields=(T2205_LINE_11_SPP_PART_CHECKED,)
)
T2205_LINE_22_PER_FORM = RecordListKind("ca/t2205.t2205_line_22", fields=(T2205_LINE_22,))

# The twelve amounts of the form, as the filer enters them, in `01p_t2205_inputs.yaml`.
INPUTS = frozenset(
    {
        "ca/t2205_line_1",
        "ca/t2205_line_2",
        "ca/t2205_line_4",
        "ca/t2205_line_6",
        "ca/t2205_line_7",
        "ca/t2205_line_11_spp_part",
        "ca/t2205_line_12",
        "ca/t2205_line_13",
        "ca/t2205_line_14",
        "ca/t2205_line_17",
        "ca/t2205_line_18",
        "ca/t2205_line_20",
    }
)

# The exports of the form: the three amounts this return reports, and the spouse's two.
EXPORTS = frozenset(
    {
        "ca/t2205_line_11_rrsp_part",
        "ca/t2205_line_11_spp_part_checked",
        "ca/t2205_line_22",
        "ca/t2205_line_10",
        "ca/t2205_line_21",
    }
)
# The exports the return reads; the spouse's line 10 and line 21 are read by nothing.
READ_EXPORTS = frozenset(
    {
        "ca/t2205_line_11_rrsp_part",
        "ca/t2205_line_11_spp_part_checked",
        "ca/t2205_line_22",
    }
)

# The return declares no output for the form: every kind it produces is read.
OUTPUTS: frozenset[str] = frozenset()


def step(name: str, output: str, **consumes: str | tuple[str, ...]) -> CapabilitySelection:
    """The selection of capability `name` consuming the given slots and producing `output`."""
    return CapabilitySelection(name=name, params={}, consumes=consumes, produces={"output": output})


def sign_choice(
    output: str, sign: str, *, when_positive: str, when_non_positive: str
) -> CapabilitySelection:
    """Line `output` chosen by the sign of line 3: Part 1 filled in (line 3 more than 0) or not."""
    return step(
        "ca/choose_by_sign",
        output,
        sign=sign,
        when_positive=(when_positive,),
        when_zero=(),
        when_negative=(),
        when_non_positive=(when_non_positive,),
        when_non_negative=(),
    )


# The steps of the form, one for each printed line that computes, with its line in the comment.
FORM_STEPS = {
    # Line 3 "Line 1 plus line 2".
    step("core/sum", "ca/t2205_line_3", parts=("ca/t2205_line_1", "ca/t2205_line_2")),
    # Line 4 is part of line 1: refused above line 1, never capped.
    step(
        "core/at_most", "ca/t2205_line_4_checked", amount="ca/t2205_line_4", bound="ca/t2205_line_1"
    ),
    # Line 5 "Line 3 minus line 4".
    step(
        "core/subtract",
        "ca/t2205_line_5",
        amount="ca/t2205_line_3",
        less="ca/t2205_line_4_checked",
    ),
    # Line 7 is part of line 6: refused above line 6, never capped.
    step(
        "core/at_most", "ca/t2205_line_7_checked", amount="ca/t2205_line_7", bound="ca/t2205_line_6"
    ),
    # Line 8 "Line 6 minus line 7".
    step(
        "core/subtract",
        "ca/t2205_line_8",
        amount="ca/t2205_line_6",
        less="ca/t2205_line_7_checked",
    ),
    # Line 10 "Enter the amount from line 5 or line 8, whichever is less." (line 9 is line 3).
    step("core/lesser_of", "ca/t2205_line_10", amounts=("ca/t2205_line_5", "ca/t2205_line_8")),
    # Line 11 "Line 9 minus line 10", line 9 being the amount from line 3.
    step("core/subtract", "ca/t2205_line_11", amount="ca/t2205_line_3", less="ca/t2205_line_10"),
    # The SPP part of line 11 is part of line 11: refused above it, never capped.
    step(
        "core/at_most",
        "ca/t2205_line_11_spp_part_checked",
        amount="ca/t2205_line_11_spp_part",
        bound="ca/t2205_line_11",
    ),
    # The rest of line 11 relates to RRSP withdrawals.
    step(
        "core/subtract",
        "ca/t2205_line_11_rrsp_part",
        amount="ca/t2205_line_11",
        less="ca/t2205_line_11_spp_part_checked",
    ),
    # Line 14 is part of line 13: refused above line 13, never capped.
    step(
        "core/at_most",
        "ca/t2205_line_14_checked",
        amount="ca/t2205_line_14",
        bound="ca/t2205_line_13",
    ),
    # Line 15 "Line 13 minus line 14".
    step(
        "core/subtract",
        "ca/t2205_line_15",
        amount="ca/t2205_line_13",
        less="ca/t2205_line_14_checked",
    ),
    # Line 16 "Line 12 plus line 15".
    step("core/sum", "ca/t2205_line_16", parts=("ca/t2205_line_12", "ca/t2205_line_15")),
    # Line 17: "If you filled in Part 1 above, enter the amount from line 6." Part 1 is filled in
    # when line 3 is more than 0; otherwise the amount typed on line 17 is used.
    sign_choice(
        "ca/t2205_line_17_used",
        "ca/t2205_line_3",
        when_positive="ca/t2205_line_6",
        when_non_positive="ca/t2205_line_17",
    ),
    # Line 18, Part 1 filled in: "add the amounts from line 7 and line 10 and enter the result".
    step(
        "core/sum",
        "ca/t2205_line_18_from_part_1",
        parts=("ca/t2205_line_7_checked", "ca/t2205_line_10"),
    ),
    # Line 18: that sum when Part 1 is filled in, otherwise the amount typed on line 18.
    sign_choice(
        "ca/t2205_line_18_used",
        "ca/t2205_line_3",
        when_positive="ca/t2205_line_18_from_part_1",
        when_non_positive="ca/t2205_line_18",
    ),
    # Line 18 is part of line 17: refused above line 17, never capped.
    step(
        "core/at_most",
        "ca/t2205_line_18_checked",
        amount="ca/t2205_line_18_used",
        bound="ca/t2205_line_17_used",
    ),
    # Line 19 "Line 17 minus line 18".
    step(
        "core/subtract",
        "ca/t2205_line_19",
        amount="ca/t2205_line_17_used",
        less="ca/t2205_line_18_checked",
    ),
    # Line 21 "Enter the amount from line 16 or line 19, whichever is less."
    step("core/lesser_of", "ca/t2205_line_21", amounts=("ca/t2205_line_16", "ca/t2205_line_19")),
    # Line 22 "Line 20 minus line 21." Signed: the form prints no floor.
    step("core/subtract", "ca/t2205_line_22", amount="ca/t2205_line_20", less="ca/t2205_line_21"),
}

# The wiring of the form's steps, as `test_manifest_t2205.py` reads it from the composed form: the
# capability class, the kinds it consumes and the kinds it produces.
FORM_WIRING = {
    (Sum, frozenset({T2205_LINE_1, T2205_LINE_2}), frozenset({T2205_LINE_3})),
    (AtMost, frozenset({T2205_LINE_4, T2205_LINE_1}), frozenset({T2205_LINE_4_CHECKED})),
    (Subtract, frozenset({T2205_LINE_3, T2205_LINE_4_CHECKED}), frozenset({T2205_LINE_5})),
    (AtMost, frozenset({T2205_LINE_7, T2205_LINE_6}), frozenset({T2205_LINE_7_CHECKED})),
    (Subtract, frozenset({T2205_LINE_6, T2205_LINE_7_CHECKED}), frozenset({T2205_LINE_8})),
    (LesserOf, frozenset({T2205_LINE_5, T2205_LINE_8}), frozenset({T2205_LINE_10})),
    (Subtract, frozenset({T2205_LINE_3, T2205_LINE_10}), frozenset({T2205_LINE_11})),
    (
        AtMost,
        frozenset({T2205_LINE_11_SPP_PART, T2205_LINE_11}),
        frozenset({T2205_LINE_11_SPP_PART_CHECKED}),
    ),
    (
        Subtract,
        frozenset({T2205_LINE_11, T2205_LINE_11_SPP_PART_CHECKED}),
        frozenset({T2205_LINE_11_RRSP_PART}),
    ),
    (AtMost, frozenset({T2205_LINE_14, T2205_LINE_13}), frozenset({T2205_LINE_14_CHECKED})),
    (Subtract, frozenset({T2205_LINE_13, T2205_LINE_14_CHECKED}), frozenset({T2205_LINE_15})),
    (Sum, frozenset({T2205_LINE_12, T2205_LINE_15}), frozenset({T2205_LINE_16})),
    (
        ChooseBySign,
        frozenset({T2205_LINE_3, T2205_LINE_6, T2205_LINE_17}),
        frozenset({T2205_LINE_17_USED}),
    ),
    (
        Sum,
        frozenset({T2205_LINE_7_CHECKED, T2205_LINE_10}),
        frozenset({T2205_LINE_18_FROM_PART_1}),
    ),
    (
        ChooseBySign,
        frozenset({T2205_LINE_3, T2205_LINE_18_FROM_PART_1, T2205_LINE_18}),
        frozenset({T2205_LINE_18_USED}),
    ),
    (
        AtMost,
        frozenset({T2205_LINE_18_USED, T2205_LINE_17_USED}),
        frozenset({T2205_LINE_18_CHECKED}),
    ),
    (
        Subtract,
        frozenset({T2205_LINE_17_USED, T2205_LINE_18_CHECKED}),
        frozenset({T2205_LINE_19}),
    ),
    (LesserOf, frozenset({T2205_LINE_16, T2205_LINE_19}), frozenset({T2205_LINE_21})),
    (Subtract, frozenset({T2205_LINE_20, T2205_LINE_21}), frozenset({T2205_LINE_22})),
}

# The return's own steps, in `03v_t2205_routing.yaml`: the totals of the three exports the return
# reads, and the split of the SPP part and of line 22 between T1 line 11500 (the filer is 65 or
# older at the end of the year, `ca/born_in_1960_or_earlier_checked` is 1) and line 13000.
STEPS: set[CapabilitySelection] = {
    # The RRSP part of line 11: T1 line 12900.
    step(
        "core/record_total",
        "ca/t2205_on_line_12900",
        records="ca/t2205.t2205_line_11_rrsp_part",
    ),
    # The SPP part of line 11, checked.
    step(
        "core/record_total",
        "ca/t2205_spp_part_total",
        records="ca/t2205.t2205_line_11_spp_part_checked",
    ),
    # Line 22.
    step("core/record_total", "ca/t2205_line_22_total", records="ca/t2205.t2205_line_22"),
    # The SPP part: "on line 11500 of your own income tax and benefit return if you are 65 or
    # older at the end of the year, or on line 13000 otherwise".
    step(
        "core/times_count",
        "ca/t2205_spp_part_on_line_11500",
        amount="ca/t2205_spp_part_total",
        count="ca/born_in_1960_or_earlier_checked",
    ),
    step(
        "core/subtract",
        "ca/t2205_spp_part_on_line_13000",
        amount="ca/t2205_spp_part_total",
        less="ca/t2205_spp_part_on_line_11500",
    ),
    # Line 22: "If you were 65 or older at the end of the year ..., report this amount on line 11500
    # ... Otherwise, report it on line 13000."
    step(
        "core/times_count",
        "ca/t2205_line_22_on_line_11500",
        amount="ca/t2205_line_22_total",
        count="ca/born_in_1960_or_earlier_checked",
    ),
    step(
        "core/subtract",
        "ca/t2205_line_22_on_line_13000",
        amount="ca/t2205_line_22_total",
        less="ca/t2205_line_22_on_line_11500",
    ),
    # The two amounts on T1 line 11500 and on T1 line 13000.
    step(
        "core/sum",
        "ca/t2205_on_line_11500",
        parts=("ca/t2205_spp_part_on_line_11500", "ca/t2205_line_22_on_line_11500"),
    ),
    step(
        "core/sum",
        "ca/t2205_on_line_13000",
        parts=("ca/t2205_spp_part_on_line_13000", "ca/t2205_line_22_on_line_13000"),
    ),
}

WIRING: set[object] = {
    (
        RecordTotal,
        frozenset({T2205_LINE_11_RRSP_PART_PER_FORM}),
        frozenset({T2205_ON_LINE_12900}),
    ),
    (
        RecordTotal,
        frozenset({T2205_LINE_11_SPP_PART_CHECKED_PER_FORM}),
        frozenset({T2205_SPP_PART_TOTAL}),
    ),
    (RecordTotal, frozenset({T2205_LINE_22_PER_FORM}), frozenset({T2205_LINE_22_TOTAL})),
    (
        TimesCount,
        frozenset({T2205_SPP_PART_TOTAL, BORN_IN_1960_OR_EARLIER_CHECKED}),
        frozenset({T2205_SPP_PART_ON_LINE_11500}),
    ),
    (
        Subtract,
        frozenset({T2205_SPP_PART_TOTAL, T2205_SPP_PART_ON_LINE_11500}),
        frozenset({T2205_SPP_PART_ON_LINE_13000}),
    ),
    (
        TimesCount,
        frozenset({T2205_LINE_22_TOTAL, BORN_IN_1960_OR_EARLIER_CHECKED}),
        frozenset({T2205_LINE_22_ON_LINE_11500}),
    ),
    (
        Subtract,
        frozenset({T2205_LINE_22_TOTAL, T2205_LINE_22_ON_LINE_11500}),
        frozenset({T2205_LINE_22_ON_LINE_13000}),
    ),
    (
        Sum,
        frozenset({T2205_SPP_PART_ON_LINE_11500, T2205_LINE_22_ON_LINE_11500}),
        frozenset({T2205_ON_LINE_11500}),
    ),
    (
        Sum,
        frozenset({T2205_SPP_PART_ON_LINE_13000, T2205_LINE_22_ON_LINE_13000}),
        frozenset({T2205_ON_LINE_13000}),
    ),
}
