"""The Alberta package list and the registries built over it, for the older Alberta tests.

Alberta is listed in `tax_engine.registrations.JURISDICTIONS` (as is Ontario), and a test of the
registered engine takes the `take_home_service` fixture of `conftest.py` or the registries of
`tax_engine.registrations`. The tests written before the listing build their own package list
(core, federal, Alberta) here and take their kinds, units, capabilities and parameter parsers from
it, as `tests/kinds.py` and `tests/capabilities.py` do for the bundled list. Each registry is
built once per test process; never register into one.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import UnitRegistry


@cache
def alberta_packages() -> JurisdictionPackages:
    """The packages an Alberta return needs: core, the federal package and Alberta."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_ab,
        )
    )


@cache
def alberta_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Alberta package list; never register into it."""
    kinds = ArtifactRegistry()
    alberta_packages().register(kinds)
    return kinds


@cache
def alberta_units() -> UnitRegistry:
    """The units of the Alberta package list; never register into it."""
    registry = UnitRegistry()
    alberta_packages().register_units(registry)
    return registry


@cache
def alberta_capabilities() -> CapabilityRegistry:
    """The capabilities of the Alberta package list; never register into it."""
    registry = CapabilityRegistry()
    alberta_packages().register_capabilities(registry)
    return registry


@cache
def alberta_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the Alberta package list; never register into it."""
    registry = ParameterParserRegistry()
    alberta_packages().register_parameter_parsers(registry)
    return registry


def alberta_service(tmp_path: Path, manifest: str) -> TaxComputationService:
    """The engine over the Alberta package list, with `manifest` as the Alberta 2025 manifest.

    The manifest text is written to a temporary folder that stands in for the Alberta package's
    own directory, so a test can declare imports (and their dataset swaps) without the real
    manifest; every other root, and the Alberta datasets, are the real ones.
    """
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "manifest.yaml").write_text(manifest, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )
