"""The Saskatchewan 2026 return for a filer aged 65 or older: SK428 line 82 (Saskatchewan tax)
with the provisional 2026 age amount (5,901.00), age amount income threshold (43,927.00) and
senior supplementary amount (2,569), each the 2025 form's figure indexed by the 2026 factor.

The registered engine runs over the real Saskatchewan manifest for 2026 with the gross salary and
the year of birth 1950 as the only inputs. Worked by hand at a salary of $30,000, below the
threshold so the age amount is claimed whole: the tax at 10.5% is 3,150.00; the credits are the
basic personal amount 20,381 + the age amount 5,901 + the senior supplementary amount 2,569 + EI
489.00 (1.63% of 30,000; no CPP at this age) = 29,340.00, which at 10.5% is 3,080.70; line 82 is
3,150.00 - 3,080.70 = 69.30. Without a birth year the same salary pays 793.10.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.registrations import artifact_kinds

D = Decimal
SASKATCHEWAN = JurisdictionCode("CA-SK")
SK428 = "ca-sk/sk428"
LINE_82 = "ca-sk/sk428_saskatchewan_tax_line_82"


def _line_82(salary: str, birth_year: int | None) -> Decimal:
    salary_input: tuple[Artifact[Decimal], ...] = (Artifact(EMPLOYMENT_INCOME, D(salary)),)
    year_input: tuple[Artifact[int], ...] = (
        () if birth_year is None else (Artifact(BIRTH_YEAR, birth_year),)
    )
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(SASKATCHEWAN, 2026, (*salary_input, *year_input))
    )
    kind = artifact_kinds().kind(LINE_82)
    assert isinstance(kind, AmountKind)
    (sheet,) = worksheets[SK428]
    return sheet.get(kind).value


def test_line_82_born_1950_at_30000_uses_the_indexed_age_figures() -> None:
    assert _line_82("30000", 1950) == D("69.30")


def test_line_82_born_1950_is_lower_than_without_a_birth_year() -> None:
    assert _line_82("30000", None) == D("793.10")
