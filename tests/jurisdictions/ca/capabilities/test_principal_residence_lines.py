"""Unit tests for the capabilities of lines 27 to 53 of Form T2091(IND) Part 2, and their shared
base `PrincipalResidenceRows`, which is not registered. Each capability is registered as
`ca/principal_residence_line_<n>`. Form T2091(IND), "Complete Part 2 if the property disposed of is
one of two or more properties that qualify as principal residences a family member owned on
December 31, 1981, and continuously thereafter until its disposition." Area A, "Pre-1982 gain": "If
you designated the property as a principal residence for all the years you owned it before 1982, do
not complete lines 25 to 32. Instead, enter "0" on line 33." Line 27 "Line 25 minus line 26", line
29 "Line 2 plus 1 (see note on page 4)", line 30 "Multiply line 28 by line 29.", line 32 "Divide
line 30 by line 31." (31 is "Number of years from line 6"), line 33 "Line 27 minus line 32 (if
negative, enter "0")". Area B, "Post-1981 gain": "If you designated the property as a principal
residence for all the years you owned it after 1981, do not complete lines 34 to 44. Instead, enter
"0" on line 45 and complete area D." and, for line 35, "If the fair market value of the property on
December 31, 1981, is more than the amount on line 34, do not complete lines 35 to 44. Instead,
enter "0" on line 45 and complete areas C and D." Line 38 "Add lines 35 to 37." (line 13 and line
9), line 39 "Line 34 minus line 38", line 42 "Multiply line 40 by line 41." (line 1), line 44
"Divide line 42 by line 43." (line 5), line 45 "Line 39 minus line 44 (if negative, enter "0")".
Area C, "Post-1981 loss": line 48 "Line 46 minus line 47 (if negative, enter "0")". Area D, "Net
capital gain": line 51 "Line 49 plus line 50", line 53 "Line 51 minus line 52 (if negative, enter
"0")". Each subclass of `PrincipalResidenceRows` is one capability for one line. Its slots: one
parameter `rounding` (a `rounding_only` dataset: lines 32 and 44 divide), one consumed `properties`
(the record list of `ca/principal_residence_properties`) and one produced `output`, the total over
the properties of that line, 0 for an empty list. Each property is worked on its own, never pooled.
A line whose area the form says not to complete is 0. Each records one `PrincipalResidenceLine<n>`
per property, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InvalidCapabilityError,
    MissingArtifactError,
    UnknownRegistrationError,
    ValidationError,
)
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingRule
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.domain.trace.base import TraceLine
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_27 import (
    PrincipalResidencePart2Line27,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_29 import (
    PrincipalResidencePart2Line29,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_30 import (
    PrincipalResidencePart2Line30,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_32 import (
    PrincipalResidencePart2Line32,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_33 import (
    PrincipalResidencePart2Line33,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_38 import (
    PrincipalResidencePart2Line38,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_39 import (
    PrincipalResidencePart2Line39,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_42 import (
    PrincipalResidencePart2Line42,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_44 import (
    PrincipalResidencePart2Line44,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_45 import (
    PrincipalResidencePart2Line45,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_48 import (
    PrincipalResidencePart2Line48,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_51 import (
    PrincipalResidencePart2Line51,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_53 import (
    PrincipalResidencePart2Line53,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_rows import (
    PrincipalResidenceRows,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    PRINCIPAL_RESIDENCE_LINE_27,
    PRINCIPAL_RESIDENCE_LINE_29,
    PRINCIPAL_RESIDENCE_LINE_30,
    PRINCIPAL_RESIDENCE_LINE_32,
    PRINCIPAL_RESIDENCE_LINE_33,
    PRINCIPAL_RESIDENCE_LINE_38,
    PRINCIPAL_RESIDENCE_LINE_39,
    PRINCIPAL_RESIDENCE_LINE_42,
    PRINCIPAL_RESIDENCE_LINE_44,
    PRINCIPAL_RESIDENCE_LINE_45,
    PRINCIPAL_RESIDENCE_LINE_48,
    PRINCIPAL_RESIDENCE_LINE_51,
    PRINCIPAL_RESIDENCE_LINE_53,
    PRINCIPAL_RESIDENCE_PROPERTIES,
)
from tax_calculator.jurisdictions.ca.trace import (
    PrincipalResidenceLine27,
    PrincipalResidenceLine29,
    PrincipalResidenceLine30,
    PrincipalResidenceLine32,
    PrincipalResidenceLine33,
    PrincipalResidenceLine38,
    PrincipalResidenceLine39,
    PrincipalResidenceLine42,
    PrincipalResidenceLine44,
    PrincipalResidenceLine45,
    PrincipalResidenceLine48,
    PrincipalResidenceLine51,
    PrincipalResidenceLine53,
)
from tests.jurisdictions.ca.capabilities.principal_residence_figures import (
    CENT,
    DOLLAR_FLOOR,
    PART_2_ALL_YEARS_AFTER_1981,
    PART_2_ALL_YEARS_BEFORE_1982,
    PART_2_HALF_CENT_LINE_44,
    PART_2_LESSER_IS_LINE_53,
    PART_2_LOSS,
    PART_2_NO_YEARS_OWNED,
    PART_2_NOT_APPLYING,
    PART_2_ROUNDED_LINE_32,
    PART_2_ROUNDED_LINE_44,
    PART_2_WORKED,
    Part2Figures,
    properties,
    rounding,
)

D = Decimal

# Figures of the test properties, by name, as in `principal_residence_figures`.
FIGURES: dict[str, Part2Figures] = {
    "worked": PART_2_WORKED,
    "lesser": PART_2_LESSER_IS_LINE_53,
    "loss": PART_2_LOSS,
    "all_after": PART_2_ALL_YEARS_AFTER_1981,
    "all_before": PART_2_ALL_YEARS_BEFORE_1982,
    "not_applying": PART_2_NOT_APPLYING,
}

# A property whose FMV on December 31, 1981 (30,000.00) is less than its adjusted cost base then
# (40,000.00): line 27 = -10,000.00; line 29 = 2; line 30 = -20,000.00; line 32 = -20,000.00 / 4 =
# -5,000.00; line 33 = max(0, -10,000.00 + 5,000.00) = 0. Area B: line 38 = 30,000.00 + 10,000.00 +
# 5,000.00 = 45,000.00; line 39 = 255,000.00; line 45 = 102,000.00 (line 44 = 153,000.00).
NEGATIVE_AREA_A: Part2Figures = (
    6,
    1,
    10,
    4,
    "300000.00",
    "5000.00",
    "100000.00",
    1,
    1,
    "40000.00",
    "30000.00",
    "10000.00",
)

# A property whose proceeds (100,000.00) fall short of its FMV on December 31, 1981 plus the
# later adjustments and outlays (110,000.00): line 38 = 90,000.00 + 20,000.00 + 0 = 110,000.00;
# line 39 = -10,000.00; line 42 = -10,000.00 x 2 = -20,000.00; line 44 = -20,000.00 / 10 =
# -2,000.00; line 45 = max(0, -10,000.00 + 2,000.00) = 0.
NEGATIVE_AREA_B: Part2Figures = (
    2,
    1,
    10,
    4,
    "100000.00",
    "0.00",
    "50000.00",
    0,
    1,
    "60000.00",
    "90000.00",
    "20000.00",
)

# The value of each line for each property, in dollars or as a count: the worked example, the
# example where line 53 is the lesser, the loss, the two all-years cases and a property not using
# Part 2. Each is worked in the comments of `principal_residence_figures`.
VALUES: dict[int, dict[str, str]] = {
    27: {
        "worked": "50000.00",
        "lesser": "0",
        "loss": "60000.00",
        "all_after": "60000.00",
        "all_before": "0",
        "not_applying": "0",
    },
    29: {
        "worked": "2",
        "lesser": "0",
        "loss": "1",
        "all_after": "1",
        "all_before": "0",
        "not_applying": "0",
    },
    30: {
        "worked": "100000.00",
        "lesser": "0",
        "loss": "60000.00",
        "all_after": "60000.00",
        "all_before": "0",
        "not_applying": "0",
    },
    32: {
        "worked": "25000.00",
        "lesser": "0",
        "loss": "30000.00",
        "all_after": "30000.00",
        "all_before": "0",
        "not_applying": "0",
    },
    33: {
        "worked": "25000.00",
        "lesser": "0",
        "loss": "30000.00",
        "all_after": "30000.00",
        "all_before": "0",
        "not_applying": "0",
    },
    38: {
        "worked": "105000.00",
        "lesser": "280000.00",
        "loss": "0",
        "all_after": "0",
        "all_before": "40000.00",
        "not_applying": "0",
    },
    39: {
        "worked": "195000.00",
        "lesser": "20000.00",
        "loss": "0",
        "all_after": "0",
        "all_before": "60000.00",
        "not_applying": "0",
    },
    42: {
        "worked": "1170000.00",
        "lesser": "40000.00",
        "loss": "0",
        "all_after": "0",
        "all_before": "60000.00",
        "not_applying": "0",
    },
    44: {
        "worked": "117000.00",
        "lesser": "4000.00",
        "loss": "0",
        "all_after": "0",
        "all_before": "20000.00",
        "not_applying": "0",
    },
    45: {
        "worked": "78000.00",
        "lesser": "16000.00",
        "loss": "0",
        "all_after": "0",
        "all_before": "40000.00",
        "not_applying": "0",
    },
    48: {
        "worked": "0",
        "lesser": "0",
        "loss": "20000.00",
        "all_after": "0",
        "all_before": "0",
        "not_applying": "0",
    },
    51: {
        "worked": "103000.00",
        "lesser": "16000.00",
        "loss": "30000.00",
        "all_after": "30000.00",
        "all_before": "40000.00",
        "not_applying": "0",
    },
    53: {
        "worked": "103000.00",
        "lesser": "16000.00",
        "loss": "10000.00",
        "all_after": "30000.00",
        "all_before": "40000.00",
        "not_applying": "0",
    },
}

# Whether the form's step for the line is completed for each property (not "not completed, 0"):
# area A (lines 27 to 33) is skipped when every year before 1982 is designated; area B (lines 38 to
# 45) when every year after 1981 is designated or the FMV on December 31, 1981 is more than the
# proceeds; area C (line 48) when every year after 1981 is designated. Lines 51 and 53 always are.
COMPLETED: dict[int, dict[str, bool]] = {}
for _line in (27, 29, 30, 32, 33):
    COMPLETED[_line] = {
        "worked": True,
        "lesser": False,
        "loss": True,
        "all_after": True,
        "all_before": False,
        "not_applying": False,
    }
for _line in (38, 39, 42, 44, 45):
    COMPLETED[_line] = {
        "worked": True,
        "lesser": True,
        "loss": False,
        "all_after": False,
        "all_before": True,
        "not_applying": False,
    }
COMPLETED[48] = {
    "worked": True,
    "lesser": True,
    "loss": True,
    "all_after": False,
    "all_before": True,
    "not_applying": False,
}

for _line in (51, 53):
    COMPLETED[_line] = {
        "worked": True,
        "lesser": True,
        "loss": True,
        "all_after": True,
        "all_before": True,
        "not_applying": False,
    }

CAPABILITIES: dict[int, Any] = {
    27: PrincipalResidencePart2Line27,
    29: PrincipalResidencePart2Line29,
    30: PrincipalResidencePart2Line30,
    32: PrincipalResidencePart2Line32,
    33: PrincipalResidencePart2Line33,
    38: PrincipalResidencePart2Line38,
    39: PrincipalResidencePart2Line39,
    42: PrincipalResidencePart2Line42,
    44: PrincipalResidencePart2Line44,
    45: PrincipalResidencePart2Line45,
    48: PrincipalResidencePart2Line48,
    51: PrincipalResidencePart2Line51,
    53: PrincipalResidencePart2Line53,
}

KINDS: dict[int, ArtifactKind[Decimal]] = {
    27: PRINCIPAL_RESIDENCE_LINE_27,
    29: PRINCIPAL_RESIDENCE_LINE_29,
    30: PRINCIPAL_RESIDENCE_LINE_30,
    32: PRINCIPAL_RESIDENCE_LINE_32,
    33: PRINCIPAL_RESIDENCE_LINE_33,
    38: PRINCIPAL_RESIDENCE_LINE_38,
    39: PRINCIPAL_RESIDENCE_LINE_39,
    42: PRINCIPAL_RESIDENCE_LINE_42,
    44: PRINCIPAL_RESIDENCE_LINE_44,
    45: PRINCIPAL_RESIDENCE_LINE_45,
    48: PRINCIPAL_RESIDENCE_LINE_48,
    51: PRINCIPAL_RESIDENCE_LINE_51,
    53: PRINCIPAL_RESIDENCE_LINE_53,
}

TRACE_LINES: dict[int, type[TraceLine]] = {
    27: PrincipalResidenceLine27,
    29: PrincipalResidenceLine29,
    30: PrincipalResidenceLine30,
    32: PrincipalResidenceLine32,
    33: PrincipalResidenceLine33,
    38: PrincipalResidenceLine38,
    39: PrincipalResidenceLine39,
    42: PrincipalResidenceLine42,
    44: PrincipalResidenceLine44,
    45: PrincipalResidenceLine45,
    48: PrincipalResidenceLine48,
    51: PrincipalResidenceLine51,
    53: PrincipalResidenceLine53,
}

LINE_NUMBERS = list(CAPABILITIES)
PARTS = list(FIGURES)


def capability(line: int, rounding_data: ParameterDataset[RoundingOnly] | None = None) -> Any:
    """The capability of `line`, wired to the `ca/principal_residence_properties` record list and
    its kind; by default the dataset rounds half up to the cent."""
    return CAPABILITIES[line](
        rounding_data or rounding(), PRINCIPAL_RESIDENCE_PROPERTIES, KINDS[line]
    )


def output_of(line: int, *given: Part2Figures, rule: RoundingRule = CENT) -> Artifact[Any]:
    """The output of `line` over the properties `given`, in the order given."""
    outputs: tuple[Artifact[Any], ...] = (
        capability(line, rounding(rule)).compute((properties(*given),)).outputs
    )
    (output,) = outputs
    return output


def value_of(line: int, *given: Part2Figures, rule: RoundingRule = CENT) -> Decimal:
    value = output_of(line, *given, rule=rule).value
    assert isinstance(value, Decimal)
    return value


# --- contract and wiring ------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_registered_under_its_line(line: int) -> None:
    registered = CapabilityRegistry.shared().get(f"ca/principal_residence_line_{line}")

    assert registered is CAPABILITIES[line]
    assert registered.__module__ == (
        f"tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_{line}"
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_exported_from_the_ca_capabilities_package(line: int) -> None:
    assert f"principal_residence_line_{line}" in ca_capabilities.__all__
    module = getattr(ca_capabilities, f"principal_residence_line_{line}")
    assert getattr(module, CAPABILITIES[line].__name__) is CAPABILITIES[line]


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_a_subclass_of_the_shared_rows_base(line: int) -> None:
    assert issubclass(CAPABILITIES[line], PrincipalResidenceRows)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_declares_its_contract(line: int) -> None:
    assert capability(line).consumes == frozenset({PRINCIPAL_RESIDENCE_PROPERTIES})
    assert capability(line).produces == frozenset({KINDS[line]})


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_leaves_its_contract_to_the_base(line: int) -> None:
    assert "consumes" not in vars(CAPABILITIES[line])
    assert "produces" not in vars(CAPABILITIES[line])


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_declares_its_slots(line: int) -> None:
    cls = CAPABILITIES[line]
    assert cls.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert list(cls.PARAMETERS) == ["rounding"]
    assert cls.CONSUMES == {"properties": RecordList}
    assert cls.PRODUCES == {"output": Decimal}
    assert not cls.is_list_slot("properties")


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_its_slots_are_read_only(line: int) -> None:
    cls = CAPABILITIES[line]
    for slots in (cls.PARAMETERS, cls.CONSUMES, cls.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(PrincipalResidencePart2Line27.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(PrincipalResidencePart2Line27.CONSUMES, Mapping[str, type])
    assert_type(PrincipalResidencePart2Line27.PRODUCES, Mapping[str, type])


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_built_from_its_slot_names_as_keywords(line: int) -> None:
    wired = CAPABILITIES[line](
        rounding=rounding(),
        properties=PRINCIPAL_RESIDENCE_PROPERTIES,
        output=KINDS[line],
    )

    assert wired.compute((properties(PART_2_WORKED),)).outputs == (
        Artifact(KINDS[line], D(VALUES[line]["worked"])),
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_takes_no_separate_rounding_argument(line: int) -> None:
    with pytest.raises(TypeError):
        CAPABILITIES[line](rounding(), PRINCIPAL_RESIDENCE_PROPERTIES, KINDS[line], CENT)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_rejects_a_money_kind_for_its_properties(line: int) -> None:
    name = CAPABILITIES[line].__name__
    with pytest.raises(InvalidCapabilityError, match=f"{name}.*'properties'"):
        CAPABILITIES[line](rounding(), CAREGIVER_AMOUNT, KINDS[line])


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_is_not_generic_over_artifacts(line: int) -> None:
    assert not getattr(CAPABILITIES[line], "__type_params__", ())
    assert not getattr(CAPABILITIES[line], "__parameters__", ())


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_has_one_output_of_its_kind(line: int) -> None:
    outputs = capability(line).compute((properties(PART_2_WORKED),)).outputs

    assert len(outputs) == 1
    assert outputs[0].kind is KINDS[line]
    assert type(outputs[0].value) is Decimal


# --- computing: the worked example and the other properties -------------------------------------


@pytest.mark.parametrize(
    ("line", "part"), [(line, part) for line in LINE_NUMBERS for part in PARTS]
)
def test_each_line_of_each_property(line: int, part: str) -> None:
    assert value_of(line, FIGURES[part]) == D(VALUES[line][part])


def test_the_worked_example_by_hand() -> None:
    # Line 27 = 90,000.00 - 40,000.00; line 30 = 50,000.00 x 2; line 32 = 100,000.00 / 4; line 33 =
    # 50,000.00 - 25,000.00; line 38 = 90,000.00 + 10,000.00 + 5,000.00; line 42 = 195,000.00 x 6;
    # line 44 = 1,170,000.00 / 10; line 45 = 195,000.00 - 117,000.00; line 48 = 0 (FMV below the
    # proceeds); line 51 = 25,000.00 + 78,000.00; line 53 = 103,000.00.
    assert [value_of(line, PART_2_WORKED) for line in (27, 30, 32, 33)] == [
        D("50000.00"),
        D("100000.00"),
        D("25000.00"),
        D("25000.00"),
    ]
    assert [value_of(line, PART_2_WORKED) for line in (38, 42, 44, 45)] == [
        D("105000.00"),
        D("1170000.00"),
        D("117000.00"),
        D("78000.00"),
    ]
    assert value_of(53, PART_2_WORKED) == D("103000.00")


def test_a_negative_line_27_is_not_floored() -> None:
    # No floor on line 27 itself: 30,000.00 - 40,000.00 = -10,000.00, and line 33 is 0.
    assert value_of(27, NEGATIVE_AREA_A) == D("-10000.00")
    assert value_of(30, NEGATIVE_AREA_A) == D("-20000.00")
    assert value_of(32, NEGATIVE_AREA_A) == D("-5000.00")
    assert value_of(33, NEGATIVE_AREA_A) == D("0")


def test_a_negative_line_39_is_not_floored_and_line_45_is_not_below_zero() -> None:
    assert value_of(38, NEGATIVE_AREA_B) == D("110000.00")
    assert value_of(39, NEGATIVE_AREA_B) == D("-10000.00")
    assert value_of(42, NEGATIVE_AREA_B) == D("-20000.00")
    assert value_of(44, NEGATIVE_AREA_B) == D("-2000.00")
    assert value_of(45, NEGATIVE_AREA_B) == D("0")


@pytest.mark.parametrize("line", [27, 30, 32, 39, 42, 44])
def test_the_lines_that_may_be_negative_are_signed_kinds(line: int) -> None:
    assert KINDS[line].value_type is Decimal
    assert KINDS[line].non_negative is False


@pytest.mark.parametrize("line", [29, 33, 38, 45, 48, 51, 53])
def test_the_lines_that_are_never_negative_are_non_negative_kinds(line: int) -> None:
    assert KINDS[line].value_type is Decimal
    assert KINDS[line].non_negative is True


# --- computing: skipped areas -------------------------------------------------------------------


@pytest.mark.parametrize("line", [27, 29, 30, 32, 33])
def test_every_year_before_1982_designated_skips_area_a(line: int) -> None:
    # Designated for all the years owned before 1982 (2 of 2): lines 27 to 32 are not completed,
    # line 33 is 0, though the FMV (40,000.00) is less than the adjusted cost base (60,000.00).
    assert value_of(line, PART_2_ALL_YEARS_BEFORE_1982) == D("0")


@pytest.mark.parametrize("line", [38, 39, 42, 44, 45])
def test_every_year_after_1981_designated_skips_area_b(line: int) -> None:
    assert value_of(line, PART_2_ALL_YEARS_AFTER_1981) == D("0")


def test_every_year_after_1981_designated_leaves_area_c_not_completed() -> None:
    # The FMV (120,000.00) is more than the proceeds (100,000.00), yet line 48 is 0.
    assert value_of(48, PART_2_ALL_YEARS_AFTER_1981) == D("0")
    assert value_of(53, PART_2_ALL_YEARS_AFTER_1981) == D("30000.00")


def test_a_fmv_above_the_proceeds_skips_area_b_and_completes_area_c() -> None:
    # Line 45 is 0 and line 48 is 120,000.00 - 100,000.00 = 20,000.00.
    for line in (38, 39, 42, 44, 45):
        assert value_of(line, PART_2_LOSS) == D("0"), line
    assert value_of(48, PART_2_LOSS) == D("20000.00")


def test_a_fmv_below_the_proceeds_leaves_area_c_at_zero() -> None:
    # Line 48 = max(0, 90,000.00 - 300,000.00) = 0.
    assert value_of(48, PART_2_WORKED) == D("0")


def test_a_property_not_using_part_2_is_zero_on_every_line() -> None:
    for line in LINE_NUMBERS:
        assert value_of(line, PART_2_NOT_APPLYING) == D("0"), line


# --- computing: how many properties -------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_no_properties_give_zero(line: int) -> None:
    output = capability(line).compute((properties(),)).outputs

    assert output == (Artifact(KINDS[line], D("0")),)
    assert type(output[0].value) is Decimal


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_two_properties_give_the_sum_of_their_own_amounts(line: int) -> None:
    together = value_of(line, PART_2_WORKED, PART_2_LOSS)

    assert together == D(VALUES[line]["worked"]) + D(VALUES[line]["loss"])


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_the_total_does_not_depend_on_the_order(line: int) -> None:
    assert value_of(line, PART_2_WORKED, PART_2_LOSS, PART_2_ALL_YEARS_BEFORE_1982) == value_of(
        line, PART_2_ALL_YEARS_BEFORE_1982, PART_2_WORKED, PART_2_LOSS
    )


def test_a_property_with_a_skipped_area_adds_nothing_to_the_others() -> None:
    # Line 33: the worked example's 25,000.00 and 0 from the all-years-before-1982 property.
    assert value_of(33, PART_2_WORKED, PART_2_ALL_YEARS_BEFORE_1982) == D("25000.00")


def test_a_property_not_using_part_2_adds_nothing_to_the_others() -> None:
    assert value_of(53, PART_2_WORKED, PART_2_NOT_APPLYING) == D("103000.00")


# --- computing: rounding ------------------------------------------------------------------------


def test_line_32_is_rounded_half_up_to_the_cent() -> None:
    # 50,000.00 / 3 = 16,666.666..., to the cent 16,666.67; line 33 = 50,000.00 - 16,666.67.
    assert value_of(32, PART_2_ROUNDED_LINE_32) == D("16666.67")
    assert value_of(33, PART_2_ROUNDED_LINE_32) == D("33333.33")


def test_line_32_follows_the_datasets_rule_and_line_33_takes_the_rounded_line_32() -> None:
    assert value_of(32, PART_2_ROUNDED_LINE_32, rule=DOLLAR_FLOOR) == D("16666")
    assert value_of(33, PART_2_ROUNDED_LINE_32, rule=DOLLAR_FLOOR) == D("33334")


def test_line_44_is_rounded_half_up_to_the_cent() -> None:
    # 100,000.00 / 3 = 33,333.333..., to the cent 33,333.33; line 45 = 100,000.00 - 33,333.33.
    assert value_of(44, PART_2_ROUNDED_LINE_44) == D("33333.33")
    assert value_of(45, PART_2_ROUNDED_LINE_44) == D("66666.67")


def test_line_44_follows_the_datasets_rule() -> None:
    assert value_of(44, PART_2_ROUNDED_LINE_44, rule=DOLLAR_FLOOR) == D("33333")
    assert value_of(45, PART_2_ROUNDED_LINE_44, rule=DOLLAR_FLOOR) == D("66667")


def test_a_half_cent_on_line_44_is_rounded_up() -> None:
    # 1.00 / 8 = 0.125, half up to the cent 0.13; line 45 = 1.00 - 0.13 = 0.87.
    assert value_of(44, PART_2_HALF_CENT_LINE_44) == D("0.13")
    assert value_of(45, PART_2_HALF_CENT_LINE_44) == D("0.87")


def test_a_half_cent_on_line_44_with_a_whole_dollar_rule_is_rounded_down() -> None:
    assert value_of(44, PART_2_HALF_CENT_LINE_44, rule=DOLLAR_FLOOR) == D("0")
    assert value_of(45, PART_2_HALF_CENT_LINE_44, rule=DOLLAR_FLOOR) == D("1.00")


@pytest.mark.parametrize("line", [27, 29, 30, 38, 39, 42, 48])
def test_lines_that_do_not_divide_ignore_the_rounding_rule(line: int) -> None:
    for part in ("worked", "loss"):
        assert value_of(line, FIGURES[part], rule=DOLLAR_FLOOR) == value_of(line, FIGURES[part]), (
            line,
            part,
        )


def test_each_property_is_rounded_before_the_totals_are_summed() -> None:
    # Each property's line 32 is rounded first: 16,666.67 + 16,666.67 = 33,333.34. Summing the
    # exact quotients first would give 33,333.33.
    assert value_of(32, PART_2_ROUNDED_LINE_32, PART_2_ROUNDED_LINE_32) == D("33333.34")


def test_the_rounded_amount_carries_the_increments_scale() -> None:
    value = value_of(32, PART_2_ROUNDED_LINE_32)

    assert str(value) == "16666.67"


# --- computing: refusals ------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_a_property_owned_for_no_years_is_refused_as_part_1_is(line: int) -> None:
    with pytest.raises(ValidationError, match=r"the years owned \(lines 5 and 6\) are 0"):
        value_of(line, PART_2_NO_YEARS_OWNED)


def test_the_refusal_names_the_property_by_its_position() -> None:
    with pytest.raises(ValidationError, match="property 2: the years owned"):
        value_of(33, PART_2_WORKED, PART_2_NO_YEARS_OWNED)


# --- computing: inputs --------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_ignores_artifacts_it_does_not_consume(line: int) -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    result = capability(line).compute((other, properties(PART_2_WORKED)))

    assert result.outputs == (Artifact(KINDS[line], D(VALUES[line]["worked"])),)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_missing_properties_is_a_missing_artifact(line: int) -> None:
    with pytest.raises(MissingArtifactError, match="principal_residence_properties"):
        capability(line).compute(())


# --- trace --------------------------------------------------------------------------------------


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_one_line_per_property_then_the_total(line: int) -> None:
    trace = capability(line).compute((properties(PART_2_WORKED, PART_2_LOSS),)).trace

    assert [type(item) for item in trace] == [
        TRACE_LINES[line],
        TRACE_LINES[line],
        ItemsTotalLine,
    ]
    total = D(VALUES[line]["worked"]) + D(VALUES[line]["loss"])
    assert trace[-1] == ItemsTotalLine(
        KINDS[line],
        ((1, D(VALUES[line]["worked"])), (2, D(VALUES[line]["loss"]))),
        total,
    )


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_the_callers_order_with_positions_from_one(line: int) -> None:
    trace = capability(line).compute((properties(PART_2_LOSS, PART_2_WORKED),)).trace

    items: list[Any] = list(trace[:-1])
    assert [item.position for item in items] == [1, 2]
    assert [item.result for item in items] == [D(VALUES[line]["loss"]), D(VALUES[line]["worked"])]


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_traces_no_properties_as_only_an_empty_total(line: int) -> None:
    trace = capability(line).compute((properties(),)).trace

    assert trace == (ItemsTotalLine(KINDS[line], (), D("0")),)


@pytest.mark.parametrize("line", LINE_NUMBERS)
def test_the_last_trace_line_amount_is_the_output(line: int) -> None:
    result = capability(line).compute((properties(PART_2_WORKED, PART_2_LOSS),))

    total: Any = result.trace[-1]
    assert total.amount == result.outputs[0].value


@pytest.mark.parametrize(("line", "part"), [(line, part) for line in COMPLETED for part in PARTS])
def test_traces_whether_the_step_is_completed_for_each_property(line: int, part: str) -> None:
    (item, _total) = capability(line).compute((properties(FIGURES[part]),)).trace

    assert cast(Any, item).completed is COMPLETED[line][part]


@pytest.mark.parametrize("line", [51, 53])
def test_the_net_capital_gain_lines_are_not_completed_without_part_2(line: int) -> None:
    # Area D has no figures of its own: without Part 2 the line is not completed and reads 0.
    (item, _total) = capability(line).compute((properties(PART_2_NOT_APPLYING),)).trace

    assert cast(Any, item).completed is False
    assert cast(Any, item).result == D("0")


def test_compute_is_repeatable() -> None:
    wired = capability(53)

    first = wired.compute((properties(PART_2_WORKED, PART_2_LOSS),))
    second = wired.compute((properties(PART_2_WORKED, PART_2_LOSS),))

    assert first == second


def test_the_rounding_rule_comes_from_the_dataset() -> None:
    wired = capability(44, rounding(DOLLAR_FLOOR))

    (output,) = wired.compute((properties(PART_2_ROUNDED_LINE_44),)).outputs

    assert output.value == D("33333")


# --- the base, and the types ---------------------------------------------------------------------


def test_the_base_is_not_registered() -> None:
    with pytest.raises(UnknownRegistrationError):
        CapabilityRegistry.shared().get("ca/principal_residence_rows")


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        PrincipalResidencePart2Line27(
            rate,  # type: ignore[arg-type]
            PRINCIPAL_RESIDENCE_PROPERTIES,
            KINDS[27],
        )

    assert callable(wire)


# --- signed zero ----------------------------------------------------------------------------------

# No years designated after 1981, so line 42 is line 39 times 0; line 39 is negative. Line 38 =
# 5,000.00 + 20,000.00 = 25,000.00 and line 39 = 10,000.00 - 25,000.00 = -15,000.00.
NEGATIVE_LINE_39_NO_YEARS_AFTER_1981: Part2Figures = (
    0,
    1,
    10,
    4,
    "10000.00",
    "0.00",
    "1000.00",
    0,
    1,
    "0.00",
    "5000.00",
    "20000.00",
)


def test_a_negative_line_39_times_no_years_is_zero_not_negative_zero() -> None:
    assert value_of(39, NEGATIVE_LINE_39_NO_YEARS_AFTER_1981) == D("-15000.00")
    line_42 = value_of(42, NEGATIVE_LINE_39_NO_YEARS_AFTER_1981)

    assert line_42 == D("0")
    assert not line_42.is_signed()


def test_a_negative_line_39_times_no_years_reads_as_zero_in_english() -> None:
    (line_42, _total) = (
        capability(42).compute((properties(NEGATIVE_LINE_39_NO_YEARS_AFTER_1981),)).trace
    )

    text = EnglishTraceRenderer().render(line_42)

    assert "-0" not in text
    assert text.endswith("line 42 0 = line 39 -15000 times line 1 0")
