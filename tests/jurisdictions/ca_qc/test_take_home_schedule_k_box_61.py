"""Schedule K (2025) box 61, the months checked from July to December, as the real parts wire it.

Form text (Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part B, section 1): "Number of months
checked from July to December ... 61". The form prints no table; the box counts the months checked
for line 50, and the answer to line 50 means covered all year (owner's optional-answer ruling, 19
Nov 2026), so a yes is 6 months of the half and a no is 0. The `ca-qc/schedule_k_months_box_61`
dataset holds those two rows and `ca/amount_by_count` reads the checked answer. The months are
hand-computed, not printed, and do not depend on the salary.

The real input part, the line 50 part and the box 61 part are composed under a test-local header
and form declaration over the Quebec package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
    SCHEDULE_K_MONTHS_JULY_TO_DECEMBER_BOX_61,
)
from tests.jurisdictions.ca_qc.support import (
    quebec_capabilities,
    quebec_kinds,
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)
from tests.kinds import non_negative

D = Decimal
QC_PARTS = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025"
INPUT_PART = QC_PARTS / "tp1_schedule_k_line_50_input.yaml"
LINE_50_PART = QC_PARTS / "tp1_schedule_k_line_50.yaml"
LINE_PART = QC_PARTS / "tp1_schedule_k_box_61.yaml"
FORM = "ca-qc/tp1_schedule_k"
BOX_61 = "ca-qc/schedule_k_months_july_to_december_box_61"
HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM_PART = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {BOX_61}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_PART, encoding="utf-8")
    for number, found in enumerate((INPUT_PART, LINE_50_PART, LINE_PART), start=2):
        (folder / f"{number:02d}_{found.name}").write_text(
            found.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**quebec_packages().roots(), Namespace("ca-qc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, quebec_kinds(), quebec_units()),
        YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units()),
        quebec_capabilities(),
    )


def _box_61(tmp_path: Path, salary: str, answer: int | None = None) -> Decimal:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if answer is not None:
        given.append(Artifact(SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, answer))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-QC"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet.get(SCHEDULE_K_MONTHS_JULY_TO_DECEMBER_BOX_61).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_box_61_is_0_by_default(tmp_path: Path, salary: str) -> None:
    assert _box_61(tmp_path, salary) == D("0.00")


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_box_61_is_6_when_line_50_is_yes(tmp_path: Path, salary: str) -> None:
    assert _box_61(tmp_path, salary, 1) == D("6.00")


def test_box_61_is_0_when_line_50_is_no(tmp_path: Path) -> None:
    assert _box_61(tmp_path, "70000", 0) == D("0.00")


def test_an_answer_above_1_is_refused_before_box_61(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _box_61(tmp_path, "70000", 2)


def test_the_part_is_one_amount_by_count_step_on_the_checked_answer() -> None:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "ca/amount_by_count",
        "title": "Number of months checked from July to December",
        "reference": "61",
        "unit": "core/months",
        "params": {"table": "ca-qc/schedule_k_months_box_61"},
        "consumes": {"count": "ca-qc/schedule_k_group_plan_covered_checked_line_50"},
        "produces": {"output": BOX_61},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(BOX_61)

    assert kind is SCHEDULE_K_MONTHS_JULY_TO_DECEMBER_BOX_61
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
