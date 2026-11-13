"""Form AB428 (2026, Alberta tax, single filer) from the salary alone: the real Alberta manifest
composed end to end for tax year 2026, through the registered engine.

The Alberta 2026 datasets are PROVISIONAL: each carries a `# Provisional:` header, the 2026 forms
(Form AB428, CRA 5009-c; Worksheet AB428, CRA 5009-d; Schedule 6, CRA 5009-S6) are not yet
published, and the figures come from T4127 (Jan 2026) or are carried forward or inferred from 2025
(the four Alberta Schedule 6 figures and the supplemental credit base are inferred). The pinned
figures are therefore not confirmed CRA figures: they follow the provisional datasets, and must be
re-checked when CRA publishes the 2026 forms.

The Alberta manifest is 2025-only but the engine runs 2026 on it, reading each dataset family's
2026 file. The bundled engine (`build_tax_computation`, Alberta listed in
`registrations.JURISDICTIONS`) runs with the gross salary (`ca/employment_income`) the only input
and every optional input left blank. It asserts the Alberta tax of AB428 line 75 and the return's
T1 line 167 ("ca/refund_or_balance_owing") at salaries of $20,000, $70,000 and $200,000, and the
intermediate figures of the form on the way (lines 54, 62, 66 and 68).

Form text (Form AB428, CRA 5009-c): "Line 75: Line 73 minus line 74 (if negative, enter "0")
Enter this amount on line 42800 of your return. Alberta tax =".

Every figure here was computed by hand, independently of the engine, with plain decimal
arithmetic from the 2026 Alberta and federal datasets (CPP and EI per the datasets, T4127 for the
2026 figures), and the engine then agreed to the cent: lines 54, 62, 66, 68 and 75, and T1 line
167 (federal tax less the federal credits, plus Alberta tax, less the Canada workers benefit of
Alberta Schedule 6). Line 167 is the refund (negative) or balance owing (positive) of the return:
at $20,000 the Canada workers benefit and the credits exceed the tax, so it is negative. For
comparison, the 2025 line 75 figures are 0.00 / 3,598.12 / 17,680.36.
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
    return build_tax_computation().compute(ALBERTA, 2026, Artifact(EMPLOYMENT_INCOME, D(salary)))


@pytest.mark.parametrize(
    ("salary", "alberta_tax"),
    [("20000", "0.00"), ("70000", "3534.79"), ("200000", "17500.28")],
)
def test_line_75_is_the_alberta_tax(salary: str, alberta_tax: str) -> None:
    (ab428,) = _worksheets(salary)[AB428]

    assert _figure(ab428, LINE_75) == D(alberta_tax)


@pytest.mark.parametrize(
    ("salary", "refund_or_balance_owing"),
    [("20000", "-1681.51"), ("70000", "10812.98"), ("200000", "56376.82")],
)
def test_t1_line_167_is_the_refund_or_balance_owing(
    salary: str, refund_or_balance_owing: str
) -> None:
    (summary,) = _worksheets(salary)[RETURN]

    assert _figure(summary, LINE_167) == D(refund_or_balance_owing)


@pytest.mark.parametrize(
    ("salary", "line_54", "line_62", "line_66", "line_68"),
    [
        ("20000", "1912.94", "1912.94", "0.00", "0.00"),
        ("70000", "2174.71", "2174.71", "3534.79", "3534.79"),
        ("200000", "2192.92", "2192.92", "17500.28", "17500.28"),
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
