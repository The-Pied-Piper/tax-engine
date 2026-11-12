"""The Ontario return summary carries the Ontario marginal rate, through the real engine.

The Ontario marginal rate is the ON428 line 5 bracket rate (`ca-on/ontario_bracket_rate_return`)
times the Ontario surtax factor (`ca-on/ontario_surtax_factor`, ON428 lines 66 and 67):
the share of a further dollar of Ontario tax-bearing income that goes to Ontario tax with the
surtax. No new form text: the printed rates are those of line 5 ("Line 5: Rate 5.05%", "9.15%",
"11.16%", "12.16%", "13.16%", CRA 5006-c-25e.txt) and the surtax rates those of line 66 "(Line 65
minus $5,710) multiplied by 20%" and line 67 "(Line 65 minus $7,307) multiplied by 36%". The rate
times the factor is not a printed line, so the step is untitled and carries no line reference.

The return summary has one `core/multiply_by_rate` step in `return.yaml`: base
`ca-on/ontario_surtax_factor`, rate `ca-on/ontario_bracket_rate_return`, the dataset
`ca-on/exact_rounding` (`rounding: none`, the product is exact), unit `core/percent`, producing the
new non-negative Ontario amount kind `ca-on/ontario_marginal_rate`. The return's exports are that
rate and T1 line 167: the bracket rate and the surtax factor are now read inside the return, so
they are no longer exported.

Figures (the real bundled manifest, salary the only input), each the exact product of the line 5
rate and the factor, worked by hand. The factor by salary is the one pinned in
`end_to_end/test_return_surtax_factor.py` (line 65 is 300.14 at $20,000, 3,311.45 at $70,000,
6,015.78 at $100,000, 6,994.12 at $110,000, 8,110.12 at $120,000, 11,458.12 at $150,000):

- $20,000: 0.0505 x 1 = 0.0505 (5.05%)
- $70,000: 0.0915 x 1 = 0.0915 (9.15%)
- $100,000: 0.0915 x 1.20 = 0.1098 (10.98%), in the 20% surtax range
- $110,000: 0.1116 x 1.20 = 0.13392 (13.392%), in the 20% surtax range
- $120,000: 0.1116 x 1.56 = 0.174096 (17.4096%), over the 36% threshold
- $150,000: 0.1116 x 1.56 = 0.174096 (17.4096%), over the 36% threshold
- $200,000: 0.1216 x 1.56 = 0.189696 (18.9696%), over the 36% threshold
- $275,000: 0.1316 x 1.56 = 0.205296 (20.5296%), the top bracket over the 36% threshold

The return's exports and step wiring are pinned in `test_take_home_manifest.py`, and the $70,000
take-home (53,468.68) in `test_take_home_return_ontario_bracket_rate.py`.
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
from tax_engine.domain.trace import MultipliedByRateLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService, header_without_imports
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
HEADER = header_without_imports()
RETURN_PART = (TAKE_HOME / "return.yaml").read_text(encoding="utf-8")
RETURN = "ca-on/return"
RATE = "ca-on/ontario_bracket_rate_return"
FACTOR = "ca-on/ontario_surtax_factor"
MARGINAL = "ca-on/ontario_marginal_rate"

PARTS = (
    "salary.yaml",
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml", "salary.yaml"}
    ),
)

# Salary, the line 5 rate, the surtax factor and the marginal rate, from runs of the real parts.
FIGURES = [
    ("20000", "0.0505", "1", "0.0505"),
    ("70000", "0.0915", "1", "0.0915"),
    ("100000", "0.0915", "1.20", "0.1098"),
    ("110000", "0.1116", "1.20", "0.13392"),
    ("120000", "0.1116", "1.56", "0.174096"),
    ("150000", "0.1116", "1.56", "0.174096"),
    ("200000", "0.1216", "1.56", "0.189696"),
    ("275000", "0.1316", "1.56", "0.205296"),
]


def _summary(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    service = take_home_service(HEADER, RETURN_PART, *PARTS)
    worksheets = service.compute(ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (summary,) = worksheets[RETURN]
    return summary


def _marginal_line(sheet: Worksheet) -> MultipliedByRateLine:
    """The one trace line of the marginal rate step, found by its output kind."""
    kind = bundled_kinds().kind(MARGINAL)
    (line,) = [
        line
        for line in sheet.trace
        if isinstance(line, MultipliedByRateLine) and line.output.label == kind.label
    ]
    return line


def test_the_marginal_rate_kind_is_a_registered_non_negative_amount() -> None:
    kind = bundled_kinds().kind(MARGINAL)

    assert kind.identifier == MARGINAL
    assert non_negative(kind)
    assert kind.value_type is Decimal


@pytest.mark.parametrize(("salary", "rate", "factor", "marginal"), FIGURES)
def test_the_marginal_rate_is_the_bracket_rate_times_the_surtax_factor(
    take_home_service: TakeHomeService, salary: str, rate: str, factor: str, marginal: str
) -> None:
    summary = _summary(take_home_service, salary)
    kinds = bundled_kinds()

    assert summary.get(kinds.kind(RATE)).value == D(rate)
    assert summary.get(kinds.kind(FACTOR)).value == D(factor)
    assert summary.get(kinds.kind(MARGINAL)).value == D(marginal)
    assert D(rate) * D(factor) == D(marginal)


def test_the_bundled_return_gives_9_15_percent_at_70000() -> None:
    # No fixture: the bundled Ontario manifest, as the calculator loads it.
    worksheets = build_tax_computation().compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (summary,) = worksheets[RETURN]

    assert summary.get(bundled_kinds().kind(MARGINAL)).value == D("0.0915")


def test_the_marginal_rate_is_not_rounded_to_the_cent() -> None:
    # 0.1316 x 1.56 = 0.205296 keeps all its places: no dollars-and-cents rule is applied.
    worksheets = build_tax_computation().compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D("275000"))
    )
    (summary,) = worksheets[RETURN]
    value = summary.get(bundled_kinds().kind(MARGINAL)).value

    assert value == D("0.205296")
    assert value.as_tuple().exponent == -6


def test_the_return_prints_the_marginal_rate_as_a_percentage_in_the_core_percent_unit(
    take_home_service: TakeHomeService,
) -> None:
    summary = _summary(take_home_service, "70000")

    unit = summary.unit(bundled_kinds().kind(MARGINAL).label)

    assert unit is not None
    assert unit.identifier == "core/percent"


def test_the_marginal_rate_step_has_no_reference_and_no_title(
    take_home_service: TakeHomeService,
) -> None:
    summary = _summary(take_home_service, "70000")
    label = bundled_kinds().kind(MARGINAL).label

    assert summary.reference(label) is None
    assert summary.title(label) is None


@pytest.mark.parametrize(("salary", "rate", "factor", "marginal"), FIGURES)
def test_the_marginal_rate_is_traced_as_one_exact_multiplication(
    take_home_service: TakeHomeService, salary: str, rate: str, factor: str, marginal: str
) -> None:
    sheet = _summary(take_home_service, salary)
    kinds = bundled_kinds()

    line = _marginal_line(sheet)

    assert line.base_kind.label == kinds.kind(FACTOR).label
    assert line.base_value == D(factor)
    assert line.rate_kind.label == kinds.kind(RATE).label
    assert line.rate_value == D(rate)
    assert line.rounding == NO_ROUNDING
    assert line.result == D(marginal)
    assert line.amount == sheet.get(kinds.kind(MARGINAL)).value


def test_the_marginal_rate_comes_after_the_bracket_rate_and_the_surtax_factor_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _summary(take_home_service, "100000")
    kinds = bundled_kinds()
    labels = [line.label for line in sheet.trace]

    marginal = labels.index(kinds.kind(MARGINAL).label)

    assert labels.index(kinds.kind(RATE).label) < marginal
    assert labels.index(kinds.kind(FACTOR).label) < marginal
    assert labels.count(kinds.kind(MARGINAL).label) == 1


@pytest.mark.parametrize(
    ("salary", "rate", "factor", "marginal"),
    [
        ("70000", "9.15%", "1.00", "9.15%"),
        ("100000", "9.15%", "1.20", "10.98%"),
        ("110000", "11.16%", "1.20", "13.392%"),
        ("275000", "13.16%", "1.56", "20.5296%"),
    ],
)
def test_the_marginal_rate_is_explained_in_english_as_percentages(
    take_home_service: TakeHomeService, salary: str, rate: str, factor: str, marginal: str
) -> None:
    sheet = _summary(take_home_service, salary)
    line = _marginal_line(sheet)

    sentence = EnglishTraceRenderer().render(line, sheet)

    # The rate is named as the return names it and prints as a percentage; the base is the plain
    # factor; the product prints as a percentage and the sentence says it is not rounded.
    assert re.fullmatch(
        rf".+ \({re.escape(rate)}\) of .+ \({re.escape(factor)}\) gives "
        rf"{re.escape(marginal)} \(not rounded\)\.?",
        sentence,
    )
