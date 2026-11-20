"""Revenu Quebec TP-1 (2025) line 389, "Multiply line 388 by 20%", as the Quebec take-home manifest
wires it: one `core/apply_rate` over line 388 with the printed rate from the dataset
`ca-qc/tp1_line_389_rate`, rounded half-up to the cent by the dataset's rule. Line 388 (the printed
sum of lines 378 to 385) is one optional input, read as 0 when the caller leaves it out. The
expected figures are hand-computed from the printed lines, not a Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP1_LINE_388, TP1_LINE_389
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import LINE_389_PARTS, credits_sheet
from tests.kinds import non_negative

D = Decimal
FORM = "ca-qc/tp1_credits"
PART = "tp1_credits_line_389.yaml"
IDENTIFIER = "ca-qc/tp1_line_389"
EXPORTS = (IDENTIFIER,)


def test_line_389_with_line_388_blank_is_zero(take_home_service: TakeHomeService) -> None:
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_389_PARTS)

    assert str(sheet.get(TP1_LINE_389).value) == "0.00"


def test_line_389_is_line_388_at_20_percent(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_LINE_388, D("1234.56"))
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_389_PARTS, given)

    # 1,234.56 x 0.20 = 246.912, rounded half-up to the cent.
    assert str(sheet.get(TP1_LINE_389).value) == "246.91"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_apply_rate_over_line_388_with_a_blank_read_as_zero() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "389",
        "unit": "ca/cad",
        "params": {"rate": "ca-qc/tp1_line_389_rate"},
        "consumes": {"base": "ca-qc/tp1_line_388"},
        "blank": {"base": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is TP1_LINE_389
    assert isinstance(TP1_LINE_389, AmountKind)
    assert non_negative(TP1_LINE_389)
