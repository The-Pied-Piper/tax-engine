"""Schedule ON428 (2025, Ontario tax, single filer) from the salary alone: the form's real parts
composed end to end.

Every ON428 line part has its own test with its neighbours typed in. This module composes the
whole form: it copies `salary.yaml`, every Schedule 8 part (lines 19 and 25 come from there), every
T2204 part (line 21 reads T2204 line 16), every `t1_taxable_income*.yaml` part (line 1 reads T1 line
26000), every `on428_a*.yaml` part (line 85 reads ON428-A line 20) and every `on428*.yaml` part of
the ON428 folder into a temporary manifest folder beside a test-only header, and types in only the
gross salary (`ca/employment_income`). The real header is not used because its output, T1 line 167,
is not built yet. This is not a worked return: no return file, no slips, one form.

Line 2 is a copy of line 1 and has no step, so it has no pin. Line 9 is the basic personal amount
(`ca-on/basic_personal_amount`) and line 18 reads it. Line 5 is a rate, so it has no cents check.
Line 85 is the LIFT credit from ON428-A, read as a record list. Lines 1 to 8 are Part A, the
bracket column of the taxable income on line 1.

Form text: Schedule ON428 (CRA 5006-C, 2025), "Line 1: Enter your taxable income from line 26000
of your return."; "Line 3: 105,775.00" (column 3); "Line 5: Rate 11.16%"; "Line 6: Line 4
multiplied by the percentage from line 5"; "Line 7: 7,510.09" (column 3); "Line 8: Line 6 plus
line 7 Ontario tax on taxable income"; "Line 9 and line 58040: Basic personal amount Claim
$12,747"; "Line 66: (Line 65 minus $5,710) multiplied by 20% (if negative, enter "0") ="; "Line
67: (Line 65 minus $7,307) multiplied by 36% (if negative, enter "0") ="; "Line 74: Basic
reduction 294.00"; "Line 78: Amount from line 77 above multiplied by 2 ="; "Line 80: Line 78 minus
line 79 (if negative, enter "0") Ontario tax reduction ="; "Line 85 and line 62140: Low-income
individuals and families tax (LIFT) credit (complete Schedule ON428-A)"; "Line 89 - Ontario health
premium", with the chart rows "Row 1: Taxable Income $20,000 or less" (premium $0), "Row 7:
Taxable Income more than $48,600 but not more than $72,000" ($600) and "Row 9: Taxable Income more
than $72,600 but not more than $200,000" ($750); "Line 90: Line 88 plus line 89 Enter this amount
on line 42800 of your return. Ontario tax =". Line 1 is the T1 taxable income (T1 line 26000),
which is the salary less the Schedule 8 enhanced contributions (CRA 5000-S8, 2025).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import (
    BASIC_PERSONAL_AMOUNT,
    ON428_BASIC_REDUCTION_LINE_74,
    ON428_BRACKET_COLUMN_RATE_LINE_5,
    ON428_BRACKET_LOWER_BOUND_LINE_3,
    ON428_CPP_BASE_CREDIT_AMOUNT_LINE_19,
    ON428_CPP_EI_CREDIT_AMOUNTS_LINE_24,
    ON428_CREDIT_AMOUNTS_AT_CREDIT_RATE_LINE_46,
    ON428_CREDITS_SUBTOTAL_LINE_25,
    ON428_CREDITS_WITH_DISABILITY_LINE_31,
    ON428_CREDITS_WITH_PENSION_LINE_28,
    ON428_CREDITS_WITH_TRANSFERS_LINE_35,
    ON428_EI_CREDIT_AMOUNT_LINE_21,
    ON428_EXCESS_TIMES_COLUMN_RATE_LINE_6,
    ON428_LIFT_CREDIT_LINE_85,
    ON428_NON_REFUNDABLE_CREDITS_LINE_50,
    ON428_ONTARIO_HEALTH_PREMIUM_LINE_89,
    ON428_ONTARIO_TAX_LINE_90,
    ON428_ONTARIO_TAX_REDUCTION_LINE_80,
    ON428_PERSONAL_AMOUNTS_SUBTOTAL_LINE_18,
    ON428_SURTAX_20_PERCENT_TIER_LINE_66,
    ON428_SURTAX_36_PERCENT_TIER_LINE_67,
    ON428_SURTAX_BASE_LINE_65,
    ON428_SURTAX_TOTAL_LINE_68,
    ON428_TAX_AFTER_DIVIDEND_CREDIT_LINE_71,
    ON428_TAX_AFTER_FARMERS_FOOD_DONATION_CREDIT_LINE_88,
    ON428_TAX_AFTER_FOREIGN_TAX_CREDIT_LINE_83,
    ON428_TAX_AFTER_LIFT_CREDIT_LINE_86,
    ON428_TAX_AFTER_MINIMUM_TAX_CARRYOVER_LINE_61,
    ON428_TAX_AFTER_TAX_REDUCTION_LINE_81,
    ON428_TAX_AT_COLUMN_START_LINE_7,
    ON428_TAX_MINUS_CREDITS_LINE_53,
    ON428_TAX_ON_TAXABLE_INCOME_LINE_8,
    ON428_TAX_REDUCTION_DOUBLED_LINE_78,
    ON428_TAX_REDUCTION_LINE_77,
    ON428_TAX_WITH_MINIMUM_TAX_ADDITION_LINE_73,
    ON428_TAX_WITH_SPLIT_INCOME_LINE_55,
    ON428_TAX_WITH_SURTAX_LINE_69,
    ON428_TAXABLE_INCOME_LINE_1,
    ON428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4,
    ON428_TOTAL_CREDIT_AMOUNTS_LINE_44,
)
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The real ON428 declaration (`on428.yaml`) carries the form and its exports, so the fixture's own
# form text is an empty mapping.
FORM = "{}\n"
# The ON428 parts are globbed in their own folder: a recursive `on428*.yaml` glob would also match
# each ON428-A part (`on428_a/on428_a*.yaml`) and copy it twice.
ON428 = TAKE_HOME / "on428"
ON428_A = TAKE_HOME / "on428_a"
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t2204*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t1_taxable_income*.yaml"))),
    *(part.name for part in sorted(ON428_A.glob("on428_a*.yaml"))),
    *(part.name for part in sorted(ON428.glob("on428*.yaml"))),
)

# Amount lines by form line. Line 2 is a copy of line 1 and line 1 is the taxable income the
# records give, so both are read through their producers; line 5 is a rate.
AMOUNT_LINES: dict[str, AmountKind] = {
    "1": ON428_TAXABLE_INCOME_LINE_1,
    "3": ON428_BRACKET_LOWER_BOUND_LINE_3,
    "4": ON428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4,
    "5": ON428_BRACKET_COLUMN_RATE_LINE_5,
    "6": ON428_EXCESS_TIMES_COLUMN_RATE_LINE_6,
    "7": ON428_TAX_AT_COLUMN_START_LINE_7,
    "8": ON428_TAX_ON_TAXABLE_INCOME_LINE_8,
    "9": BASIC_PERSONAL_AMOUNT,
    "18": ON428_PERSONAL_AMOUNTS_SUBTOTAL_LINE_18,
    "19": ON428_CPP_BASE_CREDIT_AMOUNT_LINE_19,
    "21": ON428_EI_CREDIT_AMOUNT_LINE_21,
    "24": ON428_CPP_EI_CREDIT_AMOUNTS_LINE_24,
    "25": ON428_CREDITS_SUBTOTAL_LINE_25,
    "28": ON428_CREDITS_WITH_PENSION_LINE_28,
    "31": ON428_CREDITS_WITH_DISABILITY_LINE_31,
    "35": ON428_CREDITS_WITH_TRANSFERS_LINE_35,
    "44": ON428_TOTAL_CREDIT_AMOUNTS_LINE_44,
    "46": ON428_CREDIT_AMOUNTS_AT_CREDIT_RATE_LINE_46,
    "50": ON428_NON_REFUNDABLE_CREDITS_LINE_50,
    "53": ON428_TAX_MINUS_CREDITS_LINE_53,
    "55": ON428_TAX_WITH_SPLIT_INCOME_LINE_55,
    "61": ON428_TAX_AFTER_MINIMUM_TAX_CARRYOVER_LINE_61,
    "65": ON428_SURTAX_BASE_LINE_65,
    "66": ON428_SURTAX_20_PERCENT_TIER_LINE_66,
    "67": ON428_SURTAX_36_PERCENT_TIER_LINE_67,
    "68": ON428_SURTAX_TOTAL_LINE_68,
    "69": ON428_TAX_WITH_SURTAX_LINE_69,
    "71": ON428_TAX_AFTER_DIVIDEND_CREDIT_LINE_71,
    "73": ON428_TAX_WITH_MINIMUM_TAX_ADDITION_LINE_73,
    "74": ON428_BASIC_REDUCTION_LINE_74,
    "77": ON428_TAX_REDUCTION_LINE_77,
    "78": ON428_TAX_REDUCTION_DOUBLED_LINE_78,
    "80": ON428_ONTARIO_TAX_REDUCTION_LINE_80,
    "81": ON428_TAX_AFTER_TAX_REDUCTION_LINE_81,
    "83": ON428_TAX_AFTER_FOREIGN_TAX_CREDIT_LINE_83,
    "85": ON428_LIFT_CREDIT_LINE_85,
    "86": ON428_TAX_AFTER_LIFT_CREDIT_LINE_86,
    "88": ON428_TAX_AFTER_FARMERS_FOOD_DONATION_CREDIT_LINE_88,
    "89": ON428_ONTARIO_HEALTH_PREMIUM_LINE_89,
    "90": ON428_ONTARIO_TAX_LINE_90,
}
# Every amount line but 5 (a rate). Lines 3 and 78 and the floored zeros are a known gap (see
# `test_every_cent_line_has_two_decimals_known_gap`), so the passing test below pins the rest.
ALL_CENT_LINES = tuple(line for line in AMOUNT_LINES if line != "5")
CENT_LINES = (
    "1", "4", "6", "7", "8", "9", "18", "19", "21", "24", "25", "28", "31", "35", "44", "46",
    "50", "53", "55", "61", "65", "66", "67", "68", "69", "71", "73", "74", "77", "80", "81",
    "83", "85", "86", "88", "89", "90",
)  # fmt: skip

# Each salary's figures by form line, hand-computed from the printed lines and the datasets they
# cite. Line 1 is the salary less the Schedule 8 enhanced contributions: 20,000 less 165 (1% of
# 16,500 above 3,500), 70,000 less 665 (1% of 66,500), 150,000 less 1,074 (1% of 67,800 plus 4% of
# 9,900 between the 71,300 and 81,200 maximums). Line 19 is 4.95% of the base amount (16,500 gives
# 816.75; 66,500 gives 3,291.75; 67,800 gives 3,356.10). Line 21 is 1.64% of earnings up to 65,700
# (328.00 at 20,000; 1,077.48 at the maximum). Line 46 is line 44 times 5.05%. Line 80 is line 78
# (588.00) minus line 79 (line 73), floored at 0. Line 85 is the LIFT credit: 5.05% of the salary
# capped at 875, reduced by 5% of the adjusted net income over 32,500. That reduction is nil at
# 20,000, and at 70,000 and 150,000 it is larger than the credit, so the credit is 0. Line 89 is
# the printed chart row for the taxable income on line 1: row 1 ($0), row 7 ($600) and row 9
# ($750). The 150,000 surtax is 20% of (line 65 minus 5,710) and 36% of (line 65 minus 7,307) on
# line 65 of 11,458.12.
CASES: list[tuple[str, dict[str, str]]] = [
    ("20000", {
        "1": "19835.00", "3": "0.00", "4": "19835.00", "5": "0.0505", "6": "1001.67",
        "7": "0.00", "8": "1001.67", "9": "12747.00", "18": "12747.00", "19": "816.75",
        "21": "328.00", "24": "1144.75", "25": "13891.75", "28": "13891.75", "31": "13891.75",
        "35": "13891.75", "44": "13891.75", "46": "701.53", "50": "701.53", "53": "300.14",
        "55": "300.14", "61": "300.14", "65": "300.14", "66": "0.00", "67": "0.00",
        "68": "0.00", "69": "300.14", "71": "300.14", "73": "300.14", "74": "294.00",
        "77": "294.00", "78": "588.00", "80": "287.86", "81": "12.28", "83": "12.28",
        "85": "875.00", "86": "0.00", "88": "0.00", "89": "0.00", "90": "0.00",
    }),
    ("70000", {
        "1": "69335.00", "3": "52886.00", "4": "16449.00", "5": "0.0915", "6": "1505.08",
        "7": "2670.74", "8": "4175.82", "9": "12747.00", "18": "12747.00", "19": "3291.75",
        "21": "1077.48", "24": "4369.23", "25": "17116.23", "28": "17116.23", "31": "17116.23",
        "35": "17116.23", "44": "17116.23", "46": "864.37", "50": "864.37", "53": "3311.45",
        "55": "3311.45", "61": "3311.45", "65": "3311.45", "66": "0.00", "67": "0.00",
        "68": "0.00", "69": "3311.45", "71": "3311.45", "73": "3311.45", "74": "294.00",
        "77": "294.00", "78": "588.00", "80": "0.00", "81": "3311.45", "83": "3311.45",
        "85": "0.00", "86": "3311.45", "88": "3311.45", "89": "600.00", "90": "3911.45",
    }),
    ("150000", {
        "1": "148926.00", "3": "105775.00", "4": "43151.00", "5": "0.1116", "6": "4815.65",
        "7": "7510.09", "8": "12325.74", "9": "12747.00", "18": "12747.00", "19": "3356.10",
        "21": "1077.48", "24": "4433.58", "25": "17180.58", "28": "17180.58", "31": "17180.58",
        "35": "17180.58", "44": "17180.58", "46": "867.62", "50": "867.62", "53": "11458.12",
        "55": "11458.12", "61": "11458.12", "65": "11458.12", "66": "1149.62", "67": "1494.40",
        "68": "2644.02", "69": "14102.14", "71": "14102.14", "73": "14102.14", "74": "294.00",
        "77": "294.00", "78": "588.00", "80": "0.00", "81": "14102.14", "83": "14102.14",
        "85": "0.00", "86": "14102.14", "88": "14102.14", "89": "750.00", "90": "14852.14",
    }),
]  # fmt: skip

# The health premium row the printed chart gives for each taxable income on line 1.
HEALTH_PREMIUM_ROWS: list[tuple[str, str, str]] = [
    ("20000", "19835.00", "0.00"),
    ("70000", "69335.00", "600.00"),
    ("150000", "148926.00", "750.00"),
]


def on428(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-on/on428"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_every_line_matches_the_printed_form(
    take_home_service: TakeHomeService, salary: str, expected: dict[str, str]
) -> None:
    sheet = on428(take_home_service, salary)

    assert {line: sheet.get(AMOUNT_LINES[line]).value for line in expected} == {
        line: D(figure) for line, figure in expected.items()
    }


BRACKET_COLUMN_TRACE = [
    ("20000", "19835", "0", "5.05%", "0"),
    ("70000", "69335", "52886", "9.15%", "2670.74"),
    ("150000", "148926", "105775", "11.16%", "7510.09"),
]


@pytest.mark.parametrize(("salary", "base", "lower", "rate", "at_start"), BRACKET_COLUMN_TRACE)
def test_lines_3_5_and_7_trace_the_output_and_the_base_they_read(
    take_home_service: TakeHomeService,
    salary: str,
    base: str,
    lower: str,
    rate: str,
    at_start: str,
) -> None:
    text = EnglishTraceRenderer().render_all(on428(take_home_service, salary).trace)

    taxable = "on428_taxable_income_line_1"
    assert [line for line in text if ": bracket " in line] == [
        f"on428_bracket_lower_bound_line_3: bracket lower bound for {taxable} {base}: {lower}",
        f"on428_bracket_column_rate_line_5: bracket rate for {taxable} {base}: {rate}",
        f"on428_tax_at_column_start_line_7: bracket tax at start for {taxable} {base}: {at_start}",
    ]


def test_the_form_exports_line_90_the_figure_t1_line_42800_reads(
    take_home_service: TakeHomeService,
) -> None:
    sheet = on428(take_home_service, "70000")

    assert sheet.get(ON428_ONTARIO_TAX_LINE_90).value == D("3911.45")


def test_the_form_exports_exactly_line_90(take_home_service: TakeHomeService) -> None:
    # Every other line is read only inside the form, so the form exports line 90 alone.
    service = take_home_service(HEADER, FORM, *PARTS)
    code = JurisdictionCode("CA-ON")
    (form,) = (f for f in service.compose(code, 2025).forms if f.name == "ca-on/on428")
    assert form.exports == (ON428_ONTARIO_TAX_LINE_90,)

    worksheets = service.compute(code, 2025, Artifact(EMPLOYMENT_INCOME, D("70000")))
    (sheet,) = worksheets["ca-on/on428"]

    assert [sheet.get(kind).value for kind in form.exports] == [D("3911.45")]


def test_the_module_composes_without_a_t1_general_part(take_home_service: TakeHomeService) -> None:
    # The form reads T1 lines 26000, 22215 and the rest from the take-home parts only; no T1
    # General form is in the folder, and the composition still holds.
    service = take_home_service(HEADER, FORM, *PARTS)
    names = {form.name for form in service.compose(JurisdictionCode("CA-ON"), 2025).forms}

    assert "ca-on/on428" in names
    assert "ca/t1_general" not in names


@pytest.mark.parametrize(("salary", "taxable_income", "premium"), HEALTH_PREMIUM_ROWS)
def test_the_health_premium_is_the_printed_row_for_the_taxable_income(
    take_home_service: TakeHomeService, salary: str, taxable_income: str, premium: str
) -> None:
    sheet = on428(take_home_service, salary)

    assert sheet.get(ON428_TAXABLE_INCOME_LINE_1).value == D(taxable_income)
    assert sheet.get(ON428_ONTARIO_HEALTH_PREMIUM_LINE_89).value == D(premium)


@pytest.mark.parametrize("salary", [case[0] for case in CASES])
def test_the_cent_lines_have_exactly_two_decimals_when_above_zero(
    take_home_service: TakeHomeService, salary: str
) -> None:
    # A line floored to "0" (lines 80, 85, 86 and 88 under their thresholds or past the
    # credit) comes back as a bare 0 with no cents, so only the lines above zero are pinned to two
    # decimals. Line 5 is a rate and is not a cent line.
    sheet = on428(take_home_service, salary)

    for line in CENT_LINES:
        value = sheet.get(AMOUNT_LINES[line]).value
        assert value == 0 or value.as_tuple().exponent == -2, line


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known gap, follow-up ticket: line 3 comes back 52886 / 105775 (brackets dataset stores "
        "whole dollars), line 78 comes back 588 (apply_fraction, no rounding), and floored zeros "
        "(lines 3, 86 and 88 at 20,000) come back as a bare 0. The values equal the printed cents; "
        "only the decimal places differ. Strict, so it fails the suite once the gap is closed."
    ),
)
@pytest.mark.parametrize("salary", [case[0] for case in CASES])
def test_every_cent_line_has_two_decimals_known_gap(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = on428(take_home_service, salary)

    for line in ALL_CENT_LINES:
        assert sheet.get(AMOUNT_LINES[line]).value.as_tuple().exponent == -2, line


def test_a_negative_salary_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(NegativeArtifactError, match="ca/employment_income cannot be negative"):
        on428(take_home_service, "-1")
