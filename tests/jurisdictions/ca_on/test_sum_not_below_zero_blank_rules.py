"""The `blank:` lines of the `core/sum_not_below_zero` steps in the CA-ON manifest (T657 charts).

A T657 chart that is not completed is left blank ("If you tick Yes, complete the corresponding
chart"), so its amount H blanks the total "Add amounts F to H (if negative, enter "0")" of Chart
2024 Period 1 and Period 2. Amounts F and G are totals of Form T2017 lines that are never blank.
Each rule names amount H; every other part, and every other `core/sum_not_below_zero` step,
refuses a blank.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON, BlankRule
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.trace.blank import BlankPassedOnLine
from tax_engine.jurisdictions.core.capabilities.sum_not_below_zero import SumNotBelowZero
from tests.kinds import bundled_kinds

D = Decimal
CA_ON = JurisdictionCode("CA-ON")

AMOUNT_H = {
    "ca/chart_2024_period_1_amounts_f_to_h": "ca/t657_chart_2024_period_1_amount_h",
    "ca/chart_2024_period_2_amounts_f_to_h": "ca/t657_chart_2024_period_2_amount_h",
}


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


def parts_of(step: CapabilitySelection) -> tuple[str, ...]:
    parts = step.consumes["parts"]
    assert isinstance(parts, tuple)
    return parts


def output_of(step: CapabilitySelection) -> str:
    output = step.produces["output"]
    assert isinstance(output, str)
    return output


def with_rules() -> list[CapabilitySelection]:
    return [step for step in steps() if step.blank]


def wired(step: CapabilitySelection) -> tuple[SumNotBelowZero, dict[str, AmountKind]]:
    """The step's total over made-up kinds, one per part, with the step's rules given by part."""
    kinds = {
        identifier: AmountKind(f"ex/part_{position}")
        for position, identifier in enumerate(parts_of(step))
    }
    rules: dict[ArtifactKind[Any], BlankRule] = {
        kinds[identifier]: PASS_ON for identifier in step.blank
    }
    total = SumNotBelowZero(tuple(kinds.values()), AmountKind("ex/total"))
    return total.with_blank_rules({}, rules), kinds


def given(kinds: dict[str, AmountKind], blanked: str) -> tuple[Artifact[Decimal], ...]:
    """Each part 10, except the one in `blanked`, which is left blank."""
    return tuple(
        Artifact(kind, BLANK if identifier == blanked else D(10))
        for identifier, kind in kinds.items()
    )


def test_the_steps_with_a_blank_rule_are_the_two_chart_2024_period_totals() -> None:
    assert {output_of(step): dict(step.blank) for step in with_rules()} == {
        output: {amount_h: PASS_ON} for output, amount_h in AMOUNT_H.items()
    }


@pytest.mark.parametrize("output", AMOUNT_H)
def test_a_blank_amount_h_blanks_the_total(output: str) -> None:
    (step,) = [each for each in with_rules() if output_of(each) == output]
    total, kinds = wired(step)

    result = total.run(given(kinds, AMOUNT_H[output]))

    assert result.outputs[0].is_blank
    assert isinstance(result.trace[0], BlankPassedOnLine)


def test_amounts_f_and_g_refuse_a_blank() -> None:
    for step in with_rules():
        total, kinds = wired(step)
        for identifier in kinds:
            if identifier in step.blank:
                continue
            with pytest.raises(BlankNotAllowedError):
                total.run(given(kinds, identifier))


def test_every_other_sum_not_below_zero_step_refuses_a_blank() -> None:
    others = [step for step in steps() if not step.blank]

    assert others
    for step in others:
        kinds = {
            identifier: AmountKind(f"ex/part_{position}")
            for position, identifier in enumerate(parts_of(step))
        }
        total = SumNotBelowZero(tuple(kinds.values()), AmountKind("ex/total"))
        for identifier in kinds:
            with pytest.raises(BlankNotAllowedError):
                total.run(given(kinds, identifier))
