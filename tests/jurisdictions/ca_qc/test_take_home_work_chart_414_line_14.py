"""Revenu Quebec Work Chart 414 (TP-1.D.GR-V 2025-12) line 14, "Add lines 10 and 11. Carry the
result to line 414 of your return (maximum $155).", as the Quebec take-home manifest part wires it,
in two steps as Schedule K line 83 does: `core/sum` of lines 10 and 11, rounded half-up to the cent
by `ca-qc/cent_rounding`, then `core/capped_amount` against the printed $155
(`ca-qc/work_chart_414_line_14_maximum`). The chart exports line 14 for TP-1 line 414. The
expected figures are hand-computed from the printed lines (not an official example): $100 gives
42.50 + 37.50, $30 gives 25.50 + 0.00.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import WORK_CHART_414_CREDIT_LINE_14
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_414_support import (
    FORM_NAME,
    LINE_14_PARTS,
    chart_sheet,
)

LINE = WORK_CHART_414_CREDIT_LINE_14
IDENTIFIER = "ca-qc/work_chart_414_credit_line_14"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize(
    ("contributions", "expected"),
    [
        (None, "0.00"),  # left blank
        ("30", "25.50"),
        ("100", "80.00"),
        ("200", "155.00"),  # the printed maximum, reached at the maximum contributions
        ("400", "155.00"),  # line 1 is capped at 200.00
    ],
)
def test_line_14_is_lines_10_and_11_up_to_155(
    take_home_service: TakeHomeService, contributions: str | None, expected: str
) -> None:
    sheet = chart_sheet(take_home_service, EXPORTS, LINE_14_PARTS, contributions)

    assert str(sheet.get(LINE).value) == expected


def test_the_part_is_the_sum_then_the_cap_and_only_the_cap_prints_the_line() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / "work_chart_414_line_14.yaml").read_text("utf-8"))

    assert part["form"] == {"name": FORM_NAME}
    total, cap = part["capabilities"]
    assert total["name"] == "core/sum"
    assert "reference" not in total
    assert total["unit"] == "ca/cad"
    assert total["params"] == {"rounding": "ca-qc/cent_rounding"}
    assert total["consumes"] == {
        "parts": ["ca-qc/work_chart_414_line_10", "ca-qc/work_chart_414_line_11"]
    }
    assert total["produces"] == {"output": "ca-qc/work_chart_414_credit_before_maximum"}
    assert cap == {
        "name": "core/capped_amount",
        "reference": "14",
        "unit": "ca/cad",
        "params": {"cap": "ca-qc/work_chart_414_line_14_maximum"},
        "consumes": {"base": "ca-qc/work_chart_414_credit_before_maximum"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_real_form_declaration_exports_line_14() -> None:
    declaration = yaml.safe_load((QUEBEC_PARTS / "work_chart_414.yaml").read_text("utf-8"))

    assert declaration["form"]["name"] == FORM_NAME
    assert declaration["form"]["required"] is True
    assert declaration["form"]["exports"] == [IDENTIFIER]
