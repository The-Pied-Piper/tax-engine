"""NL428 (2025) line 40, the disability amount for self, as the NL take-home manifest parts wire it.

Form text (Form NL428, CRA 5001-c-25e.txt, confirmed 2026-11-18): "Line 40 and line 58440:
Disability amount for self (claim $7,467 or, if you were under 18 years of age, use Worksheet
NL428)". The under-18 branch is a skipped block and is not built.

The part has three steps: `ca/yes_or_no_count` reads the optional claim (blank read as 0) and
refuses a count above 1; `core/credit_amount` produces the `ca-nl/disability_amount_self` dataset
figure (7,467); `core/times_count` multiplies it by the checked count, rounded through
`ca-nl/cent_rounding`. A salary-only filer leaves the claim blank, so line 40 is 0.00.

The real part files are loaded under a test-local header and form over the Newfoundland and
Labrador package list of `support.py`. The header and the form's export are made up here, because
the shared scaffold owns them.
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
from tax_engine.domain.trace import TimesCountLine, YesOrNoCountLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    DISABILITY_AMOUNT_SELF,
    NL428_DISABILITY_AMOUNT_SELF_CLAIMED_CHECKED_LINE_40,
    NL428_DISABILITY_AMOUNT_SELF_CLAIMED_LINE_40,
    NL428_DISABILITY_AMOUNT_SELF_LINE_40,
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
LINE_PART = PARTS / "nl428_credits_line_40.yaml"
INPUT_PART = PARTS / "nl428_credits_line_40_input.yaml"
FORM = "ca-nl/nl428_credits"
IDENTIFIER = "ca-nl/nl428_disability_amount_self_line_40"

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
        - {IDENTIFIER}
        - ca-nl/disability_amount_self
        - ca-nl/nl428_disability_amount_self_claimed_checked_line_40
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_PART, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_40.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str, claim: int | None = None) -> Worksheet:
    given: list[Artifact[Decimal] | Artifact[int]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if claim is not None:
        given.append(Artifact(NL428_DISABILITY_AMOUNT_SELF_CLAIMED_LINE_40, claim))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def line_40(tmp_path: Path, salary: str, claim: int | None = None) -> Decimal:
    return _sheet(tmp_path, salary, claim).get(NL428_DISABILITY_AMOUNT_SELF_LINE_40).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_40_is_0_when_the_claim_is_left_blank(tmp_path: Path, salary: str) -> None:
    assert line_40(tmp_path, salary) == D("0.00")


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_40_is_7467_when_the_claim_is_1(tmp_path: Path, salary: str) -> None:
    assert line_40(tmp_path, salary, 1) == D("7467.00")


def test_line_40_is_0_when_the_claim_is_0(tmp_path: Path) -> None:
    assert line_40(tmp_path, "70000", 0) == D("0.00")


def test_a_claim_of_2_is_rejected_so_the_amount_cannot_be_doubled(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        line_40(tmp_path, "70000", 2)


def test_the_steps_are_the_checked_count_the_dataset_amount_and_the_product(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", 1)

    assert sheet.get(NL428_DISABILITY_AMOUNT_SELF_CLAIMED_CHECKED_LINE_40).value == 1
    assert sheet.get(DISABILITY_AMOUNT_SELF).value == D("7467")


def test_a_blank_claim_is_checked_as_0(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert sheet.get(NL428_DISABILITY_AMOUNT_SELF_CLAIMED_CHECKED_LINE_40).value == 0


def test_the_trace_records_the_yes_or_no_check_and_the_times_count_step(tmp_path: Path) -> None:
    trace = _sheet(tmp_path, "70000", 1).trace

    assert (
        YesOrNoCountLine(
            output=NL428_DISABILITY_AMOUNT_SELF_CLAIMED_CHECKED_LINE_40,
            count_kind=NL428_DISABILITY_AMOUNT_SELF_CLAIMED_LINE_40,
            count=1,
        )
        in trace
    )
    (times,) = [line for line in trace if isinstance(line, TimesCountLine)]
    assert times.output is NL428_DISABILITY_AMOUNT_SELF_LINE_40
    assert times.amount_kind is DISABILITY_AMOUNT_SELF
    assert times.amount_value == D("7467")
    assert times.count_kind is NL428_DISABILITY_AMOUNT_SELF_CLAIMED_CHECKED_LINE_40
    assert times.count == 1
    assert times.result == D("7467.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_the_three_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    count, amount, times = part["capabilities"]
    assert count["name"] == "ca/yes_or_no_count"
    assert count["consumes"] == {"count": "ca-nl/nl428_disability_amount_self_claimed_line_40"}
    assert count["blank"] == {"count": "0"}
    assert count["produces"] == {
        "output": "ca-nl/nl428_disability_amount_self_claimed_checked_line_40"
    }
    assert amount["name"] == "core/credit_amount"
    assert amount["params"] == {"amount": "ca-nl/disability_amount_self"}
    assert amount["produces"] == {"output": "ca-nl/disability_amount_self"}
    assert times["name"] == "core/times_count"
    assert times["reference"] == "40"
    assert times["title"] == "Disability amount for self"
    assert times["unit"] == "ca/cad"
    assert times["params"] == {"rounding": "ca-nl/cent_rounding"}
    assert times["consumes"] == {
        "amount": "ca-nl/disability_amount_self",
        "count": "ca-nl/nl428_disability_amount_self_claimed_checked_line_40",
    }
    assert times["produces"] == {"output": IDENTIFIER}


@pytest.mark.parametrize("kind", [DISABILITY_AMOUNT_SELF, NL428_DISABILITY_AMOUNT_SELF_LINE_40])
def test_the_amount_kinds_are_registered_non_negative_decimal_amounts(kind: AmountKind) -> None:
    assert newfoundland_kinds().kind(kind.identifier) is kind
    assert kind.value_type is Decimal
    assert non_negative(kind)
