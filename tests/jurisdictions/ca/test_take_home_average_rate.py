"""The take-home average rate, shared by Ontario, Alberta, British Columbia, Manitoba,
Newfoundland and Labrador and Saskatchewan (2025 and 2026).

The federal form `ca/take_home_average_rate` adds the income tax (T1 line 43500 "Total payable"),
the CPP (Schedule 8 lines 25 and 28) and the EI premium (T2204 line 16), divides the total by the
salary (T1 line 10100) and rounds once with `ca/take_home_average_rate_rounding` (half-up to
0.0001). No form prints any of it, so its steps carry no title and no reference. Each province's
return summary reads the one export `ca/average_tax_rate` into its own
`<province>/average_tax_rate`.
The figures run through the real engine; the deductions at $70,000 are the take-home answer's own
and the rates are the quotients checked by hand: 16,531.32 / 70,000 = 0.236160 -> 0.2362 (Ontario
2025).
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import QuotientLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
FORM = "ca/take_home_average_rate"
AVERAGE = "ca/average_tax_rate"
DEDUCTIONS = "ca/return_total_deductions"
PROVINCES = ("on", "ab", "bc", "mb", "nl", "sk")

# province, year, salary $70,000, take-home deductions, average rate.
ANCHORS = [
    ("on", 2025, "16531.32", "0.2362"),
    ("on", 2026, "16213.75", "0.2316"),
    ("ab", 2025, "16217.99", "0.2317"),
    ("ab", 2026, "15892.80", "0.2270"),
    ("bc", 2025, "15782.26", "0.2255"),
    ("bc", 2026, "15651.85", "0.2236"),
    ("mb", 2025, "18367.46", "0.2624"),
    ("mb", 2026, "18100.68", "0.2586"),
    ("nl", 2025, "18767.36", "0.2681"),
    ("nl", 2026, "18297.00", "0.2614"),
    ("sk", 2025, "17712.17", "0.2530"),
    ("sk", 2026, "17330.69", "0.2476"),
]


def _worksheets(province: str, year: int, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode(f"CA-{province.upper()}"),
            year,
            (Artifact(EMPLOYMENT_INCOME, D(salary)),),
        )
    )


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(("province", "year", "deductions", "rate"), ANCHORS)
def test_the_average_rate_is_the_deductions_over_the_salary_half_up_to_four_places(
    province: str, year: int, deductions: str, rate: str
) -> None:
    (sheet,) = _worksheets(province, year, "70000")[FORM]

    assert _value(sheet, DEDUCTIONS) == D(deductions)
    assert _value(sheet, AVERAGE) == D(rate)
    assert (D(deductions) / D("70000")).quantize(D("0.0001"), rounding="ROUND_HALF_UP") == D(rate)


@pytest.mark.parametrize("province", PROVINCES)
def test_the_return_summary_reads_the_shared_rate_as_it_is(province: str) -> None:
    worksheets = _worksheets(province, 2025, "70000")
    (shared,) = worksheets[FORM]
    (summary,) = worksheets[f"ca-{province}/return"]

    assert _value(summary, f"ca-{province}/average_tax_rate") == _value(shared, AVERAGE)


@pytest.mark.parametrize("salary", ["0", "100"])
def test_a_salary_with_no_deductions_gives_a_rate_of_zero(salary: str) -> None:
    (sheet,) = _worksheets("on", 2025, salary)[FORM]

    assert _value(sheet, AVERAGE) == D("0")


def test_the_trace_records_one_quotient_line_of_the_deductions_over_the_salary() -> None:
    (sheet,) = _worksheets("on", 2025, "70000")[FORM]
    kinds = bundled_kinds()

    (line,) = [
        line
        for line in sheet.trace
        if isinstance(line, QuotientLine) and line.output == kinds.kind(AVERAGE)
    ]
    assert line.dividend == kinds.kind(DEDUCTIONS)
    assert line.dividend_amount == D("16531.32")
    assert line.divisor_amount == D("70000")
    assert line.result == D("0.2362")


def test_the_sentence_names_the_quotient_and_the_rounding() -> None:
    (sheet,) = _worksheets("on", 2025, "70000")[FORM]

    text = "\n".join(EnglishTraceRenderer().render_all(sheet.trace, sheet))

    assert re.search(
        r"\(CA\$16531\.32\) divided by [^()]*\(CA\$70000\.00\) gives 23\.62% "
        r"\(rounded half-up to 0\.0001\)",
        text,
    )


def test_the_sentence_says_the_divisor_is_zero_at_a_salary_of_zero() -> None:
    (sheet,) = _worksheets("on", 2025, "0")[FORM]

    text = "\n".join(EnglishTraceRenderer().render_all(sheet.trace, sheet))

    assert re.search(r"divided by [^()]*\(CA\$0\.00\), which is zero, gives ", text)


def test_no_step_of_the_form_has_a_title_or_a_reference() -> None:
    (sheet,) = _worksheets("on", 2025, "70000")[FORM]
    label = bundled_kinds().kind(AVERAGE).label

    assert sheet.title(label) is None
    assert sheet.reference(label) is None
