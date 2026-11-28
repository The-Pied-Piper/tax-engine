"""The marginal tax rate of a filer with typed part-year CPP months, through the Ontario return.

`ca/cpp_months` typed as 1 to 11 prorates the CPP basic exemption (Schedule 8 line E: $3,500 x
months / 12), so with 1, 3 or 6 months the exemption ($292, $875, $1,750) is below $2,000 and a
further dollar of salary pays CPP from the first dollar above it, before any income tax is due.
The credit on the CPP base rate and the EI premium then exceeded the federal rate before credits
(and the province's), and the subtraction that is not allowed to go negative raised at $2,000 to
$2,033 of salary. Where no tax is paid the rate is 0 (the gate), so the difference is floored at
zero before the gate applies. With 11 months the exemption ($3,208.33) is above the band, so no CPP
is charged and the full-year rates are unchanged.

Hand-computed (T1 line 114 credit rate, Schedule 8 lines A and E, T2204 line 16), born 1980,
salary only, no income tax in this range: $0 nothing; $1,999 only the
CPP base rate, 0.0595 (EI starts at $2,000); $2,000 to $2,033 the first dollar of EI insurable
earnings is taken in full, so 1 plus CPP, 1.0595; $2,034 CPP and EI, 0.0595 + EI 1.63% (2026) or
1.64% (2025) = 0.0758 or 0.0759. With 11 months no CPP: $1,999 is 0, 1 in the band, then EI alone
(0.0163, 2025 0.0164).
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
    (2025, 1, "1999", "0.0595"),
    (2025, 1, "2000", "1.0595"),
    (2025, 1, "2033", "1.0595"),
    (2025, 1, "2034", "0.0759"),
    (2025, 3, "0", "0"),
    (2025, 3, "1999", "0.0595"),
    (2025, 3, "2000", "1.0595"),
    (2025, 3, "2033", "1.0595"),
    (2025, 3, "2034", "0.0759"),
    (2025, 6, "0", "0"),
    (2025, 6, "1999", "0.0595"),
    (2025, 6, "2000", "1.0595"),
    (2025, 6, "2033", "1.0595"),
    (2025, 6, "2034", "0.0759"),
    (2025, 11, "0", "0"),
    (2025, 11, "1999", "0"),
    (2025, 11, "2000", "1.0000"),
    (2025, 11, "2033", "1.0000"),
    (2025, 11, "2034", "0.0164"),
    (2026, 1, "0", "0"),
    (2026, 1, "1999", "0.0595"),
    (2026, 1, "2000", "1.0595"),
    (2026, 1, "2033", "1.0595"),
    (2026, 1, "2034", "0.0758"),
    (2026, 3, "0", "0"),
    (2026, 3, "1999", "0.0595"),
    (2026, 3, "2000", "1.0595"),
    (2026, 3, "2033", "1.0595"),
    (2026, 3, "2034", "0.0758"),
    (2026, 6, "0", "0"),
    (2026, 6, "1999", "0.0595"),
    (2026, 6, "2000", "1.0595"),
    (2026, 6, "2033", "1.0595"),
    (2026, 6, "2034", "0.0758"),
    (2026, 11, "0", "0"),
    (2026, 11, "1999", "0"),
    (2026, 11, "2000", "1.0000"),
    (2026, 11, "2033", "1.0000"),
    (2026, 11, "2034", "0.0163"),
]


def _marginal(year: int, months: int, salary: str) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"),
            year,
            (
                Artifact(EMPLOYMENT_INCOME, D(salary)),
                Artifact(BIRTH_YEAR, 1980),
                Artifact(CPP_MONTHS, months),
            ),
        )
    )
    (summary,) = worksheets["ca-on/return"]
    value = summary.get(bundled_kinds().kind("ca-on/marginal_tax_rate")).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("year", "months", "salary", "rate"), CASES)
def test_a_typed_part_year_of_cpp_months_has_a_marginal_rate_at_every_salary(
    year: int, months: int, salary: str, rate: str
) -> None:
    assert _marginal(year, months, salary).quantize(D("0.0001")) == D(rate)
