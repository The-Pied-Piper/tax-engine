"""BC428 line 84, the political contribution tax credit checked against its printed maximum.

Form text (Form BC428, CRA 5010-c-25e.txt line 285-286, confirmed): "Line 84: British Columbia
political contribution tax credit (use Worksheet BC428) (maximum $500)". Worksheet BC428 is not
built, so line 84 is an entry line: the entered amount is rejected above the printed maximum, not
capped. The maximum is the `ca-bc/political_contribution_tax_credit_maximum` dataset, supplied by
`bc428_political_contribution_tax_credit_maximum.yaml`, a `core/credit_amount` step that carries a
plain-words title and no line number (it is not a line of the form). `bc428_line_84.yaml` is
`core/at_most`, line 84, titled and referenced "84", consuming the
`ca-bc/bc428_political_contribution_tax_credit_line_84` input against that maximum and producing
`ca-bc/bc428_british_columbia_political_contribution_tax_credit_line_84`, which line 85 subtracts.
A blank input (the default) is passed on as blank.

The real input part and the two new parts are loaded under a test-local header and form, the shared
scaffold owning those, and only the salary is typed in (plus, in some tests, the input).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
INPUT_PART = BC_PARTS / "bc428_line_84_input.yaml"
MAXIMUM_PART = BC_PARTS / "bc428_political_contribution_tax_credit_maximum.yaml"
LINE_PART = BC_PARTS / "bc428_line_84.yaml"
INPUT = "ca-bc/bc428_political_contribution_tax_credit_line_84"
MAXIMUM = "ca-bc/bc428_political_contribution_tax_credit_maximum"
LINE_84 = "ca-bc/bc428_british_columbia_political_contribution_tax_credit_line_84"
FORM_NAME = "ca-bc/bc428"

HEADER = dedent("""\
    jurisdiction: CA-BC
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
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_british_columbia_political_contribution_tax_credit_line_84
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate((INPUT_PART, MAXIMUM_PART, LINE_PART), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _line_84(tmp_path: Path, credit: str | None = None) -> Artifact[Any]:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if credit is not None:
        given.append(Artifact(british_columbia_kinds().kind(INPUT), D(credit)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-BC"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet.get(british_columbia_kinds().kind(LINE_84))


def test_an_amount_at_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_84(tmp_path, "500").value) == D("500.00")


def test_an_amount_below_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_84(tmp_path, "250.50").value) == D("250.50")


def test_an_amount_of_zero_passes(tmp_path: Path) -> None:
    assert D(_line_84(tmp_path, "0").value) == D("0")


def test_one_cent_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_84(tmp_path, "500.01")


def test_a_salary_only_run_leaves_line_84_blank(tmp_path: Path) -> None:
    assert _line_84(tmp_path).is_blank


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_maximum_part_is_one_credit_amount_step_with_a_title_and_no_reference() -> None:
    part = _part(MAXIMUM_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert "reference" not in step
    assert step == {
        "name": "core/credit_amount",
        "title": "Political contribution tax credit maximum",
        "unit": "ca/cad",
        "params": {"amount": "ca-bc/political_contribution_tax_credit_maximum"},
        "produces": {"output": MAXIMUM},
    }


def test_the_line_84_part_is_one_at_most_step_titled_and_referenced() -> None:
    part = _part(LINE_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/at_most",
        "title": "British Columbia political contribution tax credit",
        "reference": "84",
        "unit": "ca/cad",
        "consumes": {"amount": INPUT, "bound": MAXIMUM},
        "blank": {"amount": "pass_on"},
        "produces": {"output": LINE_84},
    }


@pytest.mark.parametrize("identifier", [INPUT, MAXIMUM, LINE_84])
def test_each_kind_is_a_registered_non_negative_decimal_amount_kind(identifier: str) -> None:
    kind = british_columbia_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
