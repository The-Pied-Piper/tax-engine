"""Unit tests for ImmediateExpensingAgreedLimit (`ca/immediate_expensing_agreed_limit`):
the one immediate expensing limit of a person across the statements of Forms T776, T2125, T2042
and T2121.

Area A endnote 5 of each of the four forms: "The total immediate expensing amount for the tax year
(total of column 9) is limited to the lesser of: the immediate expensing limit, which is equal to
one of the following, whichever is applicable: $1.5 million, if you are not associated with any
other eligible person or partnership (EPOP) in the tax year; amount iii of Area G, if you are
associated with one or more EPOPs in the tax year; zero, if you are associated with one or more
EPOPs and an agreement ... was not filed with the minister in a prescribed form; any amount
allocated by the minister under subsection 1104(3.4) of the Regulations". Guides T4002 and T4036:
"The deduction is limited to $1.5 million per tax year". The forms are silent on a person who files
several statements; the Guides' "per tax year" is the only statement of the cross-statement rule,
and statements whose limits disagree are refused.

Its slots: eight consumed record lists, for each form its claim list (`rental_claims`,
`business_claims`, `farm_claims`, `fish_claims`: one record per statement holding the total of
column 9) and its limit list (`rental_limits`, `business_limits`, `farm_limits`, `fish_limits`: one
record per statement holding that statement's limit), each a list of one amount field, and one
produced slot `output`. The records of a claim list and a limit list pair by position. Only the
statements whose claim is above 0 are compared; every limit among them must be equal, and the
common value is the output, 0 when no statement claims anything. Two claiming statements with
different limits are refused (`ValidationError`), naming the first statement (the list kind and the
position from 1, with its limit) and the first statement that disagrees with it, the lists taken
in the order rental, business, farm, fish. It records one `ImmediateExpensingAgreedLimitLine`
listing the compared statements and the agreed limit.

Worked statements (made-up `ex/` kinds): a rental claiming 600000 and a shop claiming 500000, both
with the limit 1500000, agree on 1500000. A rental claiming 0 whose limit is 1500000 (no write-off
and no Area G filled in) beside a shop claiming 500000 under 900000 (associated at 60%) is not
compared: the agreed limit is 900000.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
    ValidationError,
)
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.immediate_expensing_agreed_limit import (
    ImmediateExpensingAgreedLimit,
)
from tax_calculator.jurisdictions.ca.trace import ImmediateExpensingAgreedLimitLine

D = Decimal

CLAIM = ArtifactKind("ex/statement_claim", Decimal, non_negative=True)
LIMIT = ArtifactKind("ex/statement_limit", Decimal, non_negative=True)
RENTAL_CLAIMS = RecordListKind("ex/rental_claims", fields=(CLAIM,))
RENTAL_LIMITS = RecordListKind("ex/rental_limits", fields=(LIMIT,))
BUSINESS_CLAIMS = RecordListKind("ex/business_claims", fields=(CLAIM,))
BUSINESS_LIMITS = RecordListKind("ex/business_limits", fields=(LIMIT,))
FARM_CLAIMS = RecordListKind("ex/farm_claims", fields=(CLAIM,))
FARM_LIMITS = RecordListKind("ex/farm_limits", fields=(LIMIT,))
FISH_CLAIMS = RecordListKind("ex/fish_claims", fields=(CLAIM,))
FISH_LIMITS = RecordListKind("ex/fish_limits", fields=(LIMIT,))
AGREED = ArtifactKind("ex/immediate_expensing_agreed_limit", Decimal, non_negative=True)

KINDS = (
    RENTAL_CLAIMS,
    RENTAL_LIMITS,
    BUSINESS_CLAIMS,
    BUSINESS_LIMITS,
    FARM_CLAIMS,
    FARM_LIMITS,
    FISH_CLAIMS,
    FISH_LIMITS,
)
FULL = "1500000"

type Statement = tuple[str, str]  # (claim, limit)


def capability() -> ImmediateExpensingAgreedLimit:
    return ImmediateExpensingAgreedLimit(*KINDS, AGREED)


def pair(
    claims_kind: RecordListKind, limits_kind: RecordListKind, statements: tuple[Statement, ...]
) -> tuple[Artifact[Any], Artifact[Any]]:
    claims = [{CLAIM: D(claim)} for claim, _limit in statements]
    limits = [{LIMIT: D(limit)} for _claim, limit in statements]
    return (
        Artifact(claims_kind, RecordList(claims_kind.fields, claims)),
        Artifact(limits_kind, RecordList(limits_kind.fields, limits)),
    )


def inputs(
    rental: tuple[Statement, ...] = (),
    business: tuple[Statement, ...] = (),
    farm: tuple[Statement, ...] = (),
    fish: tuple[Statement, ...] = (),
) -> tuple[Artifact[Any], ...]:
    return (
        *pair(RENTAL_CLAIMS, RENTAL_LIMITS, rental),
        *pair(BUSINESS_CLAIMS, BUSINESS_LIMITS, business),
        *pair(FARM_CLAIMS, FARM_LIMITS, farm),
        *pair(FISH_CLAIMS, FISH_LIMITS, fish),
    )


def agreed(**statements: tuple[Statement, ...]) -> Decimal:
    (output,) = capability().compute(inputs(**statements)).outputs
    return cast(Decimal, output.value)


def test_is_registered_as_ca_immediate_expensing_agreed_limit() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/immediate_expensing_agreed_limit")
        is ImmediateExpensingAgreedLimit
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "immediate_expensing_agreed_limit" in ca_capabilities.__all__
    assert (
        ca_capabilities.immediate_expensing_agreed_limit.ImmediateExpensingAgreedLimit
        is ImmediateExpensingAgreedLimit
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset(KINDS)
    assert capability().produces == frozenset({AGREED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ImmediateExpensingAgreedLimit)
    assert "produces" not in vars(ImmediateExpensingAgreedLimit)


def test_declares_its_slots() -> None:
    assert ImmediateExpensingAgreedLimit.CONSUMES == {
        "rental_claims": RecordList,
        "rental_limits": RecordList,
        "business_claims": RecordList,
        "business_limits": RecordList,
        "farm_claims": RecordList,
        "farm_limits": RecordList,
        "fish_claims": RecordList,
        "fish_limits": RecordList,
    }
    assert ImmediateExpensingAgreedLimit.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for each in (ImmediateExpensingAgreedLimit.CONSUMES, ImmediateExpensingAgreedLimit.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ImmediateExpensingAgreedLimit.CONSUMES, Mapping[str, type])
    assert_type(ImmediateExpensingAgreedLimit.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ImmediateExpensingAgreedLimit(
        rental_claims=RENTAL_CLAIMS,
        rental_limits=RENTAL_LIMITS,
        business_claims=BUSINESS_CLAIMS,
        business_limits=BUSINESS_LIMITS,
        farm_claims=FARM_CLAIMS,
        farm_limits=FARM_LIMITS,
        fish_claims=FISH_CLAIMS,
        fish_limits=FISH_LIMITS,
        output=AGREED,
    )

    (output,) = wired.compute(inputs(rental=(("600000", FULL),))).outputs
    assert output == Artifact(AGREED, D(FULL))


@pytest.mark.parametrize("slot", ["rental_claims", "business_limits", "fish_claims", "farm_limits"])
def test_rejects_a_money_kind_for_a_record_list_slot(slot: str) -> None:
    wiring: dict[str, Any] = dict(zip(ImmediateExpensingAgreedLimit.CONSUMES, KINDS, strict=True))
    wiring[slot] = cast(Any, AGREED)

    with pytest.raises(InvalidCapabilityError, match=f"ImmediateExpensingAgreedLimit.*'{slot}'"):
        ImmediateExpensingAgreedLimit(**wiring, output=AGREED)


def test_rejects_a_record_list_of_two_fields_for_a_slot() -> None:
    two = RecordListKind("ex/two_fields", fields=(CLAIM, LIMIT))

    with pytest.raises(
        InvalidCapabilityError, match="ImmediateExpensingAgreedLimit.*'rental_limits'"
    ):
        ImmediateExpensingAgreedLimit(
            RENTAL_CLAIMS, two, BUSINESS_CLAIMS, BUSINESS_LIMITS, FARM_CLAIMS, FARM_LIMITS,
            FISH_CLAIMS, FISH_LIMITS, AGREED,
        )  # fmt: skip


# --- computing ----------------------------------------------------------------------------------


def test_no_statements_give_zero() -> None:
    (output,) = capability().compute(inputs()).outputs

    assert output == Artifact(AGREED, D("0"))
    assert not output.value.is_signed()


def test_claims_and_limits_of_unequal_length_are_refused() -> None:
    two = inputs(rental=(("1", FULL), ("2", FULL)))
    one = inputs(rental=(("1", FULL),))
    wired = (
        *(artifact for artifact in two if artifact.kind != RENTAL_LIMITS),
        *(artifact for artifact in one if artifact.kind == RENTAL_LIMITS),
    )

    with pytest.raises(InvalidRecordError) as raised:
        capability().compute(wired)

    assert str(raised.value) == "ex/rental_claims lists 2 statements but ex/rental_limits lists 1"


def test_one_claiming_statement_gives_its_limit() -> None:
    assert agreed(rental=(("600000", FULL),)) == D(FULL)
    assert agreed(farm=(("1", "900000"),)) == D("900000")


def test_statements_of_the_four_forms_with_one_limit_give_it() -> None:
    assert agreed(
        rental=(("600000", FULL),),
        business=(("500000", FULL),),
        farm=(("400000", FULL),),
        fish=(("1", FULL),),
    ) == D(FULL)


def test_several_statements_of_one_form_with_one_limit_give_it() -> None:
    assert agreed(business=(("1", "900000"), ("2", "900000"), ("3", "900000"))) == D("900000")


def test_a_limit_of_zero_shared_by_the_claiming_statements_gives_zero() -> None:
    # An associated EPOP with no agreement filed gives a limit of 0.
    assert agreed(rental=(("5", "0"),), fish=(("7", "0"),)) == D("0")


def test_a_statement_claiming_nothing_is_not_compared() -> None:
    # A rental with no write-off and no Area G filled in shows the full 1500000; the shop is
    # associated at 60% (900000) and claims: no refusal, the agreed limit is the shop's.
    assert agreed(rental=(("0", FULL),), business=(("500000", "900000"),)) == D("900000")


def test_a_statement_claiming_nothing_is_not_compared_whichever_comes_first() -> None:
    assert agreed(rental=(("500000", "900000"),), business=(("0", FULL),)) == D("900000")
    assert agreed(business=(("0", "600000"), ("1", FULL), ("0", "1")), fish=(("0", "2"),)) == D(
        FULL
    )


def test_statements_claiming_nothing_with_different_limits_give_zero() -> None:
    assert agreed(rental=(("0", FULL),), business=(("0", "900000"),), farm=(("0", "0"),)) == D("0")


def test_different_limits_between_forms_are_refused_naming_both_statements() -> None:
    with pytest.raises(ValidationError) as raised:
        agreed(rental=(("100", "600000"),), business=(("200", FULL),))

    assert str(raised.value) == (
        "immediate expensing limit differs between statements: "
        "ex/rental_limits statement 1 has 600000, ex/business_limits statement 1 has 1500000"
    )


def test_different_limits_within_one_form_are_refused_naming_both_statements() -> None:
    with pytest.raises(ValidationError) as raised:
        agreed(farm=(("100", FULL), ("200", "900000")))

    assert str(raised.value) == (
        "immediate expensing limit differs between statements: "
        "ex/farm_limits statement 1 has 1500000, ex/farm_limits statement 2 has 900000"
    )


def test_the_first_statement_and_the_first_that_disagrees_with_it_are_named() -> None:
    # The first compared statement is rental 1; business 1 agrees, farm 1 is the first to differ.
    with pytest.raises(ValidationError) as raised:
        agreed(
            rental=(("1", FULL),),
            business=(("1", FULL),),
            farm=(("1", "600000"),),
            fish=(("1", "700000"),),
        )

    assert str(raised.value) == (
        "immediate expensing limit differs between statements: "
        "ex/rental_limits statement 1 has 1500000, ex/farm_limits statement 1 has 600000"
    )


def test_a_position_counts_the_statements_that_claim_nothing() -> None:
    # Statement 1 claims nothing and is skipped; statements 2 and 3 are the ones compared.
    with pytest.raises(ValidationError) as raised:
        agreed(fish=(("0", "5"), ("10", FULL), ("10", "600000")))

    assert str(raised.value) == (
        "immediate expensing limit differs between statements: "
        "ex/fish_limits statement 2 has 1500000, ex/fish_limits statement 3 has 600000"
    )


def test_the_statements_that_claim_nothing_are_never_named() -> None:
    with pytest.raises(ValidationError) as raised:
        agreed(
            rental=(("0", "1"),), business=(("5", FULL),), farm=(("0", "2"),), fish=(("5", "3"),)
        )

    assert "rental_limits" not in str(raised.value)
    assert "farm_limits" not in str(raised.value)
    assert "ex/fish_limits statement 1 has 3" in str(raised.value)


def test_missing_inputs_are_missing_artifacts() -> None:
    present = inputs(rental=(("1", FULL),))

    for index, name in ((0, "ex/rental_claims"), (3, "ex/business_limits"), (7, "ex/fish_limits")):
        with pytest.raises(MissingArtifactError, match=re.escape(name)):
            capability().compute(present[:index] + present[index + 1 :])


# --- trace --------------------------------------------------------------------------------------


def test_traces_the_compared_statements_then_the_agreed_limit() -> None:
    result = capability().compute(
        inputs(rental=(("600000", FULL),), business=(("0", "900000"), ("500000", FULL)))
    )

    assert result.trace == (
        ImmediateExpensingAgreedLimitLine(
            AGREED,
            (
                (RENTAL_LIMITS, 1, D("600000"), D(FULL)),
                (BUSINESS_LIMITS, 2, D("500000"), D(FULL)),
            ),
            D(FULL),
        ),
    )


def test_traces_no_compared_statement_as_a_limit_of_zero() -> None:
    assert capability().compute(inputs()).trace == (
        ImmediateExpensingAgreedLimitLine(AGREED, (), D("0")),
    )
    assert capability().compute(inputs(rental=(("0", FULL),))).trace == (
        ImmediateExpensingAgreedLimitLine(AGREED, (), D("0")),
    )


def test_the_trace_line_amount_is_the_output() -> None:
    result = capability().compute(inputs(farm=(("1", "900000"),)))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value == D("900000")
