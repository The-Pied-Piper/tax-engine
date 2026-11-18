"""Form MB479 (2025, Manitoba credits, single filer) from the salary alone: the real Manitoba
manifest composed end to end, with Schedule MB428-A.

The registered engine (`build_tax_computation`) runs over the real Manitoba 2025 manifest, with the
gross salary (`ca/employment_income`) the only input and every optional input left blank. It
asserts MB479 line 81, the Manitoba credits of T1 line 47900, and Schedule MB428-A line 12, the
family tax benefit, at salaries of $10,000, $20,000, $70,000, $200,000 and $250,000.

Form text (Form MB479, CRA 5007-TC): line 81 "Enter this amount on line 47900 of your return.";
the wording of the line itself is to be confirmed, the form text is not in the forms folder.

The MB479 line 81 figures are 95.65 at $10,000 (the personal tax credit, which pays out only
where the Manitoba tax leaves it unused) and 0.00 at every other salary. The Schedule MB428-A
line 12 figures are 1,170.85 at $10,000, 279.85 at $20,000 and 0.00 above (the printed reduction
takes the benefit to nothing). Both are hand-computed in the form tests; here the engine's whole run
is pinned.
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
MANITOBA = JurisdictionCode("CA-MB")
MB479 = "ca-mb/mb479"
MB428_A = "ca-mb/mb428_a"
MB479_LINE_81 = "ca-mb/mb479_manitoba_credits_line_81"
MB428_A_LINE_12 = "ca-mb/mb428_a_family_tax_benefit_line_12"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(MANITOBA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))


@pytest.mark.parametrize(
    ("salary", "manitoba_credits"),
    [
        ("10000", "95.65"),
        ("20000", "0.00"),
        ("70000", "0.00"),
        ("200000", "0.00"),
        ("250000", "0.00"),
    ],
)
def test_line_81_is_the_manitoba_credits(salary: str, manitoba_credits: str) -> None:
    (mb479,) = _worksheets(salary)[MB479]

    assert _figure(mb479, MB479_LINE_81) == D(manitoba_credits)


@pytest.mark.parametrize(
    ("salary", "family_tax_benefit"),
    [
        ("10000", "1170.85"),
        ("20000", "279.85"),
        ("70000", "0.00"),
        ("200000", "0.00"),
        ("250000", "0.00"),
    ],
)
def test_mb428_a_line_12_is_the_family_tax_benefit(salary: str, family_tax_benefit: str) -> None:
    (mb428_a,) = _worksheets(salary)[MB428_A]

    assert _figure(mb428_a, MB428_A_LINE_12) == D(family_tax_benefit)
