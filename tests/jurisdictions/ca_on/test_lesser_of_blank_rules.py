"""The `blank:` lines of the `core/lesser_of` steps in the CA-ON manifest (T657).

At each T657 chart line "Enter whichever is less: ..." a blank operand blanks the result: the
other operands (the Step 1 and Step 2 limits, the chart's own amounts) are not part of a chart
that was skipped, and the least of the rest would invent a figure. The form prints no sentence for
a blank there. Every other `core/lesser_of` step names no blank rule, so it refuses a blank.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.trace.blank import BlankPassedOnLine
from tax_engine.jurisdictions.core.capabilities.lesser_of import LesserOf
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
        if step.name == "core/lesser_of"
    ]


def output_of(step: CapabilitySelection) -> str:
    output = step.produces["output"]
    assert isinstance(output, str)
    return output


def chart_steps() -> list[CapabilitySelection]:
    return [step for step in steps() if output_of(step).startswith("ca/chart_20")]


def wired(step: CapabilitySelection) -> tuple[LesserOf, tuple[ArtifactKind[Decimal], ...]]:
    amounts = step.consumes["amounts"]
    assert isinstance(amounts, tuple)
    kinds = tuple(AmountKind(f"ex/amount_{index}") for index, _ in enumerate(amounts))
    output = AmountKind("ex/least")
    rules = {slot: PASS_ON for slot in step.blank}
    return LesserOf(kinds, output).with_blank_rules(rules), kinds


def test_the_chart_steps_are_all_found() -> None:
    assert len(chart_steps()) == 48


def test_every_chart_step_passes_a_blank_on_for_all_its_amounts() -> None:
    for step in chart_steps():
        assert dict(step.blank) == {"amounts": PASS_ON}


@pytest.mark.parametrize("step", chart_steps(), ids=output_of)
def test_a_blank_operand_of_a_chart_line_blanks_the_result(step: CapabilitySelection) -> None:
    lesser, kinds = wired(step)

    for blank_at in range(len(kinds)):
        inputs = tuple(
            Artifact(kind, BLANK if index == blank_at else D(100 + index))
            for index, kind in enumerate(kinds)
        )
        result = lesser.run(inputs)
        assert result.outputs[0].is_blank
        assert isinstance(result.trace[0], BlankPassedOnLine)


def test_every_other_step_refuses_a_blank() -> None:
    others = [step for step in steps() if not output_of(step).startswith("ca/chart_20")]

    assert others
    for step in others:
        assert not step.blank
        lesser, kinds = wired(step)
        inputs = (Artifact(kinds[0], BLANK), *(Artifact(kind, D(1)) for kind in kinds[1:]))
        with pytest.raises(BlankNotAllowedError):
            lesser.run(inputs)
