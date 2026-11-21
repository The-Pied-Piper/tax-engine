"""NL428 (2025) line 37, the pension income amount, rejected above its printed maximum.

Form text (Form NL428, CRA 5001-c-25e.txt, confirmed 2026-11-18): "Line 37 and line 58360: Pension
income amount (maximum $1,000)". No arithmetic is printed, so line 37 is an entry line: the entered
amount is rejected above the printed maximum, not capped. The maximum is the
`ca-nl/pension_income_amount_maximum` dataset, supplied by a first `core/credit_amount` step that
carries no title and no line number (it is not a line of the form); the second step,
`core/at_most`, is line 37 and carries "37". A blank input (the default) is passed on as blank.
The output is not exported, as no later line reads it yet (as line 40).

The real input part and the new `nl428_credits_line_37.yaml` are loaded under a test-local header
and form over the Newfoundland and Labrador package list of `support.py`, the shared scaffold
owning those, and only the salary is typed in (plus, in some tests, the pension income amount).
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError, NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_PENSION_INCOME_AMOUNT_CLAIMED_LINE_37,
    NL428_PENSION_INCOME_AMOUNT_LINE_37,
    NL428_PENSION_INCOME_AMOUNT_MAXIMUM,
)
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_FORM, T1_LINE_10100_INPUT, T1_LINE_10100_STEP

D = Decimal
PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
INPUT_PART = PARTS / "nl428_credits_line_37_input.yaml"
LINE_PART = PARTS / "nl428_credits_line_37.yaml"
FORM = "ca-nl/nl428_credits"
CLAIMED = "ca-nl/nl428_pension_income_amount_claimed_line_37"
MAXIMUM = "ca-nl/nl428_pension_income_amount_maximum"
LINE_37 = "ca-nl/nl428_pension_income_amount_line_37"
PRINTED_BASIS = "Line 37 and line 58360: Pension income amount (maximum $1,000)"

INPUT_HEADER = """\
jurisdiction: CA-NL
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""
HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
FORM_PART = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_37}
    capabilities: []
    """)


def _input_manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(INPUT_HEADER)
    shutil.copy(INPUT_PART, folder / INPUT_PART.name)
    declared = yaml.safe_load(INPUT_PART.read_text(encoding="utf-8"))
    exports = "".join(f"    - {each['name']}\n" for each in declared["inputs"])
    (folder / "form.yaml").write_text(
        f"form:\n  name: {declared['form']['name']}\n  required: true\n  exports:\n{exports}"
        "capabilities: []\n"
    )
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(), newfoundland_kinds(), newfoundland_units()
    )
    return source.load(folder)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "00_t1_salary.yaml").write_text(
        T1_LINE_10100_INPUT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (folder / "00_t1_form.yaml").write_text(
        T1_LINE_10100_FORM.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (folder / "00_t1_line_10100.yaml").write_text(
        T1_LINE_10100_STEP.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (folder / "01_form.yaml").write_text(FORM_PART, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_37.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(),
            newfoundland_parameter_parsers(),
            newfoundland_units(),
        ),
        newfoundland_capabilities(),
    )


def _line_37(tmp_path: Path, pension: str | None = None) -> Artifact[Any]:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if pension is not None:
        given.append(Artifact(NL428_PENSION_INCOME_AMOUNT_CLAIMED_LINE_37, D(pension)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet.get(newfoundland_kinds().kind(LINE_37))


def test_an_amount_at_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_37(tmp_path, "1000").value) == D("1000.00")


def test_an_amount_below_the_maximum_passes_unchanged(tmp_path: Path) -> None:
    assert D(_line_37(tmp_path, "250.50").value) == D("250.50")


def test_an_amount_of_zero_passes(tmp_path: Path) -> None:
    assert D(_line_37(tmp_path, "0").value) == D("0")


def test_one_cent_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_37(tmp_path, "1000.01")


def test_a_large_amount_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_37(tmp_path, "5000")


def test_a_negative_amount_is_refused_by_the_non_negative_kind() -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(newfoundland_kinds().kind(CLAIMED), D("-0.01"))


def test_a_salary_only_run_computes_and_leaves_line_37_blank(tmp_path: Path) -> None:
    assert _line_37(tmp_path).is_blank


def test_a_request_that_leaves_out_line_37_is_read_as_blank(tmp_path: Path) -> None:
    kinds = newfoundland_kinds()
    declaration = _input_manifest(tmp_path).inputs[CLAIMED]
    default = declaration.default_artifact(kinds.kind(CLAIMED))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def _input_part() -> dict[str, Any]:
    part = yaml.safe_load(INPUT_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_input_part_declares_the_input_with_its_unit_reference_and_title() -> None:
    part = _input_part()

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-nl/nl428_credits"}
    assert part["inputs"] == [
        {
            "name": CLAIMED,
            "title": "Pension income amount",
            "reference": "37",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": PRINTED_BASIS,
        }
    ]
    assert list(part["inputs"][0]) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "default",
        "basis",
    ]


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_two_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
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
        "params": {"amount": "ca-nl/pension_income_amount_maximum"},
        "produces": {"output": MAXIMUM},
    }


def test_the_second_step_is_line_37_titled_and_referenced() -> None:
    _, second = _part()["capabilities"]

    assert second == {
        "name": "core/at_most",
        "title": "Pension income amount",
        "reference": "37",
        "unit": "ca/cad",
        "consumes": {"amount": CLAIMED, "bound": MAXIMUM},
        "blank": {"amount": "pass_on"},
        "produces": {"output": LINE_37},
    }


def test_the_line_part_exports_nothing() -> None:
    assert "exports" not in _part()["form"]


@pytest.mark.parametrize(
    ("identifier", "kind"),
    [
        (CLAIMED, NL428_PENSION_INCOME_AMOUNT_CLAIMED_LINE_37),
        (MAXIMUM, NL428_PENSION_INCOME_AMOUNT_MAXIMUM),
        (LINE_37, NL428_PENSION_INCOME_AMOUNT_LINE_37),
    ],
)
def test_each_kind_is_a_registered_non_negative_decimal_amount_kind(
    identifier: str, kind: AmountKind
) -> None:
    assert kind.identifier == identifier
    assert newfoundland_kinds().kind(identifier) is kind
    assert kind.value_type is Decimal
    assert non_negative(kind)
