"""NL428 (2025) line 23, the amount for an eligible dependant, as the NL take-home manifest parts
wire it.

Form text (Form NL428, CRA 5001-c-25e.txt, confirmed 2026-11-18): "Line 23 and line 58160: Line 21
minus line 22 (if negative, enter "0") (maximum $9,043) =". Line 21 is the printed base amount 9,948
(`ca-nl/eligible_dependant_amount_base`); line 22 is the optional input of its own part.

The part has six steps: `core/credit_amount` produces the base amount and the maximum,
`core/subtract_not_below_zero` takes line 22 off it (rounded through `ca-nl/cent_rounding`),
`core/lesser_of` holds the result at the printed maximum 9,043, `core/amount_by_band` turns line 20
into the most line 23 may be (the `ca-nl/eligible_dependant_spouse_gate` dataset: 9,043 where line
20 is 0.00 or blank, 0 where an amount is claimed on line 20) and `core/at_most` is line 23, which
refuses a return that claims both (guide 5000-G line 30400, "If you did not claim an amount on line
30300 of your return", which line 58160 follows; NL Income Tax Act, 2000, s. 9(1)(b)). A
blank line 22 (no eligible dependant) is passed on by all of them, so line 23 is blank.

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

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import (
    AmountByBandLine,
    AtMostLine,
    LesserOfLine,
    SubtractedNotBelowZeroLine,
)
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    ELIGIBLE_DEPENDANT_AMOUNT_BASE,
    ELIGIBLE_DEPENDANT_AMOUNT_MAXIMUM,
    NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_CHECK_LINE_23,
    NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM_LINE_23,
    NL428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_23,
    NL428_ELIGIBLE_DEPENDANT_AMOUNT_MOST_LINE_23,
    NL428_ELIGIBLE_DEPENDANT_NET_INCOME_LINE_22,
    NL428_SPOUSE_NET_INCOME_LINE_19,
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
LINE_PART = PARTS / "nl428_credits_line_23.yaml"
INPUT_PART = PARTS / "nl428_credits_line_22_input.yaml"
LINE_19_INPUT_PART = PARTS / "nl428_credits_line_19_input.yaml"
LINE_20_PART = PARTS / "nl428_credits_line_20.yaml"
FORM = "ca-nl/nl428_credits"
IDENTIFIER = "ca-nl/nl428_eligible_dependant_amount_line_23"

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
        - {IDENTIFIER}
        - ca-nl/nl428_eligible_dependant_amount_before_maximum_line_23
        - ca-nl/nl428_eligible_dependant_amount_before_check_line_23
        - ca-nl/nl428_eligible_dependant_amount_most_line_23
        - ca-nl/eligible_dependant_amount_base
        - ca-nl/eligible_dependant_amount_maximum
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
    (folder / "02_input.yaml").write_text(INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "03_line_23.yaml").write_text(LINE_PART.read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "04_line_19_input.yaml").write_text(
        LINE_19_INPUT_PART.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (folder / "05_line_20.yaml").write_text(
        LINE_20_PART.read_text(encoding="utf-8"), encoding="utf-8"
    )
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
    dependant_net_income: str | None = None,
    spouse_net_income: str | None = None,
) -> Worksheet:
    given: list[Artifact[Decimal]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if dependant_net_income is not None:
        given.append(Artifact(NL428_ELIGIBLE_DEPENDANT_NET_INCOME_LINE_22, D(dependant_net_income)))
    if spouse_net_income is not None:
        given.append(Artifact(NL428_SPOUSE_NET_INCOME_LINE_19, D(spouse_net_income)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def line_23(
    tmp_path: Path,
    salary: str,
    dependant_net_income: str | None = None,
    spouse_net_income: str | None = None,
) -> Decimal:
    return (
        _sheet(tmp_path, salary, dependant_net_income, spouse_net_income)
        .get(NL428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_23)
        .value
    )


def line_23_is_blank(tmp_path: Path, salary: str) -> bool:
    return _sheet(tmp_path, salary).get(NL428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_23).is_blank


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_23_is_blank_when_line_22_is_left_blank(tmp_path: Path, salary: str) -> None:
    assert line_23_is_blank(tmp_path, salary)


@pytest.mark.parametrize(
    ("dependant_net_income", "expected"),
    [
        ("905", "9043.00"),
        ("905.01", "9042.99"),
        ("9948", "0.00"),
    ],
)
def test_line_23_is_line_18_less_line_22_not_below_0_and_at_most_9043(
    tmp_path: Path, dependant_net_income: str, expected: str
) -> None:
    assert line_23(tmp_path, "70000", dependant_net_income) == D(expected)


def test_the_floored_zero_is_not_negative_zero(tmp_path: Path) -> None:
    assert str(line_23(tmp_path, "70000", "9948")) == "0.00"


def test_the_steps_hold_the_base_amount_and_the_difference_before_the_maximum(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", "5000")

    assert sheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BASE).value == D("9948.00")
    assert sheet.get(NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM_LINE_23).value == D("4948.00")


def test_a_blank_line_22_blanks_the_difference_as_well(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert sheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BASE).value == D("9948.00")
    assert sheet.get(ELIGIBLE_DEPENDANT_AMOUNT_MAXIMUM).value == D("9043.00")
    assert sheet.get(NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM_LINE_23).is_blank


def test_the_trace_records_the_subtraction_the_lesser_of_and_the_check(tmp_path: Path) -> None:
    trace = _sheet(tmp_path, "70000", "5000").trace

    (subtracted,) = [line for line in trace if isinstance(line, SubtractedNotBelowZeroLine)]
    assert subtracted.output is NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM_LINE_23
    assert subtracted.minuend is ELIGIBLE_DEPENDANT_AMOUNT_BASE
    assert subtracted.minuend_amount == D("9948.00")
    assert subtracted.subtrahend is NL428_ELIGIBLE_DEPENDANT_NET_INCOME_LINE_22
    assert subtracted.subtrahend_amount == D("5000")
    assert subtracted.result == D("4948.00")
    (lesser,) = [line for line in trace if isinstance(line, LesserOfLine)]
    assert lesser.output is NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_CHECK_LINE_23
    assert lesser.result == D("4948.00")
    (at_most,) = [line for line in trace if isinstance(line, AtMostLine)]
    assert at_most.output is NL428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_23
    assert at_most.amount_value == D("4948.00")
    assert at_most.bound_value == D("9043.00")


@pytest.mark.parametrize(
    ("spouse_net_income", "most"),
    [
        (None, "9043.00"),
        ("9948", "9043.00"),
        ("20000", "9043.00"),
        ("9947.99", "0.00"),
        ("0", "0.00"),
    ],
)
def test_the_most_line_23_may_be_is_the_maximum_unless_an_amount_is_claimed_on_line_20(
    tmp_path: Path, spouse_net_income: str | None, most: str
) -> None:
    # A line 22 of 9,948 makes line 23 0.00, so a claim on line 20 is not refused here.
    sheet = _sheet(tmp_path, "70000", "9948", spouse_net_income)

    assert sheet.get(NL428_ELIGIBLE_DEPENDANT_AMOUNT_MOST_LINE_23).value == D(most)


@pytest.mark.parametrize("spouse_net_income", ["9948", "20000"])
def test_line_23_is_given_when_line_20_comes_to_0(tmp_path: Path, spouse_net_income: str) -> None:
    assert line_23(tmp_path, "70000", "5000", spouse_net_income) == D("4948.00")


def test_line_23_is_given_with_no_spouse_claim_at_all(tmp_path: Path) -> None:
    assert line_23(tmp_path, "70000", "5000") == D("4948.00")


@pytest.mark.parametrize(
    ("spouse_net_income", "dependant_net_income"),
    [("0", "0"), ("5000", "5000"), ("9947.99", "9947.99"), ("9947.99", "0"), ("-500", "0")],
)
def test_a_return_claiming_both_line_20_and_line_23_is_refused(
    tmp_path: Path, spouse_net_income: str, dependant_net_income: str
) -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(tmp_path, "70000", dependant_net_income, spouse_net_income)


def test_a_line_20_claim_with_a_line_23_of_0_is_not_refused(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "9948", "0")

    assert sheet.get(NL428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_23).value == D("0.00")


def test_a_line_20_claim_with_line_22_blank_is_not_refused(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", None, "0")

    assert sheet.get(NL428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_23).is_blank


def test_the_trace_records_the_gate_on_line_20(tmp_path: Path) -> None:
    trace = _sheet(tmp_path, "70000", "5000", "20000").trace

    (gate,) = [line for line in trace if isinstance(line, AmountByBandLine)]
    assert gate.output is NL428_ELIGIBLE_DEPENDANT_AMOUNT_MOST_LINE_23
    assert gate.result == D("9043.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_the_six_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    base, maximum, subtract, lesser, gate, check = part["capabilities"]
    assert base["name"] == "core/credit_amount"
    assert base["params"] == {"amount": "ca-nl/eligible_dependant_amount_base"}
    assert base["produces"] == {"output": "ca-nl/eligible_dependant_amount_base"}
    assert maximum["name"] == "core/credit_amount"
    assert maximum["params"] == {"amount": "ca-nl/eligible_dependant_amount_maximum"}
    assert maximum["produces"] == {"output": "ca-nl/eligible_dependant_amount_maximum"}
    assert subtract["name"] == "core/subtract_not_below_zero"
    assert "reference" not in subtract
    assert subtract["unit"] == "ca/cad"
    assert subtract["params"] == {"rounding": "ca-nl/cent_rounding"}
    assert subtract["consumes"] == {
        "amount": "ca-nl/eligible_dependant_amount_base",
        "less": "ca-nl/nl428_eligible_dependant_net_income_line_22",
    }
    assert subtract["blank"] == {"less": "pass_on"}
    assert subtract["produces"] == {
        "output": "ca-nl/nl428_eligible_dependant_amount_before_maximum_line_23"
    }
    assert lesser["name"] == "core/lesser_of"
    assert "reference" not in lesser
    assert "title" not in lesser
    assert lesser["unit"] == "ca/cad"
    assert lesser["consumes"] == {
        "amounts": [
            "ca-nl/nl428_eligible_dependant_amount_before_maximum_line_23",
            "ca-nl/eligible_dependant_amount_maximum",
        ]
    }
    assert lesser["blank"] == {"amounts": "pass_on"}
    assert lesser["produces"] == {
        "output": "ca-nl/nl428_eligible_dependant_amount_before_check_line_23"
    }
    assert gate["name"] == "core/amount_by_band"
    assert "reference" not in gate
    assert gate["unit"] == "ca/cad"
    assert gate["params"] == {"table": "ca-nl/eligible_dependant_spouse_gate"}
    assert gate["consumes"] == {"base": "ca-nl/nl428_spouse_amount_line_20"}
    assert gate["blank"] == {"base": "0"}
    assert gate["produces"] == {"output": "ca-nl/nl428_eligible_dependant_amount_most_line_23"}
    assert check["name"] == "core/at_most"
    assert check["reference"] == "23"
    assert "title" not in check
    assert check["unit"] == "ca/cad"
    assert check["consumes"] == {
        "amount": "ca-nl/nl428_eligible_dependant_amount_before_check_line_23",
        "bound": "ca-nl/nl428_eligible_dependant_amount_most_line_23",
    }
    assert check["blank"] == {"amount": "pass_on"}
    assert check["produces"] == {"output": IDENTIFIER}


@pytest.mark.parametrize(
    "kind",
    [
        ELIGIBLE_DEPENDANT_AMOUNT_BASE,
        ELIGIBLE_DEPENDANT_AMOUNT_MAXIMUM,
        NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM_LINE_23,
        NL428_ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_CHECK_LINE_23,
        NL428_ELIGIBLE_DEPENDANT_AMOUNT_MOST_LINE_23,
        NL428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_23,
    ],
)
def test_the_amount_kinds_are_registered_non_negative_decimal_amounts(kind: AmountKind) -> None:
    assert newfoundland_kinds().kind(kind.identifier) is kind
    assert kind.value_type is Decimal
    assert non_negative(kind)
