"""CA-ON 2025 end to end: return cg."""

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
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66,
    TAXABLE_CAPITAL_GAINS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# Property 1: years designated after 1981 5 and from 1972 to 1981 0 (designated 5); years owned
# after 1981 43 (1983 to 2025) and from 1972 to 1981 0 (owned 43); proceeds 535000.00, outlays
# 5000.00, adjusted cost base 100000.00, plus one 1; Part 2 does not apply, so lines 11 to 13 are
# 0.00. Form T664 was filed, with the worksheet inputs: years designated after 1981 and before 1995
# 5 and years owned in the same period 12, designated proceeds 200000.00, adjusted cost base at
# February 22, 1994 100000.00, fair market value at that date 200000.00, elected capital gain
# 100000.00, months owned after February 1992 and before March 1994 24 and after 1971 and before
# March 1994 74.
PROPERTY_1 = (
    5,
    0,
    43,
    0,
    "535000.00",
    "5000.00",
    "100000.00",
    1,
    0,
    "0.00",
    "0.00",
    "0.00",
    1,
    5,
    12,
    "200000.00",
    "100000.00",
    "200000.00",
    "100000.00",
    24,
    74,
)
# Property 2: years designated after 1981 3 and from 1972 to 1981 0 (designated 3); years owned
# after 1981 41 (1985 to 2025) and from 1972 to 1981 0 (owned 41); proceeds 294000.00, outlays
# 10000.00, adjusted cost base 120000.00, plus one 1; Part 2 does not apply. Form T664 was filed,
# with the worksheet inputs: years designated and owned before 1995 3 and 10, designated proceeds
# 230000.00 (more than the fair market value, so Chart 1 applies), adjusted cost base at February
# 22, 1994 120000.00, fair market value at that date 200000.00, elected capital gain 20000.00,
# months owned after February 1992 and before March 1994 24 and after 1971 and before March 1994 74.
PROPERTY_2 = (
    3,
    0,
    41,
    0,
    "294000.00",
    "10000.00",
    "120000.00",
    1,
    0,
    "0.00",
    "0.00",
    "0.00",
    1,
    3,
    10,
    "230000.00",
    "120000.00",
    "200000.00",
    "20000.00",
    24,
    74,
)

# Each worksheet line of the return, with its kind, the capability that produces it and its total
# over the two properties: property 1 then property 2 (0 where the form says to enter "0", or where
# Chart 1 is not completed).
WORKSHEET_LINES = {
    3: (PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3, PrincipalResidenceWorksheetLine3Capability, D("8")),
    6: (PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6, PrincipalResidenceWorksheetLine6Capability, D("22")),
    16: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16,
        PrincipalResidenceWorksheetLine16Capability,
        D("220000.00"),
    ),
    17: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17,
        PrincipalResidenceWorksheetLine17Capability,
        D("10000.00"),
    ),
    18: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18,
        PrincipalResidenceWorksheetLine18Capability,
        D("190000.00"),
    ),
    19: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19,
        PrincipalResidenceWorksheetLine19Capability,
        D("390000.00"),
    ),
    21: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21,
        PrincipalResidenceWorksheetLine21Capability,
        D("170000.00"),
    ),
    23: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23,
        PrincipalResidenceWorksheetLine23Capability,
        D("10"),
    ),
    24: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24,
        PrincipalResidenceWorksheetLine24Capability,
        D("880000.00"),
    ),
    26: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26,
        PrincipalResidenceWorksheetLine26Capability,
        D("78000.00"),
    ),
    27: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27,
        PrincipalResidenceWorksheetLine27Capability,
        D("92000.00"),
    ),
    59: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59,
        PrincipalResidenceWorksheetLine59Capability,
        D("92000.00"),
    ),
    61: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61,
        PrincipalResidenceWorksheetLine61Capability,
        D("2208000.00"),
    ),
    63: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63,
        PrincipalResidenceWorksheetLine63Capability,
        D("29837.84"),
    ),
    64: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64,
        PrincipalResidenceWorksheetLine64Capability,
        D("62162.16"),
    ),
    66: (
        PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66,
        PrincipalResidenceWorksheetLine66Capability,
        D("53783.78"),
    ),
}


def return_cg(**overrides: Any) -> Worksheet:
    """Return CG's inputs, as in `returns/2025_return_cg.yaml`: employment income of 60000 and two
    principal residence properties sold, each under a capital gains election (Form T664, with
    Part 4 of Form T2091(IND) applying), neither with Part 2; `overrides` replace any keyword of
    `compute`, for the variants below.
    """
    given: dict[str, Any] = {
        "principal_residence_properties_rows": (PROPERTY_1, PROPERTY_2),
        "income_tax_deducted": "25000",
    }
    return compute("60000", (), "0", "0", "0", "0", "0", **{**given, **overrides})


def test_return_cgs_worksheet_lines_are_the_totals_over_both_properties() -> None:
    # Property 1: line 3 = 5 + 0 = 5; line 6 = 12 + 0 = 12; no Chart 1, so line 19 = 200000.00;
    # line 21 = 200000.00 - 100000.00 = 100000.00; line 23 = 5 + 1 = 6; line 24 = 600000.00; line
    # 26 = 600000.00 / 12 = 50000.00; line 27 = 50000.00; line 59 = 50000.00; line 61 = 1200000.00;
    # line 63 = 1200000.00 / 74 = 16216.22 (half-up); line 64 = 33783.78; line 66 = 33783.78.
    # Property 2: line 3 = 3; line 6 = 10; Chart 1 gives line 16 = 220000.00, line 17 = 10000.00
    # and line 18 = 190000.00, so line 19 = 190000.00; line 21 = 190000.00 - 120000.00 = 70000.00;
    # line 23 = 3 + 1 = 4; line 24 = 280000.00; line 26 = 28000.00; line 27 = 42000.00; line 59 =
    # 42000.00; line 61 = 1008000.00; line 63 = 13621.62 (half-up); line 64 = 28378.38; line 66 =
    # the lesser of 28378.38 and 20000.00, so 20000.00.
    worksheet = return_cg()

    for number, (kind, capability, total) in WORKSHEET_LINES.items():
        assert isinstance(worksheet.producer_of(kind), capability), number
        assert worksheet.get(kind).value == total, number


def test_return_cgs_part_4_lines_are_the_totals_over_both_properties() -> None:
    # Line 56 = 33783.78 + 20000.00 = 53783.78; line 57 = (370000.00 - 33783.78) + (148000.00 -
    # 20000.00) = 336216.22 + 128000.00 = 464216.22, the amount on line 15800 of Schedule 3.
    worksheet = return_cg()

    assert isinstance(
        worksheet.producer_of(PRINCIPAL_RESIDENCE_LINE_56), PrincipalResidencePart4Line56
    )
    assert worksheet.get(PRINCIPAL_RESIDENCE_LINE_56).value == D("53783.78")
    assert isinstance(
        worksheet.producer_of(PRINCIPAL_RESIDENCE_LINE_57), PrincipalResidencePart4Line57
    )
    assert worksheet.get(PRINCIPAL_RESIDENCE_LINE_57).value == D("464216.22")


def test_return_cgs_each_property_line_57_is_its_line_55_less_its_line_56() -> None:
    # Property 1 alone: line 54 = 370000.00 (line 24 = 430000.00 - 60000.00), line 55 = 370000.00,
    # line 56 = 33783.78, so line 57 = 336216.22. Property 2 alone: line 54 = 148000.00 (line 24 =
    # 164000.00 - 16000.00), line 56 = 20000.00, so line 57 = 128000.00.
    first = return_cg(principal_residence_properties_rows=(PROPERTY_1,))
    second = return_cg(principal_residence_properties_rows=(PROPERTY_2,))

    assert first.get(PRINCIPAL_RESIDENCE_GAIN).value == D("370000.00")
    assert first.get(PRINCIPAL_RESIDENCE_LINE_56).value == D("33783.78")
    assert first.get(PRINCIPAL_RESIDENCE_LINE_57).value == D("336216.22")
    assert second.get(PRINCIPAL_RESIDENCE_GAIN).value == D("148000.00")
    assert second.get(PRINCIPAL_RESIDENCE_LINE_56).value == D("20000.00")
    assert second.get(PRINCIPAL_RESIDENCE_LINE_57).value == D("128000.00")


def test_return_cgs_chart_1_is_worked_only_for_property_2() -> None:
    # Property 1: its line 7 (200000.00) is not more than its line 10 (200000.00), so there is no
    # Chart 1: line 16 is 0 and line 19 is the fair market value, 200000.00. Property 2: its line 7
    # (230000.00) is more than its line 10 (200000.00), so line 16 = 220000.00, line 17 =
    # 10000.00, line 18 = 190000.00 and line 19 = 190000.00.
    first = return_cg(principal_residence_properties_rows=(PROPERTY_1,))
    second = return_cg(principal_residence_properties_rows=(PROPERTY_2,))

    assert first.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16).value == D("0")
    assert first.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19).value == D("200000.00")
    assert second.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16).value == D("220000.00")
    assert second.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17).value == D("10000.00")
    assert second.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18).value == D("190000.00")
    assert second.get(PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19).value == D("190000.00")


def test_return_cgs_line_15800_and_taxable_gains_follow_the_line_57_total() -> None:
    # Line 57 of each form is entered on line 15800 of Schedule 3, the personal-use property gain
    # of Part 3 ("Line 9 and line 15800: Total gain only"): the rows add 0, so line 9 is 464216.22,
    # and it is the whole of the total capital gains or losses (line 21, 19700). Line 24 of
    # Schedule 3 = 464216.22 x 50% = 232108.11 exactly, so line 12700 is 232108.11. Total income
    # (line 15000) = 60000.00 + 232108.11 = 292108.11. The net and taxable income, total payable
    # and balance owing are the engine's figures, not pinned here.
    worksheet = return_cg()

    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN_ROWS).value == D("0")
    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN).value == D("464216.22")
    assert worksheet.get(CAPITAL_GAIN).value == D("464216.22")
    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("232108.11")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("232108.11")
    assert worksheet.get(TOTAL_INCOME).value == D("292108.11")


def test_no_properties_sold_add_nothing_to_the_part_4_lines() -> None:
    worksheet = return_cg(principal_residence_properties_rows=())

    for number, (kind, _, _) in WORKSHEET_LINES.items():
        assert worksheet.get(kind).value == D("0"), number
    assert worksheet.get(PRINCIPAL_RESIDENCE_LINE_56).value == D("0")
    assert worksheet.get(PRINCIPAL_RESIDENCE_LINE_57).value == D("0")
    assert worksheet.get(PRINCIPAL_RESIDENCE_GAIN).value == D("0")


def test_return_cgs_trace_names_line_57_of_each_property_in_english() -> None:
    rendered = EnglishTraceRenderer().render_all(return_cg().trace)

    first = rendered.index(
        "principal_residence_line_57: property 1: line 57 336216.22 = line 55 370000 less "
        "line 56 33783.78, not below 0"
    )
    assert rendered[first : first + 3] == (
        "principal_residence_line_57: property 1: line 57 336216.22 = line 55 370000 less "
        "line 56 33783.78, not below 0",
        "principal_residence_line_57: property 2: line 57 128000 = line 55 148000 less "
        "line 56 20000, not below 0",
        "principal_residence_line_57: item 1 336216.22 + item 2 128000 = 464216.22",
    )
