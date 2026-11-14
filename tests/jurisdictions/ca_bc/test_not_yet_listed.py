"""British Columbia is not yet in `tax_engine.registrations.JURISDICTIONS`.

Listing it makes the service's startup check build the British Columbia manifest, and a partial
manifest fails that check (T1 needs `ca/provincial_tax.amount`, which no British Columbia form
supplies until the BC428 tax form exists, and the manifest has no `inputs` yet). The end-to-end
ticket lists British Columbia and deletes this test.
"""

from __future__ import annotations

from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.registrations import JURISDICTIONS


def test_british_columbia_is_not_listed() -> None:
    assert JurisdictionCode("CA-BC") not in JURISDICTIONS.jurisdiction_codes()
