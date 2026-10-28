"""Unit tests for the capabilities of Schedule 12, the multigenerational home renovation tax credit
(T1 line 45355): the unregistered base `HomeRenovationRows` and its three registered subclasses,
`HomeRenovationLine3`, `HomeRenovationLine6` and `HomeRenovationLine7`.

Schedule 12, "Step 1", completed "for each qualifying renovation": line 3 "Line 1 minus line 2
(maximum $50,000 per qualifying renovation)"; line 4 "Maximum amount per qualifying renovation
50,000.00", the yearly `maximum` dataset; line 6 "Line 4 minus line 5"; line 7 "Enter whichever is
less: amount from line 3 or line 6. Your qualifying expenditures for the qualifying renovation".
Step 2, line 8 (line 45354) "Add the amounts from line 7 for each qualifying renovation. Your total
qualifying expenditures" is the total of line 7, and line 10 (line 45355) is the rate applied to it,
which is `core/apply_rate` and is tested with the 2025 dataset in `test_home_renovation_2025.py`.

Slots of every subclass: one parameter `maximum` (an `amount` dataset), one consumed `renovations`
(a record list with one record per qualifying renovation, holding lines 1, 2 and 5) and one produced
`output`. Each renovation is worked on its own, never pooled: the output is the total of the
renovations' figures, 0 when there are none. Line 3 caps each renovation at the `maximum`, line 6 is
the `maximum` less the amount claimed by other eligible individuals, and line 7 is the lesser of
those two. The subclass records one trace line per renovation, by position from 1, then an
`ItemsTotalLine`. The form does not say whether line 3 or line 6 is floored at 0, so no test pins a
negative figure.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, ValidationError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.home_renovation_line_3 import HomeRenovationLine3
from tax_calculator.jurisdictions.ca.capabilities.home_renovation_line_6 import HomeRenovationLine6
from tax_calculator.jurisdictions.ca.capabilities.home_renovation_line_7 import HomeRenovationLine7
from tax_calculator.jurisdictions.ca.capabilities.home_renovation_rows import HomeRenovationRows
from tax_calculator.jurisdictions.ca.catalog import (
    HOME_RENOVATION_CLAIMED_BY_OTHERS,
    HOME_RENOVATION_EXPENDITURES,
    HOME_RENOVATION_LINE_3,
    HOME_RENOVATION_LINE_6,
    HOME_RENOVATION_LINE_8,
    HOME_RENOVATION_REIMBURSED,
    HOME_RENOVATIONS,
)
from tax_calculator.jurisdictions.ca.trace import RenovationLine3, RenovationLine6, RenovationLine7

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
SCHEDULE_12 = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s12/5000-s12-25e.txt",)

# (expenditures, reimbursed, claimed by other eligible individuals), as lines 1, 2 and 5.
ONE = ("60000", "0", "0")
TWO = ("30000", "5000", "10000")
# A record whose line 2 (reimbursed) is above its line 1 (expenditures): 50,000 on 40,000.
REIMBURSED_ABOVE_EXPENDITURES = ("40000", "50000", "0")
# A record whose line 5 (claimed by others) is above the 50,000 maximum: 60,000.
CLAIMED_ABOVE_MAXIMUM = ("40000", "0", "60000")

# (capability class, its output kind, the trace line class it records)
LINES: list[tuple[type[HomeRenovationRows], ArtifactKind[Decimal], type]] = [
    (HomeRenovationLine3, HOME_RENOVATION_LINE_3, RenovationLine3),
    (HomeRenovationLine6, HOME_RENOVATION_LINE_6, RenovationLine6),
    (HomeRenovationLine7, HOME_RENOVATION_LINE_8, RenovationLine7),
]
CLASSES = [cls for cls, _, _ in LINES]
IDS = ["line_3", "line_6", "line_7"]
OUTPUT = {cls: output for cls, output, _ in LINES}
TRACE = {cls: trace for cls, _, trace in LINES}


def maximum(value: str = "50000.00") -> ParameterDataset[Amount]:
    """The 2025 `maximum` dataset, line 4 of Schedule 12: 50,000.00 by default."""
    return ParameterDataset(
        "ca/home_renovation_maximum", 2025, AMOUNT, Amount(D(value)), CENT, SCHEDULE_12
    )


def capability(cls: type[HomeRenovationRows], value: str = "50000.00") -> HomeRenovationRows:
    return cls(maximum(value), HOME_RENOVATIONS, OUTPUT[cls])


def renovations(*records: tuple[str, str, str]) -> Artifact[Any]:
    """An `ca/home_renovations` artifact of one record per renovation, in the order given."""
    rows = [
        {
            HOME_RENOVATION_EXPENDITURES: D(expenditures),
            HOME_RENOVATION_REIMBURSED: D(reimbursed),
            HOME_RENOVATION_CLAIMED_BY_OTHERS: D(claimed),
        }
        for expenditures, reimbursed, claimed in records
    ]
    return Artifact(HOME_RENOVATIONS, RecordList(HOME_RENOVATIONS.fields, rows))


def total(cls: type[HomeRenovationRows], *records: tuple[str, str, str]) -> Decimal:
    (output,) = capability(cls).compute((renovations(*records),)).outputs
    value = output.value
    assert isinstance(value, Decimal)
    return value


REGISTERED_AS = {
    HomeRenovationLine3: "ca/home_renovation_line_3",
    HomeRenovationLine6: "ca/home_renovation_line_6",
    HomeRenovationLine7: "ca/home_renovation_line_7",
}


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_is_registered_under_its_own_identifier(cls: type[HomeRenovationRows]) -> None:
    assert CapabilityRegistry.shared().get(REGISTERED_AS[cls]) is cls


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_is_exported_from_the_ca_capabilities_package(cls: type[HomeRenovationRows]) -> None:
    module = REGISTERED_AS[cls].rsplit("/", 1)[1]

    assert ca_capabilities.NAMESPACE == "ca"
    assert module in ca_capabilities.__all__
    assert getattr(ca_capabilities, module).__dict__[cls.__name__] is cls


def test_the_base_is_not_exported_or_registered() -> None:
    assert "home_renovation_rows" not in ca_capabilities.__all__
    assert (
        HomeRenovationRows.__module__
        == "tax_calculator.jurisdictions.ca.capabilities.home_renovation_rows"
    )


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_declares_its_contract(cls: type[HomeRenovationRows]) -> None:
    wired = capability(cls)

    assert wired.consumes == frozenset({HOME_RENOVATIONS})
    assert wired.produces == frozenset({OUTPUT[cls]})


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_declares_its_slots(cls: type[HomeRenovationRows]) -> None:
    assert cls.PARAMETERS == {"maximum": AMOUNT}
    assert cls.CONSUMES == {"renovations": RecordList}
    assert cls.PRODUCES == {"output": Decimal}
    assert not cls.is_list_slot("renovations")


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_its_slots_are_read_only(cls: type[HomeRenovationRows]) -> None:
    for slots in (cls.PARAMETERS, cls.CONSUMES, cls.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(HomeRenovationLine3.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(HomeRenovationLine3.CONSUMES, Mapping[str, type])
    assert_type(HomeRenovationLine3.PRODUCES, Mapping[str, type])


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_is_built_from_its_slot_names_as_keywords(cls: type[HomeRenovationRows]) -> None:
    wired = cls(
        maximum=maximum(),
        renovations=HOME_RENOVATIONS,
        output=OUTPUT[cls],
    )

    (output,) = wired.compute((renovations(ONE),)).outputs
    assert output == Artifact(OUTPUT[cls], D("50000"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        HomeRenovationLine3(  # type: ignore[call-arg]
            maximum(), HOME_RENOVATIONS, HOME_RENOVATION_LINE_3, CENT
        )


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_rejects_a_money_kind_for_its_renovations(cls: type[HomeRenovationRows]) -> None:
    with pytest.raises(InvalidCapabilityError, match=f"{cls.__name__}.*'renovations'"):
        cls(maximum(), HOME_RENOVATION_EXPENDITURES, OUTPUT[cls])  # type: ignore[arg-type]


def test_the_lines_are_capabilities_built_on_the_base() -> None:
    assert issubclass(HomeRenovationRows, Capability)
    assert issubclass(HomeRenovationLine3, HomeRenovationRows)


@pytest.mark.parametrize(
    ("cls", "records", "expected"),
    [
        (HomeRenovationLine3, (), D("0")),
        (HomeRenovationLine3, (ONE,), D("50000")),
        (HomeRenovationLine3, (TWO,), D("25000")),
        (HomeRenovationLine3, (ONE, TWO), D("75000")),
        (HomeRenovationLine6, (), D("0")),
        (HomeRenovationLine6, (ONE,), D("50000")),
        (HomeRenovationLine6, (TWO,), D("40000")),
        (HomeRenovationLine6, (ONE, TWO), D("90000")),
        (HomeRenovationLine7, (), D("0")),
        (HomeRenovationLine7, (ONE,), D("50000")),
        (HomeRenovationLine7, (TWO,), D("25000")),
        (HomeRenovationLine7, (ONE, TWO), D("75000")),
    ],
    ids=[
        "line_3_no_renovations",
        "line_3_one_at_the_maximum",
        "line_3_one_reimbursed_and_claimed",
        "line_3_two_renovations_summed",
        "line_6_no_renovations",
        "line_6_one_at_the_maximum",
        "line_6_one_claimed_by_others",
        "line_6_two_renovations_summed",
        "line_7_no_renovations",
        "line_7_one_at_the_maximum",
        "line_7_one_reimbursed_and_claimed",
        "line_7_two_renovations_summed",
    ],
)
def test_the_output_is_the_total_over_the_renovations(
    cls: type[HomeRenovationRows],
    records: tuple[tuple[str, str, str], ...],
    expected: Decimal,
) -> None:
    assert total(cls, *records) == expected


def test_line_7_is_the_lesser_of_line_3_and_line_6_for_each_renovation() -> None:
    # Two renovations: line 3 is 50,000 and 25,000, line 6 is 50,000 and 40,000, so line 7 is
    # 50,000 and 25,000, and its total is 75,000 (line 8).
    assert total(HomeRenovationLine3, ONE, TWO) == D("75000")
    assert total(HomeRenovationLine6, ONE, TWO) == D("90000")
    assert total(HomeRenovationLine7, ONE, TWO) == D("75000")


def test_the_maximum_comes_from_the_dataset_not_from_the_code() -> None:
    # A made-up 40,000 maximum in place of line 4's 50,000.00: line 3 caps the first renovation at
    # 40,000, line 6 is 40,000 less the 10,000 claimed by others for the second, and line 7 is the
    # lesser of 40,000 and 40,000 for the first.
    assert capability(HomeRenovationLine3, "40000").compute((renovations(ONE),)).outputs == (
        Artifact(HOME_RENOVATION_LINE_3, D("40000")),
    )
    assert capability(HomeRenovationLine6, "40000").compute((renovations(TWO),)).outputs == (
        Artifact(HOME_RENOVATION_LINE_6, D("30000")),
    )
    assert capability(HomeRenovationLine7, "40000").compute((renovations(ONE),)).outputs == (
        Artifact(HOME_RENOVATION_LINE_8, D("40000")),
    )


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_an_empty_list_records_only_the_total_of_no_items(cls: type[HomeRenovationRows]) -> None:
    trace = capability(cls).compute((renovations(),)).trace

    assert trace == (ItemsTotalLine(OUTPUT[cls], (), D("0")),)


def test_line_3_records_one_line_per_renovation_by_position_then_the_total() -> None:
    result = capability(HomeRenovationLine3).compute((renovations(ONE, TWO),))

    out = HOME_RENOVATION_LINE_3
    assert result.trace == (
        RenovationLine3(out, 1, D("60000"), D("0"), Amount(D("50000")), D("50000")),
        RenovationLine3(out, 2, D("30000"), D("5000"), Amount(D("50000")), D("25000")),
        ItemsTotalLine(out, ((1, D("50000")), (2, D("25000"))), D("75000")),
    )


def test_line_6_records_one_line_per_renovation_by_position_then_the_total() -> None:
    result = capability(HomeRenovationLine6).compute((renovations(ONE, TWO),))

    out = HOME_RENOVATION_LINE_6
    assert result.trace == (
        RenovationLine6(out, 1, Amount(D("50000")), D("0"), D("50000")),
        RenovationLine6(out, 2, Amount(D("50000")), D("10000"), D("40000")),
        ItemsTotalLine(out, ((1, D("50000")), (2, D("40000"))), D("90000")),
    )


def test_line_7_records_one_line_per_renovation_by_position_then_the_total() -> None:
    result = capability(HomeRenovationLine7).compute((renovations(ONE, TWO),))

    out = HOME_RENOVATION_LINE_8
    assert result.trace == (
        RenovationLine7(out, 1, D("50000"), D("50000"), D("50000")),
        RenovationLine7(out, 2, D("25000"), D("40000"), D("25000")),
        ItemsTotalLine(out, ((1, D("50000")), (2, D("25000"))), D("75000")),
    )


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_reimbursed_above_expenditures_is_refused(cls: type[HomeRenovationRows]) -> None:
    with pytest.raises(ValidationError, match=r"renovation 1.*line 2.*line 1"):
        total(cls, REIMBURSED_ABOVE_EXPENDITURES)


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_claimed_above_the_maximum_is_refused(cls: type[HomeRenovationRows]) -> None:
    with pytest.raises(ValidationError, match=r"renovation 1.*line 5.*line 4"):
        total(cls, CLAIMED_ABOVE_MAXIMUM)


@pytest.mark.parametrize("cls", CLASSES, ids=IDS)
def test_a_refused_renovation_after_a_good_one_is_named_by_its_position(
    cls: type[HomeRenovationRows],
) -> None:
    with pytest.raises(ValidationError, match=r"renovation 2.*line 2.*line 1"):
        total(cls, ONE, REIMBURSED_ABOVE_EXPENDITURES)

    with pytest.raises(ValidationError, match=r"renovation 2.*line 5.*line 4"):
        total(cls, ONE, CLAIMED_ABOVE_MAXIMUM)


@pytest.mark.parametrize(
    ("cls", "expected"),
    [
        (HomeRenovationLine3, D("0")),
        (HomeRenovationLine6, D("50000")),
        (HomeRenovationLine7, D("0")),
    ],
    ids=IDS,
)
def test_reimbursed_equal_to_expenditures_is_accepted(
    cls: type[HomeRenovationRows], expected: Decimal
) -> None:
    assert total(cls, ("40000", "40000", "0")) == expected


@pytest.mark.parametrize(
    ("cls", "expected"),
    [
        (HomeRenovationLine3, D("50000")),
        (HomeRenovationLine6, D("0")),
        (HomeRenovationLine7, D("0")),
    ],
    ids=IDS,
)
def test_claimed_equal_to_the_maximum_is_accepted(
    cls: type[HomeRenovationRows], expected: Decimal
) -> None:
    assert total(cls, ("60000", "0", "50000")) == expected
