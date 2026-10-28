"""Unit tests for the PrincipalResidenceGain capability (`ca/principal_residence_gain`), Form
T2091(IND) Section 2 Part 1 and Part 3.

Form T2091(IND), "Designation of a Property as a Principal Residence by an Individual (Other than a
Personal Trust)": "Complete a separate form for each property you sold." Line 1 "After 1981" and
line 2 "After 1971 and before 1982" of the designation, "Total number of years designated (line 1
plus line 2)" (line 3, carried to line 4); line 5 "After 1981" and line 6 "After 1971 and before
1982" of the years owned, "Total number of years owned (line 5 plus line 6)" (line 7); line 8
"Proceeds of disposition or deemed disposition", line 9 "Outlays and expenses made or incurred
related to the disposition", line 10 "Adjusted cost base at the time of disposition". Part 1: line
14 proceeds (line 8), line 15 adjusted cost base (line 10), line 16 outlays (line 9), line 17 "Line
15 plus line 16", line 18 "Line 14 minus line 17" ("Capital gain before principal residence
exemption"), line 19 "Amount from line 18", line 20 "Line 4 plus 1 (see note on page 4)", line 21
"Multiply line 19 by line 20.", line 22 "Total number of years from line 7", line 23 "Divide line
21 by line 22.", line 24 "Line 18 minus line 23 (if negative, enter "0")" ("Net capital gain").
Part 2, for a property that is one of two or more principal residences a family member owned on
December 31, 1981, and continuously until its disposition: the pre-1982 gain and the post-1981 gain
are worked in areas A to D, the lines of which are the capabilities `principal_residence_line_N`
(their tests are in `test_principal_residence_lines.py`); line 53 "Line 51 minus line 52 (if
negative, enter "0")" is the net capital gain, and line 54 "If you completed Part 2, enter whichever
amount is less: line 53 above or line 24 of Part 1. Otherwise, enter the amount from line 24." is
the lesser of line 53 and line 24 for such a property, and line 24 for any other. Note: "One year is
granted by law. If you disposed of your principal residence after October 2, 2016, and were a
non-resident throughout the year of acquisition of the property, you are not eligible to use the
"plus one" rule in this calculation."

Its slots: one parameter slot `rounding` (a `rounding_only` dataset: line 23 divides), one consumed
slot `properties` (a record list whose records hold each property's lines 1, 2, 5, 6, 8, 9 and 10,
whether the "plus one" applies, whether Part 2 applies and lines 11, 12 and 13) and one produced
slot `output`. Each property is worked on its own, never pooled: line 23 is the exact fraction
rounded once with the dataset's rule, and the output is the total of line 54. It records one
`PrincipalResidenceGainLine` per property, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InvalidCapabilityError,
    MissingArtifactError,
    ValidationError,
)
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingRule
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_gain import (
    PrincipalResidenceGain,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_rows import (
    PrincipalResidenceRows,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    PRINCIPAL_RESIDENCE_GAIN,
    PRINCIPAL_RESIDENCE_PROPERTIES,
)
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceGainLine
from tests.jurisdictions.ca.capabilities.principal_residence_figures import (
    CENT,
    DOLLAR_FLOOR,
    PART_2_ALL_YEARS_AFTER_1981,
    PART_2_ALL_YEARS_BEFORE_1982,
    PART_2_LESSER_IS_LINE_53,
    PART_2_LOSS,
    PART_2_NO_YEARS_OWNED,
    PART_2_NOT_APPLYING,
    PART_2_WORKED,
    Figures,
    Part2Figures,
    properties,
    rounding,
)

D = Decimal

# Each property's figures are read from `principal_residence_figures`: a property of eight figures
# does not use Part 2, a property of twelve gives its Part 2 figures as well.
# Gain 300,000.00; 6 years designated plus 1 over 10 owned: 210,000.00 exempt, 90,000.00 left.
EXAMPLE: Figures = (6, 0, 10, 0, "400000.00", "5000.00", "95000.00", 1)
# Gain 40,000.00; 3 years designated, no "plus one", over 5 owned: 24,000.00 exempt, 16,000.00 left.
NO_PLUS_ONE: Figures = (3, 0, 5, 0, "250000.00", "10000.00", "200000.00", 0)
# Gain 300,000.00; 2 + 3 years designated plus 1 over 6 + 4 owned: 180,000.00 exempt, 120,000.00.
BOTH_PERIODS: Figures = (2, 3, 6, 4, "500000.00", "0.00", "200000.00", 1)


def capability(
    rounding_data: ParameterDataset[RoundingOnly] | None = None,
) -> PrincipalResidenceGain:
    """By default the dataset rounds half up to the cent."""
    return PrincipalResidenceGain(
        rounding_data or rounding(), PRINCIPAL_RESIDENCE_PROPERTIES, PRINCIPAL_RESIDENCE_GAIN
    )


def compute(wired: PrincipalResidenceGain, *given: Figures | Part2Figures) -> Artifact[Any]:
    (output,) = wired.compute((properties(*given),)).outputs
    return output


def total(*given: Figures | Part2Figures) -> Decimal:
    value = compute(capability(), *given).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_principal_residence_gain() -> None:
    assert CapabilityRegistry.shared().get("ca/principal_residence_gain") is PrincipalResidenceGain


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert ca_capabilities.NAMESPACE == "ca"
    assert "principal_residence_gain" in ca_capabilities.__all__
    assert ca_capabilities.principal_residence_gain.PrincipalResidenceGain is PrincipalResidenceGain


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({PRINCIPAL_RESIDENCE_PROPERTIES})
    assert capability().produces == frozenset({PRINCIPAL_RESIDENCE_GAIN})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(PrincipalResidenceGain)
    assert "produces" not in vars(PrincipalResidenceGain)


def test_is_a_subclass_of_the_shared_rows_base() -> None:
    # The rows base works lines 18 to 24 and Part 2 for each property, as the line capabilities do.
    assert issubclass(PrincipalResidenceGain, PrincipalResidenceRows)


def test_declares_its_slots() -> None:
    assert PrincipalResidenceGain.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert list(PrincipalResidenceGain.PARAMETERS) == ["rounding"]
    assert PrincipalResidenceGain.CONSUMES == {"properties": RecordList}
    assert PrincipalResidenceGain.PRODUCES == {"output": Decimal}
    assert not PrincipalResidenceGain.is_list_slot("properties")


def test_its_slots_are_read_only() -> None:
    for slots in (
        PrincipalResidenceGain.PARAMETERS,
        PrincipalResidenceGain.CONSUMES,
        PrincipalResidenceGain.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(PrincipalResidenceGain.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(PrincipalResidenceGain.CONSUMES, Mapping[str, type])
    assert_type(PrincipalResidenceGain.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        PrincipalResidenceGain.PARAMETERS,
        PrincipalResidenceGain.CONSUMES,
        PrincipalResidenceGain.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = PrincipalResidenceGain(
        rounding=rounding(),
        properties=PRINCIPAL_RESIDENCE_PROPERTIES,
        output=PRINCIPAL_RESIDENCE_GAIN,
    )

    assert compute(wired, EXAMPLE) == Artifact(PRINCIPAL_RESIDENCE_GAIN, D("90000.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        PrincipalResidenceGain(  # type: ignore[call-arg]
            rounding(), PRINCIPAL_RESIDENCE_PROPERTIES, PRINCIPAL_RESIDENCE_GAIN, CENT
        )


def test_rejects_a_money_kind_for_its_properties() -> None:
    with pytest.raises(InvalidCapabilityError, match="PrincipalResidenceGain.*'properties'"):
        PrincipalResidenceGain(
            rounding(),
            CAREGIVER_AMOUNT,  # type: ignore[arg-type]
            PRINCIPAL_RESIDENCE_GAIN,
        )


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(PrincipalResidenceGain, "__type_params__", ())
    assert not getattr(PrincipalResidenceGain, "__parameters__", ())


# --- computing: how many properties -------------------------------------------------------------


def test_no_properties_give_zero() -> None:
    output = compute(capability())

    assert output == Artifact(PRINCIPAL_RESIDENCE_GAIN, D("0"))
    assert type(output.value) is Decimal
    assert not output.value.is_signed()


def test_one_property_gives_the_per_item_figure() -> None:
    # The worked example: line 18 = 400,000.00 - (95,000.00 + 5,000.00) = 300,000.00;
    # line 20 = 6 + 1 = 7; line 21 = 2,100,000.00; line 23 = 2,100,000.00 / 10 = 210,000.00;
    # line 24 = 300,000.00 - 210,000.00 = 90,000.00.
    assert total(EXAMPLE) == D("90000.00")


def test_two_properties_give_the_sum_of_their_own_amounts() -> None:
    assert total(EXAMPLE, NO_PLUS_ONE) == D("106000.00")


def test_three_properties_are_summed_one_by_one() -> None:
    assert total(EXAMPLE, NO_PLUS_ONE, BOTH_PERIODS) == D("226000.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(BOTH_PERIODS, EXAMPLE, NO_PLUS_ONE) == total(EXAMPLE, NO_PLUS_ONE, BOTH_PERIODS)


def test_a_property_with_nothing_left_adds_nothing_to_the_others() -> None:
    fully_exempt: Figures = (10, 0, 10, 0, "400000.00", "5000.00", "95000.00", 1)

    assert total(fully_exempt, NO_PLUS_ONE) == D("16000.00")


# --- computing: the years (lines 1 to 7, 20) ----------------------------------------------------


def test_the_designation_without_the_plus_one_multiplies_the_years_designated() -> None:
    # Line 20 = line 4 = 3 when the "plus one" does not apply: 40,000.00 x 3 / 5 = 24,000.00.
    assert total(NO_PLUS_ONE) == D("16000.00")


def test_the_plus_one_adds_a_year_to_the_designation() -> None:
    plus_one: Figures = (*NO_PLUS_ONE[:7], 1)

    # Line 20 = 3 + 1 = 4: 40,000.00 x 4 / 5 = 32,000.00 exempt.
    assert total(plus_one) == D("8000.00")


def test_the_years_designated_of_both_periods_are_added() -> None:
    # Line 3 = 2 + 3 = 5, line 20 = 6, line 7 = 6 + 4 = 10: 300,000.00 x 6 / 10 = 180,000.00.
    assert total(BOTH_PERIODS) == D("120000.00")


def test_the_years_owned_of_both_periods_are_added() -> None:
    only_before: Figures = (0, 4, 0, 10, "400000.00", "5000.00", "95000.00", 1)

    # Line 4 = 4, line 20 = 5, line 7 = 10: 300,000.00 x 5 / 10 = 150,000.00 exempt.
    assert total(only_before) == D("150000.00")


def test_the_years_owned_after_1981_alone_are_the_divisor() -> None:
    one_year: Figures = (0, 0, 1, 0, "400000.00", "5000.00", "95000.00", 1)

    # Line 20 = 0 + 1 = 1, line 7 = 1: the whole gain is exempt.
    assert total(one_year) == D("0.00")


def test_a_property_with_no_years_designated_and_no_plus_one_is_wholly_taxable() -> None:
    undesignated: Figures = (0, 0, 10, 0, "400000.00", "5000.00", "95000.00", 0)

    assert total(undesignated) == D("300000.00")


def test_a_property_owned_for_no_years_is_refused() -> None:
    # Line 22 is the divisor of line 23.
    never_owned: Figures = (0, 0, 0, 0, "400000.00", "5000.00", "95000.00", 1)

    with pytest.raises(ValidationError, match="property 1.*years owned"):
        total(never_owned)


def test_the_property_owned_for_no_years_is_named_by_its_position() -> None:
    never_owned: Figures = (0, 0, 0, 0, "400000.00", "5000.00", "95000.00", 1)

    with pytest.raises(ValidationError, match="property 2.*years owned"):
        total(EXAMPLE, never_owned)


# --- computing: the gain (lines 14 to 18) -------------------------------------------------------


def test_line_18_is_the_proceeds_less_the_cost_base_and_the_outlays() -> None:
    # 500,000.00 - (200,000.00 + 20,000.00) = 280,000.00; nothing designated, no "plus one".
    figures: Figures = (0, 0, 10, 0, "500000.00", "20000.00", "200000.00", 0)

    assert total(figures) == D("280000.00")


def test_the_outlays_reduce_the_gain() -> None:
    without: Figures = (0, 0, 10, 0, "500000.00", "0.00", "200000.00", 0)
    with_outlays: Figures = (0, 0, 10, 0, "500000.00", "20000.00", "200000.00", 0)

    assert total(without) - total(with_outlays) == D("20000.00")


def test_proceeds_equal_to_cost_base_and_outlays_leave_nothing() -> None:
    figures: Figures = (4, 0, 10, 0, "100000.00", "5000.00", "95000.00", 1)

    output = compute(capability(), figures)

    assert output == Artifact(PRINCIPAL_RESIDENCE_GAIN, D("0"))
    assert not output.value.is_signed()


# --- computing: line 24 never below zero --------------------------------------------------------


def test_a_property_designated_for_every_year_with_the_plus_one_leaves_zero_not_negative() -> None:
    # Line 20 = 10 + 1 = 11 over 10 years: line 23 = 330,000.00 exceeds line 18, line 24 is "0".
    designated_throughout: Figures = (10, 0, 10, 0, "400000.00", "5000.00", "95000.00", 1)

    output = compute(capability(), designated_throughout)

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_a_loss_leaves_zero_not_negative() -> None:
    # Line 18 = 100,000.00 - (120,000.00 + 5,000.00) = -25,000.00; line 23 = -17,500.00.
    loss: Figures = (6, 0, 10, 0, "100000.00", "5000.00", "120000.00", 1)

    output = compute(capability(), loss)

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_a_loss_does_not_reduce_the_other_properties() -> None:
    loss: Figures = (6, 0, 10, 0, "100000.00", "5000.00", "120000.00", 1)

    assert total(loss, EXAMPLE) == D("90000.00")


def test_a_gain_of_zero_leaves_zero() -> None:
    nothing: Figures = (0, 0, 10, 0, "100000.00", "0.00", "100000.00", 0)

    assert total(nothing) == D("0")


# --- computing: rounding ------------------------------------------------------------------------


def test_line_23_is_rounded_half_up_to_the_cent() -> None:
    # Line 23 = 1.00 x 1 / 8 = 0.125 exactly, which half-up rounds to 0.13: line 24 = 0.87.
    eighth: Figures = (0, 0, 8, 0, "1.00", "0.00", "0.00", 1)

    assert total(eighth) == D("0.87")


def test_line_23_rounds_down_below_the_half_cent() -> None:
    # 1.00 / 16 = 0.0625 -> 0.06: line 24 = 0.94.
    sixteenth: Figures = (0, 0, 16, 0, "1.00", "0.00", "0.00", 1)

    assert total(sixteenth) == D("0.94")


def test_line_23_that_does_not_end_is_rounded_from_the_exact_fraction() -> None:
    # 100,000.00 x 1 / 3 = 33,333.333... -> 33,333.33: line 24 = 66,666.67.
    third: Figures = (0, 0, 3, 0, "100000.00", "0.00", "0.00", 1)

    assert total(third) == D("66666.67")


def test_a_ratio_that_does_not_end_on_the_upper_side_rounds_up() -> None:
    # 100,000.00 x 2 / 3 = 66,666.666... -> 66,666.67: line 24 = 33,333.33.
    two_thirds: Figures = (1, 0, 3, 0, "100000.00", "0.00", "0.00", 1)

    assert total(two_thirds) == D("33333.33")


def test_the_rounding_is_done_once_per_property_before_they_are_summed() -> None:
    eighth: Figures = (0, 0, 8, 0, "1.00", "0.00", "0.00", 1)

    # Each: 0.125 -> 0.13, left 0.87, twice: 1.74. Rounding the exact exemptions' sum 0.25 instead
    # would give 1.75.
    assert total(eighth, eighth) == D("1.74")


def test_the_rounding_rule_comes_from_the_dataset() -> None:
    third: Figures = (0, 0, 3, 0, "100000.00", "0.00", "0.00", 1)

    # Floored to the dollar, line 23 = 33,333: line 24 = 66,667.
    assert compute(capability(rounding(DOLLAR_FLOOR)), third).value == D("66667")


def test_a_dataset_that_does_not_round_keeps_the_exact_quotient_when_it_ends() -> None:
    eighth: Figures = (0, 0, 8, 0, "1.00", "0.00", "0.00", 1)

    assert compute(capability(rounding(NO_ROUNDING)), eighth).value == D("0.875")


def test_the_rounded_amount_carries_the_increments_scale() -> None:
    assert str(compute(capability(), EXAMPLE).value) == "90000.00"


# --- computing: inputs --------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    result = capability().compute((other, properties(EXAMPLE)))

    assert result.outputs == (Artifact(PRINCIPAL_RESIDENCE_GAIN, D("90000.00")),)


def test_missing_properties_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="principal_residence_properties"):
        capability().compute(())


def test_has_one_output() -> None:
    assert len(capability().compute((properties(EXAMPLE, NO_PLUS_ONE),)).outputs) == 1


def test_the_output_is_a_decimal_of_the_output_kind() -> None:
    (output,) = capability().compute((properties(EXAMPLE),)).outputs

    assert output.kind is PRINCIPAL_RESIDENCE_GAIN
    assert type(output.value) is Decimal


# --- trace --------------------------------------------------------------------------------------


def example_line(position: int = 1, rule: RoundingRule = CENT) -> PrincipalResidenceGainLine:
    """The worked example: gain 300,000.00, 6 designated plus 1 over 10 owned."""
    return PrincipalResidenceGainLine(
        output=PRINCIPAL_RESIDENCE_GAIN,
        position=position,
        years_designated_after_1981=6,
        years_designated_1972_to_1981=0,
        designated=6,
        years_owned_after_1981=10,
        years_owned_1972_to_1981=0,
        owned=10,
        plus_one=1,
        proceeds=D("400000.00"),
        adjusted_cost_base=D("95000.00"),
        outlays=D("5000.00"),
        gain=D("300000.00"),
        line_20=7,
        line_21=D("2100000.00"),
        rounding=rule,
        exempt=D("210000.00"),
        part_2_applies=0,
        line_53=D("0"),
        line_24=D("90000.00"),
        result=D("90000.00"),
    )


def no_plus_one_line(position: int = 1) -> PrincipalResidenceGainLine:
    """Gain 40,000.00, 3 designated and no "plus one" over 5 owned."""
    return PrincipalResidenceGainLine(
        output=PRINCIPAL_RESIDENCE_GAIN,
        position=position,
        years_designated_after_1981=3,
        years_designated_1972_to_1981=0,
        designated=3,
        years_owned_after_1981=5,
        years_owned_1972_to_1981=0,
        owned=5,
        plus_one=0,
        proceeds=D("250000.00"),
        adjusted_cost_base=D("200000.00"),
        outlays=D("10000.00"),
        gain=D("40000.00"),
        line_20=3,
        line_21=D("120000.00"),
        rounding=CENT,
        exempt=D("24000.00"),
        part_2_applies=0,
        line_53=D("0"),
        line_24=D("16000.00"),
        result=D("16000.00"),
    )


def test_traces_one_line_per_property_then_the_total() -> None:
    trace = capability().compute((properties(EXAMPLE, NO_PLUS_ONE),)).trace

    assert trace == (
        example_line(1),
        no_plus_one_line(2),
        ItemsTotalLine(
            PRINCIPAL_RESIDENCE_GAIN, ((1, D("90000.00")), (2, D("16000.00"))), D("106000.00")
        ),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = capability().compute((properties(NO_PLUS_ONE, EXAMPLE),)).trace

    assert trace == (
        no_plus_one_line(1),
        example_line(2),
        ItemsTotalLine(
            PRINCIPAL_RESIDENCE_GAIN, ((1, D("16000.00")), (2, D("90000.00"))), D("106000.00")
        ),
    )


def test_traces_one_property_as_a_line_and_a_total() -> None:
    trace = capability().compute((properties(EXAMPLE),)).trace

    assert trace == (
        example_line(1),
        ItemsTotalLine(PRINCIPAL_RESIDENCE_GAIN, ((1, D("90000.00")),), D("90000.00")),
    )


def test_traces_no_properties_as_only_an_empty_total() -> None:
    trace = capability().compute((properties(),)).trace

    assert trace == (ItemsTotalLine(PRINCIPAL_RESIDENCE_GAIN, (), D("0")),)


def test_traces_the_years_of_both_periods_and_their_totals() -> None:
    (line, _) = capability().compute((properties(BOTH_PERIODS),)).trace

    assert isinstance(line, PrincipalResidenceGainLine)
    assert (line.years_designated_after_1981, line.years_designated_1972_to_1981) == (2, 3)
    assert line.designated == 5
    assert (line.years_owned_after_1981, line.years_owned_1972_to_1981) == (6, 4)
    assert line.owned == 10
    assert line.plus_one == 1
    assert line.line_20 == 6


def test_traces_the_inputs_of_lines_8_to_10() -> None:
    (line, _) = capability().compute((properties(BOTH_PERIODS),)).trace

    assert isinstance(line, PrincipalResidenceGainLine)
    assert line.proceeds == D("500000.00")
    assert line.adjusted_cost_base == D("200000.00")
    assert line.outlays == D("0.00")


def test_traces_the_figures_of_lines_18_to_24() -> None:
    (line, _) = capability().compute((properties(BOTH_PERIODS),)).trace

    assert isinstance(line, PrincipalResidenceGainLine)
    assert line.gain == D("300000.00")
    assert line.line_21 == D("1800000.00")
    assert line.exempt == D("180000.00")
    assert line.result == D("120000.00")


def test_traces_the_plus_one_off_as_line_20_equal_to_line_4() -> None:
    (line, _) = capability().compute((properties(NO_PLUS_ONE),)).trace

    assert isinstance(line, PrincipalResidenceGainLine)
    assert line.plus_one == 0
    assert line.line_20 == line.designated == 3


def test_traces_line_24_floored_at_zero_with_line_18_and_line_23_unfloored() -> None:
    loss: Figures = (6, 0, 10, 0, "100000.00", "5000.00", "120000.00", 1)

    (line, total_line) = capability().compute((properties(loss),)).trace

    assert isinstance(line, PrincipalResidenceGainLine)
    assert line.gain == D("-25000.00")
    assert line.line_21 == D("-175000.00")
    assert line.exempt == D("-17500.00")
    assert line.result == D("0")
    assert not line.result.is_signed()
    assert isinstance(total_line, ItemsTotalLine)
    assert not total_line.total.is_signed()


def test_traces_line_24_floored_at_zero_when_the_exemption_exceeds_the_gain() -> None:
    designated_throughout: Figures = (10, 0, 10, 0, "400000.00", "5000.00", "95000.00", 1)

    (line, _) = capability().compute((properties(designated_throughout),)).trace

    assert isinstance(line, PrincipalResidenceGainLine)
    assert line.gain == D("300000.00")
    assert line.exempt == D("330000.00")
    assert line.result == D("0")
    assert not line.result.is_signed()


def test_traces_the_datasets_rounding_rule_and_the_rounded_exemption() -> None:
    eighth: Figures = (0, 0, 8, 0, "1.00", "0.00", "0.00", 1)

    (line, total_line) = capability().compute((properties(eighth),)).trace

    assert isinstance(line, PrincipalResidenceGainLine)
    assert line.rounding == CENT
    # Line 21 is exact; only line 23 is rounded.
    assert line.line_21 == D("1.00")
    assert line.exempt == D("0.13")
    assert line.result == D("0.87")
    assert total_line == ItemsTotalLine(PRINCIPAL_RESIDENCE_GAIN, ((1, D("0.87")),), D("0.87"))


def test_traces_the_rule_of_a_dataset_that_floors() -> None:
    third: Figures = (0, 0, 3, 0, "100000.00", "0.00", "0.00", 1)

    (line, _) = capability(rounding(DOLLAR_FLOOR)).compute((properties(third),)).trace

    assert isinstance(line, PrincipalResidenceGainLine)
    assert line.rounding == DOLLAR_FLOOR
    assert line.exempt == D("33333")
    assert line.result == D("66667")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((properties(EXAMPLE, NO_PLUS_ONE),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
    assert [line.amount for line in result.trace[:-1]] == [D("90000.00"), D("16000.00")]


def test_the_total_is_the_sum_of_its_items() -> None:
    *_, total_line = capability().compute((properties(EXAMPLE, NO_PLUS_ONE, BOTH_PERIODS),)).trace

    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == sum((amount for _, amount in total_line.items), D("0"))


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (properties(EXAMPLE, NO_PLUS_ONE),)

    assert wired.compute(given) == wired.compute(given)


# --- Part 2 and line 54: the lesser of line 53 and line 24 --------------------------------------
#
# Each property's Part 2 lines are worked in `principal_residence_figures` (the comments there hold
# the hand computation). Line 54 is line 53 when Part 2 applies and line 53 is less than line 24,
# else line 24; a property that does not use Part 2 gives line 24 whatever its Part 2 figures.


def test_a_property_that_does_not_use_part_2_gives_line_24_whatever_its_part_2_figures() -> None:
    # Gain 195,000.00 less the exemption 111,428.57 (line 24 = 83,571.43), with the figures of the
    # worked example but Part 2 not applying: line 54 is line 24.
    assert total(PART_2_NOT_APPLYING) == D("83571.43")


def test_part_2_gives_line_24_when_line_24_is_the_lesser() -> None:
    # Line 53 is 103,000.00 and line 24 is 83,571.43: line 54 = 83,571.43.
    assert total(PART_2_WORKED) == D("83571.43")


def test_part_2_gives_line_53_when_line_53_is_the_lesser() -> None:
    # Line 24 is 133,333.33 and line 53 is 16,000.00: line 54 = 16,000.00.
    assert total(PART_2_LESSER_IS_LINE_53) == D("16000.00")


def test_part_2_gives_line_53_for_a_post_1981_loss_that_leaves_a_net_gain() -> None:
    # Line 53 is 10,000.00 and line 24 is 16,666.67: line 54 = 10,000.00.
    assert total(PART_2_LOSS) == D("10000.00")


def test_part_2_with_every_year_after_1981_designated_takes_line_24() -> None:
    # Line 53 is 30,000.00 and line 24 is 8,333.33: line 54 = 8,333.33.
    assert total(PART_2_ALL_YEARS_AFTER_1981) == D("8333.33")


def test_part_2_with_every_year_before_1982_designated_takes_line_24() -> None:
    # Line 53 is 40,000.00 and line 24 is 20,000.00: line 54 = 20,000.00.
    assert total(PART_2_ALL_YEARS_BEFORE_1982) == D("20000.00")


def test_line_54_is_taken_per_property_before_the_total() -> None:
    # 83,571.43 (worked, line 24) + 10,000.00 (loss, line 53) + 90,000.00 (no Part 2, line 24).
    assert total(PART_2_WORKED, PART_2_LOSS, EXAMPLE) == D("183571.43")


def test_the_trace_records_part_2_applying_with_lines_53_and_24() -> None:
    (line,) = capability().compute((properties(PART_2_WORKED),)).trace[:1]

    assert line == PrincipalResidenceGainLine(
        output=PRINCIPAL_RESIDENCE_GAIN,
        position=1,
        years_designated_after_1981=6,
        years_designated_1972_to_1981=1,
        designated=7,
        years_owned_after_1981=10,
        years_owned_1972_to_1981=4,
        owned=14,
        plus_one=1,
        proceeds=D("300000.00"),
        adjusted_cost_base=D("100000.00"),
        outlays=D("5000.00"),
        gain=D("195000.00"),
        line_20=8,
        line_21=D("1560000.00"),
        rounding=CENT,
        exempt=D("111428.57"),
        part_2_applies=1,
        line_53=D("103000.00"),
        line_24=D("83571.43"),
        result=D("83571.43"),
    )


def test_part_2_refused_with_no_years_owned_as_part_1_is() -> None:
    with pytest.raises(ValidationError, match="the years owned \\(lines 5 and 6\\) are 0"):
        total(PART_2_NO_YEARS_OWNED)


# --- refusals: the flags and the years a filer cannot have -------------------------------------


@pytest.mark.parametrize("plus_one", [2, 9])
def test_a_plus_one_above_1_is_refused(plus_one: int) -> None:
    # The "plus one" is one year by law (the note of Part 1): 2 would add a year no one may claim.
    above_1: Figures = (*EXAMPLE[:7], plus_one)

    with pytest.raises(ValidationError, match=r"property 1.*plus one"):
        total(above_1)


def test_a_plus_one_above_1_on_the_second_property_names_it_as_property_2() -> None:
    above_1: Figures = (*EXAMPLE[:7], 2)

    with pytest.raises(ValidationError, match=r"property 2.*plus one"):
        total(EXAMPLE, above_1)


def test_a_part_2_flag_above_1_is_refused() -> None:
    # Part 2 applies when the flag is 1 and not otherwise; a 2 would be read as "does not apply".
    above_1: Part2Figures = (
        6,
        0,
        10,
        0,
        "400000.00",
        "5000.00",
        "95000.00",
        1,
        2,
        "0.00",
        "0.00",
        "0.00",
    )

    with pytest.raises(ValidationError, match=r"property 1.*Part 2"):
        total(above_1)


def test_years_designated_after_1981_above_years_owned_after_1981_is_refused() -> None:
    # Line 1 cannot exceed line 5: 12 years designated of 10 owned would give a gain of 0.
    above_owned: Figures = (12, 0, 10, 0, "400000.00", "5000.00", "95000.00", 1)

    with pytest.raises(ValidationError, match=r"property 1.*designated.*owned"):
        total(above_owned)


def test_years_designated_1972_to_1981_above_years_owned_1972_to_1981_is_refused() -> None:
    # Line 2 cannot exceed line 6.
    above_owned: Figures = (6, 3, 10, 2, "400000.00", "5000.00", "95000.00", 1)

    with pytest.raises(ValidationError, match=r"property 1.*designated.*owned"):
        total(above_owned)


def test_designated_after_1981_is_checked_against_owned_after_1981_alone() -> None:
    # The totals fit (7 designated of 16 owned), but line 1 is above line 5 alone.
    above_owned: Figures = (7, 0, 6, 10, "400000.00", "5000.00", "95000.00", 1)

    with pytest.raises(ValidationError, match=r"property 1.*designated.*owned"):
        total(above_owned)


def test_designated_1972_to_1981_is_checked_against_owned_1972_to_1981_alone() -> None:
    # The totals fit (11 designated of 16 owned), but line 2 is above line 6 alone.
    above_owned: Figures = (0, 11, 10, 6, "400000.00", "5000.00", "95000.00", 1)

    with pytest.raises(ValidationError, match=r"property 1.*designated.*owned"):
        total(above_owned)


def test_a_designated_year_above_its_owned_years_is_named_by_the_property_position() -> None:
    above_owned: Figures = (12, 0, 10, 0, "400000.00", "5000.00", "95000.00", 1)

    with pytest.raises(ValidationError, match=r"property 2.*designated.*owned"):
        total(EXAMPLE, above_owned)
