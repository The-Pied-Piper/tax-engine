"""Where each part of the British Columbia marginal rate switches on, both tax years.

Each income tax part counts only where its own tax is above zero, and the tax reduction's slope
only inside the reduction's range, so the rate steps at the salaries below (found cent by cent from
the forms' own lines, with the extra-run check in `test_return_marginal_tax_rate_extra_run.py`
showing the rate agrees with the engine on each side). The 2026 figures are provisional, as the
2026 forms are not published.

2025, salary only:
- federal: T1 line 42900 is 0.00 at 18,820.26 and 0.01 at 18,820.27; the federal part opens
  (14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945);
- British Columbia: BC428 line 80 is 0.00 at 25,551.24 and 0.01 at 25,551.25, inside the tax
  reduction's range, so the part opens at 5.06% x 0.9241 + 3.56% x 0.99 = 0.08200346;
- the reduction's slope ends where BC428 line 79 reaches 0.00, at a salary of 41,183.21 (net
  income 40,806.38; line 78 is then 562.00): 0.08200346 falls to 0.04675946.

2026, salary only:
- federal: T1 line 42900 is 0.00 at 19,200.17 and 0.01 at 19,200.18;
- British Columbia: BC428 line 80 is 0.00 at 26,752.95 and 0.01 at 26,752.96, again inside the
  reduction's range, so the part opens at 5.6% x 0.9242 + 3.56% x 0.99 = 0.0869992;
- the reduction's slope ends at a salary of 45,370.60 (net income 44,951.89; line 78 is then
  690.00): 0.0869992 falls to 0.0517552.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")

# Year, salary, the marginal rate, the British Columbia part. The federal part is 0.1339945 (2025)
# or 0.129388 (2026) wherever the federal tax is above zero; the contributions are 0.0759 and
# 0.0758.
BOUNDARIES = [
    (2025, "18820.26", "0.0759", "0"),
    (2025, "18820.27", "0.2098945", "0"),
    (2025, "25551.24", "0.2098945", "0"),
    (2025, "25551.25", "0.29189796", "0.08200346"),
    (2025, "41183.20", "0.29189796", "0.08200346"),
    (2025, "41183.21", "0.25665396", "0.04675946"),
    (2026, "19200.17", "0.0758", "0"),
    (2026, "19200.18", "0.205188", "0"),
    (2026, "26752.95", "0.205188", "0"),
    (2026, "26752.96", "0.2921872", "0.0869992"),
    (2026, "45370.59", "0.2921872", "0.0869992"),
    (2026, "45370.60", "0.2569432", "0.0517552"),
]


@pytest.mark.parametrize(("year", "salary", "marginal", "british_columbia"), BOUNDARIES)
def test_each_part_switches_on_where_its_own_tax_turns_positive(
    year: int, salary: str, marginal: str, british_columbia: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-bc/return"]
    kinds = bundled_kinds()

    assert summary.get(kinds.kind("ca-bc/marginal_tax_rate")).value == D(marginal)
    assert summary.get(kinds.kind("ca-bc/british_columbia_marginal_rate")).value == D(
        british_columbia
    )
