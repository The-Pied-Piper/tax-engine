"""Manitoba is listed in `tax_engine.registrations.JURISDICTIONS`; the engine starts on it.

The real Manitoba 2025 manifest composes over the registries that `tax_engine.registrations`
builds, not the Manitoba package list of `support.py`; every resolvable year of every listed
jurisdiction is composed by `tests/application/services/test_every_resolvable_year.py`. The sanity
figures are the ones the Form MB428 line 82 tests pin; the full Manitoba return is tested in
`end_to_end/`, as Alberta's and British Columbia's are.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
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
MANITOBA = JurisdictionCode("CA-MB")
LINE_82 = "ca-mb/mb428_manitoba_tax_line_82"


def test_manitoba_is_listed() -> None:
    assert MANITOBA in JURISDICTIONS.jurisdiction_codes()


def test_the_manitoba_manifest_composes_over_the_registered_registries() -> None:
    registered_units = units()
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), registered_units),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), registered_units),
        capabilities(),
    )

    assert service.compose(MANITOBA, 2025) is not None


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("10000", "0.00"), ("20000", "284.08"), ("70000", "5747.59"), ("200000", "26863.55")],
)
def test_the_started_engine_computes_mb428_line_82(salary: str, expected: str) -> None:
    kinds = artifact_kinds()
    worksheets = build_tax_computation().compute(
        MANITOBA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )

    (sheet,) = worksheets["ca-mb/mb428"]
    line_82 = kinds.kind(LINE_82)
    assert isinstance(line_82, AmountKind)
    assert sheet.get(line_82).value == D(expected)
