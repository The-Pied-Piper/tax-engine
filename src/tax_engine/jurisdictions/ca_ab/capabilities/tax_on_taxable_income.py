"""Tax on taxable income: the one of AB428 line 8 and line 15 that has a figure.

AB428 line 59 "Alberta tax on taxable income from line 8 or line 15": a taxable income is in one
table only, so the other line is blank. Both blank, or both with a figure, raises a
`ValidationError`. The figure is passed on as it is: no rounding rule is applied to it.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError, ValidationError
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca_ab.trace import TaxOnTaxableIncomeLine


@capability(identifier="tax_on_taxable_income")
class TaxOnTaxableIncome(Capability):
    """Produces `output`: the amount of whichever of `line_8` and `line_15` is not blank."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"line_8": RecordList, "line_15": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = frozenset({"line_8", "line_15"})

    def __init__(self, line_8: RecordListKind, line_15: RecordListKind, output: Money) -> None:
        """Wire the capability: the two record lists it reads, the kind it makes."""
        super().__init__(line_8=line_8, line_15=line_15, output=output)
        name = type(self).__name__
        for slot, kind in (("line_8", line_8), ("line_15", line_15)):
            if not isinstance(kind, RecordListKind):
                raise InvalidCapabilityError(
                    f"{name}: CONSUMES slot '{slot}' must be a record-list kind"
                )
            if len(kind.fields) != 1 or not issubclass(kind.fields[0].value_type, Decimal):
                raise InvalidCapabilityError(
                    f"{name}: CONSUMES slot '{slot}' must be a record list of exactly one "
                    "amount field"
                )
        self._line_8 = line_8
        self._line_15 = line_15
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        name = type(self).__name__
        field_8 = self._line_8.fields[0]
        field_15 = self._line_15.fields[0]
        records_8 = self._input(inputs, self._line_8).value.records
        records_15 = self._input(inputs, self._line_15).value.records
        for slot, records in (("line 8", records_8), ("line 15", records_15)):
            if len(records) != 1:
                raise ValidationError(
                    f"{name}: {slot} must have exactly one record, not {len(records)}"
                )
        record_8 = records_8[0]
        record_15 = records_15[0]
        blank_8 = record_8.is_blank(field_8)
        blank_15 = record_15.is_blank(field_15)
        if blank_8 and blank_15:
            raise ValidationError(
                f"{name}: line 8 and line 15 are both blank; one of them must have a figure"
            )
        if not blank_8 and not blank_15:
            raise ValidationError(
                f"{name}: line 8 and line 15 both have a figure; only one of them may"
            )
        if blank_15:
            used, left_blank, amount = field_8, field_15, record_8[field_8]
        else:
            used, left_blank, amount = field_15, field_8, record_15[field_15]
        return CapabilityResult(
            outputs=(Artifact(self._output, amount),),
            trace=(TaxOnTaxableIncomeLine(self._output, used, amount, left_blank),),
        )
