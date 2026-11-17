"""Manitoba is not yet in `tax_engine.registrations.JURISDICTIONS`.

Listing it makes the service's startup check build the Manitoba manifest, and a partial manifest
fails that check (T1 needs `ca/provincial_tax.amount`, which no Manitoba form supplies until the
MB428 tax form exists, and the manifest has no `inputs` yet). The end-to-end ticket lists Manitoba
and deletes this test.
"""

from __future__ import annotations

from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.registrations import JURISDICTIONS


def test_manitoba_is_not_listed() -> None:
    assert JurisdictionCode("CA-MB") not in JURISDICTIONS.jurisdiction_codes()
