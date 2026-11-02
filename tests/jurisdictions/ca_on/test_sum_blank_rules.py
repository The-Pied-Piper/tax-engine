"""The `blank:` lines of the `core/sum` steps in the CA-ON manifest (T657 charts, Schedule 8).

A T657 chart that is not completed is left blank ("If you tick Yes, complete the corresponding
chart"), so its amount blanks the total it is added into. Schedule 8 Part 4 and Part 5 are left
blank unless they apply ("If not, leave this part blank."), and a T1 total adds the lines that apply
("Complete only the lines that apply to you"), so a part left blank adds 0 to line 22200 and the
CPP totals. Each rule names the one part that can be blank; every other part, and every other
`core/sum` step, refuses a blank.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON, BlankRule
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import CapabilitySelection

D = Decimal
CA_ON = JurisdictionCode("CA-ON")


def steps() -> list[CapabilitySelection]:
    (manifest,) = (
        YamlJurisdictionSource(tax_engine.registrations.JURISDICTIONS.roots())
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


def wired(step: CapabilitySelection) -> tuple[Sum, dict[str, ArtifactKind[Decimal]]]:
    """The step's `Sum` over made-up kinds, one per part, with the step's rules given by part."""
    kinds = {
        identifier: ArtifactKind(f"ex/part_{position}", Decimal)
        for position, identifier in enumerate(parts_of(step))
    }
    rules: dict[ArtifactKind[Decimal], BlankRule] = {
        kinds[identifier]: PASS_ON if text == "pass_on" else D(text)
        for identifier, text in step.blank.items()
    }
    total = Sum(tuple(kinds.values()), ArtifactKind("ex/total", Decimal))
    return total.with_blank_rules({}, rules), kinds


def given(
    kinds: dict[str, ArtifactKind[Decimal]], blanked: str | None
) -> tuple[Artifact[Decimal], ...]:
    """Each part 10, except the one in `blanked`, which is left blank."""
    return tuple(
        Artifact(kind, BLANK if identifier == blanked else D(10))
        for identifier, kind in kinds.items()
    )


def test_the_sum_steps_with_a_blank_rule_are_all_found() -> None:
    assert len(with_rules()) == 29


def test_every_rule_names_a_part_of_its_own_step() -> None:
    for step in with_rules():
        assert set(step.blank) <= set(parts_of(step))
        assert "parts" not in step.blank


def test_a_chart_total_passes_a_blank_chart_amount_on() -> None:
    charts = [step for step in with_rules() if not is_cpp_total(step)]

    assert len(charts) == 25
    for step in charts:
        assert set(step.blank.values()) == {"pass_on"}
        total, kinds = wired(step)
        for identifier in step.blank:
            result = total.run(given(kinds, identifier))
            assert result.outputs[0].is_blank


def test_a_cpp_total_adds_a_blank_part_as_zero() -> None:
    cpp = [step for step in with_rules() if is_cpp_total(step)]

    assert len(cpp) == 4
    for step in cpp:
        assert set(step.blank.values()) == {"0"}
        assert len(step.blank) == 2
        total, kinds = wired(step)
        for identifier in step.blank:
            result = total.run(given(kinds, identifier))
            assert result.outputs[0].value == D(10) * (len(kinds) - 1)


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
            identifier: ArtifactKind(f"ex/part_{position}", Decimal)
            for position, identifier in enumerate(parts_of(step))
        }
        total = Sum(tuple(kinds.values()), ArtifactKind("ex/total", Decimal))
        for identifier in kinds:
            with pytest.raises(BlankNotAllowedError):
                total.run(given(kinds, identifier))
