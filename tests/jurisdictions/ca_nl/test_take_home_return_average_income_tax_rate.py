"""The Newfoundland and Labrador take-home return summary's average income tax rate (2025).

Owner ruling (12 Nov 2026): the average rate is income tax divided by salary, not all deductions
(CPP and EI are not income tax). Income tax is T1 line 43500 "Total payable" (5006-R-25E: the
federal plus the Newfoundland and Labrador income tax, `ca/total_payable`); the salary is
`ca/employment_income`. The form prints no such figure, so the step has no title and no reference.

`return.yaml` mirrors the Saskatchewan and Manitoba parts. T1 exports `ca/total_payable`, and
another form's export is read only as a record list, so the return reads it with
`core/record_total` from `ca/t1_tax_and_credits.total_payable` into the return's own
`ca/total_payable` (the kind T1 produced, on the return's own sheet, so no new kind is declared for
it). Then `core/divide` takes `ca/total_payable` divided by `ca/employment_income`, rounded once by
the `ca-nl/rate_rounding` dataset (half-up to 0.0001), and produces `ca-nl/average_income_tax_rate`
(unit `core/percent`, non-negative). A salary of 0 gives a rate of 0, not an error.

The test composes the real Newfoundland and Labrador salary part and the real `return.yaml`; the
header, the declaration of the T1 tax and credits form and the steps producing its two exports are
made up here, because the shared scaffold and the T1 form own them: the stand-in steps take a given
`ca/total_credits` off the salary, so line 43500 is the salary less those credits. The worked
quotients are checked by hand: 11,497.09 / 70,000 = 0.164244..., half-up to 0.1642 (16.42%);
158.09 / 20,000 = 0.0079045, half-up to 0.0079 (0.79%).
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import QuotientLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.net_tax import TOTAL_PAYABLE
from tax_engine.jurisdictions.ca.catalog.refund import TOTAL_CREDITS
from tax_engine.jurisdictions.ca_nl.catalog import AVERAGE_INCOME_TAX_RATE
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
RETURN_PART = NL_PARTS / "return.yaml"

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/refund_or_balance_owing
      - ca-nl/average_income_tax_rate
    capabilities: []
    """)
T1_FORM = dedent("""\
    form:
      name: ca/t1_tax_and_credits
      required: true
      exports:
        - ca/refund_or_balance_owing
        - ca/total_payable
    capabilities: []
    """)
CREDITS_INPUT = dedent("""\
    inputs:
      - name: ca/total_credits
        title: "Total credits"
        reference: "48200"
        unit: ca/cad
        required: true
    """)
# The stand-ins for the T1 steps: line 43500 and line 167 are each the salary less the credits.
T1_STEPS = dedent("""\
    form:
      name: ca/t1_tax_and_credits
    capabilities:
      - name: core/subtract
        unit: ca/cad
        params:
          rounding: ca/cent_rounding
        consumes:
          amount: ca/employment_income
          less: ca/total_credits
        produces:
          output: ca/total_payable
      - name: core/subtract
        unit: ca/cad
        params:
          rounding: ca/cent_rounding
        consumes:
          amount: ca/employment_income
          less: ca/total_credits
        produces:
          output: ca/refund_or_balance_owing
    """)

# salary, credits, line 43500, the rate: the two figures the ticket names and a salary of 0.
CASES = [
    # 11,497.09 / 70,000 = 0.164244..., half-up to 0.1642 (16.42%).
    ("70000", "58502.91", "11497.09", "0.1642"),
    # 158.09 / 20,000 = 0.0079045, half-up to 0.0079 (0.79%).
    ("20000", "19841.91", "158.09", "0.0079"),
    # 0.00 / 10,000 = 0.
    ("10000", "10000.00", "0.00", "0.0000"),
]


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Newfoundland and Labrador manifest of a test header, the T1 form
    declaration, the stand-in steps and the real salary and return parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    texts = [
        ("00_header.yaml", HEADER),
        ("01_t1_form.yaml", T1_FORM),
        ("02_credits_input.yaml", CREDITS_INPUT),
        ("03_t1_steps.yaml", T1_STEPS),
        ("04_salary.yaml", (NL_PARTS / "salary.yaml").read_text(encoding="utf-8")),
        ("05_return.yaml", RETURN_PART.read_text(encoding="utf-8")),
    ]
    for name, text in texts:
        (folder / name).write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, credits: str) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(TOTAL_CREDITS, D(credits))]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets["ca-nl/return"]
    return sheet


@pytest.mark.parametrize(("salary", "credits", "total_payable", "rate"), CASES)
def test_the_average_rate_is_total_payable_over_salary_half_up_to_four_places(
    tmp_path: Path, salary: str, credits: str, total_payable: str, rate: str
) -> None:
    sheet = _sheet(tmp_path, salary, credits)

    assert sheet.get(TOTAL_PAYABLE).value == D(total_payable)
    average = sheet.get(AVERAGE_INCOME_TAX_RATE).value
    assert average == D(rate)
    assert average.as_tuple().exponent == -4
    assert average == (D(total_payable) / D(salary)).quantize(D("0.0001"), rounding="ROUND_HALF_UP")


def test_a_quotient_on_a_half_rounds_up(tmp_path: Path) -> None:
    # 1,000.05 / 20,000 = 0.0500025, half-up to 0.0500; 1,001 / 20,000 = 0.05005, half-up to 0.0501.
    sheet = _sheet(tmp_path, "20000", "18999.00")

    assert sheet.get(TOTAL_PAYABLE).value == D("1001.00")
    assert sheet.get(AVERAGE_INCOME_TAX_RATE).value == D("0.0501")


def test_a_salary_of_zero_gives_a_rate_of_zero_not_an_error(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "0", "0.00")

    assert sheet.get(AVERAGE_INCOME_TAX_RATE).value == D("0")


def test_the_trace_records_one_quotient_line_with_the_rate_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "58502.91")

    (line,) = [
        line
        for line in sheet.trace
        if isinstance(line, QuotientLine) and line.output == AVERAGE_INCOME_TAX_RATE
    ]
    assert line.dividend == TOTAL_PAYABLE
    assert line.dividend_amount == D("11497.09")
    assert line.divisor == EMPLOYMENT_INCOME
    assert line.divisor_amount == D("70000")
    assert line.result == D("0.1642")
    assert line.label == AVERAGE_INCOME_TAX_RATE.label


def test_the_sentence_names_total_payable_over_salary_and_its_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "58502.91")

    text = "\n".join(EnglishTraceRenderer().render_all(sheet.trace, sheet))

    # The step has no title and no reference, so its figures are named by their labels.
    assert re.search(
        r"\(CA\$11497\.09\) divided by [^()]*\(CA\$70000\.00\) gives 16\.42% "
        r"\(rounded half-up to 0\.0001\)",
        text,
    )


def test_the_sentence_says_the_divisor_is_zero_at_a_salary_of_zero(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "0", "0.00")

    text = "\n".join(EnglishTraceRenderer().render_all(sheet.trace, sheet))

    assert re.search(r"divided by [^()]*\(CA\$0\.00\), which is zero, gives ", text)


def test_the_step_has_no_title_and_no_reference(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "58502.91")

    assert sheet.title(AVERAGE_INCOME_TAX_RATE.label) is None
    assert sheet.reference(AVERAGE_INCOME_TAX_RATE.label) is None


def test_the_average_rate_kind_is_registered_and_non_negative() -> None:
    kind = newfoundland_kinds().kind("ca-nl/average_income_tax_rate")

    assert kind is AVERAGE_INCOME_TAX_RATE
    assert kind.identifier == "ca-nl/average_income_tax_rate"
    assert non_negative(kind) is True


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(RETURN_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _producing(output: str) -> dict[str, Any]:
    (step,) = [step for step in _steps() if step["produces"]["output"] == output]
    return step


def test_the_return_part_reads_total_payable_and_divides_it_by_the_salary() -> None:
    total = _producing("ca/total_payable")
    divide = _producing("ca-nl/average_income_tax_rate")

    assert total["name"] == "core/record_total"
    assert total["unit"] == "ca/cad"
    assert total["consumes"] == {"records": "ca/t1_tax_and_credits.total_payable"}
    assert divide["name"] == "core/divide"
    assert divide["unit"] == "core/percent"
    assert divide["params"] == {"rounding": "ca-nl/rate_rounding"}
    assert divide["consumes"] == {
        "dividend": "ca/total_payable",
        "divisor": "ca/employment_income",
    }


def test_the_two_steps_carry_no_title_and_no_reference() -> None:
    for output in ("ca/total_payable", "ca-nl/average_income_tax_rate"):
        step = _producing(output)
        assert "title" not in step
        assert "reference" not in step
