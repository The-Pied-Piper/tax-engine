"""Newfoundland and Labrador is listed in `tax_engine.registrations.JURISDICTIONS`; the engine
starts on it.

The real Newfoundland and Labrador 2025 manifest composes over the registries that
`tax_engine.registrations` builds, not the package list of `support.py`; every resolvable year of
every listed jurisdiction is composed by
`tests/application/services/test_every_resolvable_year.py`. The sanity figures are the ones the
Form NL428 line 105 tests pin; the full Newfoundland and Labrador return is tested in
`end_to_end/`, as Saskatchewan's, Manitoba's, Alberta's and British Columbia's are.
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
NEWFOUNDLAND = JurisdictionCode("CA-NL")
LINE_105 = "ca-nl/nl428_newfoundland_and_labrador_tax_line_105"


def test_newfoundland_and_labrador_is_listed() -> None:
    assert NEWFOUNDLAND in JURISDICTIONS.jurisdiction_codes()


def test_the_newfoundland_and_labrador_manifest_composes_over_the_registered_registries() -> None:
    registered_units = units()
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), registered_units),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), registered_units),
        capabilities(),
    )

    assert service.compose(NEWFOUNDLAND, 2025) is not None


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "6147.49"), ("200000", "27192.33")],
)
def test_the_started_engine_computes_nl428_line_105(salary: str, expected: str) -> None:
    kinds = artifact_kinds()
    worksheets = build_tax_computation().compute(
        NEWFOUNDLAND, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )

    (sheet,) = worksheets["ca-nl/nl428"]
    line_105 = kinds.kind(LINE_105)
    assert isinstance(line_105, AmountKind)
    assert sheet.get(line_105).value == D(expected)
