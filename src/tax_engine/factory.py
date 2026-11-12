"""Construct the default tax computation engine from the bundled jurisdictions."""

from tax_engine.adapters.inbound.trace_english.unit_text import EnglishUnitTextRegistry
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.registrations import (
    JURISDICTIONS,
    artifact_kinds,
    capabilities,
    parameter_parsers,
    units,
)


def build_tax_computation() -> TaxComputationService:
    """Build the tax computation engine over the bundled jurisdiction packages."""
    kinds = artifact_kinds()
    roots = JURISDICTIONS.roots()
    registered_units = units()
    EnglishUnitTextRegistry.shared().require(registered_units.units)
    service = TaxComputationService(
        YamlJurisdictionSource(roots, kinds, registered_units),
        YamlParameterSource(roots, parameter_parsers(), registered_units),
        capabilities(),
    )
    service.check(JURISDICTIONS.jurisdiction_codes())
    return service
