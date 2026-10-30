"""Construct the default tax computation engine from the bundled jurisdictions."""

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.registrations import JURISDICTIONS


def build_tax_computation() -> TaxComputationService:
    """Build the tax computation engine over the bundled jurisdiction packages."""
    JURISDICTIONS.register()
    roots = JURISDICTIONS.roots()
    return TaxComputationService(
        YamlJurisdictionSource(roots),
        YamlParameterSource(roots),
        CapabilityRegistry.shared(),
        ArtifactRegistry.shared(),
    )
