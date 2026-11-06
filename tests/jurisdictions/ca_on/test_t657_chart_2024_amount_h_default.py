"""Amount H of Form T657 Chart 2024 Period 1 and Period 2, a T3 box 30 reserve amount, may be left
out of a request: the chart is for a filer with a T2017 reserve or a T3 amount, so she often has no
H, and the form's "Add amounts F to H" then adds the lines she has. An H left out, or given blank,
is read as 0, so the total keeps F and G.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import InputDeclaration, Manifest
from tests.kinds import bundled_kinds

D = Decimal
CA_ON = JurisdictionCode("CA-ON")
AMOUNT_H = (
    "ca/t657_chart_2024_period_1_amount_h",
    "ca/t657_chart_2024_period_2_amount_h",
)


def manifest() -> Manifest:
    (loaded,) = (
        YamlJurisdictionSource(tax_engine.registrations.JURISDICTIONS.roots(), bundled_kinds())
        .get_jurisdiction(CA_ON)
        .manifests
    )
    return loaded


def declared() -> dict[str, InputDeclaration]:
    return dict(manifest().inputs)


@pytest.mark.parametrize("name", AMOUNT_H)
def test_amount_h_is_optional_and_read_as_zero_when_left_out(name: str) -> None:
    declaration = declared()[name]

    assert not declaration.required
    assert declaration.default is not None
    assert declaration.default.value == D(0)
    assert declaration.basis


def test_a_total_of_f_and_g_is_kept_when_h_is_left_out() -> None:
    f, g, h, total = (AmountKind(f"ex/{name}") for name in ("f", "g", "h", "total"))
    declaration = declared()[AMOUNT_H[0]]
    assert declaration.default is not None

    result = SumNotBelowZero((f, g, h), total).run(
        (Artifact(f, D(10000)), Artifact(g, D(0)), Artifact(h, declaration.default.value))
    )

    assert result.outputs == (Artifact(total, D(10000)),)


@pytest.mark.parametrize("name", AMOUNT_H)
def test_the_manifest_reads_a_left_out_amount_h_as_a_zero_artifact(name: str) -> None:
    defaults = {artifact.kind.identifier: artifact for artifact in manifest().defaults}

    assert defaults[name].value == D(0)
