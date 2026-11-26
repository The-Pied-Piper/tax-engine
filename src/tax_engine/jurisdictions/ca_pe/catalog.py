"""The Prince Edward Island artifact catalog: Prince Edward Island's own kinds, named from the
Prince Edward Island forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_pe import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, PE428 line 9 "Line 9 and line 58040: Basic personal amount Claim
$14,650": the printed $14,650, claimed whole and not income-tested."""

PE428_AGE_AMOUNT_LINE_10 = AmountKind.declare(
    CATALOG, "pe428_age_amount_line_10", non_negative=True
)
"""Age amount (if you were born in 1960 or earlier) (use Worksheet PE428) (maximum $6,510), PE428
line 10 "Line 10 and line 58080: Age amount (if you were born in 1960 or earlier) (use Worksheet
PE428) (maximum $6,510)": the amount as the filer gives it, an optional input; a blank input is
read as blank."""
