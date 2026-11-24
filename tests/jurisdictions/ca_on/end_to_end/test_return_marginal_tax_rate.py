"""The Ontario return summary carries the marginal tax rate, through the real engine.

The marginal tax rate is the change in the take-home deductions on the next dollar of salary: T1
line 43500 "Total payable", the CPP contributions (Schedule 8) and the EI premium (T2204 line 16),
for a salary-only filer. It is the sum of four parts: the federal marginal rate
(`ca-on/marginal_federal_rate`), the Ontario marginal rate (`ca-on/ontario_marginal_rate`), the
health premium rate (`ca-on/marginal_health_premium_rate`: the ON428 line 89 chart row's rate times
the part of a dollar left in the taxable income) and the contribution rate
(`ca-on/marginal_contribution_rate`: CPP base, first additional and second additional, and EI). No
new form text: the printed rates are those of T1 "Line 73: Rate" (14.5%, 20.5%, 26%, 29%, 33%, CRA
5006-r-25e.txt), ON428 "Line 5: Rate" (5.05%, 9.15%, 11.16%, 12.16%, 13.16%, CRA 5006-c-25e.txt),
the chart rows of the line 89 health premium (6% and 25%), Schedule 8 lines 11, 12 and 22 (4.95%,
1%, 4%) and T2204 line 10 (1.64%). The sum is not a printed line, so the step is untitled and has
no reference. The hand-worked figures with their parts are in
`test_return_marginal_tax_rate_values.py`; the extra-run check is in
`test_return_marginal_tax_rate_extra_run.py`.

The return summary ends with one `core/sum` step in `return.yaml`: parts the federal marginal rate,
the Ontario marginal rate, the health premium rate and the contribution rate, in that order, the
dataset `ca/take_home_average_rate_rounding` (half-up to 0.0001: the engine rounds the marginal rate
like the average rate), unit `core/percent`, producing the
non-negative Ontario amount kind `ca-on/marginal_tax_rate`. The four parts are read inside the
return, so they are not exported (pinned in `test_take_home_manifest.py`).

Figures (the real bundled manifest, salary the only input), each the exact sum of the four parts,
worked by hand from the printed rates; the engine rounds the marginal rate half-up to 0.0001 like
the average rate, so the expected marginal rate in the tests is the exact sum below rounded
half-up to four decimals (the parts stay exact). Taxable income is the T1 figure the line 89 chart
row is chosen by (salary less the CPP enhanced deduction):

- $20,000: 0.1339945 + 0 + 0 + 0.0759 = 0.2098945; the LIFT credit ($875) takes all the Ontario
  tax, so the Ontario part is 0; taxable income 19,835.00 is under the 20,000 row
- $22,000: 0.1339945 + 0 + 0.0594 + 0.0759 = 0.2692945; taxable income 21,815.00 is in the 6% row
  (20,000 to 25,000), 6% x 0.99
- $48,800: 0.1339945 + 0.09616705 + 0.2475 + 0.0759 = 0.55356155; taxable income 48,352.00 is in the
  25% row (48,000 to 48,600), and the LIFT credit falls 5% x 0.99 a dollar of net income
- $70,000: 0.1957725 + 0.08808525 + 0 + 0.0595 = 0.34335775; taxable income 69,335.00
- $120,000: 0.26 + 0.1116 x 1.56 + 0 + 0 = 0.26 + 0.174096 = 0.434096; line 65 is 8,110.12, over the
  7,307 threshold of the 36% surtax
- $275,000: 0.33 + 0.1316 x 1.56 + 0 + 0 = 0.33 + 0.205296 = 0.535296, the top brackets

Each tax part counts only where its own tax is above zero: the federal marginal rate through T1
line 42900 "Basic federal tax", the Ontario marginal rate through ON428 line 86. The gates and the
thresholds are in `test_return_marginal_tax_rate_gates.py`.

The return's step wiring is pinned in `test_take_home_manifest.py`.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService, header_without_imports
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
HEADER = header_without_imports()
RETURN_PART = (TAKE_HOME / "return.yaml").read_text(encoding="utf-8")
RETURN = "ca-on/return"
FEDERAL = "ca-on/marginal_federal_rate"
ONTARIO_RATE = "ca-on/ontario_marginal_rate"
PREMIUM = "ca-on/marginal_health_premium_rate"
CONTRIBUTION = "ca-on/marginal_contribution_rate"
MARGINAL = "ca-on/marginal_tax_rate"
LINE_167 = "ca/refund_or_balance_owing"
FOUR_PLACES = D("0.0001")
ROUNDING = RoundTo(FOUR_PLACES, RoundingMode.HALF_UP)

PARTS = (
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml"}
    ),
)

# Salary, the federal marginal rate, the Ontario marginal rate, the health premium rate, the
# contribution rate and the marginal tax rate, from runs of the real parts.
FIGURES = [
    ("20000", "0.1339945", "0", "0", "0.0759", "0.2099"),
    ("22000", "0.1339945", "0", "0.0594", "0.0759", "0.2693"),
    ("48800", "0.1339945", "0.09616705", "0.2475", "0.0759", "0.5536"),
    ("70000", "0.1957725", "0.08808525", "0", "0.0595", "0.3434"),
    ("120000", "0.26", "0.174096", "0", "0", "0.4341"),
    ("275000", "0.33", "0.205296", "0", "0", "0.5353"),
]


def _worksheets(
    take_home_service: TakeHomeService, salary: str
) -> dict[str, tuple[Worksheet, ...]]:
    service = take_home_service(HEADER, RETURN_PART, *PARTS)
    return service.compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _summary(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    (summary,) = _worksheets(take_home_service, salary)[RETURN]
    return summary


def _sum_line(sheet: Worksheet) -> SumLine:
    """The one trace line of the marginal tax rate step, found by its output kind."""
    label = bundled_kinds().kind(MARGINAL).label
    (line,) = [
        line for line in sheet.trace if isinstance(line, SumLine) and line.output.label == label
    ]
    return line


def test_the_marginal_tax_rate_kind_is_a_registered_non_negative_amount() -> None:
    kind = bundled_kinds().kind(MARGINAL)

    assert kind.identifier == MARGINAL
    assert non_negative(kind)
    assert kind.value_type is Decimal


@pytest.mark.parametrize(
    ("salary", "federal", "ontario", "premium", "contribution", "marginal"), FIGURES
)
def test_the_marginal_tax_rate_is_the_exact_sum_of_the_four_rates(
    take_home_service: TakeHomeService,
    salary: str,
    federal: str,
    ontario: str,
    premium: str,
    contribution: str,
    marginal: str,
) -> None:
    summary = _summary(take_home_service, salary)
    kinds = bundled_kinds()

    assert summary.get(kinds.kind(FEDERAL)).value == D(federal)
    assert summary.get(kinds.kind(ONTARIO_RATE)).value == D(ontario)
    assert summary.get(kinds.kind(PREMIUM)).value == D(premium)
    assert summary.get(kinds.kind(CONTRIBUTION)).value == D(contribution)
    assert summary.get(kinds.kind(MARGINAL)).value == D(marginal)
    assert (D(federal) + D(ontario) + D(premium) + D(contribution)).quantize(
        FOUR_PLACES, rounding=ROUND_HALF_UP
    ) == D(marginal)


def test_the_bundled_return_gives_34_34_percent_at_70000() -> None:
    # No fixture: the bundled Ontario manifest, as the calculator loads it.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D("70000")),))
    )
    (summary,) = worksheets[RETURN]

    assert summary.get(bundled_kinds().kind(MARGINAL)).value == D("0.3434")


def test_the_70000_take_home_stays_53468_68(take_home_service: TakeHomeService) -> None:
    worksheets = _worksheets(take_home_service, "70000")
    kinds = bundled_kinds()
    (summary,) = worksheets[RETURN]
    (schedule_8,) = worksheets["ca/schedule_8"]
    (t2204,) = worksheets["ca/t2204"]
    total_tax = summary.get(kinds.kind(LINE_167)).value
    cpp = sum(
        (
            schedule_8.get(kinds.kind(name)).value
            for name in (
                "ca/schedule_8_cpp_base_contributions_on_return",
                "ca/schedule_8_cpp_enhanced_contributions_on_return",
            )
        ),
        D("0"),
    )
    ei = t2204.get(kinds.kind("ca/t2204_premiums_deducted")).value

    assert total_tax == D("11497.09")
    assert D("70000") - cpp - ei - total_tax == D("53468.68")


def test_the_marginal_tax_rate_is_rounded_to_four_places_not_to_the_cent() -> None:
    # 0.33 + 0.205296 = 0.535296 is rounded half-up to 0.0001 like the average rate: 0.5353 keeps
    # four places, so no dollars-and-cents rule is applied.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D("275000")),))
    )
    (summary,) = worksheets[RETURN]
    value = summary.get(bundled_kinds().kind(MARGINAL)).value

    assert value == D("0.5353")
    assert value.as_tuple().exponent == -4


def test_the_return_prints_the_marginal_tax_rate_as_a_percentage_in_the_core_percent_unit(
    take_home_service: TakeHomeService,
) -> None:
    summary = _summary(take_home_service, "70000")

    unit = summary.unit(bundled_kinds().kind(MARGINAL).label)

    assert unit is not None
    assert unit.identifier == "core/percent"


def test_the_marginal_tax_rate_step_has_no_reference_and_no_title(
    take_home_service: TakeHomeService,
) -> None:
    summary = _summary(take_home_service, "70000")
    label = bundled_kinds().kind(MARGINAL).label

    assert summary.reference(label) is None
    assert summary.title(label) is None


@pytest.mark.parametrize(
    ("salary", "federal", "ontario", "premium", "contribution", "marginal"), FIGURES
)
def test_the_marginal_tax_rate_is_traced_as_one_sum_rounded_to_four_places_in_order(
    take_home_service: TakeHomeService,
    salary: str,
    federal: str,
    ontario: str,
    premium: str,
    contribution: str,
    marginal: str,
) -> None:
    sheet = _summary(take_home_service, salary)
    kinds = bundled_kinds()

    line = _sum_line(sheet)

    assert [(kind.label, value) for kind, value in line.parts] == [
        (kinds.kind(FEDERAL).label, D(federal)),
        (kinds.kind(ONTARIO_RATE).label, D(ontario)),
        (kinds.kind(PREMIUM).label, D(premium)),
        (kinds.kind(CONTRIBUTION).label, D(contribution)),
    ]
    assert line.rounding == ROUNDING
    assert line.total == D(marginal)
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


def test_the_marginal_tax_rate_comes_last_of_the_marginal_steps_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _summary(take_home_service, "100000")
    kinds = bundled_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert marginal == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in (FEDERAL, ONTARIO_RATE, PREMIUM, CONTRIBUTION):
        assert labels.index(kinds.kind(part).label) < marginal


@pytest.mark.parametrize(
    ("salary", "sentence"),
    [
        (
            "70000",
            r"\(19\.57725%\) plus .+ \(8\.808525%\) plus .+ \(0(\.0+)?%\) plus .+ \(5\.95%\)"
            r" gives 34\.34%",
        ),
        (
            "22000",
            r"\(13\.39945%\) plus .+ \(0(\.0+)?%\) plus .+ \(5\.94%\) plus .+ \(7\.59%\)"
            r" gives 26\.93%",
        ),
        (
            "275000",
            r"\(33(\.0+)?%\) plus .+ \(20\.5296%\) plus .+ \(0(\.0+)?%\) plus .+ \(0(\.0+)?%\)"
            r" gives 53\.53%",
        ),
    ],
)
def test_the_marginal_tax_rate_is_explained_in_english_as_percentages(
    take_home_service: TakeHomeService, salary: str, sentence: str
) -> None:
    sheet = _summary(take_home_service, salary)

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    # Each part is named as the return names it and prints as a percentage; the sum prints as a
    # percentage and the sentence says it is rounded half-up to 0.0001.
    assert re.fullmatch(rf".*{sentence} \(rounded half-up to 0\.0001\)\.?", text)
