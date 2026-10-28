"""CA-ON 2025 end to end: return ai."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import ValidationError
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_gain import (
    PrincipalResidenceGain,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    NET_INCOME,
    PERSONAL_USE_PROPERTY_GAIN,
    PERSONAL_USE_PROPERTY_GAIN_ROWS,
    PRINCIPAL_RESIDENCE_GAIN,
    PRINCIPAL_RESIDENCE_PROPERTIES,
    REFUND_OR_BALANCE_OWING,
    RESIDENCE_ADJUSTED_COST_BASE,
    RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
    RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
    RESIDENCE_FMV_DEC_31_1981,
    RESIDENCE_OUTLAYS,
    RESIDENCE_PART_2_APPLIES,
    RESIDENCE_PLUS_ONE_YEAR,
    RESIDENCE_PROCEEDS,
    RESIDENCE_T664_FILED,
    RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994,
    RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994,
    RESIDENCE_WS_DESIGNATED_PROCEEDS,
    RESIDENCE_WS_ELECTED_CAPITAL_GAIN,
    RESIDENCE_WS_FMV_FEB_22_1994,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_1971,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992,
    RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_WS_YEARS_OWNED_AFTER_1981,
    RESIDENCE_YEARS_DESIGNATED_1972_TO_1981,
    RESIDENCE_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_YEARS_OWNED_1972_TO_1981,
    RESIDENCE_YEARS_OWNED_AFTER_1981,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceGainLine
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute

EXAMPLE = (6, 0, 10, 0, "400000.00", "5000.00", "95000.00", 1)
NOT_ENDING = (1, 0, 6, 0, "250000.00", "0.00", "180000.00", 1)


def return_ai(**overrides: Any) -> Worksheet:
    """Return AI's inputs, as in `returns/2025_return_ai.yaml`: employment income of 60000 and two
    principal residence properties sold, each a chosen figure; `overrides` replace any keyword of
    `compute`, for the variants below.
    """
    given: dict[str, Any] = {
        "principal_residence_properties_rows": (EXAMPLE, NOT_ENDING),
        "income_tax_deducted": "25000",
    }
    return compute("60000", (), "0", "0", "0", "0", "0", **{**given, **overrides})


def test_return_ais_two_properties_have_taxable_gains_of_90000_and_46666_67() -> None:
    # Property 1 (the worked example): line 18 = 400000.00 - (95000.00 + 5000.00) = 300000.00;
    # line 20 = 6 + 1 = 7; line 21 = 2100000.00; line 23 = 2100000.00 / 10 = 210000.00; line 24 =
    # 300000.00 - 210000.00 = 90000.00. Property 2: line 18 = 250000.00 - 180000.00 = 70000.00;
    # line 20 = 1 + 1 = 2; line 21 = 140000.00; line 23 = 140000.00 / 6 = 23333.333..., half-up
    # to the cent 23333.33; line 24 = 70000.00 - 23333.33 = 46666.67. Line 54 is line 24 for each
    # (no Part 2, no Part 4), and the total is 90000.00 + 46666.67 = 136666.67.
    worksheet = return_ai()

    assert worksheet.get(PRINCIPAL_RESIDENCE_PROPERTIES).value == RecordList(
        PRINCIPAL_RESIDENCE_PROPERTIES.fields,
        [
            {
                RESIDENCE_YEARS_DESIGNATED_AFTER_1981: 6,
                RESIDENCE_YEARS_DESIGNATED_1972_TO_1981: 0,
                RESIDENCE_YEARS_OWNED_AFTER_1981: 10,
                RESIDENCE_YEARS_OWNED_1972_TO_1981: 0,
                RESIDENCE_PROCEEDS: D("400000.00"),
                RESIDENCE_OUTLAYS: D("5000.00"),
                RESIDENCE_ADJUSTED_COST_BASE: D("95000.00"),
                RESIDENCE_PLUS_ONE_YEAR: 1,
                RESIDENCE_PART_2_APPLIES: 0,
                RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981: D("0"),
                RESIDENCE_FMV_DEC_31_1981: D("0"),
                RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981: D("0"),
                RESIDENCE_T664_FILED: 0,
                RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981: 0,
                RESIDENCE_WS_YEARS_OWNED_AFTER_1981: 0,
                RESIDENCE_WS_DESIGNATED_PROCEEDS: D("0"),
                RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994: D("0"),
                RESIDENCE_WS_FMV_FEB_22_1994: D("0"),
                RESIDENCE_WS_ELECTED_CAPITAL_GAIN: D("0"),
                RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992: 0,
                RESIDENCE_WS_MONTHS_OWNED_AFTER_1971: 0,
                RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994: D("0"),
            },
            {
                RESIDENCE_YEARS_DESIGNATED_AFTER_1981: 1,
                RESIDENCE_YEARS_DESIGNATED_1972_TO_1981: 0,
                RESIDENCE_YEARS_OWNED_AFTER_1981: 6,
                RESIDENCE_YEARS_OWNED_1972_TO_1981: 0,
                RESIDENCE_PROCEEDS: D("250000.00"),
                RESIDENCE_OUTLAYS: D("0.00"),
                RESIDENCE_ADJUSTED_COST_BASE: D("180000.00"),
                RESIDENCE_PLUS_ONE_YEAR: 1,
                RESIDENCE_PART_2_APPLIES: 0,
                RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981: D("0"),
                RESIDENCE_FMV_DEC_31_1981: D("0"),
                RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981: D("0"),
                RESIDENCE_T664_FILED: 0,
                RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981: 0,
                RESIDENCE_WS_YEARS_OWNED_AFTER_1981: 0,
                RESIDENCE_WS_DESIGNATED_PROCEEDS: D("0"),
                RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994: D("0"),
                RESIDENCE_WS_FMV_FEB_22_1994: D("0"),
                RESIDENCE_WS_ELECTED_CAPITAL_GAIN: D("0"),
                RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992: 0,
                RESIDENCE_WS_MONTHS_OWNED_AFTER_1971: 0,
                RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994: D("0"),
            },
        ],
    )
    assert worksheet.producer_of(PRINCIPAL_RESIDENCE_PROPERTIES) is None
    assert isinstance(worksheet.producer_of(PRINCIPAL_RESIDENCE_GAIN), PrincipalResidenceGain)
    assert worksheet.get(PRINCIPAL_RESIDENCE_GAIN).value == D("136666.67")


def test_return_ais_trace_names_each_property_and_totals_the_taxable_gains() -> None:
    worksheet = return_ai()

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
        ),
        PrincipalResidenceGainLine(
            output=PRINCIPAL_RESIDENCE_GAIN,
            position=2,
            years_designated_after_1981=1,
            years_designated_1972_to_1981=0,
            designated=1,
            years_owned_after_1981=6,
            years_owned_1972_to_1981=0,
            owned=6,
            plus_one=1,
            proceeds=D("250000.00"),
            adjusted_cost_base=D("180000.00"),
            outlays=D("0.00"),
            gain=D("70000.00"),
            line_20=2,
            line_21=D("140000.00"),
            rounding=CENT,
            exempt=D("23333.33"),
            part_2_applies=0,
            line_53=D("0"),
            line_24=D("46666.67"),
            result=D("46666.67"),
        ),
        ItemsTotalLine(
            output=PRINCIPAL_RESIDENCE_GAIN,
            items=((1, D("90000.00")), (2, D("46666.67"))),
            total=D("136666.67"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    first = rendered.index(
        "principal_residence_gain: property 1: gain 300000 = proceeds 400000 less adjusted cost "
        "base 95000 less outlays 5000; exempt 210000 = 300000 × (6 designated + 1) ÷ 10 owned "
        "(half-up to 0.01); taxable gain 90000 = 300000 less 210000, not below 0"
    )
    assert rendered[first : first + 3] == (
        "principal_residence_gain: property 1: gain 300000 = proceeds 400000 less adjusted cost "
        "base 95000 less outlays 5000; exempt 210000 = 300000 × (6 designated + 1) ÷ 10 owned "
        "(half-up to 0.01); taxable gain 90000 = 300000 less 210000, not below 0",
        "principal_residence_gain: property 2: gain 70000 = proceeds 250000 less adjusted cost "
        "base 180000 less outlays 0; exempt 23333.33 = 70000 × (1 designated + 1) ÷ 6 owned "
        "(half-up to 0.01); taxable gain 46666.67 = 70000 less 23333.33, not below 0",
        "principal_residence_gain: item 1 90000 + item 2 46666.67 = 136666.67",
    )


def test_return_ais_taxable_gains_are_schedule_3_line_9_and_line_15800() -> None:
    # Line 54 of each form is entered on line 15800, the personal-use property gain of Schedule 3
    # Part 3 ("Line 9 and line 15800: Total gain only"): the rows add 0, so line 9 is 136666.67,
    # and it is the whole of the total capital gains or losses (line 21, 19700) and of line 22.
    worksheet = return_ai()

    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN_ROWS).value == D("0")
    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN).value == D("136666.67")
    assert worksheet.get(CAPITAL_GAIN).value == D("136666.67")


def test_return_ais_taxable_capital_gains_are_68333_34_on_line_12700() -> None:
    # Line 24 = 136666.67 x 50% = 68333.335, half-up to the cent 68333.34, positive, so line 12700
    # is 68333.34. Total income (line 15000) = 60000 + 68333.34 = 128333.34. The enhanced CPP
    # contributions (565.00) are deducted: net income and taxable income 127768.34. The total
    # payable is 31585.93 and with the chosen tax deducted of 25000, the balance owing (line 48500)
    # is 6585.93.
    worksheet = return_ai()

    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("68333.34")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("68333.34")
    assert worksheet.get(TOTAL_INCOME).value == D("128333.34")
    assert worksheet.get(NET_INCOME).value == D("127768.34")
    assert worksheet.get(TAXABLE_INCOME).value == D("127768.34")
    assert worksheet.get(TOTAL_PAYABLE).value == D("31585.93")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("6585.93")


def test_no_properties_sold_add_nothing_to_line_9() -> None:
    worksheet = return_ai(principal_residence_properties_rows=())

    assert worksheet.get(PRINCIPAL_RESIDENCE_GAIN).value == D("0")
    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN).value == D("0")
    assert worksheet.get(CAPITAL_GAIN).value == D("0")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0")
    assert worksheet.get(TOTAL_INCOME).value == D("60000")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "principal_residence_gain: no items = 0" in rendered


def test_the_taxable_gains_are_added_to_the_personal_use_property_rows_on_line_9() -> None:
    # A personal-use property row of 3000 - 1500 - 0 = 1500 ("Total gain only") plus line 54 of
    # the two forms, 136666.67: line 9 and line 15800 are 138166.67.
    worksheet = return_ai(personal_use_property_dispositions=(("3000", "1500", "0"),))

    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN_ROWS).value == D("1500")
    assert worksheet.get(PRINCIPAL_RESIDENCE_GAIN).value == D("136666.67")
    assert worksheet.get(PERSONAL_USE_PROPERTY_GAIN).value == D("138166.67")
    assert worksheet.get(CAPITAL_GAIN).value == D("138166.67")


def test_a_plus_one_of_2_on_a_property_is_refused_through_the_return() -> None:
    # The "plus one" is one year by law: a flag of 2 on property 1 refuses the return, naming it.
    plus_one_of_2 = (*EXAMPLE[:7], 2)

    with pytest.raises(ValidationError, match=r"property 1.*plus one"):
        return_ai(principal_residence_properties_rows=(plus_one_of_2, NOT_ENDING))


def test_a_part_2_flag_of_2_on_a_property_is_refused_through_the_return() -> None:
    part_2_flag_of_2 = (*EXAMPLE, 2, "0.00", "0.00", "0.00")

    with pytest.raises(ValidationError, match=r"property 1.*Part 2"):
        return_ai(principal_residence_properties_rows=(part_2_flag_of_2, NOT_ENDING))


def test_a_t664_flag_of_2_on_a_property_is_refused_through_the_return() -> None:
    t664_flag_of_2 = (
        *EXAMPLE,
        0,
        "0.00",
        "0.00",
        "0.00",
        2,
        0,
        0,
        "0.00",
        "0.00",
        "0.00",
        "0.00",
        0,
        0,
    )

    with pytest.raises(ValidationError, match=r"property 1.*T664"):
        return_ai(principal_residence_properties_rows=(t664_flag_of_2, NOT_ENDING))


def test_more_years_designated_than_owned_on_a_property_is_refused_through_the_return() -> None:
    twelve_designated_of_10 = (12, *EXAMPLE[1:])

    with pytest.raises(ValidationError, match=r"property 1.*designated.*owned"):
        return_ai(principal_residence_properties_rows=(twelve_designated_of_10, NOT_ENDING))


def test_the_years_owned_refusal_still_comes_first() -> None:
    no_years_owned_and_plus_one_of_2 = (0, 0, 0, 0, "400000.00", "5000.00", "95000.00", 2)

    with pytest.raises(ValidationError, match=r"years owned \(lines 5 and 6\) are 0"):
        return_ai(
            principal_residence_properties_rows=(no_years_owned_and_plus_one_of_2, NOT_ENDING)
        )


def test_a_property_with_every_year_designated_is_accepted() -> None:
    ten_designated_of_10 = (10, *EXAMPLE[1:])

    worksheet = return_ai(principal_residence_properties_rows=(ten_designated_of_10, NOT_ENDING))

    assert worksheet.get(PRINCIPAL_RESIDENCE_GAIN).value == D("46666.67")


def _filed_property(*, line_1: int, line_4: int, line_60: int, line_62: int) -> tuple[Any, ...]:
    return (
        *EXAMPLE,
        0,
        "0.00",
        "0.00",
        "0.00",
        1,
        line_1,
        line_4,
        "200000.00",
        "100000.00",
        "200000.00",
        "100000.00",
        line_60,
        line_62,
    )


def test_worksheet_line_1_above_line_4_is_refused_through_the_return() -> None:
    filed = _filed_property(line_1=8, line_4=7, line_60=24, line_62=74)

    with pytest.raises(ValidationError, match=r"property 1.*worksheet line 1.*more than line 4"):
        return_ai(principal_residence_properties_rows=(filed, NOT_ENDING))


def test_worksheet_line_1_above_part_1_line_1_is_refused_through_the_return() -> None:
    filed = _filed_property(line_1=11, line_4=12, line_60=24, line_62=74)

    with pytest.raises(ValidationError, match=r"property 1.*worksheet line 1.*more than the years"):
        return_ai(principal_residence_properties_rows=(filed, NOT_ENDING))


def test_worksheet_line_60_above_line_62_is_refused_through_the_return() -> None:
    filed = _filed_property(line_1=0, line_4=10, line_60=75, line_62=74)

    with pytest.raises(ValidationError, match=r"property 1.*line 60.*more than line 62"):
        return_ai(principal_residence_properties_rows=(filed, NOT_ENDING))


def test_worksheet_subsets_equal_to_their_wholes_are_accepted() -> None:
    filed = _filed_property(line_1=6, line_4=10, line_60=74, line_62=74)

    return_ai(principal_residence_properties_rows=(filed, NOT_ENDING))
