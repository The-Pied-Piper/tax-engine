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

SOLIDARITY_QST_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "solidarity_qst_base_amount", non_negative=True
)
"""Solidarity tax credit, QST component, base amount ("montant de base" 363, Table C.9 of fiche
110201, July 2026 to June 2027): the printed figure, claimed whole."""
