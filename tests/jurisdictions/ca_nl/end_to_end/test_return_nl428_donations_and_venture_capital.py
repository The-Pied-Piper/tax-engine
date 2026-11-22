"""NL428 (2025) lines 59 to 62 and 82 to 85, the donations and venture capital blocks, through the
real registered engine from a salary.

Form text (Form NL428, CRA 5001-C): line 59 "Amount from line 13 of your federal Schedule 9
multiplied by 8.7% =", line 60 "Amount from line 14 of your federal Schedule 9 multiplied by 21.8%
=", line 61 "Line 59 plus line 60 =", line 62 "Line 58 plus line 61", line 82 "Venture capital tax
credit from Certificate(s) NL VCTC", line 83 "Unused Newfoundland and Labrador venture capital tax
credit from your most recent notice of assessment or reassessment", line 84 "Line 82 plus line 83
=" and line 85 "Line 81 minus line 84 (if negative, enter "0") =". Schedule 9 line 12 (lines 13 and
14, read by lines 59 and 60, are computed from it) and the venture capital amounts of lines 82 and
83 are the caller's optional inputs; every other line is computed.

The figures are derived by hand below with Decimal, not read from the engine (not a CRA example).
A $70,000 salary alone has line 62 of 1,342.95 and line 81 of 6,147.49 (test_nl428.py pins the
salary-only tax).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
NEWFOUNDLAND = JurisdictionCode("CA-NL")
NL428 = "ca-nl/nl428"
NL428_CREDITS = "ca-nl/nl428_credits"
LINE_61 = "ca-nl/nl428_donations_and_gifts_credit_line_61"
LINE_62 = "ca-nl/nl428_non_refundable_credits_line_62"
LINE_81 = "ca-nl/nl428_tax_line_81"
LINE_84 = "ca-nl/nl428_venture_capital_tax_credit_line_84"
LINE_85 = "ca-nl/nl428_tax_line_85"
INPUTS = {
    "line_12": "ca/donations_and_gifts_line_12",
    "line_82": "ca-nl/nl428_venture_capital_tax_credit_from_certificates_line_82",
    "line_83": "ca-nl/nl428_unused_venture_capital_tax_credit_line_83",
}
SALARY_ONLY_LINE_62 = D("1342.95")
SALARY_ONLY_LINE_81 = D("6147.49")


def _kind(name: str) -> AmountKind:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return kind


def _sheets(salary: str, **given: str) -> tuple[Worksheet, Worksheet]:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(_kind(INPUTS[name]), D(value)) for name, value in given.items()]
    worksheets = build_tax_computation().compute(NEWFOUNDLAND, 2025, *artifacts)
    (credits_sheet,) = worksheets[NL428_CREDITS]
    (nl428,) = worksheets[NL428]
    return credits_sheet, nl428


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(_kind(name)).value
    assert isinstance(value, Decimal)
    return value


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), ROUND_HALF_UP)


@pytest.mark.parametrize("name", [LINE_61, LINE_84])
def test_a_salary_only_caller_has_no_claim_on_lines_61_and_84(name: str) -> None:
    credits_sheet, nl428 = _sheets("70000")

    assert _value(nl428 if name == LINE_84 else credits_sheet, name) == D("0.00")


def test_a_donations_and_venture_capital_return_at_70000() -> None:
    credits_sheet, nl428 = _sheets("70000", line_12="2200", line_82="500.00", line_83="250.00")

    # Line 12 is 2,200: line 13 is the printed 200 and line 14 is 2,000. Line 61: 200 at 8.7% plus
    # 2,000 at 21.8%.
    line_61 = _cents(D("200") * D("0.087")) + _cents(D("2000") * D("0.218"))
    assert line_61 == D("453.40")
    # Line 62: line 58 (1,342.95) plus line 61, which line 66 takes off the tax.
    line_62 = SALARY_ONLY_LINE_62 + line_61
    assert line_62 == D("1796.35")
    # Line 81 falls by the same 453.40; line 84 is 500.00 plus 250.00; line 85 is line 81 less it.
    line_81 = SALARY_ONLY_LINE_81 - line_61
    line_84 = D("500.00") + D("250.00")
    line_85 = line_81 - line_84
    assert (line_81, line_84, line_85) == (D("5694.09"), D("750.00"), D("4944.09"))

    assert _value(credits_sheet, LINE_61) == line_61
    assert _value(credits_sheet, LINE_62) == line_62
    assert _value(nl428, LINE_81) == line_81
    assert _value(nl428, LINE_84) == line_84
    assert _value(nl428, LINE_85) == line_85


def test_a_line_82_amount_above_the_lifetime_maximum_is_refused() -> None:
    # The guide (5001-PC, line 82): "The lifetime maximum you can claim is $75,000."
    _sheets("70000", line_82="75000.00")
    with pytest.raises(InputAboveBoundError):
        _sheets("70000", line_82="75000.01")
