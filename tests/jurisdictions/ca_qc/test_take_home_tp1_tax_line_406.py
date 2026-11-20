"""Revenu Quebec TP-1 (2025) line 406, "Non-refundable tax credits (line 399)", as the Quebec
take-home manifest wires it: one `core/record_total` over the line 399 export of
`ca-qc/tp1_credits`. The chain runs the real parts of the credits lines and of the forms they read
(see `tp1_tax_support.py`). The salary is $20,000, $70,000 and $200,000. The expected figures are
hand-computed from the printed lines, not a Revenu Quebec example: line 399 is 2,599.94, or
2,897.86 at $20,000 for a person living alone.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_406,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_tax_support import LINE_406_CHAIN, tax_sheet

PART = "tp1_tax_line_406.yaml"
FORM = "ca-qc/tp1_tax"
IDENTIFIER = "ca-qc/tp1_non_refundable_tax_credits_line_406"
EXPORTS = (IDENTIFIER,)
LINE_406 = TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_406


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_406_is_line_399_when_the_filer_does_not_live_alone(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = tax_sheet(take_home_service, salary, EXPORTS, (*LINE_406_CHAIN, PART))

    assert str(sheet.get(LINE_406).value) == "2599.94"


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "2897.86"), ("70000", "2599.94"), ("200000", "2599.94")]
)
def test_line_406_is_line_399_for_a_person_living_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = tax_sheet(take_home_service, salary, EXPORTS, (*LINE_406_CHAIN, PART), given)

    assert str(sheet.get(LINE_406).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_record_total_over_the_credits_export_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "title": "Non-refundable tax credits",
        "reference": "406",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/tp1_credits.tp1_non_refundable_tax_credits_line_399"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is LINE_406
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
