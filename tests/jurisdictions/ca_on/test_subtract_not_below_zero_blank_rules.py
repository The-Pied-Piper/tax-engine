"""The `blank:` lines of the `core/subtract_not_below_zero` steps in the CA-ON manifest (T657).

At each T657 chart line "amount C minus amount D (if negative, enter "0")" (and the matching 2016
lines) a blank on either side blanks the result: the form prints no sentence for a blank there, so
the 0 floor is never applied to one. Every other `core/subtract_not_below_zero` step names no
blank rule, so it refuses a blank.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.trace.blank import BlankPassedOnLine
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
        if step.name == "core/subtract_not_below_zero"
    ]


def amount_of(step: CapabilitySelection) -> str:
    amount = step.consumes["amount"]
    assert isinstance(amount, str)
    return amount


def chart_steps() -> list[CapabilitySelection]:
    return [step for step in steps() if amount_of(step).startswith("ca/chart_20")]


def wired(
    step: CapabilitySelection,
) -> tuple[SubtractNotBelowZero, ArtifactKind[Decimal], ArtifactKind[Decimal]]:
    gross = AmountKind("ex/gross")
    reduction = AmountKind("ex/reduction")
    net = AmountKind("ex/net")
    rules = {slot: PASS_ON for slot in step.blank}
    return SubtractNotBelowZero(gross, reduction, net).with_blank_rules(rules), gross, reduction


def test_the_chart_steps_are_all_found() -> None:
    assert len(chart_steps()) == 20


def test_every_chart_step_passes_a_blank_on_in_both_slots() -> None:
    for step in chart_steps():
        assert dict(step.blank) == {"amount": PASS_ON, "less": PASS_ON}


@pytest.mark.parametrize("step", chart_steps(), ids=amount_of)
def test_a_blank_on_either_side_of_a_chart_line_blanks_the_result(
    step: CapabilitySelection,
) -> None:
    subtract, gross, reduction = wired(step)

    left = subtract.run((Artifact(gross, BLANK), Artifact(reduction, D(100))))
    right = subtract.run((Artifact(gross, D(100)), Artifact(reduction, BLANK)))

    assert left.outputs[0].is_blank
    assert right.outputs[0].is_blank
    assert isinstance(right.trace[0], BlankPassedOnLine)


def test_every_other_step_refuses_a_blank() -> None:
    others = [step for step in steps() if not amount_of(step).startswith("ca/chart_20")]

    assert others
    for step in others:
        assert not step.blank
        subtract, gross, reduction = wired(step)
        with pytest.raises(BlankNotAllowedError):
            subtract.run((Artifact(gross, D(1)), Artifact(reduction, BLANK)))
