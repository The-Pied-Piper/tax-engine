"""The marginal tax rate of a filer with typed part-year QPP months, through the Quebec return.

`ca/cpp_months` typed as 1 to 11 prorates the CPP basic exemption (Schedule 8 line E: $3,500 x
months / 12), so with 1, 3 or 6 months the exemption ($292, $875, $1,750) is below $2,000 and a
further dollar of salary pays CPP from the first dollar above it, before any income tax is due.
The credit on the CPP base rate and the EI premium then exceeded the federal rate before credits
(and the province's), and the subtraction that is not allowed to go negative raised at $2,000 to
$2,033 of salary. Where no tax is paid the rate is 0 (the gate), so the difference is floored at
zero before the gate applies. With 11 months the exemption ($3,208.33) is above the band, so no CPP
is charged and the full-year rates are unchanged.

Hand-computed, salary only, born 1980, no income tax in this range (basic personal amount; T1
line 114 credit rate, Schedule 8 lines A and E, T2204): at $0 nothing; at $1,999 only the QPP base
rate (2025 6.40%, 2026 6.30%); at $2,000 the first dollar of EI insurable earnings is taken in
full, so 1 plus the QPP and QPIP rates (2025 1.0689, 2026 1.0673), which holds a little past
$2,000 and is over by $2,033; from there the QPP, EI and QPIP rates (2025 0.0820, 2026 0.0803).
With 11 months no QPP: $1,999 is 0, $2,000 is 1 plus the QPIP rate (2025 1.0049, 2026 1.0043),
then EI and QPIP (2025 0.0180, 2026 0.0173).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import CPP_MONTHS
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
# (tax year, months, salary, rate)
CASES = [
    (2025, 1, "0", "0"),
    (2025, 1, "1999", "0.0640"),
    (2025, 1, "2000", "1.0689"),
    (2025, 1, "2033", "0.0820"),
    (2025, 1, "2034", "0.0820"),
    (2025, 3, "0", "0"),
    (2025, 3, "1999", "0.0640"),
    (2025, 3, "2000", "1.0689"),
    (2025, 3, "2033", "0.0820"),
    (2025, 3, "2034", "0.0820"),
    (2025, 6, "0", "0"),
    (2025, 6, "1999", "0.0640"),
    (2025, 6, "2000", "1.0689"),
    (2025, 6, "2033", "0.0820"),
    (2025, 6, "2034", "0.0820"),
    (2025, 11, "0", "0"),
    (2025, 11, "1999", "0"),
    (2025, 11, "2000", "1.0049"),
    (2025, 11, "2033", "0.0180"),
    (2025, 11, "2034", "0.0180"),
    (2026, 1, "0", "0"),
    (2026, 1, "1999", "0.0630"),
    (2026, 1, "2000", "1.0673"),
    (2026, 1, "2033", "0.0803"),
    (2026, 1, "2034", "0.0803"),
    (2026, 3, "0", "0"),
    (2026, 3, "1999", "0.0630"),
    (2026, 3, "2000", "1.0673"),
    (2026, 3, "2033", "0.0803"),
    (2026, 3, "2034", "0.0803"),
    (2026, 6, "0", "0"),
    (2026, 6, "1999", "0.0630"),
    (2026, 6, "2000", "1.0673"),
    (2026, 6, "2033", "0.0803"),
    (2026, 6, "2034", "0.0803"),
    (2026, 11, "0", "0"),
    (2026, 11, "1999", "0"),
    (2026, 11, "2000", "1.0043"),
    (2026, 11, "2033", "0.0173"),
    (2026, 11, "2034", "0.0173"),
]


def _marginal(year: int, months: int, salary: str) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"),
            year,
            (
                Artifact(EMPLOYMENT_INCOME, D(salary)),
                Artifact(BIRTH_YEAR, 1980),
                Artifact(CPP_MONTHS, months),
            ),
        )
    )
    (summary,) = worksheets["ca-qc/return"]
    value = summary.get(bundled_kinds().kind("ca-qc/marginal_tax_rate")).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "months", "salary", "rate"), CASES)
def test_a_typed_part_year_of_cpp_months_has_a_marginal_rate_at_every_salary(
    year: int, months: int, salary: str, rate: str
) -> None:
    assert _marginal(year, months, salary).quantize(D("0.0001")) == D(rate)
