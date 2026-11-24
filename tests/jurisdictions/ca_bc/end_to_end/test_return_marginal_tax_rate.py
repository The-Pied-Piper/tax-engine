"""The British Columbia return summary carries the marginal tax rate, through the real engine.

The marginal tax rate is the change in the take-home deductions on the next dollar of salary: T1
line 43500 "Total payable", the CPP contributions (Schedule 8) and the EI premium (T2204 line 16),
for a salary-only filer. It is the sum of three parts: the federal marginal rate
(`ca-bc/marginal_federal_rate`), the British Columbia marginal rate
(`ca-bc/british_columbia_marginal_rate`) and the contribution rate
(`ca-bc/marginal_contribution_rate`: CPP base, first additional and second additional, and EI).
British Columbia has no surtax and no health premium. No new form text: the printed rates are those
of T1 "Line 73: Rate" (14.5%, 20.5%, 26%, 29%, 33%, CRA 5006-r-25e.txt), BC428 "Line 5: Rate" and
"Line 12: Rate" (5.06% to 20.5%, CRA 5010-c-25e.txt), BC428 lines 73 to 79 (the tax reduction),
Schedule 8 lines 11, 12 and 22 (4.95%, 1%, 4%) and T2204 line 10 (1.64%). The sum is not a printed
line, so the step is untitled and has no reference. The hand-worked figures with their parts are in
`test_return_marginal_tax_rate_values.py`; the extra-run check is in
`test_return_marginal_tax_rate_extra_run.py`.

The return summary ends with one `core/sum` step in `return.yaml`: parts the federal marginal rate,
the British Columbia marginal rate and the contribution rate, in that order, the dataset
`ca-bc/exact_rounding` (`rounding: none`, the sum is exact), unit `core/percent`, producing the
non-negative British Columbia amount kind `ca-bc/marginal_tax_rate`. The three parts are read inside
the return, so they are not exported.

Figures (the real parts of the take-home folder, salary the only input, 2025), each the exact sum
of the three
parts, worked by hand from the printed rates:

- $20,000: 0.1339945 + 0 + 0.0759 = 0.2098945; the tax reduction of 562 takes all the British
  Columbia tax
- $30,000: 0.1339945 + 0.08200346 + 0.0759 = 0.29189796; net income 29,735.00 is inside the tax
  reduction's range, which adds 3.56% x 0.99
- $70,000: 0.1957725 + 0.0737253 + 0.0595 = 0.3289978
- $120,000: 0.26 + 0.1229 + 0 = 0.3829
- $200,000: 0.2930542655 + 0.168 + 0 = 0.4610542655, line 12 rate and the federal basic personal
  amount falling

Each tax part counts only where its own tax is above zero: the federal marginal rate through T1
line 42900 "Basic federal tax", the British Columbia marginal rate through BC428 line 80. The gates
and the thresholds are in `test_return_marginal_tax_rate_gates.py`.
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
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_bc.conftest import TAKE_HOME, TakeHomeService, header_without_imports
from tests.kinds import bundled_kinds, non_negative

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
HEADER = header_without_imports()
RETURN_PART = (TAKE_HOME / "return.yaml").read_text(encoding="utf-8")
RETURN = "ca-bc/return"
FEDERAL = "ca-bc/marginal_federal_rate"
BC_RATE = "ca-bc/british_columbia_marginal_rate"
CONTRIBUTION = "ca-bc/marginal_contribution_rate"
MARGINAL = "ca-bc/marginal_tax_rate"
LINE_167 = "ca/refund_or_balance_owing"

PARTS = (
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml"}
    ),
)

# Salary, the federal marginal rate, the British Columbia marginal rate, the contribution rate and
# the marginal tax rate, worked by hand from the printed rates.
FIGURES = [
    ("20000", "0.1339945", "0", "0.0759", "0.2098945"),
    ("30000", "0.1339945", "0.08200346", "0.0759", "0.29189796"),
    ("70000", "0.1957725", "0.0737253", "0.0595", "0.3289978"),
    ("120000", "0.26", "0.1229", "0", "0.3829"),
    ("200000", "0.2930542655", "0.168", "0", "0.4610542655"),
]


def _worksheets(
    take_home_service: TakeHomeService, salary: str
) -> dict[str, tuple[Worksheet, ...]]:
    service = take_home_service(HEADER, RETURN_PART, *PARTS)
    return service.compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
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
    ("salary", "federal", "british_columbia", "contribution", "marginal"), FIGURES
)
def test_the_marginal_tax_rate_is_the_exact_sum_of_the_three_rates(
    take_home_service: TakeHomeService,
    salary: str,
    federal: str,
    british_columbia: str,
    contribution: str,
    marginal: str,
) -> None:
    summary = _summary(take_home_service, salary)
    kinds = bundled_kinds()

    assert summary.get(kinds.kind(FEDERAL)).value == D(federal)
    assert summary.get(kinds.kind(BC_RATE)).value == D(british_columbia)
    assert summary.get(kinds.kind(CONTRIBUTION)).value == D(contribution)
    assert summary.get(kinds.kind(MARGINAL)).value == D(marginal)
    assert D(federal) + D(british_columbia) + D(contribution) == D(marginal)


def test_the_bundled_return_gives_32_9_percent_at_70000() -> None:
    # No fixture: the bundled British Columbia manifest, as the calculator loads it.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, 2025, (Artifact(EMPLOYMENT_INCOME, D("70000")),))
    )
    (summary,) = worksheets[RETURN]

    assert summary.get(bundled_kinds().kind(MARGINAL)).value == D("0.3289978")


def test_the_70000_take_home_stays_54217_74(
    take_home_service: TakeHomeService,
) -> None:
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

    assert total_tax == D("10748.03")
    assert D("70000") - cpp - ei - total_tax == D("54217.74")


def test_the_marginal_tax_rate_is_not_rounded_to_the_cent() -> None:
    # 0.2930542655 + 0.168 = 0.4610542655 keeps all its places: no cent rule is applied.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, 2025, (Artifact(EMPLOYMENT_INCOME, D("200000")),))
    )
    (summary,) = worksheets[RETURN]
    value = summary.get(bundled_kinds().kind(MARGINAL)).value

    assert value == D("0.4610542655")
    assert value.as_tuple().exponent == -10


def test_the_return_prints_the_marginal_tax_rate_as_a_percentage_in_the_core_percent_unit(
    take_home_service: TakeHomeService,
) -> None:
    unit = _summary(take_home_service, "70000").unit(bundled_kinds().kind(MARGINAL).label)

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
    ("salary", "federal", "british_columbia", "contribution", "marginal"), FIGURES
)
def test_the_marginal_tax_rate_is_traced_as_one_exact_sum_in_order(
    take_home_service: TakeHomeService,
    salary: str,
    federal: str,
    british_columbia: str,
    contribution: str,
    marginal: str,
) -> None:
    sheet = _summary(take_home_service, salary)
    kinds = bundled_kinds()

    line = _sum_line(sheet)

    assert [(kind.label, value) for kind, value in line.parts] == [
        (kinds.kind(FEDERAL).label, D(federal)),
        (kinds.kind(BC_RATE).label, D(british_columbia)),
        (kinds.kind(CONTRIBUTION).label, D(contribution)),
    ]
    assert line.rounding == NO_ROUNDING
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
    for part in (FEDERAL, BC_RATE, CONTRIBUTION):
        assert labels.index(kinds.kind(part).label) < marginal


@pytest.mark.parametrize(
    ("salary", "sentence"),
    [
        (
            "70000",
            r"\(19\.57725%\) plus .+ \(7\.37253%\) plus .+ \(5\.95%\) gives 32\.89978%",
        ),
        (
            "20000",
            r"\(13\.39945%\) plus .+ \(0(\.0+)?%\) plus .+ \(7\.59%\) gives 20\.98945%",
        ),
        (
            "120000",
            r"\(26(\.0+)?%\) plus .+ \(12\.29%\) plus .+ \(0(\.0+)?%\) gives 38\.29%",
        ),
    ],
)
def test_the_marginal_tax_rate_is_explained_in_english_as_percentages(
    take_home_service: TakeHomeService, salary: str, sentence: str
) -> None:
    sheet = _summary(take_home_service, salary)

    text = EnglishTraceRenderer().render(_sum_line(sheet), sheet)

    # Each part is named as the return names it and prints as a percentage; the sum prints as a
    # percentage and the sentence says it is not rounded.
    assert re.fullmatch(rf".*{sentence} \(not rounded\)\.?", text)
