"""The parts of a split form share one reference, so a reader can show them as one form.

NL428, SK428, AB428 and MB428 print one title across their main and credits parts; T1 is split
into its Steps 2 to 4 and Steps 5 and 6. $70,000 of employment income, 2025 and 2026.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

_PROVINCIAL = (
    ("CA-NL", "ca-nl/nl428", "ca-nl/nl428_credits", "Form NL428: Newfoundland and Labrador Tax"),
    ("CA-SK", "ca-sk/sk428", "ca-sk/sk428_credits", "Form SK428: Saskatchewan Tax"),
    ("CA-AB", "ca-ab/ab428", "ca-ab/ab428_credits", "Form AB428: Alberta Tax and Credits"),
    ("CA-MB", "ca-mb/mb428", "ca-mb/mb428_credits", "Form MB428: Manitoba Tax"),
)


def _sheets(code: str, year: int) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        JurisdictionCode(code), year, Artifact(EMPLOYMENT_INCOME, Decimal("70000"))
    )


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(("code", "main", "credits", "reference"), _PROVINCIAL)
def test_the_two_parts_of_a_provincial_428_share_one_reference(
    code: str, main: str, credits: str, reference: str, year: int
) -> None:
    sheets = _sheets(code, year)

    (main_sheet,) = sheets[main]
    (credits_sheet,) = sheets[credits]

    assert main_sheet.form_reference == reference
    assert credits_sheet.form_reference == reference
    assert main_sheet.form_title == credits_sheet.form_title == reference


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("code", ["CA-ON", "CA-NL", "CA-SK", "CA-AB", "CA-MB"])
def test_the_two_parts_of_the_t1_share_one_reference_but_keep_their_titles(
    code: str, year: int
) -> None:
    sheets = _sheets(code, year)

    (income,) = sheets["ca/t1_taxable_income"]
    (tax,) = sheets["ca/t1_tax_and_credits"]

    assert income.form_reference == tax.form_reference == "T1 return"
    assert income.form_title != tax.form_title


def test_a_form_that_is_not_split_keeps_its_title_as_its_reference() -> None:
    (schedule_8,) = _sheets("CA-ON", 2025)["ca/schedule_8"]

    assert schedule_8.form_reference == schedule_8.form_title
