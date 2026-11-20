"""Quebec is listed in `tax_engine.registrations.JURISDICTIONS`; the engine starts on it.

The real Quebec 2025 manifest composes over the registries that `tax_engine.registrations`
builds, not the Quebec package list of `support.py`; every resolvable year of every listed
jurisdiction is composed by `tests/application/services/test_every_resolvable_year.py`. The sanity
figures are the refund or balance owing the return summary tests pin; the full Quebec return is
tested in `end_to_end/`, as the other provinces' are.
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
QUEBEC = JurisdictionCode("CA-QC")
REFUND_OR_BALANCE_OWING = "ca/refund_or_balance_owing"


def test_quebec_is_listed() -> None:
    assert QUEBEC in JURISDICTIONS.jurisdiction_codes()


def test_the_quebec_manifest_composes_over_the_registered_registries() -> None:
    registered_units = units()
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), registered_units),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), registered_units),
        capabilities(),
    )

    assert service.compose(QUEBEC, 2025) is not None


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "-3135.08"), ("70000", "14678.32"), ("200000", "71643.79")],
)
def test_the_started_engine_computes_the_refund_or_balance_owing(
    salary: str, expected: str
) -> None:
    kinds = artifact_kinds()
    worksheets = build_tax_computation().compute(
        QUEBEC, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )

    (sheet,) = worksheets["ca-qc/return"]
    line = kinds.kind(REFUND_OR_BALANCE_OWING)
    assert isinstance(line, AmountKind)
    assert sheet.get(line).value == D(expected)
