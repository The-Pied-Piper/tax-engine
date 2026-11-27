"""Nova Scotia is listed in `tax_engine.registrations.JURISDICTIONS`; the engine
starts on it.

The real Nova Scotia 2025 manifest composes over the registries that
`tax_engine.registrations` builds, not the package list of `support.py`; every resolvable year of
every listed jurisdiction is composed by
`tests/application/services/test_every_resolvable_year.py`. The sanity figures are the ones the
Form NS428 line 99 tests pin; the full Nova Scotia return is tested in
`end_to_end/`, as Newfoundland and Labrador's, Saskatchewan's, Manitoba's, Alberta's and British
Columbia's are.
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
NOVA_SCOTIA = JurisdictionCode("CA-NS")
LINE_99 = "ca-ns/ns428_nova_scotia_tax_line_99"


def test_nova_scotia_is_listed() -> None:
    assert NOVA_SCOTIA in JURISDICTIONS.jurisdiction_codes()


def test_the_nova_scotia_manifest_composes_over_the_registered_registries() -> None:
    registered_units = units()
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), registered_units),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), registered_units),
        capabilities(),
    )

    assert service.compose(NOVA_SCOTIA, 2025) is not None


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "552.33"), ("70000", "7213.10"), ("200000", "31215.18")],
)
def test_the_started_engine_computes_ns428_line_99(salary: str, expected: str) -> None:
    kinds = artifact_kinds()
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NOVA_SCOTIA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )

    (sheet,) = worksheets["ca-ns/ns428"]
    line_99 = kinds.kind(LINE_99)
    assert isinstance(line_99, AmountKind)
    assert sheet.get(line_99).value == D(expected)
