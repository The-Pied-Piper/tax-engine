"""Quebec Schedule P (TP-1.D.P-V, 2025) Part F line 90, "Add lines 88 and 89", "Tax credits
respecting the work premium", as the Quebec take-home manifest wires it: one `core/sum` of line 60
(line 88 is its copy) and line 87 (line 89 is its copy), rounded half-up to the cent, which the form
exports for TP-1 line 456.

The chains of lines 52 to 60 and 66 to 87 run for real, over the real TP-1 income parts. The
expected figures of a salary-only filer are hand-computed from the printed lines (the Quebec 2025
hand calculation of 19 Nov 2026), not from a Revenu Quebec example."""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_SUPPLEMENT_LINE_60,
    SCHEDULE_P_TAX_CREDITS_LINE_90,
    SCHEDULE_P_WORK_PREMIUM_LINE_87,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_p_family_income_support import family_income_worksheet
from tests.jurisdictions.ca_qc.support import schedule_p_form

PARTS = (
    "schedule_p_line_10.yaml",
    "schedule_p_line_13_inputs.yaml",
    "schedule_p_line_14_inputs.yaml",
    "schedule_p_line_15_inputs.yaml",
    "schedule_p_line_18.yaml",
    "schedule_p_line_22_inputs.yaml",
    "schedule_p_line_29.yaml",
    "schedule_p_line_52.yaml",
    "schedule_p_line_53_inputs.yaml",
    "schedule_p_line_54.yaml",
    "schedule_p_line_56.yaml",
    "schedule_p_line_57_inputs.yaml",
    "schedule_p_line_58_inputs.yaml",
    "schedule_p_line_59.yaml",
    "schedule_p_line_60.yaml",
    "schedule_p_line_66.yaml",
    "schedule_p_line_68.yaml",
    "schedule_p_line_70.yaml",
    "schedule_p_line_72.yaml",
    "schedule_p_line_76.yaml",
    "schedule_p_line_80.yaml",
    "schedule_p_line_82.yaml",
    "schedule_p_line_83.yaml",
    "schedule_p_line_84.yaml",
    "schedule_p_line_90.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_tax_credits_line_90")


@pytest.mark.parametrize(
    ("salary", "line_88", "line_89", "line_90"),
    [
        # Line 60 prints 0.00 (no months) and line 87 is 584.02.
        ("20000", "0.00", "584.02", "584.02"),
        ("70000", "0.00", "0.00", "0.00"),
        ("200000", "0.00", "0.00", "0.00"),
    ],
)
def test_line_90_is_line_88_plus_line_89(
    take_home_service: TakeHomeService,
    salary: str,
    line_88: str,
    line_89: str,
    line_90: str,
) -> None:
    sheet = family_income_worksheet(take_home_service, FORM, PARTS, salary)

    assert str(sheet.get(SCHEDULE_P_SUPPLEMENT_LINE_60).value) == line_88
    assert str(sheet.get(SCHEDULE_P_WORK_PREMIUM_LINE_87).value) == line_89
    assert str(sheet.get(SCHEDULE_P_TAX_CREDITS_LINE_90).value) == line_90


def test_the_form_part_names_titles_and_exports_line_90() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / "schedule_p.yaml").read_text(encoding="utf-8"))

    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert part["form"]["name"] == "ca-qc/schedule_p"
    assert part["form"]["title"] == "Schedule P: Tax Credits Respecting the Work Premium"
    assert part["form"]["exports"] == ["ca-qc/schedule_p_tax_credits_line_90"]
    assert part["capabilities"] == []
