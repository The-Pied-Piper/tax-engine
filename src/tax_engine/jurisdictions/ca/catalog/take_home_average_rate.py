"""The federal catalog: the figures a return summary totals for the take-home average rate.

No form prints any of these figures, so none has a title or a line. Each province's return reads
the exports of Schedule 8 and T2204 into its own copy, adds them to the income tax and divides the
total by the salary.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

RETURN_CPP_BASE_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "return_cpp_base_contributions", non_negative=True
)
"""The return's own copy of the CPP base contributions on the return, Schedule 8 line 25: a
`core/record_total` of the form's export, which the average rate adds."""

RETURN_CPP_ENHANCED_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "return_cpp_enhanced_contributions", non_negative=True
)
"""The return's own copy of the CPP enhanced contributions, Schedule 8 line 28 (line 12 plus line
22): a `core/record_total` of the form's export, which the average rate adds."""

RETURN_EI_PREMIUM = AmountKind.declare(CATALOG, "return_ei_premium", non_negative=True)
"""The return's own copy of the EI premium, T2204 line 16: a `core/record_total` of the form's
export, which the average rate adds."""

RETURN_TOTAL_DEDUCTIONS = AmountKind.declare(CATALOG, "return_total_deductions", non_negative=True)
"""The take-home deductions added: the income tax (T1 line 43500), the CPP, the EI premium and, in
Quebec, the QPIP premium. The average rate divides it by the salary."""

AVERAGE_TAX_RATE = AmountKind.declare(CATALOG, "average_tax_rate", non_negative=True)
"""Average tax rate on the take-home basis (no form prints it): the income tax, CPP (Schedule 8
lines 25 and 28) and EI (T2204 line 16) together divided by the salary, as a fraction, so 0.1598
is 15.98%. The federal form `ca/take_home_average_rate` exports it and each province's return
summary reads it. Paid credits are not in it. It is 0 when the salary is 0."""
