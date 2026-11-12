"""The Ontario take-home return summary's average income tax rate: total income tax over salary.

Owner ruling (12 Nov 2026): the average rate is income tax divided by salary, not all
deductions (CPP and EI are not income tax). Income tax is T1 line 43500 "Total payable" (5006-R-25E:
federal plus Ontario income tax, `ca/total_payable`), the salary is `ca/employment_income`. The form
prints no such figure, so the step has no title and no reference.

The return summary (`ca-on/return`) holds three steps for it. T1 exports `ca/total_payable`, and
another form's export is read only as a record, so the return reads it with `core/record_total`
from `ca/t1_tax_and_credits.total_payable` into the return's own `ca/total_payable` (the way it
reads `ca/refund_or_balance_owing`; the read step produces the kind T1 produced, on the return's
own sheet, so no new kind is declared for it). Then `core/divide` takes `ca/total_payable` ÷
`ca/employment_income`, rounded once by the `ca-on/rate_rounding` dataset (half-up to 0.0001), and
produces `ca-on/average_income_tax_rate` (unit `core/percent`, non-negative), which is added to the
manifest `outputs`. A salary of 0 gives a rate of 0, not an error.

Worked figures (salary only, Ontario resident, single, basic credits, 2025):
$70,000: 11,497.09 / 70,000 = 0.164244..., half-up to 0.1642 (16.42%);
$20,000: 158.09 / 20,000 = 0.0079045, half-up to 0.0079 (0.79%);
$275,000: 101,743.28 / 275,000 = 0.369975..., half-up to 0.3700 (37.00%).
The $20,000 and $275,000 figures are the engine's own total payable (recorded by a run of the real
parts) and the quotient was re-checked by hand.

The line test composes the real header, the real T1 tax and credits form and the real parts, as the
line 167 test does, with the real return part. The take-home figure of $70,000 (README: 53,468.68,
that is salary less CPP, EI and total tax, a subtraction done outside the engine) is pinned at the
end, so the new step changes none of its terms.

The English sentence prints the result as the percentage the form style prints, "16.42%", because
the step's unit is `core/percent`.
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import QuotientLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import AVERAGE_INCOME_TAX_RATE
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.jurisdictions.ca_on.test_take_home_t1_tax_and_credits_line_167 import (
    PARTS,
    REAL_FORM,
    REAL_HEADER,
)
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"
AVERAGE_RATE = "ca-on/average_income_tax_rate"
TOTAL_PAYABLE = "ca/total_payable"
LINE_167 = "ca/refund_or_balance_owing"


def _return_sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(REAL_HEADER, REAL_FORM, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[RETURN]
    return sheet


def _rate(take_home_service: TakeHomeService, salary: str) -> Decimal:
    return _return_sheet(take_home_service, salary).get(AVERAGE_INCOME_TAX_RATE).value


@pytest.mark.parametrize(
    ("salary", "total_payable", "rate"),
    [
        # 11,497.09 / 70,000 = 0.164244..., half-up to 0.1642 (16.42%).
        ("70000", "11497.09", "0.1642"),
        # 158.09 / 20,000 = 0.0079045, half-up to 0.0079 (0.79%).
        ("20000", "158.09", "0.0079"),
        # 101,743.28 / 275,000 = 0.369975..., half-up to 0.3700 (37.00%).
        ("275000", "101743.28", "0.3700"),
    ],
)
def test_the_average_rate_is_total_payable_over_salary_half_up_to_four_places(
    take_home_service: TakeHomeService, salary: str, total_payable: str, rate: str
) -> None:
    sheet = _return_sheet(take_home_service, salary)

    assert sheet.get(bundled_kinds().kind(TOTAL_PAYABLE)).value == D(total_payable)
    average = sheet.get(AVERAGE_INCOME_TAX_RATE).value
    assert average == D(rate)
    assert average.as_tuple().exponent == -4
    assert average == (D(total_payable) / D(salary)).quantize(D("0.0001"), rounding="ROUND_HALF_UP")


def test_the_average_rate_at_70000_is_0_1642(take_home_service: TakeHomeService) -> None:
    assert _rate(take_home_service, "70000") == D("0.1642")


@pytest.mark.parametrize("salary", ["10000", "35000", "70000", "100000", "150000", "275000"])
def test_the_average_rate_is_total_payable_over_salary_read_from_the_sheet(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = _return_sheet(take_home_service, salary)
    total_payable = sheet.get(bundled_kinds().kind(TOTAL_PAYABLE)).value

    assert sheet.get(AVERAGE_INCOME_TAX_RATE).value == (total_payable / D(salary)).quantize(
        D("0.0001"), rounding="ROUND_HALF_UP"
    )


def test_a_salary_of_zero_gives_a_rate_of_zero_not_an_error(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _return_sheet(take_home_service, "0")

    assert sheet.get(AVERAGE_INCOME_TAX_RATE).value == D("0")
    assert sheet.get(bundled_kinds().kind(TOTAL_PAYABLE)).value == D("0")


def test_the_trace_records_one_quotient_line_with_the_rate_rounding(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _return_sheet(take_home_service, "70000")

    (line,) = [
        line
        for line in sheet.trace
        if isinstance(line, QuotientLine) and line.output == AVERAGE_INCOME_TAX_RATE
    ]
    assert line.dividend == bundled_kinds().kind(TOTAL_PAYABLE)
    assert line.dividend_amount == D("11497.09")
    assert line.divisor == EMPLOYMENT_INCOME
    assert line.divisor_amount == D("70000")
    assert line.result == D("0.1642")
    assert line.label == AVERAGE_INCOME_TAX_RATE.label


def test_the_sentence_names_total_payable_over_salary_and_its_rounding(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _return_sheet(take_home_service, "70000")

    text = "\n".join(EnglishTraceRenderer().render_all(sheet.trace, sheet))

    # "<dividend figure> divided by <divisor figure> gives <result> (<rounding>)"; the step has no
    # title and no reference, so its figures are named by their labels.
    assert re.search(
        r"\(CA\$11497\.09\) divided by [^()]*\(CA\$70000\.00\) gives 16\.42% "
        r"\(rounded half-up to 0\.0001\)",
        text,
    )


def test_the_sentence_says_the_divisor_is_zero_at_a_salary_of_zero(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _return_sheet(take_home_service, "0")

    text = "\n".join(EnglishTraceRenderer().render_all(sheet.trace, sheet))

    assert re.search(r"divided by [^()]*\(CA\$0\.00\), which is zero, gives ", text)


def test_the_step_has_no_title_and_no_reference(take_home_service: TakeHomeService) -> None:
    sheet = _return_sheet(take_home_service, "70000")

    assert sheet.title(AVERAGE_INCOME_TAX_RATE.label) is None
    assert sheet.reference(AVERAGE_INCOME_TAX_RATE.label) is None


# --- the kind and the manifest ------------------------------------------------------------------


def test_the_average_rate_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(AVERAGE_RATE)

    assert kind is AVERAGE_INCOME_TAX_RATE
    assert kind.identifier == AVERAGE_RATE
    assert non_negative(kind) is True


def test_the_70000_take_home_is_still_53468_68() -> None:
    # README: take-home is salary less CPP, EI and total tax, done by the caller from the exports.
    # The real wiring, no fixture: every term is a figure the engine already exported, and the new
    # step must change none of them.
    kinds = bundled_kinds()
    worksheets = build_tax_computation().compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (schedule_8,) = worksheets["ca/schedule_8"]
    (t2204,) = worksheets["ca/t2204"]
    (summary,) = worksheets[RETURN]
    cpp = (
        schedule_8.get(kinds.kind("ca/schedule_8_cpp_base_contributions_on_return")).value
        + schedule_8.get(kinds.kind("ca/schedule_8_cpp_enhanced_contributions_on_return")).value
    )
    ei = t2204.get(kinds.kind("ca/t2204_premiums_deducted")).value
    total_tax = summary.get(kinds.kind(LINE_167)).value

    assert (cpp, ei, total_tax) == (D("3956.75"), D("1077.48"), D("11497.09"))
    assert D("70000") - cpp - ei - total_tax == D("53468.68")
    assert summary.get(AVERAGE_INCOME_TAX_RATE).value == D("0.1642")
