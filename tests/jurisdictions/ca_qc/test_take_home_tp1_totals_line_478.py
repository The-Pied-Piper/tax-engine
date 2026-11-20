"""Revenu Quebec TP-1 (2025) line 478, "Subtract line 476 from line 474. Refund", as the Quebec
take-home manifest wires it: one `core/subtract`, rounded half-up to the cent by
`ca-qc/cent_rounding`. Line 476 is an optional input, read as 0 when left blank; the form prints no
floor, so the refund is signed as given. The chain runs the real parts of every line that line 474
reads (see `tp1_totals_support.py`). The expected figures are hand-computed from the printed lines,
not a Revenu Quebec example."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_REFUND_LINE_478,
    TP1_REFUND_TRANSFERRED_TO_SPOUSE_LINE_476,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_478_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

D = Decimal
PART = "tp1_totals_line_478.yaml"
IDENTIFIER = "ca-qc/tp1_refund_line_478"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_478_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_478_PARTS)

    assert str(sheet.get(TP1_REFUND_LINE_478).value) == EXPECTED[salary]["478"]


def test_line_476_is_subtracted(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_REFUND_TRANSFERRED_TO_SPOUSE_LINE_476, D("75.06"))
    sheet = totals_sheet(take_home_service, "20000", totals_form(IDENTIFIER), LINE_478_PARTS, given)

    assert str(sheet.get(TP1_REFUND_LINE_478).value) == "500.00"


def test_a_line_476_above_line_474_is_not_floored(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_REFUND_TRANSFERRED_TO_SPOUSE_LINE_476, D("600"))
    sheet = totals_sheet(take_home_service, "20000", totals_form(IDENTIFIER), LINE_478_PARTS, given)

    assert str(sheet.get(TP1_REFUND_LINE_478).value) == "-24.94"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_subtract_of_line_476_from_line_474() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract",
        "title": "Refund",
        "reference": "478",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/tp1_line_474",
            "less": "ca-qc/tp1_refund_transferred_to_spouse_line_476",
        },
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_REFUND_LINE_478
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
