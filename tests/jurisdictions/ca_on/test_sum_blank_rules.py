"""The `blank:` lines of the `core/sum` steps in the CA-ON manifest (T657 charts, Schedule 8).

A T657 chart that is not completed is left blank ("If you tick Yes, complete the corresponding
chart"), so its amount blanks the total it is added into. Schedule 8 Part 4 and Part 5 are left
blank unless they apply ("If not, leave this part blank."), and a T1 total adds the lines that apply
("Complete only the lines that apply to you"), so a part left blank adds 0 to line 22200 and the
CPP totals. Each rule names the parts that can be blank; every other part, and every other
`core/sum` step, refuses a blank. A chart total adds the chart before as line B too ("If you did
not complete charts ..., enter "0""), so that part counts as 0.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON, BlankRule
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine
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
        step for form in manifest.forms for step in form.capabilities if step.name == "core/sum"
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


def is_cpp_total(step: CapabilitySelection) -> bool:
    return output_of(step).startswith("ca/cpp_")


def wired(step: CapabilitySelection) -> tuple[Sum, dict[str, AmountKind]]:
    """The step's `Sum` over made-up kinds, one per part, with the step's rules given by part."""
    kinds = {
        identifier: AmountKind(f"ex/part_{position}")
        for position, identifier in enumerate(parts_of(step))
    }
    rules: dict[ArtifactKind[Any], BlankRule] = {
        kinds[identifier]: PASS_ON if text == "pass_on" else D(text)
        for identifier, text in step.blank.items()
    }
    total = Sum(tuple(kinds.values()), AmountKind("ex/total"))
    return total.with_blank_rules({}, rules), kinds


def given(kinds: dict[str, AmountKind], blanked: str | None) -> tuple[Artifact[Decimal], ...]:
    """Each part 10, except the one in `blanked`, which is left blank."""
    return tuple(
        Artifact(kind, BLANK if identifier == blanked else D(10))
        for identifier, kind in kinds.items()
    )


def step_id(step: CapabilitySelection) -> str:
    return output_of(step)


def test_the_sum_steps_with_a_blank_rule_are_all_found() -> None:
    # 25 T657 chart totals (Charts 2016 to 2025), and line 22200 (twice, the return and its Form
    # T929 copy), 31000 and 42100.
    assert len(with_rules()) == 29


def test_every_rule_names_a_part_of_its_own_step() -> None:
    for step in with_rules():
        assert set(step.blank) <= set(parts_of(step))
        assert "parts" not in step.blank


# The three chart totals that add the chart before as line B ("If you did not complete charts for
# 2016 to 2024, enter "0".").
CARRY_PARTS = {
    "ca/chart_2024_period_2_amount_n": "ca/chart_2024_period_1_amount_n",
    "ca/chart_2025_part_1_amount_p": "ca/chart_2024_period_2_amount_n",
    "ca/chart_2025_part_2_amount_p": "ca/chart_2025_part_1_amount_p",
}


def charts() -> list[CapabilitySelection]:
    return [step for step in with_rules() if not is_cpp_total(step)]


@pytest.mark.parametrize("step", charts(), ids=step_id)
def test_a_chart_total_passes_a_blank_chart_amount_on(step: CapabilitySelection) -> None:
    total, kinds = wired(step)
    passing = [identifier for identifier, text in step.blank.items() if text == "pass_on"]

    assert passing
    for identifier in passing:
        result = total.run(given(kinds, identifier))
        assert result.outputs[0].is_blank
        assert isinstance(result.trace[0], BlankPassedOnLine)


def test_only_the_line_b_carry_of_a_chart_total_adds_a_blank_as_zero() -> None:
    zeroed = {output_of(step): step for step in charts() if "0" in step.blank.values()}

    assert set(zeroed) == set(CARRY_PARTS)
    for output, step in zeroed.items():
        assert [i for i, text in step.blank.items() if text == "0"] == [CARRY_PARTS[output]]
        total, kinds = wired(step)
        result = total.run(given(kinds, CARRY_PARTS[output]))
        assert result.outputs[0].value == D(10)
        assert isinstance(result.trace[0], BlankFallbackLine)


@pytest.mark.parametrize("step", [s for s in with_rules() if is_cpp_total(s)], ids=step_id)
def test_a_cpp_total_adds_a_blank_part_as_zero(step: CapabilitySelection) -> None:
    # Schedule 8 Part 4 and Part 5, each for its own part; the RC381 part refuses a blank.
    assert set(step.blank.values()) == {"0"}
    assert len(step.blank) == 2
    total, kinds = wired(step)
    for identifier in step.blank:
        result = total.run(given(kinds, identifier))
        assert result.outputs[0].value == D(10) * (len(kinds) - 1)
        assert isinstance(result.trace[0], BlankFallbackLine)


def test_the_cpp_totals_are_the_four_t1_totals() -> None:
    assert len([s for s in with_rules() if is_cpp_total(s)]) == 4


def test_a_part_without_a_rule_refuses_a_blank() -> None:
    for step in with_rules():
        total, kinds = wired(step)
        for identifier in kinds:
            if identifier in step.blank:
                continue
            with pytest.raises(BlankNotAllowedError):
                total.run(given(kinds, identifier))


def test_every_other_sum_step_refuses_a_blank() -> None:
    others = [step for step in steps() if not step.blank]

    assert others
    for step in others:
        kinds = {
            identifier: AmountKind(f"ex/part_{position}")
            for position, identifier in enumerate(parts_of(step))
        }
        total = Sum(tuple(kinds.values()), AmountKind("ex/total"))
        for identifier in kinds:
            with pytest.raises(BlankNotAllowedError):
                total.run(given(kinds, identifier))
