"""The British Columbia artifact catalog: British Columbia's own kinds, named from the British
Columbia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_bc import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BC428_CPP_CONTRIBUTIONS_LINE_27 = AmountKind.declare(
    CATALOG, "bc428_cpp_contributions_line_27", non_negative=True
)
"""CPP or QPP contributions, BC428 line 27 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

BC428_BRITISH_COLUMBIA_TAX_LINE_91 = AmountKind.declare(
    CATALOG, "bc428_british_columbia_tax_line_91", non_negative=True
)
"""British Columbia tax, BC428 line 91 "Enter this amount on line 42800 of your return.": the
British Columbia tax, entered on T1 line 42800."""
