"""The `blank:` lines of the `core/subtract` steps in the CA-ON manifest (T657, #98).

Form T657 line B of Charts 2017 to 2025 prints "If you did not complete charts for ..., enter
"0"", so at each of those steps a blank B reads 0. The seven T657 inputs the form lets the filer
leave out (amounts J, L and the Part 2 excluded amounts) blank the line they are taken off from.
Every other `core/subtract` step names no blank rule, so it refuses a blank.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON, BlankRule
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine

D = Decimal
CA_ON = JurisdictionCode("CA-ON")

CARRY_LESS = {
    *(f"ca/chart_{year}_total_carried" for year in range(2016, 2024)),
    "ca/chart_2024_period_1_amount_n",
    "ca/chart_2024_period_2_amount_n",
    "ca/chart_2025_part_1_amount_p",
}
INPUT_LESS = {
    "ca/t657_chart_2024_period_1_amount_j",
    "ca/t657_chart_2024_period_2_amount_j",
    "ca/t657_part_1_amount_l",
    "ca/t657_part_2_amount_l",
    "ca/t657_part_2_excluded_f",
    "ca/t657_part_2_excluded_g",
    "ca/t657_part_2_excluded_h",
}


def subtract_steps() -> list[CapabilitySelection]:
    (manifest,) = (
        YamlJurisdictionSource(tax_engine.registrations.JURISDICTIONS.roots())
        .get_jurisdiction(CA_ON)
        .manifests
    )
    return [
        step
        for form in manifest.forms
        for step in form.capabilities
        if step.name == "core/subtract"
    ]


def less_of(step: CapabilitySelection) -> str:
    less = step.consumes["less"]
    assert isinstance(less, str)
    return less


def rules(step: CapabilitySelection) -> dict[str, BlankRule]:
    return {slot: PASS_ON if text == "pass_on" else D(text) for slot, text in step.blank.items()}


def wired(
    step: CapabilitySelection,
) -> tuple[Subtract, ArtifactKind[Decimal], ArtifactKind[Decimal]]:
    gross = ArtifactKind("ex/gross", Decimal)
    reduction = ArtifactKind("ex/reduction", Decimal)
    net = ArtifactKind("ex/net", Decimal)
    return Subtract(gross, reduction, net).with_blank_rules(rules(step)), gross, reduction


def test_the_steps_of_the_carry_lines_and_the_inputs_are_all_found() -> None:
    lessers = {less_of(step) for step in subtract_steps()}

    assert CARRY_LESS <= lessers
    assert INPUT_LESS <= lessers


@pytest.mark.parametrize("less", sorted(CARRY_LESS))
def test_a_carry_line_reads_a_blank_b_as_zero(less: str) -> None:
    (step,) = (each for each in subtract_steps() if less_of(each) == less)
    assert dict(step.blank) == {"less": "0"}

    subtract, gross, reduction = wired(step)
    result = subtract.run((Artifact(gross, D(100)), Artifact(reduction, BLANK)))

    assert result.outputs[0].value == D(100)
    assert result.trace[0] == BlankFallbackLine(reduction, D(0))


@pytest.mark.parametrize("less", sorted(INPUT_LESS))
def test_a_blank_t657_input_blanks_the_line(less: str) -> None:
    (step,) = (each for each in subtract_steps() if less_of(each) == less)
    assert dict(step.blank) == {"amount": "pass_on", "less": "pass_on"}

    subtract, gross, reduction = wired(step)
    result = subtract.run((Artifact(gross, D(100)), Artifact(reduction, BLANK)))

    assert result.outputs[0].is_blank
    assert result.trace == (BlankPassedOnLine(result.outputs[0].kind, (reduction,)),)


def test_every_other_subtract_step_refuses_a_blank() -> None:
    others = [step for step in subtract_steps() if less_of(step) not in CARRY_LESS | INPUT_LESS]

    assert others
    for step in others:
        assert not step.blank
        subtract, gross, reduction = wired(step)
        with pytest.raises(BlankNotAllowedError):
            subtract.run((Artifact(gross, D(1)), Artifact(reduction, BLANK)))
