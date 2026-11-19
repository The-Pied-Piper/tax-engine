"""NL428 (2025) line 96, the reduction for a spouse or common-law partner, as the part wires it.

Form text (Form NL428, CRA 5001-c-25e.txt, confirmed 2026-11-18): "Line 96 and line 61880: Reduction
for spouse or common-law partner Claim $557". The part has three steps: `ca/yes_or_no_count` reads
the optional claim (a blank passed on) and refuses a count above 1; `core/credit_amount`
supplies the printed $557 from the `ca-nl/low_income_reduction_spouse` dataset; `core/times_count`
multiplies it by the checked claim, rounded through `ca-nl/cent_rounding`, as line 40 does for its
claim, a blank claim passed on. A salary-only filer leaves the claim out, so line 96 is blank
(Umar, 2026-11-19 16:24Z); a claim of 0 gives 0.00.

The real input part and the new `nl428_line_96.yaml` are loaded under a test-local header and form
over the Newfoundland and Labrador package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    LOW_INCOME_REDUCTION_SPOUSE,
    NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_CLAIMED_LINE_96,
    NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_LINE_96,
)
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
INPUT_PART = PARTS / "nl428_line_96_input.yaml"
LINE_PART = PARTS / "nl428_line_96.yaml"
FORM = "ca-nl/nl428"
LINE_96 = "ca-nl/nl428_reduction_for_spouse_or_common_law_partner_line_96"
HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM_PART = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_96}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_PART, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_96.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
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


def _line_96(tmp_path: Path, salary: str, claimed: int | None = None) -> Decimal | None:
    """Line 96's value, or None when the line is blank."""
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if claimed is not None:
        given.append(
            Artifact(NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_CLAIMED_LINE_96, claimed)
        )
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM]
    artifact = sheet.get(newfoundland_kinds().kind(LINE_96))
    return None if artifact.is_blank else D(artifact.value)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_96_is_blank_for_a_salary_only_filer(tmp_path: Path, salary: str) -> None:
    assert _line_96(tmp_path, salary) is None


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_96_is_the_printed_557_when_claimed(tmp_path: Path, salary: str) -> None:
    assert _line_96(tmp_path, salary, 1) == D("557.00")


def test_line_96_is_0_when_the_claim_is_0(tmp_path: Path) -> None:
    assert _line_96(tmp_path, "70000", 0) == D("0.00")


def test_a_claim_above_1_is_refused(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_96(tmp_path, "70000", 2)


def test_the_part_has_the_check_the_dataset_and_line_96_in_order() -> None:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    steps = part["capabilities"]
    assert [step["name"] for step in steps] == [
        "ca/yes_or_no_count",
        "core/credit_amount",
        "core/times_count",
    ]
    assert [step.get("reference") for step in steps] == [None, None, "96"]
    assert steps[2]["title"] == "Reduction for spouse or common-law partner"


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (LINE_96, NL428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_LINE_96),
        ("ca-nl/low_income_reduction_spouse", LOW_INCOME_REDUCTION_SPOUSE),
    ],
)
def test_the_new_kinds_are_registered_non_negative_decimal_amount_kinds(
    identifier: str, constant: AmountKind
) -> None:
    kind = newfoundland_kinds().kind(identifier)

    assert kind is constant
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
