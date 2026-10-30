"""Unit tests for PrincipalResidenceDesignationBoxCapability: Schedule 3 line 17900, the principal
residence designation box, from the consumed `ca/principal_residence_properties`.

Form 5000-S3 Part 1, line 17900: "Box 1: I designate the property as my principal residence for all
of the years that I owned it or for all of the years that I owned it except one year. Box 2: I
designate the property as my principal residence for some but not all of the years that I owned
it. Box 3: I designate the properties as my principal residences for some or all of the years that
I owned them." The output is the box, an int: 0 with no property, 3 with more than one property,
and for one property 1 when the years designated (line 3 of Form T2091(IND)) are at least the years
owned (line 7) less one, else 2. The trace is one `PrincipalResidenceDesignationBox` line, not an
items total: the box is one figure, not a total of the properties.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.capability import CapabilityRegistry, CapabilityResult
from tax_engine.domain.errors import ValidationError
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.principal_residence_designation_box import (
    PrincipalResidenceDesignationBoxCapability,
)
from tax_engine.jurisdictions.ca.capabilities.principal_residence_rows import (
    PrincipalResidenceRows,
)
from tax_engine.jurisdictions.ca.catalog import (
    PRINCIPAL_RESIDENCE_DESIGNATION_BOX,
    PRINCIPAL_RESIDENCE_PROPERTIES,
)
from tax_engine.jurisdictions.ca.trace import PrincipalResidenceDesignationBox
from tests.jurisdictions.ca.capabilities.principal_residence_figures import (
    Figures,
    properties,
    rounding,
)

D = Decimal

CAPABILITY = PrincipalResidenceDesignationBoxCapability


def years(designated: int, owned: int) -> Figures:
    """A property owned and designated for years after 1981 only (lines 1 and 5), with no money:
    its designated years are `designated` and its years owned `owned`."""
    return (designated, 0, owned, 0, "0.00", "0.00", "0.00", 0)


def years_before_and_after(
    designated_after: int, designated_before: int, owned_after: int, owned_before: int
) -> Figures:
    """A property with years from 1972 to 1981 as well (lines 2 and 6): the box takes their totals
    (lines 3 and 7) with the years after 1981."""
    return (
        designated_after,
        designated_before,
        owned_after,
        owned_before,
        "0.00",
        "0.00",
        "0.00",
        0,
    )


def capability() -> PrincipalResidenceDesignationBoxCapability:
    """The capability, wired to the `ca/principal_residence_properties` record list and its kind,
    with the rounding dataset of the siblings."""
    return CAPABILITY(
        rounding(), PRINCIPAL_RESIDENCE_PROPERTIES, PRINCIPAL_RESIDENCE_DESIGNATION_BOX
    )


def result_of(*given: Figures) -> CapabilityResult:
    """The capability's result over the properties `given`, in the order given."""
    return capability().compute((properties(*given),))


def box_of(*given: Figures) -> int:
    """The output's box over the properties `given`."""
    (output,) = result_of(*given).outputs
    assert output.kind is PRINCIPAL_RESIDENCE_DESIGNATION_BOX
    assert type(output.value) is int
    return output.value


def the_one_line(*given: Figures) -> PrincipalResidenceDesignationBox:
    """The single trace line of the result over the properties `given`."""
    (line,) = result_of(*given).trace
    assert isinstance(line, PrincipalResidenceDesignationBox)
    return line


# --- contract and wiring ------------------------------------------------------------------------


def test_is_registered_under_its_identifier() -> None:
    registered = CapabilityRegistry.shared().get("ca/principal_residence_designation_box")

    assert registered is CAPABILITY
    assert registered.__module__ == (
        "tax_engine.jurisdictions.ca.capabilities.principal_residence_designation_box"
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "principal_residence_designation_box" in ca_capabilities.__all__
    module = ca_capabilities.principal_residence_designation_box

    assert module.PrincipalResidenceDesignationBoxCapability is CAPABILITY


def test_is_a_subclass_of_the_shared_rows_base() -> None:
    assert issubclass(CAPABILITY, PrincipalResidenceRows)


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({PRINCIPAL_RESIDENCE_PROPERTIES})
    assert capability().produces == frozenset({PRINCIPAL_RESIDENCE_DESIGNATION_BOX})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CAPABILITY)
    assert "produces" not in vars(CAPABILITY)


def test_produces_one_int_output() -> None:
    assert CAPABILITY.PRODUCES == {"output": int}


def test_takes_the_rounding_dataset_as_its_only_parameter() -> None:
    assert set(CAPABILITY.PARAMETERS) == {"rounding"}


def test_the_output_kind_is_a_non_negative_int_count() -> None:
    assert PRINCIPAL_RESIDENCE_DESIGNATION_BOX.value_type is int
    assert PRINCIPAL_RESIDENCE_DESIGNATION_BOX.non_negative is True


# --- the box -----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("description", "given", "expected"),
    [
        ("no property gives box 0", (), 0),
        ("one property designated for all its years is box 1", (years(6, 6),), 1),
        ("one property designated for all but one of its years is box 1", (years(5, 6),), 1),
        ("one property designated two years short is box 2", (years(4, 6),), 2),
        (
            "one property owned one year and not designated is box 1 (all but one)",
            (years(0, 1),),
            1,
        ),
        ("one property designated for one year of six is box 2", (years(1, 6),), 2),
        (
            "the years from 1972 to 1981 count in the totals (box 1 at one year short)",
            (years_before_and_after(4, 2, 5, 2),),
            1,
        ),
        (
            "the years from 1972 to 1981 count in the totals (box 2 at two years short)",
            (years_before_and_after(4, 2, 6, 2),),
            2,
        ),
        ("two properties are box 3 whatever their years", (years(6, 6), years(6, 6)), 3),
        ("two properties, one not designated at all, are box 3", (years(6, 6), years(0, 6)), 3),
        (
            "the three properties of the T4037 example are box 3",
            (years(6, 6), years(5, 5), years(15, 15)),
            3,
        ),
    ],
)
def test_the_box_follows_the_properties_and_their_years(
    description: str, given: tuple[Figures, ...], expected: int
) -> None:
    assert box_of(*given) == expected, description


def test_the_box_is_a_plain_int_not_a_decimal() -> None:
    assert box_of(years(6, 6)) == 1
    assert type(box_of(years(6, 6))) is int


def test_the_box_of_two_properties_does_not_depend_on_their_order() -> None:
    assert box_of(years(6, 6), years(1, 6)) == box_of(years(1, 6), years(6, 6)) == 3


def test_a_property_owned_for_no_years_is_refused_by_the_rows_base() -> None:
    with pytest.raises(ValidationError, match="the years owned"):
        box_of(years(0, 0))


# --- the trace ---------------------------------------------------------------------------------


def test_the_result_is_one_trace_line_not_an_items_total() -> None:
    trace = result_of(years(6, 6)).trace

    assert len(trace) == 1
    assert not any(isinstance(line, ItemsTotalLine) for line in trace)


def test_the_line_of_one_property_holds_its_count_its_years_and_the_box() -> None:
    line = the_one_line(years(5, 6))

    assert line.output is PRINCIPAL_RESIDENCE_DESIGNATION_BOX
    assert line.properties == 1
    assert line.designated == 5
    assert line.owned == 6
    assert line.box == 1
    assert line.amount == D(1)


def test_the_line_counts_the_years_before_1982_with_the_years_after() -> None:
    line = the_one_line(years_before_and_after(4, 2, 5, 2))

    assert (line.designated, line.owned) == (6, 7)
    assert line.box == 1


def test_the_line_of_no_property_is_box_0_with_no_property() -> None:
    line = the_one_line()

    assert line.properties == 0
    assert line.box == 0
    assert line.amount == D(0)


def test_the_line_of_three_properties_counts_them_and_is_box_3() -> None:
    line = the_one_line(years(6, 6), years(5, 5), years(15, 15))

    assert line.properties == 3
    assert line.box == 3
    assert line.amount == D(3)


def test_the_trace_box_is_the_output() -> None:
    for given in ((), (years(6, 6),), (years(4, 6),), (years(6, 6), years(5, 5))):
        (output,) = result_of(*given).outputs
        assert the_one_line(*given).box == output.value, given
