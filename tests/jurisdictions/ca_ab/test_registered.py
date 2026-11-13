"""Alberta is listed in `tax_engine.registrations.JURISDICTIONS`, and the engine starts over it.

The startup check (`TaxComputationService.check`, called by `factory.build_tax_computation` for
every listed code) builds the real Alberta 2025 manifest, over the registries that
`tax_engine.registrations` builds and not the Alberta package list of `support.py`. The
sanity figures are the ones the Alberta AB428 line 75 tests pin; the full Alberta end-to-end
return is not this module's.
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
ALBERTA = JurisdictionCode("CA-AB")
LINE_75 = "ca-ab/ab428_alberta_tax_line_75"


def test_alberta_is_listed() -> None:
    assert ALBERTA in JURISDICTIONS.jurisdiction_codes()


def test_the_startup_check_builds_the_alberta_manifest_over_the_registered_registries() -> None:
    kinds = artifact_kinds()
    registered_units = units()
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), kinds, registered_units),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), registered_units),
        capabilities(),
    )

    service.check([ALBERTA])

    assert service.compose(ALBERTA, 2025) is not None


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "3598.12"), ("200000", "17680.36")],
)
def test_the_started_engine_computes_ab428_line_75(salary: str, expected: str) -> None:
    kinds = artifact_kinds()
    worksheets = build_tax_computation().compute(
        ALBERTA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )

    (sheet,) = worksheets["ca-ab/ab428"]
    line_75 = kinds.kind(LINE_75)
    assert isinstance(line_75, AmountKind)
    assert sheet.get(line_75).value == D(expected)
