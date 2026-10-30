"""Form T2091(IND) Part 4, for a property for which the filer or their spouse or common-law partner
filed Form T664 or T664(Seniors): line 56 "Reduction as a result of the capital gains election (line
66 of Form T2091(IND)-WS)" and line 57 "Line 55 minus line 56 (if negative, enter "0")", the total
capital gain that goes to Schedule 3 line 15800. Line 55 is line 54 of Part 3, the gain of the
`principal_residence_gain` capability, which is not changed here.

Each is one capability over the consumed `ca/principal_residence_properties`, subclassing the
worksheet base, so it is wired like the worksheet lines: the `rounding` and `chart_1_factor`
datasets and the record list. Line 56 is 0 for a property whose election was not filed (and then
line 57 is line 54); line 57 is floored at 0 and is not completed by a flag, as the form does not
say "if not completed".
"""

from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType
from typing import Any, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.factor import FACTOR
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.domain.trace.base import TraceLine
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_56 import (
    PrincipalResidencePart4Line56,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_line_57 import (
    PrincipalResidencePart4Line57,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_rows import (
    PrincipalResidenceWorksheetRows,
)
from tax_engine.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    PRINCIPAL_RESIDENCE_LINE_56,
    PRINCIPAL_RESIDENCE_LINE_57,
    PRINCIPAL_RESIDENCE_PROPERTIES,
)
from tax_engine.jurisdictions.ca.trace import PrincipalResidenceLine56, PrincipalResidenceLine57
from tests.jurisdictions.ca.capabilities.principal_residence_figures import (
    WORKSHEET_CHART_1,
    WORKSHEET_FILED_WITH_PART_2,
    WORKSHEET_HALF_CENT_LINE_63,
    WORKSHEET_NOT_FILED,
    WORKSHEET_NOT_FILED_WITH_PART_2,
    WORKSHEET_REDUCTION_EXCEEDS_GAIN,
    WORKSHEET_SMALL_ELECTION,
    WORKSHEET_WORKED,
    chart_1_factor,
    properties,
    rounding,
)

D = Decimal

PART_4_LINES: dict[int, Any] = {
    56: PrincipalResidencePart4Line56,
    57: PrincipalResidencePart4Line57,
}

KINDS: dict[int, ArtifactKind[Decimal]] = {
    56: PRINCIPAL_RESIDENCE_LINE_56,
    57: PRINCIPAL_RESIDENCE_LINE_57,
}

TRACE_LINES: dict[int, type[TraceLine]] = {
    56: PrincipalResidenceLine56,
    57: PrincipalResidenceLine57,
}

LINE_NUMBERS = list(PART_4_LINES)

# Line 54 of each property (Part 3 of Form T2091(IND)) is 150,000.00 for the worked example and its
# variants, and 20,000.00 for WORKSHEET_REDUCTION_EXCEEDS_GAIN, as worked in the fixtures.
EXPECTED: dict[str, dict[int, str]] = {
    "worked": {56: "33783.78", 57: "116216.22"},
    "not_filed": {56: "0", 57: "150000"},
    "chart_1": {56: "30405.41", 57: "119594.59"},
    "small_election": {56: "20000.00", 57: "130000.00"},
    "reduction_exceeds_gain": {56: "33783.78", 57: "0"},
    "half_cent": {56: "0.87", 57: "0.13"},
}

FIGURES: dict[str, Any] = {
    "worked": WORKSHEET_WORKED,
    "not_filed": WORKSHEET_NOT_FILED,
    "chart_1": WORKSHEET_CHART_1,
    "small_election": WORKSHEET_SMALL_ELECTION,
    "reduction_exceeds_gain": WORKSHEET_REDUCTION_EXCEEDS_GAIN,
    "half_cent": WORKSHEET_HALF_CENT_LINE_63,
}

PARTS = list(FIGURES)


def capability(line: int) -> Any:
    """The capability of `line`, wired to the `ca/principal_residence_properties` record list and
    its kind, with the rounding dataset and the Chart 1 factor."""
    return PART_4_LINES[line](
        rounding=rounding(),
        chart_1_factor=chart_1_factor(),
        properties=PRINCIPAL_RESIDENCE_PROPERTIES,
        output=KINDS[line],
    )


def value_of(line: int, *given: Any) -> Decimal:
    (output,) = capability(line).compute((properties(*given),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- contract and wiring ------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_registered_under_its_line(line: int) -> None:
    registered = CapabilityRegistry.shared().get(f"ca/principal_residence_line_{line}")

    assert registered is PART_4_LINES[line]
    assert (
        registered.__module__
        == f"tax_engine.jurisdictions.ca.capabilities.principal_residence_line_{line}"
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_exported_from_the_ca_capabilities_package(line: int) -> None:
    assert f"principal_residence_line_{line}" in ca_capabilities.__all__
    module = getattr(ca_capabilities, f"principal_residence_line_{line}")
    assert getattr(module, PART_4_LINES[line].__name__) is PART_4_LINES[line]


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_a_subclass_of_the_worksheet_rows_base(line: int) -> None:
    assert issubclass(PART_4_LINES[line], PrincipalResidenceWorksheetRows)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_declares_its_contract_and_its_slots(line: int) -> None:
    cls = PART_4_LINES[line]
    assert capability(line).consumes == frozenset({PRINCIPAL_RESIDENCE_PROPERTIES})
    assert capability(line).produces == frozenset({KINDS[line]})
    assert "consumes" not in vars(cls)
    assert "produces" not in vars(cls)
    assert cls.PARAMETERS == {"rounding": ROUNDING_ONLY, "chart_1_factor": FACTOR}
    assert cls.CONSUMES == {"properties": RecordList}
    assert cls.PRODUCES == {"output": Decimal}


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_its_slots_are_read_only(line: int) -> None:
    cls = PART_4_LINES[line]
    for slots in (cls.PARAMETERS, cls.CONSUMES, cls.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_built_from_its_slot_names_as_keywords(line: int) -> None:
    wired = PART_4_LINES[line](
        rounding=rounding(),
        chart_1_factor=chart_1_factor(),
        properties=PRINCIPAL_RESIDENCE_PROPERTIES,
        output=KINDS[line],
    )

    assert wired.compute((properties(WORKSHEET_WORKED),)).outputs == (
        Artifact(KINDS[line], D(EXPECTED["worked"][line])),
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_rejects_a_money_kind_for_its_properties(line: int) -> None:
    name = PART_4_LINES[line].__name__
    with pytest.raises(InvalidCapabilityError, match=f"{name}.*'properties'"):
        PART_4_LINES[line](
            rounding=rounding(),
            chart_1_factor=chart_1_factor(),
            properties=CAREGIVER_AMOUNT,
            output=KINDS[line],
        )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_has_one_output_of_its_kind(line: int) -> None:
    outputs = capability(line).compute((properties(WORKSHEET_WORKED),)).outputs

    assert len(outputs) == 1
    assert outputs[0].kind is KINDS[line]
    assert type(outputs[0].value) is Decimal


def test_line_56_may_be_negative_and_line_57_is_not() -> None:
    # Line 56 "Reduction ... (line 66 of Form T2091(IND)-WS)" prints no floor; line 57 does.
    assert KINDS[56].non_negative is False
    assert KINDS[57].non_negative is True


def test_the_kinds_are_named_after_their_lines() -> None:
    assert KINDS[56].identifier == "ca/principal_residence_line_56"
    assert KINDS[57].identifier == "ca/principal_residence_line_57"


# --- computing ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("line", "part"), [(line, part) for line in LINE_NUMBERS for part in PARTS]
)
def test_each_line_of_each_property(line: int, part: str) -> None:
    assert value_of(line, FIGURES[part]) == D(EXPECTED[part][line])


def test_line_56_is_line_66_of_the_worksheet_when_filed() -> None:
    # Line 66 of the worked example is 33,783.78, the reduction the election gives.
    assert value_of(56, WORKSHEET_WORKED) == D("33783.78")


def test_line_56_is_0_when_the_election_was_not_filed() -> None:
    assert value_of(56, WORKSHEET_NOT_FILED) == D("0")


def test_line_57_is_line_55_less_line_56_for_the_worked_example() -> None:
    # Line 55 is line 54 of Part 3: 150,000.00. Line 57 = 150,000.00 - 33,783.78 = 116,216.22.
    assert value_of(57, WORKSHEET_WORKED) == D("116216.22")


def test_line_57_is_not_below_0() -> None:
    # The election's reduction (33,783.78) is more than the property's line 54 (20,000.00).
    assert value_of(57, WORKSHEET_REDUCTION_EXCEEDS_GAIN) == D("0")


def test_line_57_is_line_54_when_the_election_was_not_filed() -> None:
    assert value_of(57, WORKSHEET_NOT_FILED) == D("150000")


def test_line_57_is_the_sum_of_the_properties_it_reads() -> None:
    assert value_of(57, WORKSHEET_WORKED, WORKSHEET_NOT_FILED) == D("266216.22")
    assert value_of(56, WORKSHEET_WORKED, WORKSHEET_NOT_FILED) == D("33783.78")


def test_no_properties_give_zero() -> None:
    assert capability(57).compute((properties(),)).outputs == (Artifact(KINDS[57], D("0")),)
    assert capability(56).compute((properties(),)).outputs == (Artifact(KINDS[56], D("0")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    result = capability(57).compute((other, properties(WORKSHEET_WORKED)))

    assert result.outputs == (Artifact(KINDS[57], D("116216.22")),)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_missing_properties_is_a_missing_artifact(line: int) -> None:
    with pytest.raises(MissingArtifactError, match="principal_residence_properties"):
        capability(line).compute(())


def test_line_57_reads_the_total_capital_gain_of_part_3() -> None:
    # Line 55 is the gain of Part 3 (line 54), 150,000.00 for the worked example.
    (item, _total) = capability(57).compute((properties(WORKSHEET_WORKED),)).trace

    assert cast(Any, item).line_55 == D("150000.00")


def test_a_chart_1_property_takes_its_line_66_into_line_57() -> None:
    assert value_of(57, WORKSHEET_CHART_1) == D("119594.59")


def test_a_half_cent_on_line_63_reaches_line_56_rounded() -> None:
    assert value_of(56, WORKSHEET_HALF_CENT_LINE_63) == D("0.87")


# --- refusals -----------------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_a_filed_property_with_part_2_applying_is_worked_not_refused(line: int) -> None:
    # Worksheet Part 2 (lines 28 to 58) is worked for it; line 56 and line 57 are then worked from
    # the Part 2 gain of Form T2091(IND) and the worksheet's line 66, not refused.
    assert isinstance(value_of(line, WORKSHEET_FILED_WITH_PART_2), Decimal)


def test_a_property_not_filed_with_part_2_is_not_refused() -> None:
    # Part 2 of the worksheet is needed only when the election was filed. Line 54 is the Part 2 gain
    # 83,571.43 (the lesser of line 53 and line 24), so line 57 is that, and line 56 is 0.
    assert value_of(56, WORKSHEET_NOT_FILED_WITH_PART_2) == D("0")
    assert value_of(57, WORKSHEET_NOT_FILED_WITH_PART_2) == D("83571.43")


# --- trace --------------------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_one_line_per_property_then_the_total(line: int) -> None:
    trace = capability(line).compute((properties(WORKSHEET_WORKED, WORKSHEET_NOT_FILED),)).trace

    assert [type(item) for item in trace] == [
        TRACE_LINES[line],
        TRACE_LINES[line],
        ItemsTotalLine,
    ]
    assert trace[-1] == ItemsTotalLine(
        KINDS[line],
        ((1, D(EXPECTED["worked"][line])), (2, D(EXPECTED["not_filed"][line]))),
        D(EXPECTED["worked"][line]) + D(EXPECTED["not_filed"][line]),
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_no_properties_as_only_an_empty_total(line: int) -> None:
    trace = capability(line).compute((properties(),)).trace

    assert trace == (ItemsTotalLine(KINDS[line], (), D("0")),)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_the_last_trace_line_amount_is_the_output(line: int) -> None:
    result = capability(line).compute((properties(WORKSHEET_WORKED, WORKSHEET_CHART_1),))

    total: Any = result.trace[-1]
    assert total.amount == result.outputs[0].value


def test_line_56_is_completed_only_when_the_election_was_filed() -> None:
    (filed, _total) = capability(56).compute((properties(WORKSHEET_WORKED),)).trace
    (not_filed, _total) = capability(56).compute((properties(WORKSHEET_NOT_FILED),)).trace

    assert cast(Any, filed).completed is True
    assert cast(Any, not_filed).completed is False
    assert cast(Any, not_filed).result == D("0")


def test_line_57_has_no_completed_flag() -> None:
    (item, _total) = capability(57).compute((properties(WORKSHEET_NOT_FILED),)).trace

    assert not hasattr(item, "completed")


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_renders_each_property_in_english(line: int) -> None:
    (item, _total) = capability(line).compute((properties(WORKSHEET_WORKED),)).trace

    assert (
        EnglishTraceRenderer()
        .render(cast(TraceLine, item))
        .startswith(f"{KINDS[line].label}: property 1: ")
    )


# --- the base ----------------------------------------------------------------------------------


def test_lines_56_and_57_add_back_to_line_55() -> None:
    # Both read worksheet line 66, so lines 56 and 57 together are line 55 (150,000.00).
    assert value_of(56, WORKSHEET_WORKED) + value_of(57, WORKSHEET_WORKED) == D("150000.00")
