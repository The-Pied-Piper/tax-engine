"""Test support: the T1 medical expenses amounts a caller gives.

T1 line 33099 is asked once, on the `ca/t1_lines_copied_by_provinces` form, as the optional input
`ca/medical_expenses`, and T1 line 33199 (other dependants) as
`ca/other_dependants_medical_expenses`. The provincial medical expenses lines read them from
there, so a test that wants one of these amounts asks for it here instead of declaring a provincial
input of its own.
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
