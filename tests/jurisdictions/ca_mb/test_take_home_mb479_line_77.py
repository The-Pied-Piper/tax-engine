"""MB479 (2025) line 77, the employee share purchase tax credit, rejected above its printed maximum.

Form text (Form MB479, CRA 5007-tc-25e.txt): "Line 77 and line 61490: Enter your Manitoba employee
share purchase tax credit from line 6 of Form T1256-2. (maximum $27,000)". The form prints no label,
so the input and the step are untitled. Line 77 is an entry line: the entered amount is rejected
above the printed maximum, not capped. The maximum is the `ca-mb/employee_share_purchase_credit_
maximum` dataset, supplied by a first `core/credit_amount` step that carries no title and no line
number (it is not a line of the form); the second step, `core/at_most`, is line 77, carries no title
and the reference "77". A blank input (the default) is passed on as blank.

The real input part and the new `mb479_line_77.yaml` are loaded under a test-local header and form,
the shared scaffold owning those, and only the salary is typed in (plus, in some tests, the credit).
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
from tax_engine.jurisdictions.ca_mb.catalog import MB479_EMPLOYEE_SHARE_PURCHASE_CREDIT_LINE_77
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
INPUT_PART = MB_PARTS / "mb479_line_77_input.yaml"
LINE_PART = MB_PARTS / "mb479_line_77.yaml"
MAXIMUM = "ca-mb/mb479_employee_share_purchase_credit_maximum"
LINE_77 = "ca-mb/mb479_employee_share_purchase_credit_checked_line_77"
CREDIT = "ca-mb/mb479_employee_share_purchase_credit_line_77"
FORM_NAME = "ca-mb/mb479"

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb479
      required: true
      exports:
        - ca-mb/mb479_employee_share_purchase_credit_checked_line_77
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_77.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _line_77(tmp_path: Path, credit: str | None = None) -> Artifact[Any]:
    given: list[Artifact[Any]] = []
    if credit is not None:
        given.append(Artifact(MB479_EMPLOYEE_SHARE_PURCHASE_CREDIT_LINE_77, D(credit)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet.get(manitoba_kinds().kind(LINE_77))


def test_an_amount_at_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_77(tmp_path, "27000").value) == D("27000.00")


def test_an_amount_below_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_77(tmp_path, "250.50").value) == D("250.50")


def test_an_amount_of_zero_passes(tmp_path: Path) -> None:
    assert D(_line_77(tmp_path, "0").value) == D("0")


def test_one_cent_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_77(tmp_path, "27000.01")


def test_a_salary_only_run_leaves_line_77_blank(tmp_path: Path) -> None:
    assert _line_77(tmp_path).is_blank


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


def test_the_first_step_supplies_the_printed_maximum_with_no_title_and_no_reference() -> None:
    first, _ = _part()["capabilities"]

    assert "title" not in first
    assert "reference" not in first
    assert first == {
        "name": "core/credit_amount",
        "unit": "ca/cad",
        "params": {"amount": "ca-mb/employee_share_purchase_credit_maximum"},
        "produces": {"output": MAXIMUM},
    }


def test_the_second_step_is_line_77_untitled_and_referenced() -> None:
    _, second = _part()["capabilities"]

    assert second == {
        "name": "core/at_most",
        "reference": "77",
        "unit": "ca/cad",
        "consumes": {"amount": CREDIT, "bound": MAXIMUM},
        "blank": {"amount": "pass_on"},
        "produces": {"output": LINE_77},
    }


@pytest.mark.parametrize("identifier", [MAXIMUM, LINE_77])
def test_each_new_kind_is_a_registered_non_negative_decimal_amount_kind(identifier: str) -> None:
    kind = manitoba_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
