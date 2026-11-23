"""Quebec input ownership (2025): a line is an input only on the form it belongs to, and every other
form imports it from that form's export.

Four groups of figures are read by two forms each:
- TP-1 lines 105 and 107 and RL-1 box 211 belong to the TP-1 income form; Work Chart 201 line 1 and
  Schedule P lines 10 and 12 read them from its exports.
- TP-1 lines 114, 128, 142, 147 and 148 belong to the TP-1 income form, which adds them into line
  199; Schedule F lines 22, 23, 26, 28 and 29 read them from its exports.
- TP-1 lines 225, 231, 234, 245 and 246 belong to the TP-1 net income form, which adds them into
  line 254; Schedule F lines 54, 56, 58, 46 and 41 read them from its exports.
- The net research grants and the WEPP payments belong to Work Chart 201 lines 3 and 4; Schedule P
  lines 13 and 15 read them from its exports.

Each figure is given once, under its owner's kind, over the real parts of the whole return, and both
forms show it. The salary is $70,000; the expected figures are hand-computed from the printed lines.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_qc.catalog import (
    RL1_SLIP_BOX_211,
    SCHEDULE_P_LINE_10,
    SCHEDULE_P_LINE_18,
    SCHEDULE_P_RESEARCH_GRANTS_LINE_13,
    SCHEDULE_P_TP1_LINE_107,
    SCHEDULE_P_WEPP_PAYMENTS_LINE_15,
    TP1_LINE_105,
    TP1_LINE_107,
    TP1_LINE_114,
    TP1_LINE_128,
    TP1_LINE_142,
    TP1_LINE_147,
    TP1_LINE_148,
    TP1_LINE_225,
    TP1_LINE_231,
    TP1_LINE_234,
    TP1_LINE_245,
    TP1_LINE_246,
    TP1_SCHEDULE_F_DEDUCTIONS_LINE_68,
    TP1_SCHEDULE_F_LINE_22,
    TP1_SCHEDULE_F_LINE_23,
    TP1_SCHEDULE_F_LINE_26,
    TP1_SCHEDULE_F_LINE_28,
    TP1_SCHEDULE_F_LINE_29,
    TP1_SCHEDULE_F_LINE_41,
    TP1_SCHEDULE_F_LINE_46,
    TP1_SCHEDULE_F_LINE_54,
    TP1_SCHEDULE_F_LINE_56,
    TP1_SCHEDULE_F_LINE_58,
    TP1_SCHEDULE_F_LINES_20_TO_33_TOTAL_LINE_34,
    TP1_TOTAL_DEDUCTIONS_LINE_254,
    TP1_TOTAL_INCOME_LINE_199,
    WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1,
    WORK_CHART_201_RESEARCH_GRANTS_LINE_3,
    WORK_CHART_201_TOTAL_LINE_6,
    WORK_CHART_201_WEPP_PAYMENTS_LINE_4,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import FORM as T1_FORM
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.return_support import PARTS, header
from tests.jurisdictions.ca_qc.tp1_net_income_support import slip_artifacts

D = Decimal
SHARED_INPUTS = {
    "ca-qc/tp1_line_105": "tp1_income",
    "ca-qc/tp1_line_107": "tp1_income",
    "ca-qc/rl1_slip_box_211": "tp1_income",
    "ca-qc/tp1_line_114": "tp1_income",
    "ca-qc/tp1_line_128": "tp1_income",
    "ca-qc/tp1_line_142": "tp1_income",
    "ca-qc/tp1_line_147": "tp1_income",
    "ca-qc/tp1_line_148": "tp1_income",
    "ca-qc/tp1_line_225": "tp1_net_income",
    "ca-qc/tp1_line_231": "tp1_net_income",
    "ca-qc/tp1_line_234": "tp1_net_income",
    "ca-qc/tp1_line_245": "tp1_net_income",
    "ca-qc/tp1_line_246": "tp1_net_income",
    "ca-qc/work_chart_201_research_grants_line_3": "work_chart_201",
    "ca-qc/work_chart_201_wepp_payments_line_4": "work_chart_201",
}
REMOVED_COPIES = (
    "ca-qc/schedule_p_research_grants_line_13",
    "ca-qc/schedule_p_wepp_payments_line_15",
    "ca-qc/tp1_schedule_f_line_22",
    "ca-qc/tp1_schedule_f_line_23",
    "ca-qc/tp1_schedule_f_line_26",
    "ca-qc/tp1_schedule_f_line_28",
    "ca-qc/tp1_schedule_f_line_29",
    "ca-qc/tp1_schedule_f_line_41",
    "ca-qc/tp1_schedule_f_line_46",
    "ca-qc/tp1_schedule_f_line_54",
    "ca-qc/tp1_schedule_f_line_56",
    "ca-qc/tp1_schedule_f_line_58",
)


def _declared_inputs() -> list[tuple[str, str]]:
    """Every input the Quebec manifest parts declare, with the form of its part."""
    declared: list[tuple[str, str]] = []
    for path in sorted(QUEBEC_PARTS.glob("*.yaml")):
        part: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        form = part.get("form", {}).get("name", "")
        declared += [(declaration["name"], form) for declaration in part.get("inputs", [])]
    return declared


def _exports(form: str) -> list[str]:
    part = yaml.safe_load((QUEBEC_PARTS / f"{form}.yaml").read_text(encoding="utf-8"))
    return list(part["form"]["exports"])


def test_each_shared_input_is_declared_once_on_the_form_it_belongs_to_and_exported() -> None:
    declared = _declared_inputs()

    for name, owner in SHARED_INPUTS.items():
        assert [form for declared_name, form in declared if declared_name == name] == [
            f"ca-qc/{owner}"
        ]
        assert name in _exports(owner)


def test_the_copies_that_other_forms_used_to_declare_are_gone() -> None:
    names = [name for name, _ in _declared_inputs()]

    for name in REMOVED_COPIES:
        assert name not in names


def test_no_input_is_declared_twice() -> None:
    names = [name for name, _ in _declared_inputs()]

    assert len(names) == len(set(names))


def _forms(take_home_service: TakeHomeService, *runs: tuple[tuple[Any, str], ...]) -> list[Any]:
    """The worksheets of each run: the same salary with that run's figures given."""
    service = take_home_service(header(), T1_FORM, *PARTS)
    forms = []
    for given in runs:
        starting = [*slip_artifacts("70000"), *(Artifact(kind, D(value)) for kind, value in given)]
        sheets = service.compute(
            TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
        )
        forms.append({name: found[0] for name, found in sheets.items()})
    return forms


def test_lines_105_and_107_and_box_211_given_once_reach_work_chart_201_and_schedule_p(
    take_home_service: TakeHomeService,
) -> None:
    (sheets,) = _forms(
        take_home_service,
        (
            (TP1_LINE_105, "1000.25"),
            (TP1_LINE_107, "2000.50"),
            (RL1_SLIP_BOX_211, "300.10"),
        ),
    )

    # Work Chart 201 line 1: 70,000 + 2,000.50 + 1,000.25 - 300.10.
    assert sheets["ca-qc/work_chart_201"].get(WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1).value == (
        D("72700.65")
    )
    schedule_p = sheets["ca-qc/schedule_p"]
    # Schedule P line 10: 70,000 + 1,000.25 - 300.10; line 12 is line 107; line 18 adds them.
    assert schedule_p.get(SCHEDULE_P_LINE_10).value == D("70700.15")
    assert schedule_p.get(SCHEDULE_P_TP1_LINE_107).value == D("2000.50")
    assert schedule_p.get(SCHEDULE_P_LINE_18).value == D("72700.65")


def test_lines_114_128_142_147_and_148_given_once_reach_schedule_f_and_tp1_line_199(
    take_home_service: TakeHomeService,
) -> None:
    (sheets,) = _forms(
        take_home_service,
        (
            (TP1_LINE_114, "200.20"),
            (TP1_LINE_128, "1380.50"),
            (TP1_LINE_142, "400.40"),
            (TP1_LINE_147, "500.50"),
            (TP1_LINE_148, "600.60"),
        ),
    )

    # Schedule F lines 22, 23, 26, 28 and 29 are the TP-1 lines; line 24 is blank, so line 25 is
    # line 23, and line 34 adds 200.20 + 1,380.50 + 400.40 + 500.50 + 600.60.
    schedule_f = sheets["ca-qc/tp1_schedule_f"]
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_22).value == D("200.20")
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_23).value == D("1380.50")
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_26).value == D("400.40")
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_28).value == D("500.50")
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_29).value == D("600.60")
    assert schedule_f.get(TP1_SCHEDULE_F_LINES_20_TO_33_TOTAL_LINE_34).value == D("3082.20")
    # TP-1 line 199 adds the same five figures to the salary: 70,000 + 3,082.20.
    assert sheets["ca-qc/tp1_income"].get(TP1_TOTAL_INCOME_LINE_199).value == D("73082.20")


def test_lines_225_231_234_245_and_246_given_once_reach_schedule_f_and_tp1_line_254(
    take_home_service: TakeHomeService,
) -> None:
    (sheets,) = _forms(
        take_home_service,
        (
            (TP1_LINE_246, "100.10"),
            (TP1_LINE_245, "200.20"),
            (TP1_LINE_225, "300.30"),
            (TP1_LINE_231, "400.40"),
            (TP1_LINE_234, "500.50"),
        ),
    )

    # Schedule F lines 41, 46, 54, 56 and 58 are the TP-1 lines 246, 245, 225, 231 and 234, and
    # line 68 adds 100.10 + 200.20 + 300.30 + 400.40 + 500.50.
    schedule_f = sheets["ca-qc/tp1_schedule_f"]
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_41).value == D("100.10")
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_46).value == D("200.20")
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_54).value == D("300.30")
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_56).value == D("400.40")
    assert schedule_f.get(TP1_SCHEDULE_F_LINE_58).value == D("500.50")
    assert schedule_f.get(TP1_SCHEDULE_F_DEDUCTIONS_LINE_68).value == D("1501.50")
    # TP-1 line 254 adds the same five figures to the 2,085.00 a 70,000 salary gives.
    assert sheets["ca-qc/tp1_net_income"].get(TP1_TOTAL_DEDUCTIONS_LINE_254).value == D("3586.50")


def test_research_grants_and_wepp_payments_given_once_reach_work_chart_201_and_schedule_p(
    take_home_service: TakeHomeService,
) -> None:
    (sheets,) = _forms(
        take_home_service,
        (
            (WORK_CHART_201_RESEARCH_GRANTS_LINE_3, "400.40"),
            (WORK_CHART_201_WEPP_PAYMENTS_LINE_4, "500.50"),
        ),
    )

    # Work Chart 201 line 6: 70,000 + 400.40 + 500.50.
    assert sheets["ca-qc/work_chart_201"].get(WORK_CHART_201_TOTAL_LINE_6).value == D("70900.90")
    schedule_p = sheets["ca-qc/schedule_p"]
    assert schedule_p.get(SCHEDULE_P_RESEARCH_GRANTS_LINE_13).value == D("400.40")
    assert schedule_p.get(SCHEDULE_P_WEPP_PAYMENTS_LINE_15).value == D("500.50")
    assert schedule_p.get(SCHEDULE_P_LINE_18).value == D("70900.90")


def test_the_printed_lines_that_read_another_forms_export_are_rounded_to_the_cent(
    take_home_service: TakeHomeService,
) -> None:
    (sheets,) = _forms(
        take_home_service,
        (
            (TP1_LINE_107, "2000.505"),
            (WORK_CHART_201_RESEARCH_GRANTS_LINE_3, "400.404"),
            (WORK_CHART_201_WEPP_PAYMENTS_LINE_4, "500.505"),
        ),
    )

    schedule_p = sheets["ca-qc/schedule_p"]
    assert schedule_p.get(SCHEDULE_P_TP1_LINE_107).value == D("2000.51")
    assert schedule_p.get(SCHEDULE_P_RESEARCH_GRANTS_LINE_13).value == D("400.40")
    assert schedule_p.get(SCHEDULE_P_WEPP_PAYMENTS_LINE_15).value == D("500.51")
    # Line 18 adds the printed (rounded) lines: 70,000 + 2,000.51 + 400.40 + 500.51.
    assert schedule_p.get(SCHEDULE_P_LINE_18).value == D("72901.42")


def test_every_part_of_the_split_tp1_shares_the_printed_title() -> None:
    forms = ("tp1_income", "tp1_net_income", "tp1_credits", "tp1_tax", "tp1_totals")

    for form in forms:
        part = yaml.safe_load((QUEBEC_PARTS / f"{form}.yaml").read_text(encoding="utf-8"))
        assert part["form"]["title"] == "Income Tax Return"
