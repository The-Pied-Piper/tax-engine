"""A jurisdiction and every manifest version stored for it (design.md §4).

It answers which manifest applies to a tax year, refusing to choose between manifests valid from
the same year; the computation-date question (retroactive successors) is deferred.
"""

from __future__ import annotations

from dataclasses import dataclass

from tax_engine.domain.errors import AmbiguousManifestError, NotFoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest


@dataclass(frozen=True, slots=True)
class Jurisdiction:
    """A jurisdiction's code and every manifest stored for it, in any order."""

    code: JurisdictionCode
    manifests: tuple[Manifest, ...]

    def manifest_for(self, tax_year: int) -> Manifest:
        """The manifest with the greatest `valid_from_tax_year` not after `tax_year`.

        Raises NotFoundError if every manifest starts later, and AmbiguousManifestError if more
        than one starts in that greatest year; both name the jurisdiction and tax year.
        """
        applicable = [m for m in self.manifests if m.valid_from_tax_year <= tax_year]
        if not applicable:
            raise NotFoundError(f"no manifest for jurisdiction {self.code} in tax year {tax_year}")
        latest = max(manifest.valid_from_tax_year for manifest in applicable)
        best = [m for m in applicable if m.valid_from_tax_year == latest]
        if len(best) > 1:
            versions = ", ".join(str(v) for v in sorted(m.version for m in best))
            raise AmbiguousManifestError(
                f"jurisdiction {self.code} has manifest versions {versions} all valid from "
                f"{latest}, so none is the one for tax year {tax_year}"
            )
        return best[0]
