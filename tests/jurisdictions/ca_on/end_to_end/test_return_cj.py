"""CA-ON 2025 end to end: return cj."""

from __future__ import annotations

from typing import Any

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_56 import (
    PrincipalResidencePart4Line56,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_57 import (
    PrincipalResidencePart4Line57,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_3 import (
    PrincipalResidenceWorksheetLine3Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_6 import (
    PrincipalResidenceWorksheetLine6Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_16 import (
    PrincipalResidenceWorksheetLine16Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_17 import (
    PrincipalResidenceWorksheetLine17Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_18 import (
    PrincipalResidenceWorksheetLine18Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_19 import (
    PrincipalResidenceWorksheetLine19Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_21 import (
    PrincipalResidenceWorksheetLine21Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_23 import (
    PrincipalResidenceWorksheetLine23Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_24 import (
    PrincipalResidenceWorksheetLine24Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_26 import (
    PrincipalResidenceWorksheetLine26Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_27 import (
    PrincipalResidenceWorksheetLine27Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_30 import (
    PrincipalResidenceWorksheetLine30Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_32 import (
    PrincipalResidenceWorksheetLine32Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_33 import (
    PrincipalResidenceWorksheetLine33Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_35 import (
    PrincipalResidenceWorksheetLine35Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_36 import (
    PrincipalResidenceWorksheetLine36Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_40 import (
    PrincipalResidenceWorksheetLine40Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_41 import (
    PrincipalResidenceWorksheetLine41Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_44 import (
    PrincipalResidenceWorksheetLine44Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_46 import (
    PrincipalResidenceWorksheetLine46Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_47 import (
    PrincipalResidenceWorksheetLine47Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_50 import (
    PrincipalResidenceWorksheetLine50Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_53 import (
    PrincipalResidenceWorksheetLine53Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_55 import (
    PrincipalResidenceWorksheetLine55Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_58 import (
    PrincipalResidenceWorksheetLine58Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_59 import (
    PrincipalResidenceWorksheetLine59Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_61 import (
    PrincipalResidenceWorksheetLine61Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_63 import (
    PrincipalResidenceWorksheetLine63Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_64 import (
    PrincipalResidenceWorksheetLine64Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_66 import (
    PrincipalResidenceWorksheetLine66Capability,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    PERSONAL_USE_PROPERTY_GAIN,
    PERSONAL_USE_PROPERTY_GAIN_ROWS,
    PRINCIPAL_RESIDENCE_GAIN,
    PRINCIPAL_RESIDENCE_LINE_56,
    PRINCIPAL_RESIDENCE_LINE_57,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_30,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_32,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_33,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_35,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_36,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_40,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_41,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_44,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_46,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_53,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_55,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_58,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66,
    TAXABLE_CAPITAL_GAINS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# Property 1: years designated after 1981 20 and from 1972 to 1981 1 (designated 21); years owned
# after 1981 44 and from 1972 to 1981 4 (owned 48); proceeds 700000.00, outlays 20000.00, adjusted
# cost base 200000.00, plus one 1. Part 2 applies, so lines 11 to 13 are 120000.00 (the cost base
# on December 31, 1981), 240000.00 (the fair market value on that date) and 10000.00 (the
# adjustments after 1981). Form T664 was filed, with the worksheet inputs: years
# designated after 1981 and before 1995 4 and years owned in the same period 13, designated
# proceeds 280000.00, adjusted cost base at February 22, 1994 210000.00, fair market value at that
# date 300000.00, elected capital gain 150000.00, months owned after February 1992 and before March
# 1994 24 and after 1971 and before March 1994 150, and adjustments after 1981 and before February
# 23, 1994 6000.00.
PROPERTY_1 = (
    20,
    1,
    44,
    4,
    "700000.00",
    "20000.00",
    "200000.00",
    1,
    1,
    "120000.00",
    "240000.00",
    "10000.00",
    1,
    4,
    13,
    "280000.00",
    "210000.00",
    "300000.00",
    "150000.00",
    24,
    150,
    "6000.00",
)

# Property 2: years designated after 1981 10 and from 1972 to 1981 0 (designated 10); years owned
# after 1981 30 and from 1972 to 1981 2 (owned 32); proceeds 500000.00, outlays 5000.00, adjusted
# cost base 175000.00, plus one 1. Part 2 applies: cost base on December 31, 1981 200000.00, fair
# market value on that date 360000.00 (more than its line 19, so worksheet area B is skipped) and
# adjustments after 1981 20000.00. Form T664 was filed, with the worksheet inputs: years designated
# after 1981 and before 1995 3 and years owned in the same period 13, designated proceeds
# 340000.00 (more than the fair market value, so Chart 1 applies), adjusted cost base at February
# 22, 1994 180000.00, fair market value at that date 300000.00, elected capital gain 60000.00,
# months owned after February 1992 and before March 1994 20 and after 1971 and before March 1994
# 150, and adjustments after 1981 and before February 23, 1994 4000.00.
PROPERTY_2 = (
    10,
    0,
    30,
    2,
    "500000.00",
    "5000.00",
    "175000.00",
    1,
    1,
    "200000.00",
    "360000.00",
    "20000.00",
    1,
    3,
    13,
    "340000.00",
    "180000.00",
    "300000.00",
    "60000.00",
    20,
    150,
    "4000.00",
)

# Each worksheet line of the return, with its kind, the capability that produces it and its total
# over the two properties: property 1 then property 2 (0 where the form says to enter "0", or where
# a step is not completed). Part 2 of the worksheet (lines 28 to 58) is worked for both properties.
WORKSHEET_LINES = {
    3: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3,
        PrincipalResidenceWorksheetLine3Capability,
        D("8"),
    ),
    6: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6,
        PrincipalResidenceWorksheetLine6Capability,
        D("32"),
    ),
    16: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16,
        PrincipalResidenceWorksheetLine16Capability,
        D("330000.00"),
    ),
    17: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17,
        PrincipalResidenceWorksheetLine17Capability,
        D("10000.00"),
    ),
    18: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18,
        PrincipalResidenceWorksheetLine18Capability,
        D("290000.00"),
    ),
    19: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19,
        PrincipalResidenceWorksheetLine19Capability,
        D("590000.00"),
    ),
    21: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21,
        PrincipalResidenceWorksheetLine21Capability,
        D("200000.00"),
    ),
    23: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23,
        PrincipalResidenceWorksheetLine23Capability,
        D("10"),
    ),
    24: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24,
        PrincipalResidenceWorksheetLine24Capability,
        D("980000.00"),
    ),
    26: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26,
        PrincipalResidenceWorksheetLine26Capability,
        D("61098.04"),
    ),
    27: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27,
        PrincipalResidenceWorksheetLine27Capability,
        D("138901.96"),
    ),
    30: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_30,
        PrincipalResidenceWorksheetLine30Capability,
        D("280000.00"),
    ),
    32: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_32,
        PrincipalResidenceWorksheetLine32Capability,
        D("3"),
    ),
    33: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_33,
        PrincipalResidenceWorksheetLine33Capability,
        D("400000.00"),
    ),
    35: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_35,
        PrincipalResidenceWorksheetLine35Capability,
        D("140000.00"),
    ),
    36: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_36,
        PrincipalResidenceWorksheetLine36Capability,
        D("140000.00"),
    ),
    40: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_40,
        PrincipalResidenceWorksheetLine40Capability,
        D("246000.00"),
    ),
    41: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_41,
        PrincipalResidenceWorksheetLine41Capability,
        D("54000.00"),
    ),
    44: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_44,
        PrincipalResidenceWorksheetLine44Capability,
        D("216000.00"),
    ),
    46: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_46,
        PrincipalResidenceWorksheetLine46Capability,
        D("16615.38"),
    ),
    47: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47,
        PrincipalResidenceWorksheetLine47Capability,
        D("37384.62"),
    ),
    50: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50,
        PrincipalResidenceWorksheetLine50Capability,
        D("70000.00"),
    ),
    53: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_53,
        PrincipalResidenceWorksheetLine53Capability,
        D("177384.62"),
    ),
    55: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_55,
        PrincipalResidenceWorksheetLine55Capability,
        D("107384.62"),
    ),
    58: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_58,
        PrincipalResidenceWorksheetLine58Capability,
        D("68235.29"),
    ),
    59: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59,
        PrincipalResidenceWorksheetLine59Capability,
        D("68235.29"),
    ),
    61: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61,
        PrincipalResidenceWorksheetLine61Capability,
        D("1597646.96"),
    ),
    63: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63,
        PrincipalResidenceWorksheetLine63Capability,
        D("10650.98"),
    ),
    64: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64,
        PrincipalResidenceWorksheetLine64Capability,
        D("57584.31"),
    ),
    66: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66,
        PrincipalResidenceWorksheetLine66Capability,
        D("57584.31"),
    ),
}


def return_cj(**overrides: Any) -> Worksheet:
    """Return CJ's inputs, as in `returns/2025_return_cj.yaml`: employment income of 60000 and two
    principal residence properties sold, each under a capital gains election (Form T664, with Part
    4 of Form T2091(IND) applying), each with Part 2 applying; `overrides` replace any keyword of
    `compute`, for the variants below.
    """
    given: dict[str, Any] = {
        "principal_residence_properties_rows": (PROPERTY_1, PROPERTY_2),
        "income_tax_deducted": "25000",
    }
    return compute("60000", (), "0", "0", "0", "0", "0", **{**given, **overrides})


def test_return_cjs_worksheet_lines_are_the_totals_over_both_properties() -> None:
    # Part 1 of the worksheet and the lines of Part 2 and Part 3 that the properties give; each
    # total is the sum of the property's own line (see the comments of the yaml for each one).
    worksheet = return_cj()

    for number, (kind, capability, total) in WORKSHEET_LINES.items():
        assert isinstance(worksheet.producer_of(kind), capability), number
        assert worksheet.get(kind).value == total, number


def test_return_cjs_part_4_lines_are_the_totals_over_both_properties() -> None:
    # Line 56 = 48917.64 + 8666.67 = 57584.31; line 57 = (260000.00 - 48917.64) + (156666.67 -
    # 8666.67) = 211082.36 + 148000.00 = 359082.36, the amount on line 15800 of Schedule 3.
    worksheet = return_cj()

    assert isinstance(
        worksheet.producer_of(PRINCIPAL_RESIDENCE_LINE_56), PrincipalResidencePart4Line56
    )
    assert worksheet.get(PRINCIPAL_RESIDENCE_LINE_56).value == D("57584.31")
    assert isinstance(
        worksheet.producer_of(PRINCIPAL_RESIDENCE_LINE_57), PrincipalResidencePart4Line57
    )
    assert worksheet.get(PRINCIPAL_RESIDENCE_LINE_57).value == D("359082.36")


def test_return_cjs_each_property_line_57_is_its_line_55_less_its_line_56() -> None:
    # Property 1 alone: line 54 = 260000.00, so line 55 = 260000.00 and line 56 = 48917.64, so line
    # 57 = 211082.36. Property 2 alone: line 54 = 156666.67, line 56 = 8666.67, so line 57 =
    # 148000.00.
    first = return_cj(principal_residence_properties_rows=(PROPERTY_1,))
    second = return_cj(principal_residence_properties_rows=(PROPERTY_2,))

    assert first.get(PRINCIPAL_RESIDENCE_GAIN).value == D("260000.00")
    assert first.get(PRINCIPAL_RESIDENCE_LINE_56).value == D("48917.64")
    assert first.get(PRINCIPAL_RESIDENCE_LINE_57).value == D("211082.36")
    assert second.get(PRINCIPAL_RESIDENCE_GAIN).value == D("156666.67")
    assert second.get(PRINCIPAL_RESIDENCE_LINE_56).value == D("8666.67")
    assert second.get(PRINCIPAL_RESIDENCE_LINE_57).value == D("148000.00")


def test_return_cjs_part_2_area_b_is_skipped_for_property_2_and_worked_for_property_1() -> None:
    # Property 2: its line 11 (360000.00) is more than its line 19 (290000.00), so the worksheet's
    # area B (lines 40 to 47) is 0 and line 50 (area C) is 360000.00 - 290000.00 = 70000.00.
    # Property 1: area B is worked, line 47 = 37384.62, and its area C line 50 is 0.
    first = return_cj(principal_residence_properties_rows=(PROPERTY_1,))
    second = return_cj(principal_residence_properties_rows=(PROPERTY_2,))

    assert first.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47).value == D("37384.62")
    assert first.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50).value == D("0")
    assert second.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47).value == D("0")
    assert second.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50).value == D("70000.00")


def test_return_cjs_line_59_is_line_58_of_each_property_that_completes_part_2() -> None:
    # Line 59 of Part 3 is line 58 of Part 2 for both properties: 58235.29 and 10000.00.
    first = return_cj(principal_residence_properties_rows=(PROPERTY_1,))
    second = return_cj(principal_residence_properties_rows=(PROPERTY_2,))

    assert first.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59).value == D("58235.29")
    assert second.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59).value == D("10000.00")


def test_return_cjs_line_15800_and_taxable_gains_follow_the_line_57_total() -> None:
    # Line 57 of each form is entered on line 15800 of Schedule 3, the personal-use property gain
    # of Part 3 ("Line 9 and line 15800: Total gain only"): the rows add 0, so line 9 is 359082.36,
    # and it is the whole of the total capital gains or losses (line 21, 19700). Line 24 of Schedule
    # 3 = 359082.36 x 50% = 179541.18 exactly, so line 12700 is 179541.18. Total income (line
    # 15000) = 60000.00 + 179541.18 = 239541.18. The net and taxable income, total payable and
    # balance owing are the engine's figures, not pinned here.
    worksheet = return_cj()

    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN_ROWS).value == D("0")
    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN).value == D("359082.36")
    assert worksheet.get(CAPITAL_GAIN).value == D("359082.36")
    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("179541.18")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("179541.18")
    assert worksheet.get(TOTAL_INCOME).value == D("239541.18")


def test_no_properties_sold_add_nothing_to_the_part_2_or_part_4_lines() -> None:
    worksheet = return_cj(principal_residence_properties_rows=())

    for number, (kind, _, _) in WORKSHEET_LINES.items():
        assert worksheet.get(kind).value == D("0"), number
    assert worksheet.get(PRINCIPAL_RESIDENCE_LINE_56).value == D("0")
    assert worksheet.get(PRINCIPAL_RESIDENCE_LINE_57).value == D("0")
    assert worksheet.get(PRINCIPAL_RESIDENCE_GAIN).value == D("0")


def test_return_cjs_trace_names_line_57_and_line_59_of_each_property_in_english() -> None:
    rendered = EnglishTraceRenderer().render_all(return_cj().trace)

    first = rendered.index(
        "principal_residence_line_57: property 1: line 57 211082.36 = line 55 260000 less "
        "line 56 48917.64, not below 0"
    )
    assert rendered[first : first + 3] == (
        "principal_residence_line_57: property 1: line 57 211082.36 = line 55 260000 less "
        "line 56 48917.64, not below 0",
        "principal_residence_line_57: property 2: line 57 148000 = line 55 156666.67 less "
        "line 56 8666.67, not below 0",
        "principal_residence_line_57: item 1 211082.36 + item 2 148000 = 359082.36",
    )
    assert (
        "principal_residence_worksheet_line_59: property 2: worksheet line 59 10000 = "
        "worksheet line 58 10000 (Part 2 completed)"
    ) in rendered
