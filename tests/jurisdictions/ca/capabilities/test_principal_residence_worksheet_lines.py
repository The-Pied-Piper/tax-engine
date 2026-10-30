"""The lines of Form T2091(IND)-WS, the Principal Residence Worksheet, that Form T2091(IND) Part 4
reads: Chart 1 (lines 14 to 19), Part 1 (lines 21 to 27) and Part 3 (lines 59 to 66), one
capability per computed line, each the total over the consumed `ca/principal_residence_properties`.

Each capability is registered under `ca/principal_residence_worksheet_line_N`, subclasses
`PrincipalResidenceWorksheetRows` (which is not registered itself), and takes the `rounding`
dataset (lines 26 and 63 divide) and the `chart_1_factor` dataset (line 16 multiplies by the
printed 1.1, rounded by that dataset's own rule). Each trace line is a
`PrincipalResidenceWorksheetLineN`, with its own English sentence. A property whose T664 election
was not filed is 0 on every line.
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
from tax_engine.domain.errors import (
    InvalidCapabilityError,
    MissingArtifactError,
    UnknownRegistrationError,
    ValidationError,
)
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.factor import FACTOR
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.domain.trace.base import TraceLine
from tax_engine.jurisdictions.ca.capabilities.principal_residence_rows import (
    PrincipalResidenceRows,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_3 import (
    PrincipalResidenceWorksheetLine3Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_6 import (
    PrincipalResidenceWorksheetLine6Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_16 import (
    PrincipalResidenceWorksheetLine16Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_17 import (
    PrincipalResidenceWorksheetLine17Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_18 import (
    PrincipalResidenceWorksheetLine18Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_19 import (
    PrincipalResidenceWorksheetLine19Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_21 import (
    PrincipalResidenceWorksheetLine21Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_23 import (
    PrincipalResidenceWorksheetLine23Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_24 import (
    PrincipalResidenceWorksheetLine24Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_26 import (
    PrincipalResidenceWorksheetLine26Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_27 import (
    PrincipalResidenceWorksheetLine27Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_30 import (
    PrincipalResidenceWorksheetLine30Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_32 import (
    PrincipalResidenceWorksheetLine32Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_33 import (
    PrincipalResidenceWorksheetLine33Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_35 import (
    PrincipalResidenceWorksheetLine35Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_36 import (
    PrincipalResidenceWorksheetLine36Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_40 import (
    PrincipalResidenceWorksheetLine40Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_41 import (
    PrincipalResidenceWorksheetLine41Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_44 import (
    PrincipalResidenceWorksheetLine44Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_46 import (
    PrincipalResidenceWorksheetLine46Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_47 import (
    PrincipalResidenceWorksheetLine47Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_50 import (
    PrincipalResidenceWorksheetLine50Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_53 import (
    PrincipalResidenceWorksheetLine53Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_55 import (
    PrincipalResidenceWorksheetLine55Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_58 import (
    PrincipalResidenceWorksheetLine58Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_59 import (
    PrincipalResidenceWorksheetLine59Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_61 import (
    PrincipalResidenceWorksheetLine61Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_63 import (
    PrincipalResidenceWorksheetLine63Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_64 import (
    PrincipalResidenceWorksheetLine64Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_66 import (
    PrincipalResidenceWorksheetLine66Capability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_rows import (
    PrincipalResidenceWorksheetRows,
)
from tax_engine.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    PRINCIPAL_RESIDENCE_PROPERTIES,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_30,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_32,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_33,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_35,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_36,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_40,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_41,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_44,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_46,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_53,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_55,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_58,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66,
)
from tax_engine.jurisdictions.ca.trace import (
    PrincipalResidenceWorksheetLine3,
    PrincipalResidenceWorksheetLine6,
    PrincipalResidenceWorksheetLine16,
    PrincipalResidenceWorksheetLine17,
    PrincipalResidenceWorksheetLine18,
    PrincipalResidenceWorksheetLine19,
    PrincipalResidenceWorksheetLine21,
    PrincipalResidenceWorksheetLine23,
    PrincipalResidenceWorksheetLine24,
    PrincipalResidenceWorksheetLine26,
    PrincipalResidenceWorksheetLine27,
    PrincipalResidenceWorksheetLine30,
    PrincipalResidenceWorksheetLine32,
    PrincipalResidenceWorksheetLine33,
    PrincipalResidenceWorksheetLine35,
    PrincipalResidenceWorksheetLine36,
    PrincipalResidenceWorksheetLine40,
    PrincipalResidenceWorksheetLine41,
    PrincipalResidenceWorksheetLine44,
    PrincipalResidenceWorksheetLine46,
    PrincipalResidenceWorksheetLine47,
    PrincipalResidenceWorksheetLine50,
    PrincipalResidenceWorksheetLine53,
    PrincipalResidenceWorksheetLine55,
    PrincipalResidenceWorksheetLine58,
    PrincipalResidenceWorksheetLine59,
    PrincipalResidenceWorksheetLine61,
    PrincipalResidenceWorksheetLine63,
    PrincipalResidenceWorksheetLine64,
    PrincipalResidenceWorksheetLine66,
)
from tests.jurisdictions.ca.capabilities.principal_residence_figures import (
    CENT,
    DOLLAR_FLOOR,
    PART_2_NO_YEARS_OWNED,
    WORKSHEET_CHART_1,
    WORKSHEET_CHART_1_CENTS,
    WORKSHEET_CHART_1_NEGATIVE,
    WORKSHEET_DESIGNATED_ABOVE_OWNED,
    WORKSHEET_DESIGNATED_ABOVE_PART_1,
    WORKSHEET_FILED_WITH_PART_2,
    WORKSHEET_HALF_CENT_LINE_63,
    WORKSHEET_MONTHS_ABOVE_WHOLE,
    WORKSHEET_NO_MONTHS_AFTER_1971,
    WORKSHEET_NO_YEARS_OWNED_1995,
    WORKSHEET_NOT_FILED,
    WORKSHEET_NOT_FILED_WITH_PART_2,
    WORKSHEET_ROUNDED_LINE_26,
    WORKSHEET_SMALL_ELECTION,
    WORKSHEET_T664_OF_2,
    WORKSHEET_WORKED,
    chart_1_factor,
    properties,
    rounding,
)

D = Decimal

WORKSHEET_LINES: dict[int, Any] = {
    3: PrincipalResidenceWorksheetLine3Capability,
    6: PrincipalResidenceWorksheetLine6Capability,
    16: PrincipalResidenceWorksheetLine16Capability,
    17: PrincipalResidenceWorksheetLine17Capability,
    18: PrincipalResidenceWorksheetLine18Capability,
    19: PrincipalResidenceWorksheetLine19Capability,
    21: PrincipalResidenceWorksheetLine21Capability,
    23: PrincipalResidenceWorksheetLine23Capability,
    24: PrincipalResidenceWorksheetLine24Capability,
    26: PrincipalResidenceWorksheetLine26Capability,
    27: PrincipalResidenceWorksheetLine27Capability,
    59: PrincipalResidenceWorksheetLine59Capability,
    61: PrincipalResidenceWorksheetLine61Capability,
    63: PrincipalResidenceWorksheetLine63Capability,
    64: PrincipalResidenceWorksheetLine64Capability,
    66: PrincipalResidenceWorksheetLine66Capability,
    30: PrincipalResidenceWorksheetLine30Capability,
    32: PrincipalResidenceWorksheetLine32Capability,
    33: PrincipalResidenceWorksheetLine33Capability,
    35: PrincipalResidenceWorksheetLine35Capability,
    36: PrincipalResidenceWorksheetLine36Capability,
    40: PrincipalResidenceWorksheetLine40Capability,
    41: PrincipalResidenceWorksheetLine41Capability,
    44: PrincipalResidenceWorksheetLine44Capability,
    46: PrincipalResidenceWorksheetLine46Capability,
    47: PrincipalResidenceWorksheetLine47Capability,
    50: PrincipalResidenceWorksheetLine50Capability,
    53: PrincipalResidenceWorksheetLine53Capability,
    55: PrincipalResidenceWorksheetLine55Capability,
    58: PrincipalResidenceWorksheetLine58Capability,
}

KINDS: dict[int, ArtifactKind[Decimal]] = {
    3: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3,
    6: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6,
    16: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16,
    17: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17,
    18: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18,
    19: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19,
    21: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21,
    23: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23,
    24: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24,
    26: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26,
    27: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27,
    59: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59,
    61: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61,
    63: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63,
    64: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64,
    66: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66,
    30: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_30,
    32: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_32,
    33: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_33,
    35: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_35,
    36: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_36,
    40: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_40,
    41: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_41,
    44: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_44,
    46: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_46,
    47: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47,
    50: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50,
    53: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_53,
    55: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_55,
    58: PRINCIPAL_RESIDENCE_WORKSHEET_LINE_58,
}

TRACE_LINES: dict[int, type[TraceLine]] = {
    3: PrincipalResidenceWorksheetLine3,
    6: PrincipalResidenceWorksheetLine6,
    16: PrincipalResidenceWorksheetLine16,
    17: PrincipalResidenceWorksheetLine17,
    18: PrincipalResidenceWorksheetLine18,
    19: PrincipalResidenceWorksheetLine19,
    21: PrincipalResidenceWorksheetLine21,
    23: PrincipalResidenceWorksheetLine23,
    24: PrincipalResidenceWorksheetLine24,
    26: PrincipalResidenceWorksheetLine26,
    27: PrincipalResidenceWorksheetLine27,
    59: PrincipalResidenceWorksheetLine59,
    61: PrincipalResidenceWorksheetLine61,
    63: PrincipalResidenceWorksheetLine63,
    64: PrincipalResidenceWorksheetLine64,
    66: PrincipalResidenceWorksheetLine66,
    30: PrincipalResidenceWorksheetLine30,
    32: PrincipalResidenceWorksheetLine32,
    33: PrincipalResidenceWorksheetLine33,
    35: PrincipalResidenceWorksheetLine35,
    36: PrincipalResidenceWorksheetLine36,
    40: PrincipalResidenceWorksheetLine40,
    41: PrincipalResidenceWorksheetLine41,
    44: PrincipalResidenceWorksheetLine44,
    46: PrincipalResidenceWorksheetLine46,
    47: PrincipalResidenceWorksheetLine47,
    50: PrincipalResidenceWorksheetLine50,
    53: PrincipalResidenceWorksheetLine53,
    55: PrincipalResidenceWorksheetLine55,
    58: PrincipalResidenceWorksheetLine58,
}

LINE_NUMBERS = list(WORKSHEET_LINES)

# The lines of Part 2 (lines 28 to 58): completed only when Part 2 of Form T2091(IND) applies, which
# it does not in the worked example or the Chart 1 example, so they are 0 there. Their figures are
# pinned in test_principal_residence_part_2_worksheet_lines.py.
PART_2_LINES = {30, 32, 33, 35, 36, 40, 41, 44, 46, 47, 50, 53, 55, 58}

# The lines of Chart 1: completed only when line 7 is more than line 10.
CHART_LINES = {16, 17, 18}

# Worked example (WORKSHEET_WORKED): Chart 1 does not apply, so lines 16 to 18 are 0.
VALUES_WORKED: dict[int, str] = {
    3: "5",
    6: "12",
    16: "0",
    17: "0",
    18: "0",
    19: "200000",
    21: "100000",
    23: "6",
    24: "600000",
    26: "50000",
    27: "50000",
    59: "50000",
    61: "1200000",
    63: "16216.22",
    64: "33783.78",
    66: "33783.78",
    30: "0",
    32: "0",
    33: "0",
    35: "0",
    36: "0",
    40: "0",
    41: "0",
    44: "0",
    46: "0",
    47: "0",
    50: "0",
    53: "0",
    55: "0",
    58: "0",
}

# Chart 1 (WORKSHEET_CHART_1): line 7 230,000.00 is more than line 10 200,000.00.
VALUES_CHART_1: dict[int, str] = {
    3: "5",
    6: "12",
    16: "220000.00",
    17: "10000.00",
    18: "190000.00",
    19: "190000",
    21: "90000",
    23: "6",
    24: "540000",
    26: "45000",
    27: "45000",
    59: "45000",
    61: "1080000",
    63: "14594.59",
    64: "30405.41",
    66: "30405.41",
    30: "0",
    32: "0",
    33: "0",
    35: "0",
    36: "0",
    40: "0",
    41: "0",
    44: "0",
    46: "0",
    47: "0",
    50: "0",
    53: "0",
    55: "0",
    58: "0",
}

# T664 not filed (WORKSHEET_NOT_FILED): every worksheet line is not completed, and 0.
VALUES_NOT_FILED: dict[int, str] = {line: "0" for line in LINE_NUMBERS}


def capability(
    line: int,
    rounding_data: ParameterDataset[RoundingOnly] | None = None,
    factor: ParameterDataset[Any] | None = None,
) -> Any:
    """The capability of `line`, wired to the `ca/principal_residence_properties` record list and
    its kind; by default the rounding dataset rounds half up to the cent, and the Chart 1 factor is
    the printed 1.1, rounded half up to the cent."""
    return WORKSHEET_LINES[line](
        rounding=rounding_data or rounding(),
        chart_1_factor=factor or chart_1_factor(),
        properties=PRINCIPAL_RESIDENCE_PROPERTIES,
        output=KINDS[line],
    )


def output_of(
    line: int,
    *given: Any,
    rule: Any = CENT,
    factor_rule: Any = CENT,
) -> Artifact[Any]:
    """The output of `line` over the properties `given`, in the order given."""
    outputs: tuple[Artifact[Any], ...] = (
        capability(line, rounding(rule), chart_1_factor(rule=factor_rule))
        .compute((properties(*given),))
        .outputs
    )
    (output,) = outputs
    return output


def value_of(line: int, *given: Any, rule: Any = CENT, factor_rule: Any = CENT) -> Decimal:
    value = output_of(line, *given, rule=rule, factor_rule=factor_rule).value
    assert isinstance(value, Decimal)
    return value


# --- contract and wiring ------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_registered_under_its_identifier(line: int) -> None:
    registered = CapabilityRegistry.shared().get(f"ca/principal_residence_worksheet_line_{line}")

    assert registered is WORKSHEET_LINES[line]
    assert registered.__module__ == (
        f"tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_line_{line}"
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_exported_from_the_ca_capabilities_package(line: int) -> None:
    assert f"principal_residence_worksheet_line_{line}" in ca_capabilities.__all__
    module = getattr(ca_capabilities, f"principal_residence_worksheet_line_{line}")
    assert getattr(module, WORKSHEET_LINES[line].__name__) is WORKSHEET_LINES[line]


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_a_subclass_of_the_worksheet_rows_base(line: int) -> None:
    assert issubclass(WORKSHEET_LINES[line], PrincipalResidenceWorksheetRows)
    assert issubclass(WORKSHEET_LINES[line], PrincipalResidenceRows)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_declares_its_contract(line: int) -> None:
    assert capability(line).consumes == frozenset({PRINCIPAL_RESIDENCE_PROPERTIES})
    assert capability(line).produces == frozenset({KINDS[line]})


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_leaves_its_contract_to_the_base(line: int) -> None:
    assert "consumes" not in vars(WORKSHEET_LINES[line])
    assert "produces" not in vars(WORKSHEET_LINES[line])


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_declares_its_slots(line: int) -> None:
    cls = WORKSHEET_LINES[line]
    assert cls.PARAMETERS == {"rounding": ROUNDING_ONLY, "chart_1_factor": FACTOR}
    assert list(cls.PARAMETERS) == ["rounding", "chart_1_factor"]
    assert cls.CONSUMES == {"properties": RecordList}
    assert cls.PRODUCES == {"output": Decimal}
    assert not cls.is_list_slot("properties")


def test_the_worksheet_base_declares_the_two_datasets_its_lines_read() -> None:
    assert PrincipalResidenceWorksheetRows.PARAMETERS == {
        "rounding": ROUNDING_ONLY,
        "chart_1_factor": FACTOR,
    }
    assert list(PrincipalResidenceWorksheetRows.PARAMETERS) == ["rounding", "chart_1_factor"]


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_its_slots_are_read_only(line: int) -> None:
    cls = WORKSHEET_LINES[line]
    for slots in (cls.PARAMETERS, cls.CONSUMES, cls.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_built_from_its_slot_names_as_keywords(line: int) -> None:
    wired = WORKSHEET_LINES[line](
        rounding=rounding(),
        chart_1_factor=chart_1_factor(),
        properties=PRINCIPAL_RESIDENCE_PROPERTIES,
        output=KINDS[line],
    )

    assert wired.compute((properties(WORKSHEET_WORKED),)).outputs == (
        Artifact(KINDS[line], D(VALUES_WORKED[line])),
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_takes_no_separate_rounding_argument(line: int) -> None:
    with pytest.raises(TypeError):
        WORKSHEET_LINES[line](
            rounding(),
            chart_1_factor(),
            PRINCIPAL_RESIDENCE_PROPERTIES,
            KINDS[line],
            CENT,
        )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_rejects_a_money_kind_for_its_properties(line: int) -> None:
    name = WORKSHEET_LINES[line].__name__
    with pytest.raises(InvalidCapabilityError, match=f"{name}.*'properties'"):
        WORKSHEET_LINES[line](
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


def test_the_worksheet_base_is_not_registered() -> None:
    with pytest.raises(UnknownRegistrationError):
        CapabilityRegistry.shared().get("ca/principal_residence_worksheet_rows")


# --- computing: the worked example, Chart 1 and the other lines ----------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_each_line_of_the_worked_example(line: int) -> None:
    assert value_of(line, WORKSHEET_WORKED) == D(VALUES_WORKED[line])


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_each_line_of_chart_1(line: int) -> None:
    assert value_of(line, WORKSHEET_CHART_1) == D(VALUES_CHART_1[line])


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_each_line_is_0_when_the_election_was_not_filed(line: int) -> None:
    assert value_of(line, WORKSHEET_NOT_FILED) == D(VALUES_NOT_FILED[line])


def test_the_worked_example_by_hand() -> None:
    # Line 3 = 5 + 0; line 6 = 12 + 0; line 19 = 200,000.00 (line 7 is not more than line 10, so
    # no Chart 1); line 21 = 200,000.00 - 100,000.00; line 23 = 5 + 1; line 24 = 100,000.00 x 6;
    # line 26 = 600,000.00 / 12; line 61 = 50,000.00 x 24; line 63 = 1,200,000.00 / 74, which is
    # 16,216.216..., half up to 16,216.22; line 64 = 50,000.00 - 16,216.22; line 66 = the lesser of
    # that and 100,000.00.
    assert [value_of(line, WORKSHEET_WORKED) for line in (3, 6, 19, 21, 23)] == [
        D("5"),
        D("12"),
        D("200000.00"),
        D("100000.00"),
        D("6"),
    ]
    assert value_of(24, WORKSHEET_WORKED) == D("600000.00")
    assert value_of(26, WORKSHEET_WORKED) == D("50000.00")
    assert value_of(61, WORKSHEET_WORKED) == D("1200000.00")
    assert value_of(63, WORKSHEET_WORKED) == D("16216.22")
    assert value_of(64, WORKSHEET_WORKED) == D("33783.78")
    assert value_of(66, WORKSHEET_WORKED) == D("33783.78")


def test_chart_1_lines_when_line_7_is_more_than_line_10() -> None:
    # Line 16 = 200,000.00 x 1.1 = 220,000.00; line 17 = 230,000.00 - 220,000.00 = 10,000.00;
    # line 18 = 200,000.00 - 10,000.00 = 190,000.00 = line 19.
    assert value_of(16, WORKSHEET_CHART_1) == D("220000.00")
    assert value_of(17, WORKSHEET_CHART_1) == D("10000.00")
    assert value_of(18, WORKSHEET_CHART_1) == D("190000.00")
    assert value_of(19, WORKSHEET_CHART_1) == D("190000.00")


def test_chart_1_line_18_is_not_floored_when_line_7_is_far_above_line_10() -> None:
    # Line 17 is 500,000.00 - 220,000.00 = 280,000.00, so line 18 = 200,000.00 - 280,000.00.
    assert value_of(17, WORKSHEET_CHART_1_NEGATIVE) == D("280000.00")
    assert value_of(18, WORKSHEET_CHART_1_NEGATIVE) == D("-80000.00")
    assert value_of(19, WORKSHEET_CHART_1_NEGATIVE) == D("-80000.00")
    assert value_of(21, WORKSHEET_CHART_1_NEGATIVE) == D("-180000.00")


def test_line_16_is_rounded_by_the_chart_1_factor_rule() -> None:
    # Line 14 is 100,000.05, so line 16 = 110,000.055, half up to the cent 110,000.06.
    assert value_of(16, WORKSHEET_CHART_1_CENTS, factor_rule=CENT) == D("110000.06")
    assert value_of(16, WORKSHEET_CHART_1_CENTS, factor_rule=DOLLAR_FLOOR) == D("110000")


def test_line_26_is_rounded_by_the_datasets_rule() -> None:
    # 400,000.00 / 3 = 133,333.333..., half up to the cent 133,333.33 or whole dollars 133,333.
    assert value_of(26, WORKSHEET_ROUNDED_LINE_26) == D("133333.33")
    assert value_of(26, WORKSHEET_ROUNDED_LINE_26, rule=DOLLAR_FLOOR) == D("133333")


def test_line_63_is_rounded_by_the_datasets_rule() -> None:
    assert value_of(63, WORKSHEET_WORKED) == D("16216.22")
    assert value_of(63, WORKSHEET_WORKED, rule=DOLLAR_FLOOR) == D("16216")


def test_line_63_a_half_cent_rounds_up_and_line_64_takes_the_rounded_figure() -> None:
    # Line 63 = 1.00 / 8 = 0.125, half up to 0.13; line 64 = 1.00 - 0.13 = 0.87; line 66 is the
    # lesser of 0.87 and 5.00.
    assert value_of(63, WORKSHEET_HALF_CENT_LINE_63) == D("0.13")
    assert value_of(64, WORKSHEET_HALF_CENT_LINE_63) == D("0.87")
    assert value_of(66, WORKSHEET_HALF_CENT_LINE_63) == D("0.87")


def test_line_66_is_the_lesser_of_lines_64_and_65() -> None:
    # Line 65 is the elected capital gain, 100,000.00, which is more than line 64 (33,783.78), so
    # line 66 is line 64. With the election at 20,000.00 it is the lesser, so line 66 is that.
    assert value_of(66, WORKSHEET_WORKED) == D("33783.78")
    assert value_of(66, WORKSHEET_SMALL_ELECTION) == D("20000.00")


def test_the_lines_that_may_be_negative_are_signed_kinds() -> None:
    for line in (18, 19, 21, 24, 26, 27, 59, 61, 63, 64, 66):
        assert KINDS[line].non_negative is False, line


def test_the_lines_that_are_never_negative_are_non_negative_kinds() -> None:
    for line in (3, 6, 16, 17, 23):
        assert KINDS[line].non_negative is True, line


def test_a_worksheet_line_is_a_decimal_even_for_a_count_of_years() -> None:
    assert type(value_of(3, WORKSHEET_WORKED)) is Decimal
    assert type(value_of(23, WORKSHEET_WORKED)) is Decimal


# --- computing: the properties ------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_no_properties_give_zero(line: int) -> None:
    result = capability(line).compute((properties(),))

    assert result.outputs == (Artifact(KINDS[line], D("0")),)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_two_properties_give_the_sum_of_their_own_amounts(line: int) -> None:
    total = value_of(line, WORKSHEET_WORKED, WORKSHEET_CHART_1)

    assert total == D(VALUES_WORKED[line]) + D(VALUES_CHART_1[line])


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_the_total_does_not_depend_on_the_order(line: int) -> None:
    assert value_of(line, WORKSHEET_WORKED, WORKSHEET_CHART_1) == value_of(
        line, WORKSHEET_CHART_1, WORKSHEET_WORKED
    )


def test_a_property_not_filed_adds_nothing_to_the_others() -> None:
    assert value_of(66, WORKSHEET_WORKED, WORKSHEET_NOT_FILED) == D("33783.78")
    assert value_of(27, WORKSHEET_WORKED, WORKSHEET_NOT_FILED) == D("50000.00")


def test_a_property_not_filed_with_part_2_is_not_refused_and_is_0() -> None:
    assert value_of(27, WORKSHEET_NOT_FILED_WITH_PART_2) == D("0")
    assert value_of(63, WORKSHEET_NOT_FILED_WITH_PART_2) == D("0")


def test_compute_is_repeatable() -> None:
    wired = capability(63)

    first = wired.compute((properties(WORKSHEET_WORKED, WORKSHEET_CHART_1),))
    second = wired.compute((properties(WORKSHEET_WORKED, WORKSHEET_CHART_1),))

    assert first == second


# --- computing: refusals ------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_a_filed_property_with_part_2_applying_is_worked_not_refused(line: int) -> None:
    # Part 2 of the worksheet (lines 28 to 58) is worked for it, so the line is a decimal; the
    # figures of Part 2 are pinned in test_principal_residence_part_2_worksheet_lines.py.
    assert isinstance(value_of(line, WORKSHEET_FILED_WITH_PART_2), Decimal)


def test_a_filed_property_with_part_2_is_worked_beside_the_others() -> None:
    # Line 27 of the worked example stays 50,000.00 beside a property with Part 2 applying.
    assert isinstance(value_of(27, WORKSHEET_WORKED, WORKSHEET_FILED_WITH_PART_2), Decimal)
    assert value_of(27, WORKSHEET_WORKED) == D("50000.00")


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_a_filed_property_with_no_years_owned_before_1995_is_refused(line: int) -> None:
    with pytest.raises(ValidationError, match=r"property 1.*line 4.*line 5"):
        value_of(line, WORKSHEET_NO_YEARS_OWNED_1995)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_a_filed_property_with_no_months_owned_after_1971_is_refused(line: int) -> None:
    with pytest.raises(ValidationError, match=r"property 1.*line 62"):
        value_of(line, WORKSHEET_NO_MONTHS_AFTER_1971)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_more_years_designated_than_owned_before_1995_is_refused(line: int) -> None:
    with pytest.raises(ValidationError, match=r"property 1.*line 1.*more than line 4"):
        value_of(line, WORKSHEET_DESIGNATED_ABOVE_OWNED)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_more_years_designated_before_1995_than_after_1981_is_refused(line: int) -> None:
    with pytest.raises(
        ValidationError, match=r"property 1.*line 1.*more than the years designated"
    ):
        value_of(line, WORKSHEET_DESIGNATED_ABOVE_PART_1)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_more_months_after_february_1992_than_after_1971_is_refused(line: int) -> None:
    with pytest.raises(ValidationError, match=r"property 1.*line 60.*more than line 62"):
        value_of(line, WORKSHEET_MONTHS_ABOVE_WHOLE)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_a_subset_above_its_whole_on_the_second_property_names_it_as_property_2(
    line: int,
) -> None:
    for bad in (
        WORKSHEET_DESIGNATED_ABOVE_OWNED,
        WORKSHEET_DESIGNATED_ABOVE_PART_1,
        WORKSHEET_MONTHS_ABOVE_WHOLE,
    ):
        with pytest.raises(ValidationError, match=r"property 2"):
            value_of(line, WORKSHEET_WORKED, bad)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_a_t664_flag_above_1_is_refused(line: int) -> None:
    # The flag is 1 when Form T664 was filed and 0 when not; a 2 would be read as "not filed".
    with pytest.raises(ValidationError, match=r"property 1.*T664"):
        value_of(line, WORKSHEET_T664_OF_2)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_a_t664_flag_above_1_on_the_second_property_names_it_as_property_2(line: int) -> None:
    with pytest.raises(ValidationError, match=r"property 2.*T664"):
        value_of(line, WORKSHEET_WORKED, WORKSHEET_T664_OF_2)


def test_a_property_owned_for_no_years_is_still_refused_as_part_1_is() -> None:
    with pytest.raises(ValidationError, match="property 2: the years owned"):
        value_of(27, WORKSHEET_WORKED, PART_2_NO_YEARS_OWNED)


# --- computing: inputs --------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_ignores_artifacts_it_does_not_consume(line: int) -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    result = capability(line).compute((other, properties(WORKSHEET_WORKED)))

    assert result.outputs == (Artifact(KINDS[line], D(VALUES_WORKED[line])),)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_missing_properties_is_a_missing_artifact(line: int) -> None:
    with pytest.raises(MissingArtifactError, match="principal_residence_properties"):
        capability(line).compute(())


# --- trace --------------------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_one_line_per_property_then_the_total(line: int) -> None:
    trace = capability(line).compute((properties(WORKSHEET_WORKED, WORKSHEET_CHART_1),)).trace

    assert [type(item) for item in trace] == [
        TRACE_LINES[line],
        TRACE_LINES[line],
        ItemsTotalLine,
    ]
    total = D(VALUES_WORKED[line]) + D(VALUES_CHART_1[line])
    assert trace[-1] == ItemsTotalLine(
        KINDS[line],
        ((1, D(VALUES_WORKED[line])), (2, D(VALUES_CHART_1[line]))),
        total,
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_the_callers_order_with_positions_from_one(line: int) -> None:
    trace = capability(line).compute((properties(WORKSHEET_CHART_1, WORKSHEET_WORKED),)).trace

    items: list[Any] = list(trace[:-1])
    assert [item.position for item in items] == [1, 2]
    assert [item.result for item in items] == [D(VALUES_CHART_1[line]), D(VALUES_WORKED[line])]


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_no_properties_as_only_an_empty_total(line: int) -> None:
    trace = capability(line).compute((properties(),)).trace

    assert trace == (ItemsTotalLine(KINDS[line], (), D("0")),)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_the_last_trace_line_amount_is_the_output(line: int) -> None:
    result = capability(line).compute((properties(WORKSHEET_WORKED, WORKSHEET_CHART_1),))

    total: Any = result.trace[-1]
    assert total.amount == result.outputs[0].value


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_whether_the_step_is_completed_on_a_filed_property(line: int) -> None:
    # Lines 16 to 18 are completed only when Chart 1 applies, and lines 28 to 58 only when Part 2
    # applies; every other line is completed when the election was filed.
    (item, _total) = capability(line).compute((properties(WORKSHEET_WORKED),)).trace

    assert cast(Any, item).completed is (line not in CHART_LINES | PART_2_LINES)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_a_property_not_filed_as_not_completed_and_0(line: int) -> None:
    (item, _total) = capability(line).compute((properties(WORKSHEET_NOT_FILED),)).trace

    assert cast(Any, item).completed is False
    assert cast(Any, item).result == D("0")


@pytest.mark.parametrize("line", sorted(CHART_LINES))
def test_chart_1_lines_are_completed_when_line_7_is_more_than_line_10(line: int) -> None:
    (item, _total) = capability(line).compute((properties(WORKSHEET_CHART_1),)).trace

    assert cast(Any, item).completed is True


def test_line_19_says_whether_chart_1_was_completed() -> None:
    (chart, _total) = capability(19).compute((properties(WORKSHEET_CHART_1),)).trace
    (no_chart, _total) = capability(19).compute((properties(WORKSHEET_WORKED),)).trace

    assert cast(Any, chart).chart_completed is True
    assert cast(Any, chart).result == D("190000.00")
    assert cast(Any, no_chart).chart_completed is False
    assert cast(Any, no_chart).result == D("200000.00")


@pytest.mark.parametrize("line", [26, 63])
def test_the_dividing_lines_trace_their_rounding_rule(line: int) -> None:
    (item, _total) = capability(line).compute((properties(WORKSHEET_WORKED),)).trace

    assert cast(Any, item).rounding == CENT


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_renders_each_line_of_the_worksheet_in_english(line: int) -> None:
    (item, _total) = capability(line).compute((properties(WORKSHEET_WORKED),)).trace

    assert (
        EnglishTraceRenderer()
        .render(cast(TraceLine, item))
        .startswith(f"{KINDS[line].label}: property 1: ")
    )
