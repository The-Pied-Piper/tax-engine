"""The Prince Edward Island package scaffold (2025): the package imports and its manifest loads. The
package is not yet listed in `registrations.JURISDICTIONS`: the manifest is complete only when the
later tickets merge."""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_pe
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.registrations import JURISDICTIONS
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_kinds,
    prince_edward_island_packages,
    prince_edward_island_units,
)

PE_DIR = Path(tax_engine.jurisdictions.ca_pe.__file__).parent


def test_the_package_names_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_pe.NAMESPACE == "ca-pe"


def test_the_manifest_loads_with_the_federal_imports() -> None:
    source = YamlJurisdictionSource(
        prince_edward_island_packages().roots(),
        prince_edward_island_kinds(),
        prince_edward_island_units(),
    )

    manifest = source.load(PE_DIR / "manifests" / "2025")

    assert manifest.jurisdiction.value == "CA-PE"
    assert manifest.valid_from_tax_year == 2025


def test_the_package_is_not_yet_listed_in_the_registered_jurisdictions() -> None:
    assert "ca-pe" not in {str(namespace) for namespace in JURISDICTIONS.roots()}
