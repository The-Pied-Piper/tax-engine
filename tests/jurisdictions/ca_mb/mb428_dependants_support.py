"""Support for the Worksheet MB428 section "Line 58729" tests: a list of dependants and the engine.

Each dependant is one column of the worksheet: line 1 and line 2 (None leaves line 2 blank).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb
from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
COLUMNS_FORM = "ca-mb/worksheet_mb428_other_dependants"
TOTAL_FORM = "ca-mb/worksheet_mb428_other_dependants_total"
CREDITS_FORM = "ca-mb/mb428_credits"
LINE_1 = "ca-mb/worksheet_mb428_other_dependants_medical_expenses_line_1"
LINE_2 = "ca-mb/worksheet_mb428_other_dependants_medical_expenses_line_2"
LINE_3 = "ca-mb/worksheet_mb428_other_dependants_medical_expenses_line_3"
LINE_4 = "ca-mb/worksheet_mb428_other_dependants_medical_expenses_line_4"


def load_part(name: str) -> dict[str, Any]:
    part = yaml.safe_load((MB_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def dependants(*columns: tuple[str, str | None]) -> Artifact[Any]:
    """The list of dependants, one record for each (line 1, line 2) pair."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_1: D(line_1),
            mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_2: BLANK if line_2 is None else D(line_2),
        }
        for line_1, line_2 in columns
    ]
    return Artifact(
        mb.WORKSHEET_MB428_OTHER_DEPENDANTS,
        RecordList(mb.WORKSHEET_MB428_OTHER_DEPENDANTS.fields, records),
    )


def sheets(form: str, *columns: tuple[str, str | None]) -> tuple[Worksheet, ...]:
    """The worksheets of `form` for a $70,000 salary and the given dependants."""
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if columns:
        given.append(dependants(*columns))
    return build_tax_computation().compute(JurisdictionCode("CA-MB"), 2025, *given)[form]


def amount(sheet: Worksheet, kind: Any) -> Decimal:
    value = sheet.get(kind).value
    assert isinstance(value, Decimal)
    return value
