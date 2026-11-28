"""Revenu Quebec TP-1 (2025) line 391, "Tax credit for career extension. Complete form TP-752.PC-V",
as the Quebec take-home manifest wires it: one `core/record_total` over the form's line 50 export
(`ca-qc/tp752_pc.tp752_pc_line_50`, "Carry this amount to line 391 of your return"), which line 399
adds. It is no longer an optional input (see `test_take_home_tp1_credits_line_399_inputs.py`). A
filer with no birth year, or born too late to be 65 on December 31, has no credit: 0.00. The chain
runs the real parts of the form and of the forms it reads (see `tp1_credits_support.py`).
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.jurisdictions.ca_qc.catalog import TP1_LINE_391, TP752_PC_LINE_50
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import (
    FORM,
    LINE_391_PARTS,
    chain_sheet,
    chain_sheets,
)
from tests.jurisdictions.ca_qc.tp752_pc_support import FORM as TP752_FORM
from tests.kinds import non_negative

PART = "tp1_credits_line_391.yaml"
IDENTIFIER = "ca-qc/tp1_line_391"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_391_is_0_when_the_caller_gives_no_birth_year(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = chain_sheet(take_home_service, salary, EXPORTS, LINE_391_PARTS)

    assert str(sheet.get(TP1_LINE_391).value) == "0.00"


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_line_391_is_line_50_of_the_form_for_a_filer_born_in_1955(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheets = chain_sheets(
        take_home_service, salary, EXPORTS, LINE_391_PARTS, Artifact(BIRTH_YEAR, 1955)
    )

    (sheet,) = sheets[FORM]
    (credit,) = sheets[TP752_FORM]
    assert sheet.get(TP1_LINE_391).value == credit.get(TP752_PC_LINE_50).value
    # At $70,000 line 40 (1,750.00 less 7% of line 36 over 56,500) is under line 49, so it is paid.
    assert (salary != "70000") or sheet.get(TP1_LINE_391).value > 0


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_record_total_over_the_form_export_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "title": "Tax credit for career extension",
        "reference": "391",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/tp752_pc.tp752_pc_line_50"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is TP1_LINE_391
    assert isinstance(TP1_LINE_391, AmountKind)
    assert non_negative(TP1_LINE_391)
