"""Unit tests for the CoopEducationCredit capability (`ca-on/coop_education_credit`).

Worksheet ON479, "Line 20 - Ontario co-operative education tax credit", is completed for each
qualifying work placement: line 1 is the eligible expenditures (line A) "multiplied by 25%"; line
3 is amount A multiplied by the 5% of line 2; line 12 is line 3 multiplied by line 11; line 13 is
"Line 1 plus line 12 (maximum $3,000 per student)"; "Enter the total amount claimed for all
qualifying work placements on line 20". The capability consumes the record list of the placements
and line 11 (the share of the 5% that remains) and produces the total of every placement's line
13, which is ON479 line 20 and line 63300.

Its parameter slots are two `rate` datasets (`expenditure_rate`, `supplement_rate`) and an `amount`
dataset (`maximum`). Lines 1, 3 and 12 are exact: the rate datasets round nothing, whatever their
`rounding` says. Line 13 is the lesser of line 1 plus line 12 and the maximum, rounded with the
maximum dataset's rule, like `core/capped_amount`; the total adds those rounded lines. It records
one `PlacementCreditLine` per placement, naming it by its position from 1, then one
`ItemsTotalLine` for the total.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType

import pytest

import tax_engine.jurisdictions.ca_on
import tax_engine.jurisdictions.ca_on.capabilities
import tax_engine.registrations
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    DuplicateArtifactError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca_on.capabilities.coop_education_credit import (
    CoopEducationCredit,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    COOP_EDUCATION_CREDIT,
    COOP_EDUCATION_PLACEMENT_EXPENDITURES,
    COOP_EDUCATION_PLACEMENTS,
    COOP_EDUCATION_REMAINING_SHARE,
)
from tax_engine.jurisdictions.ca_on.trace import PlacementCreditLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
SOURCES = ("https://example.org/worksheet",)


def rate(value: str, rounding: RoundingRule = CENT) -> ParameterDataset[Rate]:
    """A made-up `rate` dataset; by default it carries the half-up cent rule every dataset does."""
    return ParameterDataset("ex/some_rate", 2025, RATE, Rate(D(value)), rounding, SOURCES)


def maximum(value: str = "3000", rounding: RoundingRule = CENT) -> ParameterDataset[Amount]:
    return ParameterDataset("ex/some_maximum", 2025, AMOUNT, Amount(D(value)), rounding, SOURCES)


def capability(
    expenditure_rate: ParameterDataset[Rate] | None = None,
    supplement_rate: ParameterDataset[Rate] | None = None,
    cap: ParameterDataset[Amount] | None = None,
) -> CoopEducationCredit:
    """By default the worksheet's 25%, 5% and $3,000."""
    return CoopEducationCredit(
        expenditure_rate=expenditure_rate or rate("0.25"),
        supplement_rate=supplement_rate or rate("0.05"),
        maximum=cap or maximum(),
        placements=COOP_EDUCATION_PLACEMENTS,
        remaining_share=COOP_EDUCATION_REMAINING_SHARE,
        output=COOP_EDUCATION_CREDIT,
    )


def placements(*expenditures: str) -> Artifact[RecordList]:
    """An `ca-on/coop_education_placements` artifact of one record per amount, in order."""
    records = [{COOP_EDUCATION_PLACEMENT_EXPENDITURES: D(amount)} for amount in expenditures]
    return Artifact(
        COOP_EDUCATION_PLACEMENTS, RecordList(COOP_EDUCATION_PLACEMENTS.fields, records)
    )


def share(value: str) -> Artifact[Decimal]:
    return Artifact(COOP_EDUCATION_REMAINING_SHARE, D(value))


def credit_of(
    remaining_share: str, *expenditures: str, wired: CoopEducationCredit | None = None
) -> Decimal:
    result = (wired or capability()).compute((placements(*expenditures), share(remaining_share)))
    (artifact,) = result.outputs
    assert artifact.kind == COOP_EDUCATION_CREDIT
    value = artifact.value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_on_coop_education_credit() -> None:
    assert tax_engine.registrations.CORE_PACKAGES  # importing registrations imports the packages

    registered = CapabilityRegistry.shared().get("ca-on/coop_education_credit")

    assert registered is CoopEducationCredit


def test_its_package_declares_the_ca_on_namespace_and_exports_the_module() -> None:
    package = tax_engine.jurisdictions.ca_on.capabilities

    assert package.NAMESPACE == tax_engine.jurisdictions.ca_on.NAMESPACE == "ca-on"
    assert "coop_education_credit" in package.__all__
    assert package.coop_education_credit.CoopEducationCredit is CoopEducationCredit


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset(
        {COOP_EDUCATION_PLACEMENTS, COOP_EDUCATION_REMAINING_SHARE}
    )
    assert capability().produces == frozenset({COOP_EDUCATION_CREDIT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CoopEducationCredit)
    assert "produces" not in vars(CoopEducationCredit)


def test_declares_its_slots() -> None:
    assert CoopEducationCredit.PARAMETERS == {
        "expenditure_rate": RATE,
        "supplement_rate": RATE,
        "maximum": AMOUNT,
    }
    assert CoopEducationCredit.PARAMETERS["expenditure_rate"] is RATE
    assert CoopEducationCredit.PARAMETERS["supplement_rate"] is RATE
    assert CoopEducationCredit.PARAMETERS["maximum"] is AMOUNT
    assert CoopEducationCredit.CONSUMES == {"placements": RecordList, "remaining_share": Decimal}
    assert CoopEducationCredit.PRODUCES == {"output": Decimal}
    assert not CoopEducationCredit.is_list_slot("placements")
    assert not CoopEducationCredit.is_list_slot("remaining_share")


def test_its_slots_are_read_only() -> None:
    for slots in (
        CoopEducationCredit.PARAMETERS,
        CoopEducationCredit.CONSUMES,
        CoopEducationCredit.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)
        assert isinstance(slots, Mapping)


def test_rejects_a_money_kind_for_its_placements() -> None:
    other = ArtifactKind("ex/not_a_list", Decimal)

    with pytest.raises(InvalidCapabilityError, match="CoopEducationCredit.*'placements'"):
        CoopEducationCredit(
            expenditure_rate=rate("0.25"),
            supplement_rate=rate("0.05"),
            maximum=maximum(),
            placements=other,  # type: ignore[arg-type]
            remaining_share=COOP_EDUCATION_REMAINING_SHARE,
            output=COOP_EDUCATION_CREDIT,
        )


def test_rejects_a_record_list_kind_for_its_remaining_share() -> None:
    with pytest.raises(InvalidCapabilityError, match="CoopEducationCredit.*'remaining_share'"):
        CoopEducationCredit(
            expenditure_rate=rate("0.25"),
            supplement_rate=rate("0.05"),
            maximum=maximum(),
            placements=COOP_EDUCATION_PLACEMENTS,
            remaining_share=COOP_EDUCATION_PLACEMENTS,  # type: ignore[arg-type]
            output=COOP_EDUCATION_CREDIT,
        )


def test_rejects_a_record_list_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CoopEducationCredit.*'output'"):
        CoopEducationCredit(
            expenditure_rate=rate("0.25"),
            supplement_rate=rate("0.05"),
            maximum=maximum(),
            placements=COOP_EDUCATION_PLACEMENTS,
            remaining_share=COOP_EDUCATION_REMAINING_SHARE,
            output=COOP_EDUCATION_PLACEMENTS,  # type: ignore[arg-type]
        )


# --- the worksheet's examples ---------------------------------------------------------------
#
# Two placements, eligible expenditures of 8,000 and 15,000. Line 11, the remaining share of the
# 5%, is 1.00 less line 8, (payroll - 400,000.00) / 200,000.00, not below zero.


def test_a_payroll_of_500000_gives_5200() -> None:
    # Line 8 = 0.5, line 11 = 0.5. Placement 1: 2,000 + 400 x 0.5 = 2,200. Placement 2:
    # 3,750 + 750 x 0.5 = 4,125, capped at 3,000. Line 20 = 5,200.
    assert credit_of("0.5", "8000", "15000") == D("5200")


def test_a_payroll_of_700000_gives_5000() -> None:
    # Line 8 = 1.5, line 11 = 0: 2,000 and 3,750 capped at 3,000.
    assert credit_of("0", "8000", "15000") == D("5000")


def test_a_payroll_of_300000_gives_5400() -> None:
    # Line 6 = 0, line 8 = 0, line 11 = 1: 2,000 + 400 = 2,400 and 3,750 + 750 = 4,500 capped.
    assert credit_of("1", "8000", "15000") == D("5400")


def test_a_payroll_of_400000_is_30_percent_of_each_placement() -> None:
    # Line 11 = 1.00 - 0 = 1: 25% + 5% = 30% of 8,000 and of 5,000.
    assert credit_of("1", "8000", "5000") == D("2400") + D("1500")


def test_a_payroll_of_600000_is_25_percent_of_each_placement() -> None:
    # Line 8 = 1, line 11 = 0: 25% of 8,000 and of 5,000.
    assert credit_of("0", "8000", "5000") == D("2000") + D("1250")


def test_the_remaining_share_is_exact_and_never_rounded() -> None:
    # A share of 0.375 (payroll 475,000): 400 x 0.375 = 150 exactly, so 2,150.
    assert credit_of("0.375", "8000") == D("2150")


def test_an_empty_list_gives_zero() -> None:
    assert credit_of("0.5") == D("0")
    assert credit_of("1") == D("0")
    assert credit_of("0") == D("0")


def test_one_placement_is_its_own_line_13() -> None:
    assert credit_of("0.5", "8000") == D("2200")


def test_a_placement_of_zero_adds_nothing() -> None:
    assert credit_of("0.5", "0", "8000") == D("2200")


def test_the_total_does_not_depend_on_the_order_of_the_placements() -> None:
    assert credit_of("0.5", "15000", "8000") == credit_of("0.5", "8000", "15000")


def test_equal_placements_are_each_counted() -> None:
    assert credit_of("0.5", "8000", "8000", "8000") == D("6600")


# --- the maximum of each student ------------------------------------------------------------


def test_the_maximum_applies_to_each_placement_and_not_to_the_total() -> None:
    # Three placements of 15,000 at 30% = 4,500 each, 3,000 each, not 3,000 in all.
    assert credit_of("1", "15000", "15000", "15000") == D("9000")


def test_a_placement_whose_line_13_is_exactly_the_maximum_is_not_reduced() -> None:
    # 10,000 x 30% = 3,000.00 exactly.
    assert credit_of("1", "10000") == D("3000")


def test_a_placement_a_little_below_the_maximum_keeps_its_line_13() -> None:
    # 9,999.90 x 30% = 2,999.97 exactly.
    assert credit_of("1", "9999.90") == D("2999.97")


def test_a_placement_a_little_above_the_maximum_is_capped() -> None:
    # 10,000.10 x 30% = 3,000.03.
    assert credit_of("1", "10000.10") == D("3000")


def test_a_huge_expenditure_is_capped_at_the_maximum() -> None:
    assert credit_of("0", "1000000000") == D("3000")


def test_the_maximum_is_the_datasets_amount() -> None:
    assert credit_of("1", "10000", wired=capability(cap=maximum("2500"))) == D("2500")
    assert credit_of("1", "10000", wired=capability(cap=maximum("4000"))) == D("3000")
    assert credit_of("1", "20000", wired=capability(cap=maximum("4000"))) == D("4000")


def test_the_rates_are_the_datasets_rates() -> None:
    wired = capability(expenditure_rate=rate("0.10"), supplement_rate=rate("0.02"))

    # 1,000 x 10% = 100 and 1,000 x 2% x 0.5 = 10.
    assert credit_of("0.5", "1000", wired=wired) == D("110")


# --- rounding -------------------------------------------------------------------------------


def test_lines_1_3_and_12_are_exact_and_only_line_13_is_rounded() -> None:
    # 0.14: line 1 = 0.035, line 3 = 0.007, line 12 = 0.007; line 13 = 0.042, half-up 0.04.
    # Rounding lines 1 and 12 on their own would give 0.04 + 0.01 = 0.05.
    assert credit_of("1", "0.14") == D("0.04")


def test_the_rate_datasets_rounding_rule_is_not_applied() -> None:
    exact = capability(
        expenditure_rate=rate("0.25", NO_ROUNDING), supplement_rate=rate("0.05", NO_ROUNDING)
    )
    cent = capability(expenditure_rate=rate("0.25", CENT), supplement_rate=rate("0.05", CENT))

    assert credit_of("1", "0.14", wired=cent) == credit_of("1", "0.14", wired=exact) == D("0.04")


@pytest.mark.parametrize(
    ("expenditure", "line_13"),
    [
        # 25% of 0.02 = 0.005, a tie, half-up to 0.01; of 0.01 = 0.0025, down to 0.00.
        ("0.02", "0.01"),
        ("0.01", "0.00"),
        # 25% of 0.06 = 0.015, a tie, up to 0.02; of 0.05 = 0.0125, down to 0.01.
        ("0.06", "0.02"),
        ("0.05", "0.01"),
        # 8,000.02 x 25% = 2,000.005, a tie, up to 2,000.01.
        ("8000.02", "2000.01"),
        ("8000.01", "2000.00"),
    ],
)
def test_line_13_is_rounded_half_up_to_the_cent_with_no_supplement(
    expenditure: str, line_13: str
) -> None:
    assert credit_of("0", expenditure) == D(line_13)


def test_each_placements_line_13_is_rounded_before_the_total_is_added() -> None:
    # Two placements of 0.10: line 1 is 0.025 each, 0.03 each half-up, and 0.06 in all. Rounding
    # their sum 0.05 once would give 0.05.
    assert credit_of("0", "0.10", "0.10") == D("0.06")


def test_line_13_is_rounded_with_the_maximum_datasets_rule() -> None:
    exact = capability(cap=maximum("3000", NO_ROUNDING))

    # With no rounding, 0.14 gives line 13 = 0.042 itself.
    assert credit_of("1", "0.14", wired=exact) == D("0.042")


def test_the_maximum_is_rounded_with_its_own_rule_when_it_applies() -> None:
    wired = capability(cap=maximum("3000.005", CENT))

    # The lesser is the maximum 3000.005, a tie, half-up to 3000.01.
    assert credit_of("1", "100000", wired=wired) == D("3000.01")


def test_produces_a_decimal_total_of_exact_cents() -> None:
    total = credit_of("0.5", "8000", "15000")

    assert type(total) is Decimal
    assert total == D("5200.00")


# --- the artifact and the trace -----------------------------------------------------------------


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute((placements("8000", "15000"), share("0.5")))

    assert result.outputs == (Artifact(COOP_EDUCATION_CREDIT, D("5200")),)


def credit_line(
    position: int, expenditure: str, line_1: str, line_3: str, line_12: str, line_13: str,
    share_amount: str = "0.5",
) -> PlacementCreditLine:  # fmt: skip
    return PlacementCreditLine(
        output=COOP_EDUCATION_CREDIT,
        position=position,
        field=COOP_EDUCATION_PLACEMENT_EXPENDITURES,
        expenditure=D(expenditure),
        line_1=D(line_1),
        line_3=D(line_3),
        line_12=D(line_12),
        line_13=D(line_13),
        remaining_share=COOP_EDUCATION_REMAINING_SHARE,
        remaining_share_amount=D(share_amount),
        expenditure_rate=Rate(D("0.25")),
        supplement_rate=Rate(D("0.05")),
        maximum=Amount(D("3000")),
        rounding=CENT,
    )


def test_records_one_trace_line_per_placement_in_order_then_the_total() -> None:
    result = capability().compute((placements("8000", "15000"), share("0.5")))

    assert result.trace == (
        credit_line(1, "8000", "2000", "400", "200", "2200"),
        credit_line(2, "15000", "3750", "750", "375", "3000"),
        ItemsTotalLine(
            output=COOP_EDUCATION_CREDIT,
            items=((1, D("2200")), (2, D("3000"))),
            total=D("5200"),
        ),
    )


def test_the_trace_shows_line_13_capped_and_lines_1_3_and_12_unrounded() -> None:
    result = capability().compute((placements("0.14", "20000"), share("1")))

    first, second, total = result.trace
    assert isinstance(first, PlacementCreditLine)
    assert isinstance(second, PlacementCreditLine)
    assert (first.line_1, first.line_3, first.line_12, first.line_13) == (
        D("0.035"),
        D("0.007"),
        D("0.007"),
        D("0.04"),
    )
    # 20,000: line 1 = 5,000, line 3 = 1,000, line 12 = 1,000, line 13 = 6,000 capped at 3,000.
    assert (second.line_1, second.line_3, second.line_12, second.line_13) == (
        D("5000"),
        D("1000"),
        D("1000"),
        D("3000"),
    )
    assert total == ItemsTotalLine(
        COOP_EDUCATION_CREDIT, ((1, D("0.04")), (2, D("3000"))), D("3000.04")
    )
    assert total.amount == D("3000.04")


def test_the_total_line_is_the_sum_of_the_items_line_13() -> None:
    result = capability().compute((placements("8000", "15000", "100"), share("0.5")))

    *items, total = result.trace
    assert all(isinstance(line, PlacementCreditLine) for line in items)
    assert isinstance(total, ItemsTotalLine)
    assert [line.line_13 for line in items if isinstance(line, PlacementCreditLine)] == [
        amount for _, amount in total.items
    ]
    assert sum((amount for _, amount in total.items), D(0)) == total.total


def test_records_only_the_total_line_for_an_empty_list() -> None:
    result = capability().compute((placements(), share("1.00")))

    assert result.trace == (ItemsTotalLine(COOP_EDUCATION_CREDIT, (), D("0")),)


def test_records_one_trace_line_per_placement_and_one_total_whatever_the_number() -> None:
    for amounts in ((), ("1",), ("1", "2"), ("1", "2", "3", "4")):
        trace = capability().compute((placements(*amounts), share("1"))).trace
        assert len(trace) == len(amounts) + 1
        assert [getattr(line, "position", None) for line in trace[:-1]] == list(
            range(1, len(amounts) + 1)
        )


def test_the_trace_keeps_the_callers_order_not_the_sorted_one() -> None:
    result = capability().compute((placements("15000", "8000"), share("0.5")))

    first, second, total = result.trace
    assert isinstance(first, PlacementCreditLine)
    assert isinstance(second, PlacementCreditLine)
    assert [first.expenditure, second.expenditure] == [D("15000"), D("8000")]
    assert isinstance(total, ItemsTotalLine)
    assert [position for position, _ in total.items] == [1, 2]


def test_each_item_line_carries_the_datasets_rates_and_maximum_and_the_maximums_rounding() -> None:
    wired = capability(
        expenditure_rate=rate("0.10", NO_ROUNDING),
        supplement_rate=rate("0.02", NO_ROUNDING),
        cap=maximum("2500", NO_ROUNDING),
    )

    line, _ = wired.compute((placements("1000"), share("0.5"))).trace
    assert isinstance(line, PlacementCreditLine)
    assert line.remaining_share == COOP_EDUCATION_REMAINING_SHARE
    assert line.remaining_share_amount == D("0.5")
    assert line.expenditure_rate == Rate(D("0.10"))
    assert line.supplement_rate == Rate(D("0.02"))
    assert line.maximum == Amount(D("2500"))
    assert line.rounding == NO_ROUNDING


def test_its_trace_reads_item_by_item_in_english() -> None:
    result = capability().compute((placements("8000", "15000"), share("0.5")))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "coop_education_credit: item 1 coop_education_placement_expenditures 8000: "
        "line 1 2000, line 3 400, line 12 200, line 13 2200 (half-up to 0.01)",
        "coop_education_credit: item 2 coop_education_placement_expenditures 15000: "
        "line 1 3750, line 3 750, line 12 375, line 13 3000 (half-up to 0.01)",
        "coop_education_credit: item 1 2200 + item 2 3000 = 5200",
    )


def test_its_trace_for_an_empty_list_says_no_items() -> None:
    result = capability().compute((placements(), share("1.00")))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "coop_education_credit: no items = 0",
    )


def test_its_trace_for_one_placement_with_a_full_share_reads_in_english() -> None:
    result = capability().compute((placements("8000"), share("1")))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "coop_education_credit: item 1 coop_education_placement_expenditures 8000: "
        "line 1 2000, line 3 400, line 12 400, line 13 2400 (half-up to 0.01)",
        "coop_education_credit: item 1 2400 = 2400",
    )


# --- the inputs --------------------------------------------------------------------------------


def test_needs_its_placements() -> None:
    with pytest.raises(MissingArtifactError, match="CoopEducationCredit.*placements"):
        capability().compute((share("1"),))


def test_needs_its_remaining_share() -> None:
    with pytest.raises(MissingArtifactError, match="CoopEducationCredit.*remaining_share"):
        capability().compute((placements("8000"),))


def test_refuses_two_values_for_the_remaining_share() -> None:
    with pytest.raises(DuplicateArtifactError, match="CoopEducationCredit"):
        capability().compute((placements("8000"), share("1"), share("0")))


def test_does_not_consume_anything_else() -> None:
    other = Artifact(ArtifactKind("ex/other", Decimal), D("1"))

    result = capability().compute((other, placements("8000"), share("1")))

    assert result.outputs == (Artifact(COOP_EDUCATION_CREDIT, D("2400")),)
