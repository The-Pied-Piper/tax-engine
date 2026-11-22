"""British Columbia is listed in `tax_engine.registrations.JURISDICTIONS`; the engine starts on it.

The real British Columbia 2025 and 2026 manifests compose over the registries that
`tax_engine.registrations` builds, not the British Columbia package list of `support.py`; every
resolvable year of every listed jurisdiction is composed by
`tests/application/services/test_every_resolvable_year.py`. The sanity figures are the ones the
Form BC428 line 91 tests pin; the full British Columbia return is tested in `end_to_end/`, as
Alberta's is.
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
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
LINE_91 = "ca-bc/bc428_british_columbia_tax_line_91"


def test_british_columbia_is_listed() -> None:
    assert BRITISH_COLUMBIA in JURISDICTIONS.jurisdiction_codes()


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_british_columbia_manifest_composes_over_the_registered_registries(year: int) -> None:
    registered_units = units()
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), registered_units),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), registered_units),
        capabilities(),
    )

    assert service.compose(BRITISH_COLUMBIA, year) is not None


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "3162.39"), ("200000", "19230.76")],
)
def test_the_started_engine_computes_bc428_line_91(salary: str, expected: str) -> None:
    kinds = artifact_kinds()
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )

    (sheet,) = worksheets["ca-bc/bc428"]
    line_91 = kinds.kind(LINE_91)
    assert isinstance(line_91, AmountKind)
    assert sheet.get(line_91).value == D(expected)
