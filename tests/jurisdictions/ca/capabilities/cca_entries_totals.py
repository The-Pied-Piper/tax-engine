"""Shared helpers for the totals over the rows of the CCA table, T776 Area A: rows and cases.

Each of the three capabilities totals some columns of the Area A rows (the opening UCC, the
additions, the remaining personal part). They differ only in the columns they total and in the
trace line they record, so the cases they share are the methods of `CcaEntriesTotalCases`; each
test module subclasses it with its own capability and columns.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityRegistry
from tax_calculator.domain.errors import MissingArtifactError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.cca_entries_total import CcaEntriesTotal
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_DIEP_ADDITIONS,
    CCA_PERSONAL_PART_REMAINING,
    CCA_RIIP_ADDITIONS,
    CCA_UCC_AT_START,
)

D = Decimal

ALL_FIELDS = (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_START,
    CCA_ADDITIONS,
    CCA_DIEP_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_RIIP_ADDITIONS,
    CCA_CLAIMED,
    CCA_PERSONAL_PART_REMAINING,
)
CLASSES = RecordListKind("ex/entries_classes", fields=ALL_FIELDS)
SHORT = RecordListKind("ex/entries_short_classes", fields=(CCA_CLASS_NUMBER, CCA_CLAIMED))
TOTAL = ArtifactKind("ex/entries_total", Decimal, non_negative=True)

COLUMNS = {
    "ucc": CCA_UCC_AT_START,
    "additions": CCA_ADDITIONS,
    "diep": CCA_DIEP_ADDITIONS,
    "aiip": CCA_AIIP_ADDITIONS,
    "riip": CCA_RIIP_ADDITIONS,
    "personal": CCA_PERSONAL_PART_REMAINING,
}


def wired(cls: Any, classes: RecordListKind = CLASSES) -> Capability:
    return cls(classes, TOTAL)  # type: ignore[no-any-return]


def row(**amounts: str) -> dict[ArtifactKind[Any], Decimal]:
    """An Area A row of the columns named (`ucc`, `additions`, `diep`, `aiip`, `riip`, `personal`);
    the others are 0."""
    record: dict[ArtifactKind[Any], Decimal] = {
        CCA_CLASS_NUMBER: D("1"),
        CCA_CLAIMED: D("0"),
        **dict.fromkeys(COLUMNS.values(), D("0")),
    }
    for name, amount in amounts.items():
        record[COLUMNS[name]] = D(amount)
    return record


def classes(*rows: dict[ArtifactKind[Any], Decimal]) -> Artifact[Any]:
    return Artifact(CLASSES, RecordList(CLASSES.fields, list(rows)))


def total(cls: Any, *rows: dict[ArtifactKind[Any], Decimal]) -> Decimal:
    """The total of `cls` for the rows given."""
    (output,) = wired(cls).compute((classes(*rows),)).outputs
    assert output.kind is TOTAL
    return output.value  # type: ignore[no-any-return]


class CcaEntriesTotalCases:
    """The cases of a CCA entries total, for the subclass's own capability and columns.

    A subclass sets `CAPABILITY`, `IDENTIFIER`, `MODULE` (its name in the capabilities package)
    and `COLUMNS_TOTALLED` (the names, as in `COLUMNS`, of the columns of `row` it totals).
    """

    CAPABILITY: Any
    IDENTIFIER: str
    MODULE: str
    COLUMNS_TOTALLED: tuple[str, ...]

    def test_is_registered_under_its_identifier(self) -> None:
        assert CapabilityRegistry.shared().get(self.IDENTIFIER) is self.CAPABILITY
        assert issubclass(self.CAPABILITY, CcaEntriesTotal)

    def test_is_exported_from_the_ca_capabilities_package(self) -> None:
        assert self.MODULE in ca_capabilities.__all__
        module = getattr(ca_capabilities, self.MODULE)
        assert module.__dict__[self.CAPABILITY.__name__] is self.CAPABILITY

    def test_declares_its_contract_and_leaves_it_to_the_base(self) -> None:
        assert wired(self.CAPABILITY).consumes == frozenset({CLASSES})
        assert wired(self.CAPABILITY).produces == frozenset({TOTAL})
        assert "consumes" not in vars(self.CAPABILITY)
        assert "produces" not in vars(self.CAPABILITY)

    def test_declares_its_columns(self) -> None:
        assert self.CAPABILITY.FIELDS == tuple(COLUMNS[name] for name in self.COLUMNS_TOTALLED)

    def test_declares_its_slots(self) -> None:
        assert self.CAPABILITY.CONSUMES == {"classes": RecordList}
        assert self.CAPABILITY.PRODUCES == {"output": Decimal}

    def test_its_slots_are_read_only(self) -> None:
        for slots in (self.CAPABILITY.CONSUMES, self.CAPABILITY.PRODUCES):
            assert isinstance(slots, MappingProxyType | Mapping)
            with pytest.raises(TypeError):
                slots["extra"] = Decimal  # type: ignore[index]

    def test_no_rows_total_0(self) -> None:
        assert total(self.CAPABILITY) == D("0")

    def test_each_of_its_columns_alone_is_its_total(self) -> None:
        for column in self.COLUMNS_TOTALLED:
            assert total(self.CAPABILITY, row(**{column: "5"})) == D("5")

    def test_the_other_columns_and_a_claim_are_not_a_total(self) -> None:
        others = {name: "7" for name in COLUMNS if name not in self.COLUMNS_TOTALLED}
        claimed = row(**others)
        claimed[CCA_CLAIMED] = D("900")

        assert total(self.CAPABILITY, claimed) == D("0")

    def test_a_column_the_list_does_not_list_counts_0(self) -> None:
        short = Artifact(
            SHORT, RecordList(SHORT.fields, [{CCA_CLASS_NUMBER: D("1"), CCA_CLAIMED: D("5")}])
        )

        (output,) = wired(self.CAPABILITY, SHORT).compute((short,)).outputs

        assert output.value == D("0")

    def test_a_missing_list_is_refused(self) -> None:
        with pytest.raises(MissingArtifactError):
            wired(self.CAPABILITY).compute(())
