"""New Brunswick is listed in `tax_engine.registrations.JURISDICTIONS`; the engine starts on it.

The real New Brunswick 2025 manifest composes over the registries that `tax_engine.registrations`
builds; every resolvable year of every listed jurisdiction is composed by
`tests/application/services/test_every_resolvable_year.py`. The skeleton names no form of its own
yet: the figures are pinned by the tests of the tickets that build Form NB428.
"""

from __future__ import annotations

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.registrations import (
    JURISDICTIONS,
    artifact_kinds,
    capabilities,
    parameter_parsers,
    units,
)

NEW_BRUNSWICK = JurisdictionCode("CA-NB")


def test_new_brunswick_is_listed() -> None:
    assert NEW_BRUNSWICK in JURISDICTIONS.jurisdiction_codes()


def test_the_new_brunswick_manifest_composes_over_the_registered_registries() -> None:
    registered_units = units()
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), registered_units),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), registered_units),
        capabilities(),
    )

    assert service.compose(NEW_BRUNSWICK, 2025) is not None
