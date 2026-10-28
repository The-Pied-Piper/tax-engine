"""ImmediateExpensingAgreedLimit: the one immediate expensing limit of a person across the
statements of Forms T776, T2125, T2042 and T2121.

Area A endnote 5 of each of the four forms: "The total immediate expensing amount for the tax year
(total of column 9) is limited to the lesser of: the immediate expensing limit, which is equal to
one of the following, whichever is applicable: $1.5 million, if you are not associated with any
other eligible person or partnership (EPOP) in the tax year; amount iii of Area G, if you are
associated with one or more EPOPs in the tax year; zero, if you are associated with one or more
EPOPs and an agreement ... was not filed with the minister in a prescribed form; any amount
allocated by the minister under subsection 1104(3.4) of the Regulations". Guides T4002 and T4036:
"The deduction is limited to $1.5 million per tax year". The forms print the limit for each
statement and are silent on a person who files several statements, and on statements whose limits
differ; the Guides' "per tax year" is the only statement of the rule across statements. The limits
compared are those before the days scaling of each statement's fiscal period (Income Tax
Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation year that is less
than 51 weeks, its immediate expensing limit for the year is that proportion of its immediate
expensing limit for the year determined without reference to this paragraph that the number of days
in the year is of 365"), so a statement of a short period and one of a full year share one limit;
each form still checks its own claim against its scaled limit.

The consumed slots are eight record lists, for each form its claim list (`rental_claims`,
`business_claims`, `farm_claims`, `fish_claims`: one record per statement holding the total of
column 9) and its limit list (`rental_limits`, `business_limits`, `farm_limits`, `fish_limits`: one
record per statement holding that statement's limit), each a list of one amount field. The records
of a claim list and of its limit list pair by position; lists of different lengths are refused
(`InvalidRecordError`). Only the statements whose claim is above 0 are compared, in the order
rental, business, farm, fish: every limit among them must be equal, and the common value is the
output, 0 when no statement claims anything. Two compared statements with different limits are
refused (`ValidationError`), naming the first statement (the limit list's kind and the position
from 1, with its limit) and the first statement that disagrees with it. It records one
`ImmediateExpensingAgreedLimitLine` listing the compared statements and the agreed limit.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import (
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
    ValidationError,
)
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.trace import ImmediateExpensingAgreedLimitLine


@capability(identifier="immediate_expensing_agreed_limit")
class ImmediateExpensingAgreedLimit(Capability):
    """Produces `output`: the limit that every consumed statement claiming above 0 shares, 0 when
    none claims."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "rental_claims": RecordList,
        "rental_limits": RecordList,
        "business_claims": RecordList,
        "business_limits": RecordList,
        "farm_claims": RecordList,
        "farm_limits": RecordList,
        "fish_claims": RecordList,
        "fish_limits": RecordList,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rental_claims: RecordListKind,
        rental_limits: RecordListKind,
        business_claims: RecordListKind,
        business_limits: RecordListKind,
        farm_claims: RecordListKind,
        farm_limits: RecordListKind,
        fish_claims: RecordListKind,
        fish_limits: RecordListKind,
        output: Money,
    ) -> None:
        """Wire the capability: for each form its claim list and its limit list, then the kind
        produced.

        Raises InvalidCapabilityError when a list does not have exactly one amount field.
        """
        super().__init__(
            rental_claims=rental_claims,
            rental_limits=rental_limits,
            business_claims=business_claims,
            business_limits=business_limits,
            farm_claims=farm_claims,
            farm_limits=farm_limits,
            fish_claims=fish_claims,
            fish_limits=fish_limits,
            output=output,
        )
        for slot, kind in (
            ("rental_claims", rental_claims),
            ("rental_limits", rental_limits),
            ("business_claims", business_claims),
            ("business_limits", business_limits),
            ("farm_claims", farm_claims),
            ("farm_limits", farm_limits),
            ("fish_claims", fish_claims),
            ("fish_limits", fish_limits),
        ):
            self._check_one_amount_field(slot, kind)
        self._pairs = (
            (rental_claims, rental_limits),
            (business_claims, business_limits),
            (farm_claims, farm_limits),
            (fish_claims, fish_limits),
        )
        self._output = output

    def _check_one_amount_field(self, slot: str, kind: RecordListKind) -> None:
        if len(kind.fields) != 1 or not issubclass(kind.fields[0].value_type, Decimal):
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot {slot!r} must be a record list of "
                "exactly one amount field"
            )

    def _amounts(
        self, inputs: tuple[Artifact[Any], ...], kind: RecordListKind
    ) -> tuple[Decimal, ...]:
        if not any(artifact.kind == kind for artifact in inputs):
            raise MissingArtifactError(f"{type(self).__name__} needs {kind.identifier!r}")
        records = self._input(inputs, kind).value.records
        return tuple(record[kind.fields[0]] for record in records)

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        compared: list[tuple[RecordListKind, int, Decimal, Decimal]] = []
        for claims_kind, limits_kind in self._pairs:
            claims = self._amounts(inputs, claims_kind)
            limits = self._amounts(inputs, limits_kind)
            if len(claims) != len(limits):
                raise InvalidRecordError(
                    f"{claims_kind.identifier} lists {len(claims)} statements but "
                    f"{limits_kind.identifier} lists {len(limits)}"
                )
            compared.extend(
                (limits_kind, position, claim, limit)
                for position, (claim, limit) in enumerate(zip(claims, limits, strict=True), start=1)
                if claim > 0
            )
        agreed = compared[0][3] if compared else Decimal(0)
        for kind, position, _claim, limit in compared:
            if limit != agreed:
                first_kind, first_position, _first_claim, first_limit = compared[0]
                raise ValidationError(
                    "immediate expensing limit differs between statements: "
                    f"{first_kind.identifier} statement {first_position} has {first_limit}, "
                    f"{kind.identifier} statement {position} has {limit}"
                )
        return CapabilityResult(
            outputs=(Artifact(self._output, agreed),),
            trace=(ImmediateExpensingAgreedLimitLine(self._output, tuple(compared), agreed),),
        )
