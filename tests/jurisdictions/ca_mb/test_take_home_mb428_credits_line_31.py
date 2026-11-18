"""MB428 (2025) line 31, the pension income amount, rejected above its printed maximum.

Form text (Form MB428, Manitoba Tax, CRA 5007-c-25e.txt): "Line 31 and line 58360: Pension income
amount (maximum $1,000)". No arithmetic is printed, so line 31 is an entry line: the entered amount
is rejected above the printed maximum, not capped. The maximum is the `ca-mb/pension_income_amount_
maximum` dataset, supplied by a first `core/credit_amount` step that carries a plain-words title
and no line number (it is not a line of the form); the second step, `core/at_most`, is line
31 and carries "31". A blank input (the default) is passed on as blank.

The real input part and the new `mb428_credits_line_31.yaml` are loaded under a test-local header
and form, the shared scaffold owning those, and only the salary is typed in (plus, in some tests,
the pension income amount).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_mb.catalog import MB428_PENSION_INCOME_AMOUNT
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
INPUT_PART = MB_PARTS / "mb428_credits_line_31_input.yaml"
LINE_PART = MB_PARTS / "mb428_credits_line_31.yaml"
MAXIMUM = "ca-mb/mb428_pension_income_amount_maximum"
LINE_31 = "ca-mb/mb428_pension_income_amount_line_31"
PENSION = "ca-mb/mb428_pension_income_amount"
FORM_NAME = "ca-mb/mb428_credits"

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_pension_income_amount_line_31
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_31.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _line_31(tmp_path: Path, pension: str | None = None) -> Artifact[Any]:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if pension is not None:
        given.append(Artifact(MB428_PENSION_INCOME_AMOUNT, D(pension)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet.get(manitoba_kinds().kind(LINE_31))


def test_an_amount_at_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_31(tmp_path, "1000").value) == D("1000.00")


def test_an_amount_below_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_31(tmp_path, "250.50").value) == D("250.50")


def test_an_amount_of_zero_passes(tmp_path: Path) -> None:
    assert D(_line_31(tmp_path, "0").value) == D("0")


def test_one_cent_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_31(tmp_path, "1000.01")


def test_a_salary_only_run_leaves_line_31_blank(tmp_path: Path) -> None:
    assert _line_31(tmp_path).is_blank


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_two_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    first, second = part["capabilities"]
    assert first["name"] == "core/credit_amount"
    assert second["name"] == "core/at_most"


def test_the_first_step_supplies_the_printed_maximum_with_a_title_and_no_reference() -> None:
    first, _ = _part()["capabilities"]

    assert "reference" not in first
    assert first == {
        "name": "core/credit_amount",
        "title": "Most you can claim for pension income",
        "unit": "ca/cad",
        "params": {"amount": "ca-mb/pension_income_amount_maximum"},
        "produces": {"output": MAXIMUM},
    }


def test_the_second_step_is_line_31_titled_and_referenced() -> None:
    _, second = _part()["capabilities"]

    assert second == {
        "name": "core/at_most",
        "title": "Pension income amount",
        "reference": "31",
        "unit": "ca/cad",
        "consumes": {"amount": PENSION, "bound": MAXIMUM},
        "blank": {"amount": "pass_on"},
        "produces": {"output": LINE_31},
    }


@pytest.mark.parametrize("identifier", [MAXIMUM, LINE_31])
def test_each_new_kind_is_a_registered_non_negative_decimal_amount_kind(identifier: str) -> None:
    kind = manitoba_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
