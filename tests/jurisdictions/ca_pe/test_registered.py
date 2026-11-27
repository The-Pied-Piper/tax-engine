"""Prince Edward Island is listed in `tax_engine.registrations.JURISDICTIONS`; the engine
starts on it.

The real Prince Edward Island 2025 manifest composes over the registries that
`tax_engine.registrations` builds, not the package list of `support.py`; every resolvable year of
every listed jurisdiction is composed by
`tests/application/services/test_every_resolvable_year.py`. The sanity figures are the ones the
Form PE428 line 97 tests pin; the full Prince Edward Island return is tested in
`end_to_end/`, as Saskatchewan's, Manitoba's, Alberta's and British Columbia's are.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import (
    JURISDICTIONS,
    artifact_kinds,
    capabilities,
    parameter_parsers,
    units,
)

D = Decimal
PRINCE_EDWARD_ISLAND = JurisdictionCode("CA-PE")
LINE_97 = "ca-pe/pe428_prince_edward_island_tax_line_97"


def test_prince_edward_island_is_listed() -> None:
    assert PRINCE_EDWARD_ISLAND in JURISDICTIONS.jurisdiction_codes()


def test_the_prince_edward_island_manifest_composes_over_the_registered_registries() -> None:
    registered_units = units()
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), registered_units),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), registered_units),
        capabilities(),
    )

    assert service.compose(PRINCE_EDWARD_ISLAND, 2025) is not None


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "33.83"), ("70000", "6355.92"), ("200000", "29633.15")],
)
def test_the_started_engine_computes_pe428_line_97(salary: str, expected: str) -> None:
    kinds = artifact_kinds()
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )

    (sheet,) = worksheets["ca-pe/pe428"]
    line_97 = kinds.kind(LINE_97)
    assert isinstance(line_97, AmountKind)
    assert sheet.get(line_97).value == D(expected)
