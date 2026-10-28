"""Unit tests for the RateByIncomeBand capability (`ca-on/rate_by_income_band`).

Schedule ON479-A (2025, 5006-TCA), line 7: "If your family adjusted income on line 5 is "0",
enter 75%. If not, enter the tax credit rate that applies to your family adjusted income from the
table below." Its slots: one parameter slot `table` (a `rate_table` dataset), one consumed slot
`income` (a `Decimal` kind) and one produced slot `output`, a kind whose values are `Rate`s. A
figure of exactly 0 gives the table's `rate_at_zero`; above 0 the rate is that of the last row
whose `more_than` the figure exceeds, so in an overlap (CRA's typo row) the later row wins. The
rate is a printed figure, never rounded. A negative figure is refused: line 5 cannot be negative.
It records one `RateByIncomeBandLine`.

The table, in `on479a_table.py`, is ON479-A's "Family adjusted income and Tax credit rate" table
copied row for row from `docs/cra-forms-2025/5006-tca-25e.txt`, the 9% row as printed ("more than
$132,000 but not more than $136,500: 9%", overlapping "more than $135,600 but not more than
$139,200: 7%"). The artifact kinds and dataset family are made up; the wiring comes later.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca_on.capabilities as ca_on_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import DomainError, InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rate_table import RATE_TABLE, RateTable
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.domain.trace import RateByIncomeBandLine
from tax_calculator.jurisdictions.ca_on.capabilities.rate_by_income_band import RateByIncomeBand
from tests.jurisdictions.ca_on.capabilities.on479a_table import (
    FAMILY_INCOME,
    ON479A_ROWS,
    form_row,
    table,
)

D = Decimal

CARE_RATE = ArtifactKind("ex/care_rate", Rate)


def capability(table_data: ParameterDataset[RateTable] | None = None) -> RateByIncomeBand:
    """By default ON479-A's table, read for the made-up family income."""
    return RateByIncomeBand(table_data or table(), FAMILY_INCOME, CARE_RATE)


def compute(wired: RateByIncomeBand, income: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(FAMILY_INCOME, D(income)),)).outputs
    return output


def rate_for(income: str, wired: RateByIncomeBand | None = None) -> Decimal:
    value = compute(wired or capability(), income).value
    assert isinstance(value, Rate)
    return value.value


def test_is_registered_as_ca_on_rate_by_income_band() -> None:
    assert CapabilityRegistry.shared().get("ca-on/rate_by_income_band") is RateByIncomeBand


def test_is_exported_from_the_ca_on_capabilities_package() -> None:
    assert "rate_by_income_band" in ca_on_capabilities.__all__
    assert ca_on_capabilities.rate_by_income_band.RateByIncomeBand is RateByIncomeBand


def test_its_package_declares_the_ca_on_namespace() -> None:
    assert ca_on_capabilities.NAMESPACE == "ca-on"
    assert ca_on_capabilities.__all__[0] == "NAMESPACE"


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({FAMILY_INCOME})
    assert capability().produces == frozenset({CARE_RATE})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(RateByIncomeBand)
    assert "produces" not in vars(RateByIncomeBand)


def test_declares_its_slots() -> None:
    assert RateByIncomeBand.PARAMETERS == {"table": RATE_TABLE}
    assert RateByIncomeBand.PARAMETERS["table"] is RATE_TABLE
    assert RateByIncomeBand.CONSUMES == {"income": Decimal}
    assert RateByIncomeBand.PRODUCES == {"output": Rate}
    assert not RateByIncomeBand.is_list_slot("income")


def test_its_slots_are_read_only() -> None:
    for slots in (
        RateByIncomeBand.PARAMETERS,
        RateByIncomeBand.CONSUMES,
        RateByIncomeBand.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(RateByIncomeBand.PARAMETERS, Mapping[str, ParameterKind[RateTable]])
    assert_type(RateByIncomeBand.CONSUMES, Mapping[str, type])
    assert_type(RateByIncomeBand.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        RateByIncomeBand.PARAMETERS,
        RateByIncomeBand.CONSUMES,
        RateByIncomeBand.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = RateByIncomeBand(table=table(), income=FAMILY_INCOME, output=CARE_RATE)

    assert compute(wired, "50000") == Artifact(CARE_RATE, Rate(D("0.55")))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        RateByIncomeBand(table(), FAMILY_INCOME, CARE_RATE, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_a_money_kind_as_its_output() -> None:
    money = ArtifactKind("ex/care_rate_as_money", Decimal)

    with pytest.raises(InvalidCapabilityError, match="RateByIncomeBand.*'output'"):
        RateByIncomeBand(table(), FAMILY_INCOME, money)  # type: ignore[arg-type]


def test_rejects_a_rate_kind_as_its_income() -> None:
    other_rate = ArtifactKind("ex/other_rate", Rate)

    with pytest.raises(InvalidCapabilityError, match="RateByIncomeBand.*'income'"):
        RateByIncomeBand(table(), other_rate, CARE_RATE)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_income() -> None:
    with pytest.raises(InvalidCapabilityError, match="RateByIncomeBand.*'income'"):
        RateByIncomeBand(table(), (FAMILY_INCOME,), CARE_RATE)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[RateTable]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        RateByIncomeBand(rate, FAMILY_INCOME, CARE_RATE)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(RateByIncomeBand, "__type_params__", ())
    assert not getattr(RateByIncomeBand, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("income", "rate"),
    [
        pytest.param("10000", "0.75", id="10000-is-75"),
        pytest.param("45500", "0.55", id="45500-is-55"),
        pytest.param("50000", "0.55", id="50000-is-55"),
        pytest.param("150001", "0", id="150001-is-0"),
        pytest.param("20000", "0.75", id="edge-20000-is-75"),
        pytest.param("20001", "0.73", id="edge-20001-is-73"),
        pytest.param("40000", "0.59", id="edge-40000-is-59"),
        pytest.param("60000", "0.51", id="edge-60000-is-51"),
    ],
)
def test_gives_the_forms_rate(income: str, rate: str) -> None:
    output = compute(capability(), income)

    assert output == Artifact(CARE_RATE, Rate(D(rate)))
    assert type(output.value) is Rate


# --- computing: the whole table ---------------------------------------------------------------


def test_a_zero_income_gets_the_rate_at_zero() -> None:
    # "If your family adjusted income on line 5 is "0", enter 75%."
    assert rate_for("0") == D("0.75")
    assert rate_for("0.00") == D("0.75")
    assert rate_for("-0") == D("0.75")


def test_the_rate_at_zero_comes_from_the_table_not_its_first_row() -> None:
    made_up = RateTable(
        Rate(D("0.5")), (form_row("0", "1000", "0.3"), form_row("1000", None, "0.1"))
    )
    wired = capability(table(made_up))

    assert rate_for("0", wired) == D("0.5")
    assert rate_for("0.01", wired) == D("0.3")


def test_a_cent_of_income_falls_in_the_first_row() -> None:
    assert rate_for("0.01") == D("0.75")


@pytest.mark.parametrize(
    ("more_than", "not_more_than", "rate"),
    # The typo row, whose printed upper bound falls inside the next row, has its own test below.
    [printed for printed in ON479A_ROWS if printed[1] not in (None, "136500")],
)
def test_each_bounded_row_holds_from_just_above_its_lower_to_its_upper(
    more_than: str, not_more_than: str, rate: str
) -> None:
    assert rate_for(str(D(more_than) + D("0.01"))) == D(rate)
    assert rate_for(not_more_than) == D(rate)


@pytest.mark.parametrize(
    ("not_more_than", "next_rate"),
    [
        (below[1], above[2])
        for below, above in zip(ON479A_ROWS, ON479A_ROWS[1:], strict=False)
        if below[1] != "136500"
    ],
)
def test_just_above_each_rows_upper_bound_is_the_next_rows_rate(
    not_more_than: str, next_rate: str
) -> None:
    assert rate_for(str(D(not_more_than) + D("0.01"))) == D(next_rate)


@pytest.mark.parametrize("income", ["150000.01", "200000", "1000000000"])
def test_above_the_last_bound_the_rate_is_zero(income: str) -> None:
    assert rate_for(income) == D("0")


def test_the_last_bounded_row_ends_at_its_upper_bound() -> None:
    assert rate_for("150000") == D("0.01")


@pytest.mark.parametrize(
    ("income", "rate"),
    [
        pytest.param("132000", "0.11", id="end-of-11"),
        pytest.param("132000.01", "0.09", id="start-of-9"),
        pytest.param("135600", "0.09", id="9-ends-at-135600"),
        pytest.param("135600.01", "0.07", id="overlap-starts-7"),
        pytest.param("136000", "0.07", id="inside-overlap-7"),
        pytest.param("136500", "0.07", id="printed-end-of-9-is-7"),
        pytest.param("136500.01", "0.07", id="after-printed-end-7"),
        pytest.param("139200", "0.07", id="end-of-7"),
    ],
)
def test_the_typo_row_ends_where_the_next_row_starts(income: str, rate: str) -> None:
    # The later row wins in the overlap, matching "the 9% row ends at 135,600".
    assert rate_for(income) == D(rate)


def test_keeps_the_rate_exactly_as_the_table_gives_it() -> None:
    made_up = RateTable(
        Rate(D("0.750")), (form_row("0", "1000", "0.30"), form_row("1000", None, "0.0"))
    )
    wired = capability(table(made_up))

    assert str(rate_for("500", wired)) == "0.30"
    assert str(rate_for("5000", wired)) == "0.0"
    assert str(rate_for("0", wired)) == "0.750"


def test_a_single_unbounded_row_gives_its_rate_to_every_positive_figure() -> None:
    wired = capability(table(RateTable(Rate(D("0.6")), (form_row("0", None, "0.4"),))))

    assert rate_for("0.01", wired) == D("0.4")
    assert rate_for("1000000", wired) == D("0.4")
    assert rate_for("0", wired) == D("0.6")


@pytest.mark.parametrize("income", ["-0.01", "-1", "-50000"])
def test_a_negative_income_is_refused(income: str) -> None:
    with pytest.raises(DomainError, match="negative"):
        capability().compute((Artifact(FAMILY_INCOME, D(income)),))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(FAMILY_INCOME, D("50000"))))

    assert result.outputs == (Artifact(CARE_RATE, Rate(D("0.55"))),)


def test_a_missing_income_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="family_adjusted_income"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_rate_by_income_band_line() -> None:
    trace = capability().compute((Artifact(FAMILY_INCOME, D("45500")),)).trace

    assert trace == (
        RateByIncomeBandLine(
            output=CARE_RATE,
            income=FAMILY_INCOME,
            income_amount=D("45500"),
            row=form_row("45000", "50000", "0.55"),
            rate=Rate(D("0.55")),
        ),
    )


def test_traces_the_unbounded_last_row() -> None:
    (line,) = capability().compute((Artifact(FAMILY_INCOME, D("150001")),)).trace

    assert line == RateByIncomeBandLine(
        CARE_RATE, FAMILY_INCOME, D("150001"), form_row("150000", None, "0"), Rate(D("0"))
    )


def test_traces_no_row_for_a_zero_income() -> None:
    (line,) = capability().compute((Artifact(FAMILY_INCOME, D("0")),)).trace

    assert line == RateByIncomeBandLine(CARE_RATE, FAMILY_INCOME, D("0"), None, Rate(D("0.75")))


def test_traces_the_later_row_in_the_overlap() -> None:
    (line,) = capability().compute((Artifact(FAMILY_INCOME, D("136000")),)).trace

    assert isinstance(line, RateByIncomeBandLine)
    assert line.row == form_row("135600", "139200", "0.07")


def test_trace_amount_is_the_rates_value() -> None:
    trace = capability().compute((Artifact(FAMILY_INCOME, D("50000")),)).trace

    assert [line.amount for line in trace] == [D("0.55")]


def test_trace_rate_is_the_output() -> None:
    result = capability().compute((Artifact(FAMILY_INCOME, D("20001")),))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, RateByIncomeBandLine)
    assert line.rate == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(FAMILY_INCOME, D("50000")),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
