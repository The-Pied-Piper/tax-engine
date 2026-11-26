"""New Brunswick is not yet listed in `tax_engine.registrations.JURISDICTIONS`.

The all-years test composes every listed jurisdiction for every tax year up to the greatest year a
dataset names, 2026, and New Brunswick has no 2026 dataset yet (the New Brunswick 2026 datasets
ticket adds them), so the return summary ticket lists it after that ticket. Until then the real
2025 manifest composes over New Brunswick's own package list (`support.py`), as Nova Scotia's does.
"""

from __future__ import annotations

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.registrations import JURISDICTIONS
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
    new_brunswick_units,
)

NEW_BRUNSWICK = JurisdictionCode("CA-NB")


def test_new_brunswick_is_not_listed_yet() -> None:
    assert NEW_BRUNSWICK not in JURISDICTIONS.jurisdiction_codes()


def test_the_new_brunswick_2025_manifest_composes_over_its_own_package_list() -> None:
    service = TaxComputationService(
        YamlJurisdictionSource(
            new_brunswick_packages().roots(), new_brunswick_kinds(), new_brunswick_units()
        ),
        YamlParameterSource(
            new_brunswick_packages().roots(),
            new_brunswick_parameter_parsers(),
            new_brunswick_units(),
        ),
        new_brunswick_capabilities(),
    )

    assert service.compose(NEW_BRUNSWICK, 2025) is not None
