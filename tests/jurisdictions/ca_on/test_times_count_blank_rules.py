"""The `blank:` lines of the `core/times_count` steps in the CA-ON manifest (Schedule 8).

At each line the form completes only when Part 4 (or Part 5) of Schedule 8 is completed ("If not,
leave this part blank.") a blank count or a blank amount blanks the result; a filled count of 0
still gives a plain 0. Every other `core/times_count` step names no blank rule, so it refuses a
blank.
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
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.trace.blank import BlankPassedOnLine
from tax_engine.jurisdictions.core.capabilities.times_count import TimesCount
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
        if step.name == "core/times_count"
    ]


def count_of(step: CapabilitySelection) -> str:
    count = step.consumes["count"]
    assert isinstance(count, str)
    return count


def part_steps() -> list[CapabilitySelection]:
    return [step for step in steps() if count_of(step).startswith("ca/cpp_part_")]


def step_id(step: CapabilitySelection) -> str:
    produced = step.produces["output"]
    assert isinstance(produced, str)
    return produced


def wired(
    step: CapabilitySelection,
) -> tuple[TimesCount, ArtifactKind[Decimal], ArtifactKind[int]]:
    amount = AmountKind("ex/amount")
    count = CountKind("ex/count")
    output = AmountKind("ex/output")
    rules = {slot: PASS_ON for slot in step.blank}
    return TimesCount(amount, count, output).with_blank_rules(rules), amount, count


def test_the_schedule_8_part_steps_are_all_found() -> None:
    # Part 4 and Part 5, each for the 22200 deduction, 31000 credit and 42100 payable lines, and
    # the 22200 pair again in the T929 copies.
    assert len(part_steps()) == 8


def test_every_part_step_passes_a_blank_on_in_both_slots() -> None:
    for step in part_steps():
        assert dict(step.blank) == {"amount": PASS_ON, "count": PASS_ON}


@pytest.mark.parametrize("step", part_steps(), ids=lambda s: f"{step_id(s)}-{count_of(s)}")
def test_a_blank_part_or_amount_blanks_the_result_and_zero_stays_zero(
    step: CapabilitySelection,
) -> None:
    times, amount, count = wired(step)

    blank_count = times.run((Artifact(amount, D(100)), Artifact(count, BLANK)))
    blank_amount = times.run((Artifact(amount, BLANK), Artifact(count, 1)))
    zero = times.run((Artifact(amount, D(100)), Artifact(count, 0)))

    assert blank_count.outputs[0].is_blank
    assert blank_amount.outputs[0].is_blank
    assert isinstance(blank_count.trace[0], BlankPassedOnLine)
    assert zero.outputs[0].value == D(0)


def test_every_other_step_refuses_a_blank() -> None:
    others = [step for step in steps() if not count_of(step).startswith("ca/cpp_part_")]

    assert others
    for step in others:
        assert not step.blank
        times, amount, count = wired(step)
        with pytest.raises(BlankNotAllowedError):
            times.run((Artifact(amount, D(1)), Artifact(count, BLANK)))
