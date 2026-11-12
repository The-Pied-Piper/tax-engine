"""The Ontario return summary carries the marginal tax rate, through the real engine.

The marginal tax rate is the extra income tax on the next dollar of salary: the federal marginal
rate (`ca/federal_marginal_rate`, the T1 line 73 bracket rate), the Ontario marginal rate
(`ca-on/ontario_marginal_rate`, the ON428 line 5 bracket rate times the surtax factor of lines 66
and 67) and the Ontario health premium slope (`ca-on/return_health_premium_slope`, the rate of the
ON428 line 89 chart row). CPP and EI are not counted. No new form text: the printed rates are those
of T1 "Line 73: Rate" (14.5%, 20.5%, 26%, 29%, 33%, CRA 5006-r-25e.txt) and ON428 "Line 5: Rate"
(5.05%, 9.15%, 11.16%, 12.16%, 13.16%, CRA 5006-c-25e.txt), and the chart rows of the line 89 health
premium (6% and 25%). The sum is not a printed line, so the step is untitled and has no reference.

The return summary ends with one `core/sum` step in `return.yaml`: parts the federal marginal
rate, the Ontario marginal rate and the health premium slope, in that order, the dataset
`ca-on/exact_rounding` (`rounding: none`, the sum is exact), unit `core/percent`, producing the new
non-negative Ontario amount kind `ca-on/marginal_tax_rate`. The three parts are now read inside the
return, so they are no longer exported (pinned in `test_take_home_manifest.py`).

Figures (the real bundled manifest, salary the only input), each the exact sum of the three parts,
worked by hand from the printed rates. Taxable income is the T1 figure the line 73 column and the
line 89 chart row are chosen by:

- $20,000: 0.145 + 0.0505 + 0 = 0.1955 (19.55%); taxable income 19,835.00 is under the 20,000 row
- $22,000: 0.145 + 0.0505 + 0.06 = 0.2555 (25.55%); taxable income 21,815.00 is in the 6% row
  (20,000 to 25,000)
- $48,800: 0.145 + 0.0505 + 0.25 = 0.4455 (44.55%); taxable income 48,347.00 is in the 25% row
  (48,000 to 48,600)
- $70,000: 0.205 + 0.0915 + 0 = 0.2965 (29.65%); taxable income 69,335.00
- $120,000: 0.26 + 0.1116 x 1.56 + 0 = 0.26 + 0.174096 = 0.434096 (43.4096%); line 65 is 8,110.12,
  over the 7,307 threshold of the 36% surtax
- $275,000: 0.33 + 0.1316 x 1.56 + 0 = 0.33 + 0.205296 = 0.535296 (53.5296%), the top brackets

The return's step wiring is pinned in `test_take_home_manifest.py`.
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.rounding import NO_ROUNDING
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
FEDERAL = "ca/federal_marginal_rate"
ONTARIO_RATE = "ca-on/ontario_marginal_rate"
SLOPE = "ca-on/return_health_premium_slope"
MARGINAL = "ca-on/marginal_tax_rate"
LINE_167 = "ca/refund_or_balance_owing"

PARTS = (
    "salary.yaml",
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml", "salary.yaml"}
    ),
)

# Salary, the federal marginal rate, the Ontario marginal rate, the health premium slope and the
# marginal tax rate, from runs of the real parts.
FIGURES = [
    ("20000", "0.145", "0.0505", "0", "0.1955"),
    ("22000", "0.145", "0.0505", "0.06", "0.2555"),
    ("48800", "0.145", "0.0505", "0.25", "0.4455"),
    ("70000", "0.205", "0.0915", "0", "0.2965"),
    ("120000", "0.26", "0.174096", "0", "0.434096"),
    ("275000", "0.33", "0.205296", "0", "0.535296"),
]


def _worksheets(
    take_home_service: TakeHomeService, salary: str
) -> dict[str, tuple[Worksheet, ...]]:
    service = take_home_service(HEADER, RETURN_PART, *PARTS)
    return service.compute(ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))


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


@pytest.mark.parametrize(("salary", "federal", "ontario", "slope", "marginal"), FIGURES)
def test_the_marginal_tax_rate_is_the_exact_sum_of_the_three_rates(
    take_home_service: TakeHomeService,
    salary: str,
    federal: str,
    ontario: str,
    slope: str,
    marginal: str,
) -> None:
    summary = _summary(take_home_service, salary)
    kinds = bundled_kinds()

    assert summary.get(kinds.kind(FEDERAL)).value == D(federal)
    assert summary.get(kinds.kind(ONTARIO_RATE)).value == D(ontario)
    assert summary.get(kinds.kind(SLOPE)).value == D(slope)
    assert summary.get(kinds.kind(MARGINAL)).value == D(marginal)
    assert D(federal) + D(ontario) + D(slope) == D(marginal)


def test_the_bundled_return_gives_29_65_percent_at_70000() -> None:
    # No fixture: the bundled Ontario manifest, as the calculator loads it.
    worksheets = build_tax_computation().compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (summary,) = worksheets[RETURN]

    assert summary.get(bundled_kinds().kind(MARGINAL)).value == D("0.2965")


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


def test_the_marginal_tax_rate_is_not_rounded_to_the_cent() -> None:
    # 0.33 + 0.205296 = 0.535296 keeps all its places: no dollars-and-cents rule is applied.
    worksheets = build_tax_computation().compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D("275000"))
    )
    (summary,) = worksheets[RETURN]
    value = summary.get(bundled_kinds().kind(MARGINAL)).value

    assert value == D("0.535296")
    assert value.as_tuple().exponent == -6


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


@pytest.mark.parametrize(("salary", "federal", "ontario", "slope", "marginal"), FIGURES)
def test_the_marginal_tax_rate_is_traced_as_one_exact_sum_in_order(
    take_home_service: TakeHomeService,
    salary: str,
    federal: str,
    ontario: str,
    slope: str,
    marginal: str,
) -> None:
    sheet = _summary(take_home_service, salary)
    kinds = bundled_kinds()

    line = _sum_line(sheet)

    assert [(kind.label, value) for kind, value in line.parts] == [
        (kinds.kind(FEDERAL).label, D(federal)),
        (kinds.kind(ONTARIO_RATE).label, D(ontario)),
        (kinds.kind(SLOPE).label, D(slope)),
    ]
    assert line.rounding == NO_ROUNDING
    assert line.total == D(marginal)
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


def test_the_marginal_tax_rate_comes_last_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _summary(take_home_service, "100000")
    kinds = bundled_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert marginal == len(labels) - 1
    assert labels.count(kinds.kind(MARGINAL).label) == 1
    for part in (FEDERAL, ONTARIO_RATE, SLOPE):
        assert labels.index(kinds.kind(part).label) < marginal


@pytest.mark.parametrize(
    ("salary", "sentence"),
    [
        ("70000", r"\(20\.5%\) plus .+ \(9\.15%\) plus .+ \(0(\.0+)?%\) gives 29\.65%"),
        ("22000", r"\(14\.5%\) plus .+ \(5\.05%\) plus .+ \(6(\.0+)?%\) gives 25\.55%"),
        ("275000", r"\(33(\.0+)?%\) plus .+ \(20\.5296%\) plus .+ \(0(\.0+)?%\) gives 53\.5296%"),
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
