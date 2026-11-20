"""The Quebec artifact catalog: Quebec's own kinds, named
from the Quebec forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_qc import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

T1_LINE_21 = AmountKind.declare(CATALOG, "t1_line_21")
"""Add lines 1 to 20, 5005-R line 21 "Line 21: Add lines 1 to 20.": the employment income of line 1
(`ca/employment_income`) and line 2 (`ca/other_employment_income`); lines 3 to 20 are not built (the
salary-only filer has none). Produced by one core/sum (`t1_taxable_income_line_21.yaml`)."""

NET_SELF_EMPLOYMENT_INCOME = AmountKind.declare(CATALOG, "net_self_employment_income")
"""Net self-employment income, 5005-R line 27 "Line 27: Add lines 22 to 26. Net self-employment
income =": the printed sum of the skipped block of lines 22 to 26, one optional input read as 0. Not
floored: the form prints no floor and a loss is shown in brackets."""

T1_LINE_28 = AmountKind.declare(CATALOG, "t1_line_28")
"""Line 21 plus line 27, 5005-R line 28 "Line 28: Line 21 plus line 27 =". Not floored: line 27 may
be a loss. Produced by one core/sum (`t1_taxable_income_line_28.yaml`)."""
