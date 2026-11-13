"""Form AB428 (2025, Alberta tax, single filer) from the salary alone: the real Alberta manifest
composed end to end, through the registered engine.

Every AB428 line part has its own test with its neighbours typed in. This module runs the whole
chain: the bundled engine (`build_tax_computation`, Alberta listed in
`registrations.JURISDICTIONS`) over the real Alberta 2025 manifest, with the gross salary
(`ca/employment_income`) the only input and every optional input left blank. It asserts the Alberta
tax of AB428 line 75 and the return's T1 line 167 ("ca/refund_or_balance_owing") at salaries of
$20,000, $70,000 and $200,000, and the intermediate figures of the form on the way (lines 54, 62,
66 and 68).

Form text (Form AB428, CRA 5009-c): "Line 75: Line 73 minus line 74 (if negative, enter "0")
Enter this amount on line 42800 of your return. Alberta tax =".

The line 75 figures are the ticket's hand-computed values (from the printed form and the repo
figures, not a CRA example): 0.00 / 3,598.12 / 17,680.36. The T1 line 167 figures, and the
intermediate lines, are the engine's own: they were not computed by hand and pin the current
output of the whole chain. Line 167 is the refund (negative) or balance owing (positive) of the
return: at $20,000 the Canada workers benefit and the credits exceed the tax, so it is negative.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
ALBERTA = JurisdictionCode("CA-AB")
AB428 = "ca-ab/ab428"
AB428_CREDITS = "ca-ab/ab428_credits"
RETURN = "ca-ab/return"
LINE_54 = "ca-ab/ab428_credits_at_rate_line_54"
LINE_62 = "ca-ab/ab428_credits_from_line_58_line_62"
LINE_66 = "ca-ab/ab428_tax_after_credits_line_66"
LINE_68 = "ca-ab/ab428_tax_line_68"
LINE_75 = "ca-ab/ab428_alberta_tax_line_75"
LINE_167 = "ca/refund_or_balance_owing"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(ALBERTA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))


@pytest.mark.parametrize(
    ("salary", "alberta_tax"),
    [("20000", "0.00"), ("70000", "3598.12"), ("200000", "17680.36")],
)
def test_line_75_is_the_alberta_tax(salary: str, alberta_tax: str) -> None:
    (ab428,) = _worksheets(salary)[AB428]

    assert _figure(ab428, LINE_75) == D(alberta_tax)


@pytest.mark.parametrize(
    ("salary", "refund_or_balance_owing"),
    [("20000", "-1591.91"), ("70000", "11183.76"), ("200000", "57148.10")],
)
def test_t1_line_167_is_the_refund_or_balance_owing(
    salary: str, refund_or_balance_owing: str
) -> None:
    (summary,) = _worksheets(salary)[RETURN]

    assert _figure(summary, LINE_167) == D(refund_or_balance_owing)


@pytest.mark.parametrize(
    ("salary", "line_54", "line_62", "line_66", "line_68"),
    [
        ("20000", "1877.42", "1877.42", "0.00", "0.00"),
        ("70000", "2135.38", "2135.38", "3598.12", "3598.12"),
        ("200000", "2140.53", "2140.53", "17680.36", "17680.36"),
    ],
)
def test_the_lines_leading_to_line_75(
    salary: str, line_54: str, line_62: str, line_66: str, line_68: str
) -> None:
    worksheets = _worksheets(salary)
    (credits,) = worksheets[AB428_CREDITS]
    (ab428,) = worksheets[AB428]

    assert _figure(credits, LINE_54) == D(line_54)
    assert _figure(ab428, LINE_62) == D(line_62)
    assert _figure(ab428, LINE_66) == D(line_66)
    assert _figure(ab428, LINE_68) == D(line_68)
