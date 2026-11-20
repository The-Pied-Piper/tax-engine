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

TP1_PENSIONABLE_SALARY_GIVEN_LINE_98_1 = AmountKind.declare(
    CATALOG, "tp1_pensionable_salary_given_line_98_1", non_negative=True
)
"""Pensionable salary or wages (QPP) as given, TP-1 line 98.1 "Pensionable salary or wages (QPP).
RL-1 slip, box G": the figure the caller copies from the RL-1 slip; blank when the caller does
not give it, and line 98.1 is then computed from the salary."""

TP1_PENSIONABLE_SALARY_LINE_98_1 = AmountKind.declare(
    CATALOG, "tp1_pensionable_salary_line_98_1", non_negative=True
)
"""Pensionable salary or wages (QPP), TP-1 line 98.1 "Pensionable salary or wages (QPP). RL-1 slip,
box G": the figure given, else the salary up to $81,200."""
