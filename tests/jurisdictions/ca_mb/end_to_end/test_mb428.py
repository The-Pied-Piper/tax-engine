"""Form MB428 (2025, Manitoba tax, single filer) from the salary alone: the real Manitoba manifest
composed end to end.

Every MB428 line part has its own test with its neighbours typed in. This module runs the whole
chain: the registered engine (`build_tax_computation`) over the real Manitoba 2025 manifest, with
the gross salary (`ca/employment_income`) the only input and every optional input left blank. It
asserts the Manitoba tax of MB428 line 82 at salaries of $10,000, $20,000, $70,000, $200,000 and
$250,000, and the basic personal amount of Worksheet MB428 line 9 at the same salaries.

Form text (Form MB428, CRA 5007-C): line 82 "Enter this amount on line 42800 of your return.";
the wording of the line itself is to be confirmed, the form text is not in the forms folder.

The line 82 figures are 0.00 / 284.08 / 5,747.59 / 26,863.55 / 35,980.46. At $70,000 they are
derived apart from the engine in `test_line_82_at_70000_follows_from_the_printed_figures`. The
Worksheet MB428 line 9 figure is the basic personal amount: 15,780.00 up to the printed income
threshold, then reduced; at a salary of $250,000 the phase-out leaves 11,919.74. The 250,000 figures
are the engine's own, not computed by hand; the form text of the worksheet is to be confirmed.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
MANITOBA = JurisdictionCode("CA-MB")
MB428 = "ca-mb/mb428"
MB428_CREDITS = "ca-mb/mb428_credits"
WORKSHEET = "ca-mb/worksheet_mb428"
LINE_1 = "ca-mb/mb428_taxable_income_line_1"
LINE_33 = "ca-mb/mb428_credits_subtotal_line_33"
LINE_82 = "ca-mb/mb428_manitoba_tax_line_82"
WORKSHEET_LINE_9 = "ca-mb/worksheet_mb428_basic_personal_amount_line_9"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), ROUND_HALF_UP)


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(MANITOBA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))


@pytest.mark.parametrize(
    ("salary", "manitoba_tax"),
    [
        ("10000", "0.00"),
        ("20000", "284.08"),
        ("70000", "5747.59"),
        ("200000", "26863.55"),
        ("250000", "35980.46"),
    ],
)
def test_line_82_is_the_manitoba_tax(salary: str, manitoba_tax: str) -> None:
    (mb428,) = _worksheets(salary)[MB428]

    assert _figure(mb428, LINE_82) == D(manitoba_tax)


def test_line_82_at_70000_follows_from_the_printed_figures() -> None:
    worksheets = _worksheets("70000")
    (credits_sheet,) = worksheets[MB428_CREDITS]
    taxable_income = _figure(credits_sheet, LINE_1)
    credits_base = _figure(credits_sheet, LINE_33)
    tax_on_taxable_income = _cents(
        D("47000") * D("0.108") + (taxable_income - D("47000")) * D("0.1275")
    )
    credits = _cents(credits_base * D("0.108"))

    assert taxable_income == D("69335.00")
    assert credits_base == D("20149.23")
    assert tax_on_taxable_income == D("7923.71")
    assert credits == D("2176.12")
    assert tax_on_taxable_income - credits == D("5747.59")
    (mb428,) = worksheets[MB428]
    assert _figure(mb428, LINE_82) == D("5747.59")


@pytest.mark.parametrize(
    ("salary", "basic_personal_amount"),
    [
        ("10000", "15780.00"),
        ("20000", "15780.00"),
        ("70000", "15780.00"),
        ("200000", "15780.00"),
        ("250000", "11919.74"),
    ],
)
def test_worksheet_line_9_is_the_basic_personal_amount(
    salary: str, basic_personal_amount: str
) -> None:
    (worksheet,) = _worksheets(salary)[WORKSHEET]

    assert _figure(worksheet, WORKSHEET_LINE_9) == D(basic_personal_amount)
