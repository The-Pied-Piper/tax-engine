"""CA-ON 2025 end to end: return bw."""

from __future__ import annotations

from typing import Any

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.capabilities.principal_residence_gain import (
    PrincipalResidenceGain,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_27 import (
    PrincipalResidencePart2Line27,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_29 import (
    PrincipalResidencePart2Line29,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_30 import (
    PrincipalResidencePart2Line30,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_32 import (
    PrincipalResidencePart2Line32,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_33 import (
    PrincipalResidencePart2Line33,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_38 import (
    PrincipalResidencePart2Line38,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_39 import (
    PrincipalResidencePart2Line39,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_42 import (
    PrincipalResidencePart2Line42,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_44 import (
    PrincipalResidencePart2Line44,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_45 import (
    PrincipalResidencePart2Line45,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_48 import (
    PrincipalResidencePart2Line48,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_51 import (
    PrincipalResidencePart2Line51,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_53 import (
    PrincipalResidencePart2Line53,
)
from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    PERSONAL_USE_PROPERTY_GAIN,
    PERSONAL_USE_PROPERTY_GAIN_ROWS,
    PRINCIPAL_RESIDENCE_GAIN,
    PRINCIPAL_RESIDENCE_LINE_27,
    PRINCIPAL_RESIDENCE_LINE_29,
    PRINCIPAL_RESIDENCE_LINE_30,
    PRINCIPAL_RESIDENCE_LINE_32,
    PRINCIPAL_RESIDENCE_LINE_33,
    PRINCIPAL_RESIDENCE_LINE_38,
    PRINCIPAL_RESIDENCE_LINE_39,
    PRINCIPAL_RESIDENCE_LINE_42,
    PRINCIPAL_RESIDENCE_LINE_44,
    PRINCIPAL_RESIDENCE_LINE_45,
    PRINCIPAL_RESIDENCE_LINE_48,
    PRINCIPAL_RESIDENCE_LINE_51,
    PRINCIPAL_RESIDENCE_LINE_53,
    TAXABLE_CAPITAL_GAINS,
    TOTAL_INCOME,
)
from tax_engine.jurisdictions.ca.trace import (
    PrincipalResidenceGainLine,
    PrincipalResidenceLine33,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute

# Property 1: years designated after 1981 6 and from 1972 to 1981 1 (designated 7); years owned
# after 1981 10 and from 1972 to 1981 4 (owned 14); proceeds 300000.00, outlays 5000.00, adjusted
# cost base 100000.00, plus one 1; Part 2 applies, with line 11 40000.00, line 12 90000.00 and
# line 13 10000.00.
PROPERTY_1 = (
    6,
    1,
    10,
    4,
    "300000.00",
    "5000.00",
    "100000.00",
    1,
    1,
    "40000.00",
    "90000.00",
    "10000.00",
)
# Property 2: years designated after 1981 2 and from 1972 to 1981 2 (designated 4); years owned
# after 1981 10 and from 1972 to 1981 2 (owned 12); proceeds 300000.00, outlays 0.00, adjusted cost
# base 100000.00, no plus one; Part 2 applies, with line 11 150000.00, line 12 280000.00 and line 13
# 0.00.
PROPERTY_2 = (2, 2, 10, 2, "300000.00", "0.00", "100000.00", 0, 1, "150000.00", "280000.00", "0.00")

# Each Part 2 line of the return, with its kind, the capability that produces it and its total over
# the two properties: property 1 then property 2 (0 where the form says to enter "0", or where the
# area is not completed).
PART_2_LINES = {
    27: (PRINCIPAL_RESIDENCE_LINE_27, PrincipalResidencePart2Line27, D("50000.00")),
    29: (PRINCIPAL_RESIDENCE_LINE_29, PrincipalResidencePart2Line29, D("2")),
    30: (PRINCIPAL_RESIDENCE_LINE_30, PrincipalResidencePart2Line30, D("100000.00")),
    32: (PRINCIPAL_RESIDENCE_LINE_32, PrincipalResidencePart2Line32, D("25000.00")),
    33: (PRINCIPAL_RESIDENCE_LINE_33, PrincipalResidencePart2Line33, D("25000.00")),
    38: (PRINCIPAL_RESIDENCE_LINE_38, PrincipalResidencePart2Line38, D("385000.00")),
    39: (PRINCIPAL_RESIDENCE_LINE_39, PrincipalResidencePart2Line39, D("215000.00")),
    42: (PRINCIPAL_RESIDENCE_LINE_42, PrincipalResidencePart2Line42, D("1210000.00")),
    44: (PRINCIPAL_RESIDENCE_LINE_44, PrincipalResidencePart2Line44, D("121000.00")),
    45: (PRINCIPAL_RESIDENCE_LINE_45, PrincipalResidencePart2Line45, D("94000.00")),
    48: (PRINCIPAL_RESIDENCE_LINE_48, PrincipalResidencePart2Line48, D("0")),
    51: (PRINCIPAL_RESIDENCE_LINE_51, PrincipalResidencePart2Line51, D("119000.00")),
    53: (PRINCIPAL_RESIDENCE_LINE_53, PrincipalResidencePart2Line53, D("119000.00")),
}


def return_bw(**overrides: Any) -> Worksheet:
    """Return BW's inputs, as in `returns/2025_return_bw.yaml`: employment income of 60000 and two
    principal residence properties sold, each a chosen figure, both with Part 2 of Form T2091(IND)
    applying; `overrides` replace any keyword of `compute`, for the variants below.
    """
    given: dict[str, Any] = {
        "principal_residence_properties_rows": (PROPERTY_1, PROPERTY_2),
        "income_tax_deducted": "25000",
    }
    return compute("60000", (), "0", "0", "0", "0", "0", **{**given, **overrides})


def test_return_bws_part_2_lines_are_the_totals_over_both_properties() -> None:
    # Property 1: line 27 = 90000.00 - 40000.00 = 50000.00; line 30 = 50000.00 x 2 = 100000.00;
    # line 32 = 100000.00 / 4 = 25000.00; line 33 = 25000.00. Property 1 area B: line 38 =
    # 90000.00 + 10000.00 + 5000.00 = 105000.00; line 39 = 195000.00; line 42 = 195000.00 x 6 =
    # 1170000.00; line 44 = 117000.00; line 45 = 78000.00. Property 1 area D: line 51 = 25000.00 +
    # 78000.00 = 103000.00; line 53 = 103000.00. Property 2 area A is skipped (lines 27 to 33 are
    # 0; line 29 is 0), and its area B: line 38 = 280000.00; line 39 = 20000.00; line 42 =
    # 20000.00 x 2 = 40000.00; line 44 = 4000.00; line 45 = 16000.00; line 48 = 280000.00 -
    # 300000.00, below 0, so 0; line 51 = 0 + 16000.00 = 16000.00; line 53 = 16000.00. Each line is
    # the total over the two properties.
    worksheet = return_bw()

    for number, (kind, capability, total) in PART_2_LINES.items():
        assert isinstance(worksheet.producer_of(kind), capability), number
        assert worksheet.get(kind).value == total, number


def test_return_bws_line_54_is_the_lesser_of_line_53_and_line_24_for_each_property() -> None:
    # Property 1: line 24 = 83571.43 (line 18 = 195000.00, line 23 = 111428.57), line 53 =
    # 103000.00, so line 54 = 83571.43. Property 2: line 24 = 133333.33, line 53 = 16000.00, so
    # line 54 = 16000.00. The total is 83571.43 + 16000.00 = 99571.43, the amount on line 15800
    # of Schedule 3.
    worksheet = return_bw()

    assert isinstance(worksheet.producer_of(PRINCIPAL_RESIDENCE_GAIN), PrincipalResidenceGain)
    assert worksheet.get(PRINCIPAL_RESIDENCE_GAIN).value == D("99571.43")


def test_return_bws_taxable_gains_are_schedule_3_line_9_and_line_15800() -> None:
    # Line 54 of each form is entered on line 15800 of Schedule 3, the personal-use property gain
    # of Part 3 ("Line 9 and line 15800: Total gain only"): the rows add 0, so line 9 is 99571.43,
    # and it is the whole of the total capital gains or losses (line 21, 19700).
    worksheet = return_bw()

    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN_ROWS).value == D("0")
    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN).value == D("99571.43")
    assert worksheet.get(CAPITAL_GAIN).value == D("99571.43")


def test_return_bws_taxable_capital_gains_are_49785_72_on_line_12700() -> None:
    # Line 24 of Schedule 3 = 99571.43 x 50% = 49785.715, half-up to the cent 49785.72, positive, so
    # line 12700 is 49785.72. Total income (line 15000) = 60000 + 49785.72 = 109785.72. The net and
    # taxable income, total payable and balance owing are the engine's figures, not pinned here.
    worksheet = return_bw()

    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("49785.72")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("49785.72")
    assert worksheet.get(TOTAL_INCOME).value == D("109785.72")


def test_return_bws_trace_names_each_property_and_totals_line_54() -> None:
    worksheet = return_bw()

    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, PrincipalResidenceGainLine | ItemsTotalLine)
        and line.output == PRINCIPAL_RESIDENCE_GAIN
    ]
    assert lines == [
        PrincipalResidenceGainLine(
            output=PRINCIPAL_RESIDENCE_GAIN,
            position=1,
            years_designated_after_1981=6,
            years_designated_1972_to_1981=1,
            designated=7,
            years_owned_after_1981=10,
            years_owned_1972_to_1981=4,
            owned=14,
            plus_one=1,
            proceeds=D("300000.00"),
            adjusted_cost_base=D("100000.00"),
            outlays=D("5000.00"),
            gain=D("195000.00"),
            line_20=8,
            line_21=D("1560000.00"),
            rounding=CENT,
            exempt=D("111428.57"),
            part_2_applies=1,
            line_53=D("103000.00"),
            line_24=D("83571.43"),
            result=D("83571.43"),
        ),
        PrincipalResidenceGainLine(
            output=PRINCIPAL_RESIDENCE_GAIN,
            position=2,
            years_designated_after_1981=2,
            years_designated_1972_to_1981=2,
            designated=4,
            years_owned_after_1981=10,
            years_owned_1972_to_1981=2,
            owned=12,
            plus_one=0,
            proceeds=D("300000.00"),
            adjusted_cost_base=D("100000.00"),
            outlays=D("0.00"),
            gain=D("200000.00"),
            line_20=4,
            line_21=D("800000.00"),
            rounding=CENT,
            exempt=D("66666.67"),
            part_2_applies=1,
            line_53=D("16000.00"),
            line_24=D("133333.33"),
            result=D("16000.00"),
        ),
        ItemsTotalLine(
            output=PRINCIPAL_RESIDENCE_GAIN,
            items=((1, D("83571.43")), (2, D("16000.00"))),
            total=D("99571.43"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    first = rendered.index(
        "principal_residence_gain: property 1: gain 195000 = proceeds 300000 less adjusted cost "
        "base 100000 less outlays 5000; exempt 111428.57 = 195000 × (7 designated + 1) ÷ 14 owned "
        "(half-up to 0.01); taxable gain 83571.43 = 195000 less 111428.57, not below 0; Part 2 net "
        "capital gain 103000; total capital gain 83571.43 = lesser of 103000 and 83571.43"
    )
    assert rendered[first : first + 3] == (
        "principal_residence_gain: property 1: gain 195000 = proceeds 300000 less adjusted cost "
        "base 100000 less outlays 5000; exempt 111428.57 = 195000 × (7 designated + 1) ÷ 14 owned "
        "(half-up to 0.01); taxable gain 83571.43 = 195000 less 111428.57, not below 0; Part 2 net "
        "capital gain 103000; total capital gain 83571.43 = lesser of 103000 and 83571.43",
        "principal_residence_gain: property 2: gain 200000 = proceeds 300000 less adjusted cost "
        "base 100000 less outlays 0; exempt 66666.67 = 200000 × (4 designated + 0) ÷ 12 owned "
        "(half-up to 0.01); taxable gain 133333.33 = 200000 less 66666.67, not below 0; Part 2 net "
        "capital gain 16000; total capital gain 16000 = lesser of 16000 and 133333.33",
        "principal_residence_gain: item 1 83571.43 + item 2 16000 = 99571.43",
    )


def test_return_bws_trace_names_the_pre_1982_gain_of_each_property_in_english() -> None:
    # Line 33 of Part 2 for property 1: line 27 50000 less line 32 25000, not below 0, so 25000.
    # Property 2 has area A skipped (every year before 1982 designated), so its line 33 is not
    # completed and is 0. The total over the two properties is 25000.
    worksheet = return_bw()

    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, PrincipalResidenceLine33 | ItemsTotalLine)
        and line.output == PRINCIPAL_RESIDENCE_LINE_33
    ]
    assert [type(line) for line in lines] == [
        PrincipalResidenceLine33,
        PrincipalResidenceLine33,
        ItemsTotalLine,
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    property_1 = (
        "principal_residence_line_33: property 1: line 33 25000 = line 27 50000 less line 32 "
        "25000, not below 0"
    )
    first = rendered.index(property_1)
    assert rendered[first : first + 3] == (
        property_1,
        "principal_residence_line_33: property 2: line 33 not completed, 0",
        "principal_residence_line_33: item 1 25000 + item 2 0 = 25000",
    )


def test_no_properties_sold_add_nothing_to_the_part_2_lines() -> None:
    worksheet = return_bw(principal_residence_properties_rows=())

    for number, (kind, _, _) in PART_2_LINES.items():
        assert worksheet.get(kind).value == D("0"), number
    assert worksheet.get(PRINCIPAL_RESIDENCE_GAIN).value == D("0")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "principal_residence_line_33: no items = 0" in rendered
