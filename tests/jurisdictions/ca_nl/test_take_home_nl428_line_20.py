"""NL428 (2025) line 20, the spouse or common-law partner amount, as the NL take-home manifest parts
wire it.

Form text (Form NL428, CRA 5001-c-25e.txt, confirmed 2026-11-18): "Line 20 and line 58120: Line 18
minus line 19 (if negative, enter "0") (maximum $9,043) =". Line 18 is the printed base amount 9,948
(`ca-nl/spouse_amount_base`); line 19 is the optional input of its own part, a blank read as 0.

The part has three steps: `core/credit_amount` produces the base amount,
`core/subtract_not_below_zero` takes line 19 off it (rounded through `ca-nl/cent_rounding`), and
`core/capped_amount` holds the result at the printed maximum 9,043.

The real part files are loaded under a test-local header and form over the Newfoundland and
Labrador package list of `support.py`.
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
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import CappedAmountLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_SPOUSE_AMOUNT_BEFORE_MAXIMUM_LINE_20,
    NL428_SPOUSE_AMOUNT_LINE_20,
    NL428_SPOUSE_NET_INCOME_LINE_19,
    SPOUSE_AMOUNT_BASE,
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
LINE_PART = PARTS / "nl428_credits_line_20.yaml"
INPUT_PART = PARTS / "nl428_credits_line_19_input.yaml"
FORM = "ca-nl/nl428_credits"
IDENTIFIER = "ca-nl/nl428_spouse_amount_line_20"

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
        - ca-nl/nl428_spouse_amount_before_maximum_line_20
        - ca-nl/spouse_amount_base
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_PART, encoding="utf-8")
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_20.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str, spouse_net_income: str | None = None) -> Worksheet:
    given: list[Artifact[Decimal]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if spouse_net_income is not None:
        given.append(Artifact(NL428_SPOUSE_NET_INCOME_LINE_19, D(spouse_net_income)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def line_20(tmp_path: Path, salary: str, spouse_net_income: str | None = None) -> Decimal:
    return _sheet(tmp_path, salary, spouse_net_income).get(NL428_SPOUSE_AMOUNT_LINE_20).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_20_is_the_maximum_when_line_19_is_left_blank(tmp_path: Path, salary: str) -> None:
    assert line_20(tmp_path, salary) == D("9043.00")


@pytest.mark.parametrize(
    ("spouse_net_income", "expected"),
    [
        ("0", "9043.00"),
        ("905", "9043.00"),
        ("905.01", "9042.99"),
        ("5000", "4948.00"),
        ("9948", "0.00"),
        ("30000", "0.00"),
        ("-1000", "9043.00"),
    ],
)
def test_line_20_is_line_18_less_line_19_not_below_0_and_at_most_9043(
    tmp_path: Path, spouse_net_income: str, expected: str
) -> None:
    assert line_20(tmp_path, "70000", spouse_net_income) == D(expected)


def test_the_floored_zero_is_not_negative_zero(tmp_path: Path) -> None:
    assert str(line_20(tmp_path, "70000", "9948")) == "0.00"


def test_the_steps_hold_the_base_amount_and_the_difference_before_the_maximum(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", "5000")

    assert sheet.get(SPOUSE_AMOUNT_BASE).value == D("9948.00")
    assert sheet.get(NL428_SPOUSE_AMOUNT_BEFORE_MAXIMUM_LINE_20).value == D("4948.00")


def test_the_difference_is_above_the_maximum_for_a_blank_line_19(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert sheet.get(NL428_SPOUSE_AMOUNT_BEFORE_MAXIMUM_LINE_20).value == D("9948.00")
    assert sheet.get(NL428_SPOUSE_AMOUNT_LINE_20).value == D("9043.00")


def test_the_trace_records_the_subtraction_and_the_maximum(tmp_path: Path) -> None:
    trace = _sheet(tmp_path, "70000", "5000").trace

    (subtracted,) = [line for line in trace if isinstance(line, SubtractedNotBelowZeroLine)]
    assert subtracted.output is NL428_SPOUSE_AMOUNT_BEFORE_MAXIMUM_LINE_20
    assert subtracted.minuend is SPOUSE_AMOUNT_BASE
    assert subtracted.minuend_amount == D("9948.00")
    assert subtracted.subtrahend is NL428_SPOUSE_NET_INCOME_LINE_19
    assert subtracted.subtrahend_amount == D("5000")
    assert subtracted.result == D("4948.00")
    (capped,) = [line for line in trace if isinstance(line, CappedAmountLine)]
    assert capped.output is NL428_SPOUSE_AMOUNT_LINE_20
    assert capped.result == D("4948.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_the_three_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    base, subtract, capped = part["capabilities"]
    assert base["name"] == "core/credit_amount"
    assert base["params"] == {"amount": "ca-nl/spouse_amount_base"}
    assert base["produces"] == {"output": "ca-nl/spouse_amount_base"}
    assert subtract["name"] == "core/subtract_not_below_zero"
    assert "reference" not in subtract
    assert subtract["unit"] == "ca/cad"
    assert subtract["params"] == {"rounding": "ca-nl/cent_rounding"}
    assert subtract["consumes"] == {
        "amount": "ca-nl/spouse_amount_base",
        "less": "ca-nl/nl428_spouse_net_income_line_19",
    }
    assert subtract["blank"] == {"less": "0"}
    assert subtract["produces"] == {"output": "ca-nl/nl428_spouse_amount_before_maximum_line_20"}
    assert capped["name"] == "core/capped_amount"
    assert capped["reference"] == "20"
    assert "title" not in capped
    assert capped["unit"] == "ca/cad"
    assert capped["params"] == {"cap": "ca-nl/spouse_amount_maximum"}
    assert capped["consumes"] == {"base": "ca-nl/nl428_spouse_amount_before_maximum_line_20"}
    assert capped["produces"] == {"output": IDENTIFIER}


@pytest.mark.parametrize(
    "kind",
    [SPOUSE_AMOUNT_BASE, NL428_SPOUSE_AMOUNT_BEFORE_MAXIMUM_LINE_20, NL428_SPOUSE_AMOUNT_LINE_20],
)
def test_the_amount_kinds_are_registered_non_negative_decimal_amounts(kind: AmountKind) -> None:
    assert newfoundland_kinds().kind(kind.identifier) is kind
    assert kind.value_type is Decimal
    assert non_negative(kind)
