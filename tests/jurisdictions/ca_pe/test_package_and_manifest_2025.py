"""The Prince Edward Island package scaffold (2025): the package imports, its manifest loads and
`ca-pe/cent_rounding` (Form PE428, 5002-C) is half-up to the cent. The package is not yet listed in
`registrations.JURISDICTIONS`: the manifest is complete only when the later tickets merge."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca_pe
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.registrations import JURISDICTIONS
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_kinds,
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
    prince_edward_island_units,
)

PE_DIR = Path(tax_engine.jurisdictions.ca_pe.__file__).parent
FAMILY = "ca-pe/cent_rounding"


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


def test_2025_cent_rounding_is_half_up_to_the_cent() -> None:
    source = YamlParameterSource(
        prince_edward_island_packages().roots(),
        prince_edward_island_parameter_parsers(),
        prince_edward_island_units(),
    )

    data = source.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt",
    )


def test_the_package_is_not_yet_listed_in_the_registered_jurisdictions() -> None:
    assert "ca-pe" not in {str(namespace) for namespace in JURISDICTIONS.roots()}
