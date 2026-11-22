"""Construct the default tax computation engine from the bundled jurisdictions."""

from tax_engine.adapters.inbound.take_home_text import EnglishTakeHomeText
from tax_engine.adapters.inbound.trace_english.unit_text import EnglishUnitTextRegistry
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.take_home import TakeHomeService
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
    return _build()[1]


def build_take_home() -> TakeHomeService:
    """Build the take-home service over the bundled jurisdiction packages, in English."""
    jurisdictions, computation = _build()
    return TakeHomeService(jurisdictions, computation, EnglishTakeHomeText())


def _build() -> tuple[YamlJurisdictionSource, TaxComputationService]:
    kinds = artifact_kinds()
    roots = JURISDICTIONS.roots()
    registered_units = units()
    EnglishUnitTextRegistry.shared().require(registered_units.units)
    jurisdictions = YamlJurisdictionSource(roots, kinds, registered_units)
    computation = TaxComputationService(
        jurisdictions,
        YamlParameterSource(roots, parameter_parsers(), registered_units),
        capabilities(),
    )
    return jurisdictions, computation
