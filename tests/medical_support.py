"""Test support: the one medical expenses amount a caller gives.

T1 line 33099 is asked once, on the `ca/t1_medical_expenses` form, as the optional input
`ca/medical_expenses`; every provincial medical expenses line reads it from there. A test that
wants a medical amount asks for it here instead of declaring a provincial input of its own.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.registrations import artifact_kinds

MEDICAL_EXPENSES = "ca/medical_expenses"


def medical_expenses(amount: str) -> Artifact[Decimal]:
    """The caller's T1 line 33099 amount, as a starting artifact."""
    kind = artifact_kinds().kind(MEDICAL_EXPENSES)
    assert isinstance(kind, AmountKind)
    return Artifact(kind, Decimal(amount))


def other_dependants_medical_expenses(amount: str) -> Artifact[Decimal]:
    """The caller's T1 line 33199 amount (other dependants), as a starting artifact."""
    kind = artifact_kinds().kind("ca/other_dependants_medical_expenses")
    assert isinstance(kind, AmountKind)
    return Artifact(kind, Decimal(amount))
