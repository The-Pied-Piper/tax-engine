"""The federal Canada artifact catalog: artifact kinds named from Canada's own return (§2, §8).

Amounts are `Decimal`, non-negative unless the form prints no floor. Identifiers are stable:
`tests/jurisdictions/ca/test_catalog.py` snapshots them.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca.catalog.base import CATALOG as CATALOG

# The family modules are imported in the order of the T1, which is the order the kinds are
# declared on CATALOG, so they are not sorted.
# isort: off
from tax_engine.jurisdictions.ca.catalog.income import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.rrsp_fhsa import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.deductions import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t777 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1032_pension_income_splitting import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1043 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1139 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1206_share_dispositions import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t746 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t90 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t936 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t2205 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t1212 import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.t2017_reserve import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.taxable_income import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.capital_gains_deduction_charts import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.personal_amounts import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.non_refundable_credits import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.credits_against_federal_tax import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.investment_tax_credit import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.resp_aips import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.other_inputs import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.net_tax import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.alternative_minimum_tax import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.refundable_credits import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.refund import *  # noqa: F403
from tax_engine.jurisdictions.ca.catalog.rc381_cpp_qpp import *  # noqa: F403
# isort: on
