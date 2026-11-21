"""MB428 (2025) lines 43 to 50, the medical expenses block, through the real engine from a salary.

Form text (Form MB428, CRA 5007-c-25e.txt): line 43 "Amount from line 33099 of your return", line 44
"Amount from line 23600 of your return", line 45 "Applicable rate 3%", line 46 "Line 44 multiplied
by the percentage from line 45 =", line 47 "Enter whichever is less: $1,728 or the amount from
line 46.", line 48 "Line 43 minus line 47 (if negative, enter "0") =", line 49 "Allowable amount of
medical expenses for other dependants (use Worksheet MB428)" and line 50 "Line 48 plus line 49 =".
Line 43 is the caller's optional input; line 49 is Worksheet MB428 line 4 (section "Line 58729"),
the total of one column for each dependant the caller lists; every other line is computed.

The hand figures are asserted (not a CRA example). A $70,000 salary has net income 69,335.00 (the
salary less the enhanced CPP deduction), so line 46 is 3% of it, 2,080.05, and line 47 stops at the
printed 1,728.00. Line 51 is line 42 (20,149.23) plus line 50, and line 57 is 10.8% of it (line 53)
plus line 56.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import tax_engine.jurisdictions.ca_mb.catalog as mb
from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

D = Decimal
MANITOBA = JurisdictionCode("CA-MB")


def _credits(
    salary: str, dependants: tuple[tuple[str, str | None], ...] = (), **given: str
) -> Worksheet:
    """The credits form for `salary`; each dependant is its worksheet line 1 and line 2 (None is
    left blank)."""
    artifacts: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if "line_43" in given:
        artifacts.append(Artifact(mb.MB428_MEDICAL_EXPENSES_LINE_43, D(given["line_43"])))
    if dependants:
        columns = RecordList(
            mb.WORKSHEET_MB428_OTHER_DEPENDANTS.fields,
            [
                {
                    mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_1: D(line_1),
                    mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_2: BLANK
                    if line_2 is None
                    else D(line_2),
                }
                for line_1, line_2 in dependants
            ],
        )
        artifacts.append(Artifact(mb.WORKSHEET_MB428_OTHER_DEPENDANTS, columns))
    (sheet,) = build_tax_computation().compute(MANITOBA, 2025, *artifacts)["ca-mb/mb428_credits"]
    return sheet


def _value(sheet: Worksheet, kind: AmountKind) -> Decimal:
    value = sheet.get(kind).value
    assert isinstance(value, Decimal)
    return value


def test_a_salary_only_caller_has_no_medical_claim() -> None:
    sheet = _credits("70000")

    assert _value(sheet, mb.MB428_NET_INCOME_LINE_44) == D("69335.00")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_46) == D("2080.05")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_47) == D("1728.00")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48) == D("0.00")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_LINE_50) == D("0.00")
    assert _value(sheet, mb.MB428_CREDITS_TOTAL_LINE_51) == D("20149.23")
    assert _value(sheet, mb.MB428_NON_REFUNDABLE_CREDITS_LINE_57) == D("2176.12")


def test_a_medical_claim_above_the_cap_adds_to_line_50() -> None:
    sheet = _credits("70000", (("250.50", None),), line_43="5000")

    # Line 48 is 5,000.00 less the 1,728.00 cap; line 50 adds the 250.50 of line 49 (one dependant
    # whose line 2 is left blank, read as 0).
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48) == D("3272.00")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_LINE_50) == D("3522.50")
    # Line 51 is line 42 (20,149.23) plus line 50; line 53 is 10.8% of it, 2,556.55.
    assert _value(sheet, mb.MB428_CREDITS_TOTAL_LINE_51) == D("23671.73")
    assert _value(sheet, mb.MB428_NON_REFUNDABLE_CREDITS_LINE_57) == D("2556.55")


def test_a_claim_below_the_threshold_is_not_negative() -> None:
    sheet = _credits("70000", line_43="1000")

    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48) == D("0.00")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_LINE_50) == D("0.00")


def test_line_47_is_line_46_when_line_46_is_under_the_cap() -> None:
    # A $40,000 salary has net income 39,xxx, whose 3% is under 1,728.
    sheet = _credits("40000", line_43="2000")
    line_44 = _value(sheet, mb.MB428_NET_INCOME_LINE_44)
    line_46 = (line_44 * D("0.03")).quantize(D("0.01"))

    assert line_46 < D("1728")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_46) == line_46
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_47) == line_46
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48) == D("2000.00") - line_46


def test_other_dependants_alone_make_line_50() -> None:
    sheet = _credits("70000", (("1000", "0"),))

    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48) == D("0.00")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_LINE_50) == D("1000.00")


def test_each_dependant_is_one_column_of_the_worksheet() -> None:
    # Column 1: 900.00 - 400.00 = 500.00. Column 2: 300.00 - 450.00 is negative, so 0.00. Column 3:
    # 1,200.00 with line 2 left blank is 1,200.00. Line 4 (line 49) is 500.00 + 0.00 + 1,200.00.
    sheet = _credits("70000", (("900", "400"), ("300", "450"), ("1200", None)))

    assert _value(sheet, mb.MB428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49) == D("1700.00")
    assert _value(sheet, mb.MB428_MEDICAL_EXPENSES_LINE_50) == D("1700.00")
    # Line 51 is line 42 (20,149.23) plus line 50.
    assert _value(sheet, mb.MB428_CREDITS_TOTAL_LINE_51) == D("21849.23")


def test_a_salary_only_caller_has_line_49_of_zero() -> None:
    sheet = _credits("70000")

    assert _value(sheet, mb.MB428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49) == D("0.00")
