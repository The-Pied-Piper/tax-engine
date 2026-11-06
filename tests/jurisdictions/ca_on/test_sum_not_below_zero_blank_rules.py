"""The `core/sum_not_below_zero` steps in the CA-ON manifest give no `blank:` rule.

Amount H of Chart 2024 Period 1 and Period 2 is an optional input read as 0 when left out
(test_t657_chart_2024_amount_h_default.py), and every other part is a computed or required line,
so each step refuses a blank part.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import CapabilitySelection
from tests.kinds import bundled_kinds

D = Decimal
CA_ON = JurisdictionCode("CA-ON")


def steps() -> list[CapabilitySelection]:
    (manifest,) = (
        YamlJurisdictionSource(tax_engine.registrations.JURISDICTIONS.roots(), bundled_kinds())
        .get_jurisdiction(CA_ON)
        .manifests
    )
    return [
        step
        for form in manifest.forms
        for step in form.capabilities
        if step.name == "core/sum_not_below_zero"
    ]


def test_no_sum_not_below_zero_step_has_a_blank_rule() -> None:
    assert steps()
    assert [step for step in steps() if step.blank] == []


def test_every_sum_not_below_zero_step_refuses_a_blank_part() -> None:
    for step in steps():
        parts = step.consumes["parts"]
        assert isinstance(parts, tuple)
        kinds = [AmountKind(f"ex/part_{position}") for position, _ in enumerate(parts)]
        total = SumNotBelowZero(tuple(kinds), AmountKind("ex/total"))
        for blanked in kinds:
            given = tuple(Artifact(kind, BLANK if kind == blanked else D(10)) for kind in kinds)
            with pytest.raises(BlankNotAllowedError):
                total.run(given)
