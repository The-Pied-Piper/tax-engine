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

PPIP_PREMIUMS_GIVEN = AmountKind.declare(CATALOG, "ppip_premiums_given", non_negative=True)
"""PPIP premiums paid as given, 5005-R line 91 "Line 91 and line 31205: Provincial parental
insurance plan (PPIP) premiums paid (box 55 of all T4 slips) (maximum $484.12)": the figure the
caller gives, from the T4 slips; blank when the caller does not give it, and line 91 is then
computed."""

PPIP_PREMIUMS_PAID = AmountKind.declare(CATALOG, "ppip_premiums_paid", non_negative=True)
"""PPIP premiums paid, 5005-R line 91 "Line 91 and line 31205: Provincial parental insurance plan
(PPIP) premiums paid (box 55 of all T4 slips) (maximum $484.12)": the given figure
(`ca-qc/ppip_premiums_given`) or, when none is given, 0.494% of the employment income to the
$98,000 maximum insurable income (maximum $484.12). TP-1 line 97 (RL-1 box H) is the same figure."""
