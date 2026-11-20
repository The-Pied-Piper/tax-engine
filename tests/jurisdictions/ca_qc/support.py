"""The Quebec package list and the registries built over it.

Quebec is not yet listed in `tax_engine.registrations.JURISDICTIONS`, so the
tests of this package build their own package list (core, federal, Quebec)
here and take their kinds and capabilities from it. Each registry is built once per test process;
never register into one.
"""

from decimal import Decimal
from functools import cache
from pathlib import Path

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_qc
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact, ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import UnitRegistry
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import T2204_PREMIUMS_DEDUCTED_GIVEN


@cache
def quebec_packages() -> JurisdictionPackages:
    """The packages a Quebec return needs: core, federal and ca-qc."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_qc,
        )
    )


@cache
def quebec_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Quebec package list; never register into it."""
    kinds = ArtifactRegistry()
    quebec_packages().register(kinds)
    return kinds


@cache
def quebec_units() -> UnitRegistry:
    """The units of the Quebec package list; never register into it."""
    registry = UnitRegistry()
    quebec_packages().register_units(registry)
    return registry


@cache
def quebec_capabilities() -> CapabilityRegistry:
    """The capabilities of the Quebec package list; never register into it."""
    registry = CapabilityRegistry()
    quebec_packages().register_capabilities(registry)
    return registry


@cache
def quebec_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the Quebec list; never register into it."""
    registry = ParameterParserRegistry()
    quebec_packages().register_parameter_parsers(registry)
    return registry


def quebec_service(tmp_path: Path, manifest: str) -> TaxComputationService:
    """The engine over the Quebec package list, with `manifest` as the Quebec 2025 manifest.

    The manifest text is written to a temporary folder that stands in for the Quebec package's own
    directory, so a test can declare inputs and outputs (the real manifest declares none yet) and
    import forms with their dataset swaps; every other root, and the Quebec datasets, are the real
    ones.
    """
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "manifest.yaml").write_text(manifest, encoding="utf-8")
    roots = {**quebec_packages().roots(), Namespace("ca-qc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, quebec_kinds(), quebec_units()),
        YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units()),
        quebec_capabilities(),
    )


def t2204_worksheet(
    service: TaxComputationService, salary: str, given: str | None = None
) -> Worksheet:
    """The Quebec T2204 worksheet for a salary; line 4 is left blank unless `given` is passed."""
    starting = [Artifact(EMPLOYMENT_INCOME, Decimal(salary))]
    if given is not None:
        starting.append(Artifact(T2204_PREMIUMS_DEDUCTED_GIVEN, Decimal(given)))
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca/t2204"]
    return sheet
