"""NL428 (2025) line 40, the disability amount for self, as the NL take-home manifest parts wire it.

Form text (Form NL428, CRA 5001-c-25e.txt, confirmed 2026-11-18): "Line 40 and line 58440:
Disability amount for self (claim $7,467 or, if you were under 18 years of age, use Worksheet
NL428)". The under-18 branch is Worksheet NL428 line 58440 line 7 (5001-d-25e.txt, confirmed
2026-11-19), built in the `ca-nl/nl428_worksheet` form.

The part has six steps: `ca/yes_or_no_count` reads the optional claim (blank read as 0) and
refuses a count above 1; `core/credit_amount` produces the `ca-nl/disability_amount_self` dataset
figure (7,467); `ca/yes_or_no_count` reads the shared under-18 answer (blank read as 0, so 18 or
over); `core/record_total` reads Worksheet NL428 line 7; `core/choose_by_count` picks 7,467 for a
filer 18 or over and the worksheet amount for one under 18; `core/times_count` multiplies the
chosen amount by the checked claim, rounded through `ca-nl/cent_rounding`. A salary-only filer
leaves the claim blank, so line 40 is 0.00.

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

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError, NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import ChosenByCountLine, TimesCountLine, YesOrNoCountLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    DISABILITY_SELF_CARE_EXPENSES,
    UNDER_18_ON_DECEMBER_31,
    UNDER_18_ON_DECEMBER_31_CHECKED,
)
from tax_engine.jurisdictions.ca_nl.catalog import (
    DISABILITY_AMOUNT_SELF,
    NL428_DISABILITY_AMOUNT_SELF_BASIS_LINE_40,
    NL428_DISABILITY_AMOUNT_SELF_CLAIMED_CHECKED_LINE_40,
    NL428_DISABILITY_AMOUNT_SELF_CLAIMED_LINE_40,
    NL428_DISABILITY_AMOUNT_SELF_LINE_40,
    NL428_DISABILITY_AMOUNT_SELF_WORKSHEET_LINE_40,
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
LINE_PART = PARTS / "nl428_credits_line_40.yaml"
INPUT_PART = PARTS / "nl428_credits_line_40_input.yaml"
WORKSHEET_PARTS = (
    "worksheet_nl428_line_58440_input.yaml",
    "worksheet_nl428_line_3_input.yaml",
    "worksheet_nl428_58440_line_5.yaml",
    "worksheet_nl428_58440_line_6.yaml",
    "worksheet_nl428_58440_line_7.yaml",
)
FORM = "ca-nl/nl428_credits"
IDENTIFIER = "ca-nl/nl428_disability_amount_self_line_40"

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
WORKSHEET_FORM_PART = dedent("""\
    form:
      name: ca-nl/nl428_worksheet
      required: true
      exports:
        - ca-nl/worksheet_nl428_disability_self_line_7
    """)
FORM_PART = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {IDENTIFIER}
        - ca-nl/disability_amount_self
        - ca-nl/nl428_disability_amount_self_claimed_checked_line_40
        - ca-nl/nl428_disability_amount_self_worksheet_line_40
        - ca-nl/nl428_disability_amount_self_basis_line_40
        - ca/under_18_on_december_31_checked
    """)


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
    (folder / "01_worksheet_form.yaml").write_text(WORKSHEET_FORM_PART, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    for number, name in enumerate(WORKSHEET_PARTS, start=10):
        (folder / f"{number}_{name}").write_text(
            (PARTS / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
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


def _sheet(
    tmp_path: Path,
    salary: str,
    claim: int | None = None,
    under_18: int | None = None,
    care_expenses: str | None = None,
) -> Worksheet:
    given: list[Artifact[Decimal] | Artifact[int]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if claim is not None:
        given.append(Artifact(NL428_DISABILITY_AMOUNT_SELF_CLAIMED_LINE_40, claim))
    if under_18 is not None:
        given.append(Artifact(UNDER_18_ON_DECEMBER_31, under_18))
    if care_expenses is not None:
        given.append(Artifact(DISABILITY_SELF_CARE_EXPENSES, D(care_expenses)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def line_40(
    tmp_path: Path,
    salary: str,
    claim: int | None = None,
    under_18: int | None = None,
    care_expenses: str | None = None,
) -> Decimal:
    sheet = _sheet(tmp_path, salary, claim, under_18, care_expenses)
    return sheet.get(NL428_DISABILITY_AMOUNT_SELF_LINE_40).value


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_40_is_0_when_the_claim_is_left_blank(tmp_path: Path, salary: str) -> None:
    assert line_40(tmp_path, salary) == D("0.00")


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_40_is_7467_when_the_claim_is_1(tmp_path: Path, salary: str) -> None:
    assert line_40(tmp_path, salary, 1) == D("7467.00")


def test_line_40_is_0_when_the_claim_is_0(tmp_path: Path) -> None:
    assert line_40(tmp_path, "70000", 0) == D("0.00")


def test_a_claim_of_2_is_rejected_so_the_amount_cannot_be_doubled(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        line_40(tmp_path, "70000", 2)


def test_the_steps_are_the_checked_count_the_dataset_amount_and_the_basis(
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
    assert times.amount_kind is NL428_DISABILITY_AMOUNT_SELF_BASIS_LINE_40
    assert times.amount_value == D("7467.00")
    assert times.count_kind is NL428_DISABILITY_AMOUNT_SELF_CLAIMED_CHECKED_LINE_40
    assert times.count == 1
    assert times.result == D("7467.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_the_six_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    count, amount, under_18, worksheet, choose, times = part["capabilities"]
    assert count["name"] == "ca/yes_or_no_count"
    assert count["consumes"] == {"count": "ca-nl/nl428_disability_amount_self_claimed_line_40"}
    assert count["blank"] == {"count": "0"}
    assert count["produces"] == {
        "output": "ca-nl/nl428_disability_amount_self_claimed_checked_line_40"
    }
    assert amount["name"] == "core/credit_amount"
    assert amount["params"] == {"amount": "ca-nl/disability_amount_self"}
    assert amount["produces"] == {"output": "ca-nl/disability_amount_self"}
    assert under_18["name"] == "ca/yes_or_no_count"
    assert under_18["consumes"] == {"count": "ca/under_18_on_december_31"}
    assert under_18["blank"] == {"count": "0"}
    assert under_18["produces"] == {"output": "ca/under_18_on_december_31_checked"}
    assert worksheet["name"] == "core/record_total"
    assert worksheet["unit"] == "ca/cad"
    assert worksheet["consumes"] == {
        "records": "ca-nl/nl428_worksheet.worksheet_nl428_disability_self_line_7"
    }
    assert worksheet["produces"] == {
        "output": "ca-nl/nl428_disability_amount_self_worksheet_line_40"
    }
    assert choose["name"] == "core/choose_by_count"
    assert choose["unit"] == "ca/cad"
    assert choose["consumes"] == {
        "count": "ca/under_18_on_december_31_checked",
        "when_none": "ca-nl/disability_amount_self",
        "when_any": "ca-nl/nl428_disability_amount_self_worksheet_line_40",
    }
    assert choose["produces"] == {"output": "ca-nl/nl428_disability_amount_self_basis_line_40"}
    assert times["name"] == "core/times_count"
    assert times["reference"] == "40"
    assert times["title"] == "Disability amount for self"
    assert times["unit"] == "ca/cad"
    assert times["params"] == {"rounding": "ca-nl/cent_rounding"}
    assert times["consumes"] == {
        "amount": "ca-nl/nl428_disability_amount_self_basis_line_40",
        "count": "ca-nl/nl428_disability_amount_self_claimed_checked_line_40",
    }
    assert times["produces"] == {"output": IDENTIFIER}


@pytest.mark.parametrize(
    "kind",
    [
        DISABILITY_AMOUNT_SELF,
        NL428_DISABILITY_AMOUNT_SELF_LINE_40,
        NL428_DISABILITY_AMOUNT_SELF_WORKSHEET_LINE_40,
        NL428_DISABILITY_AMOUNT_SELF_BASIS_LINE_40,
    ],
)
def test_the_amount_kinds_are_registered_non_negative_decimal_amounts(kind: AmountKind) -> None:
    assert newfoundland_kinds().kind(kind.identifier) is kind
    assert kind.value_type is Decimal
    assert non_negative(kind)


# The under-18 branch: (care expenses, Worksheet NL428 line 7), hand-computed from the printed
# figures, not a CRA example. Line 5 = expenses less 2,987 (not below 0); line 6 = 3,514 less line
# 5 (not below 0); line 7 = 7,467 plus line 6.
UNDER_18_CASES = [
    (None, "10981.00"),
    ("4987", "8981.00"),
    ("6501", "7467.00"),
]


@pytest.mark.parametrize(("care", "amount"), UNDER_18_CASES)
def test_line_40_for_a_filer_under_18_who_claims_is_the_worksheet_line_7(
    tmp_path: Path, care: str | None, amount: str
) -> None:
    assert line_40(tmp_path, "70000", 1, 1, care) == D(amount)


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_the_under_18_amount_does_not_depend_on_the_salary(tmp_path: Path, salary: str) -> None:
    assert line_40(tmp_path, salary, 1, 1, "4987") == D("8981.00")


@pytest.mark.parametrize("claim", [None, 0])
def test_line_40_is_0_for_a_filer_under_18_who_does_not_claim(
    tmp_path: Path, claim: int | None
) -> None:
    assert line_40(tmp_path, "70000", claim, 1, "4987") == D("0.00")


@pytest.mark.parametrize("under_18", [None, 0])
def test_a_blank_or_0_under_18_answer_keeps_the_flat_7467(
    tmp_path: Path, under_18: int | None
) -> None:
    assert line_40(tmp_path, "70000", 1, under_18, "4987") == D("7467.00")


def test_an_under_18_answer_of_2_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        line_40(tmp_path, "70000", 1, 2)


def test_a_negative_care_expense_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(NegativeArtifactError):
        line_40(tmp_path, "70000", 1, 1, "-1")


def test_the_worksheet_amount_and_the_basis_are_kept_as_steps(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", 1, 1, "4987")

    assert sheet.get(UNDER_18_ON_DECEMBER_31_CHECKED).value == 1
    assert sheet.get(NL428_DISABILITY_AMOUNT_SELF_WORKSHEET_LINE_40).value == D("8981.00")
    assert sheet.get(NL428_DISABILITY_AMOUNT_SELF_BASIS_LINE_40).value == D("8981.00")


def test_a_blank_under_18_answer_is_checked_as_0(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", 1)

    assert sheet.get(UNDER_18_ON_DECEMBER_31_CHECKED).value == 0
    assert sheet.get(NL428_DISABILITY_AMOUNT_SELF_BASIS_LINE_40).value == D("7467.00")


def test_the_trace_records_which_amount_the_under_18_answer_chose(tmp_path: Path) -> None:
    trace = _sheet(tmp_path, "70000", 1, 1, "4987").trace

    (chosen,) = [line for line in trace if isinstance(line, ChosenByCountLine)]
    assert chosen.output is NL428_DISABILITY_AMOUNT_SELF_BASIS_LINE_40
    assert chosen.count_kind is UNDER_18_ON_DECEMBER_31_CHECKED
    assert chosen.count == 1
    assert chosen.chosen_kind is NL428_DISABILITY_AMOUNT_SELF_WORKSHEET_LINE_40
    assert chosen.chosen_value == D("8981.00")
