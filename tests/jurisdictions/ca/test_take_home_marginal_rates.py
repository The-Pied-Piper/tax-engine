"""The federal form `ca/take_home_marginal_rates`: the federal part of the take-home marginal rate.

The form works from the salary alone and exports four rates, each per further dollar of salary and
exact: the net income rate (1 less the CPP first additional and second additional rates), the
credit-earning contribution rate (the CPP base rate plus the EI rate of T2204 line 16), the federal
marginal rate (counted only where the basic federal tax, T1 line 42900, is above zero) and the
contribution rate (the four contribution rates added). A province's return imports the form and
reads the exports; Ontario's is the first.

The shape tests pin the form's layout, its steps in order and that it holds no provincial fact.
The value tests run the real Ontario return, which imports the form, and read the form's own sheet
at a few salaries, worked by hand from the printed rates (T1 "Line 73: Rate", Schedule 8 lines 11,
12 and 22, T2204 lines 10 and 16, the Federal Worksheet 5000-D1 for the basic personal amount):

- 2025, $2,020: only the EI of line 16 moves, 1 for 1 (the 100% band): the credit-earning rate
  and the contribution rate are 1, the net income rate is 1, and no federal tax is paid: 0.
- 2025, $10,000: CPP 4.95% + 1% and EI 1.64%; N = 1 - 0.01 = 0.99; no federal tax: 0.
- 2025, $70,000: over the EI maximum, CPP 4.95% + 1%; federal 20.5% x 0.99 - 14.5% x 0.0495.
- 2025, $75,000: CPP2 band, N = 0.96, no CPP base or EI; federal 20.5% x 0.96.
- 2025, $200,000: no contributions; 29% + 14.5% x 1,591 / 75,532 (0.0210639 to seven places).
- 2026, $70,000: federal 20.5% x 0.99 - 14% x 0.0495; EI over its $68,900 maximum.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Form
from tax_engine.jurisdictions.ca.catalog.deductions import CPP_MONTHS
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.federal_forms import FEDERAL_FORMS
from tests.kinds import bundled_kinds
from tests.manifest_support import real_manifest

D = Decimal
FORM = "ca/take_home_marginal_rates"
FOLDER = FEDERAL_FORMS / "take_home_marginal_rates"
EXACT = {"rounding": "ca/exact_rounding"}
GATE = "ca/marginal_rate_gate"

Step = tuple[str, dict[str, str], dict[str, Any], dict[str, str]]


def _form() -> Form:
    (form,) = (form for form in real_manifest("CA-ON").forms if form.name == FORM)
    return form


def _steps() -> list[Step]:
    return [
        (step.name, dict(step.params), dict(step.consumes), dict(step.produces))
        for step in _form().capabilities
    ]


def _band(table: str, base: str, output: str) -> Step:
    return ("core/amount_by_band_rate", {"table": table}, {"base": base}, {"output": output})


def _tier_rate(tier: str, earnings: str, output: str) -> Step:
    return ("ca/contribution_tier_rate", {"tier": tier}, {"earnings": earnings}, {"output": output})


def _record_total(records: str, output: str) -> Step:
    return ("core/record_total", {}, {"records": records}, {"output": output})


def _multiply(base: str, rate: str, output: str) -> Step:
    return ("core/multiply_by_rate", EXACT, {"base": base, "rate": rate}, {"output": output})


def _subtract(amount: str, less: str, output: str) -> Step:
    return ("core/subtract", EXACT, {"amount": amount, "less": less}, {"output": output})


def _sum(parts: tuple[str, ...], output: str) -> Step:
    return ("core/sum", EXACT, {"parts": parts}, {"output": output})


def test_the_form_is_a_required_form_without_instances_or_inputs() -> None:
    form = _form()

    assert form.required
    assert form.instances is None
    assert form.inputs == ()


def test_the_form_exports_the_four_rates_a_provincial_return_reads() -> None:
    assert set(_form().exports) == {
        "ca/marginal_net_income_rate",
        "ca/marginal_credit_contribution_rate",
        "ca/marginal_federal_rate",
        "ca/marginal_contribution_rate",
    }


def test_every_step_is_a_percent_except_the_dollar_figures_it_reads() -> None:
    dollars = {
        "ca/marginal_salary",
        "ca/marginal_net_income",
        "ca/marginal_age_income_over_threshold",
        "ca/marginal_age_amount_claimed",
        "ca/marginal_basic_federal_tax",
        "ca/marginal_cpp_line_2",
        "ca/marginal_cpp_line_5",
        "ca/marginal_cpp_basic_exemption",
        "ca/marginal_cpp_maximum_pensionable_earnings",
        "ca/marginal_cpp_additional_maximum_pensionable_earnings",
        "ca/marginal_cpp_line_5_room",
        "ca/marginal_cpp_line_2_room",
        "ca/marginal_cpp_line_7_signed",
        "ca/marginal_cpp_line_4_signed",
        "ca/marginal_ei_line_1",
        "ca/marginal_ei_line_7",
        "ca/marginal_ei_line_10",
    }

    units = {
        step.produces["output"]: step.unit
        for step in _form().capabilities
        if step.produces["output"] not in dollars
    }

    assert set(units.values()) == {"core/percent"}
    assert {step.unit for step in _form().capabilities if step.produces["output"] in dollars} == {
        "ca/cad"
    }


def test_the_cpp_rates_read_the_signed_schedule_8_figures() -> None:
    # Schedule 8 line 5 less the basic exemption (line 7 before its floor and maximum) and line 2
    # less the maximum pensionable earnings (line 4 before its floor) are signed, so a rate is 0
    # below its band and not 0 at the band's start.
    steps = _steps()
    cpp = [step for step in steps if step[3]["output"].startswith("ca/marginal_cpp_")]

    assert cpp == [
        _record_total("ca/schedule_8.cpp_part_3_line_2", "ca/marginal_cpp_line_2"),
        _record_total("ca/schedule_8.cpp_part_3_line_5", "ca/marginal_cpp_line_5"),
        _record_total("ca/schedule_8.cpp_basic_exemption", "ca/marginal_cpp_basic_exemption"),
        _record_total(
            "ca/schedule_8.cpp_maximum_pensionable_earnings",
            "ca/marginal_cpp_maximum_pensionable_earnings",
        ),
        _record_total(
            "ca/schedule_8.cpp_additional_maximum_pensionable_earnings",
            "ca/marginal_cpp_additional_maximum_pensionable_earnings",
        ),
        _subtract(
            "ca/marginal_cpp_line_5",
            "ca/marginal_cpp_basic_exemption",
            "ca/marginal_cpp_line_7_signed",
        ),
        _subtract(
            "ca/marginal_cpp_line_2",
            "ca/marginal_cpp_maximum_pensionable_earnings",
            "ca/marginal_cpp_line_4_signed",
        ),
        _subtract(
            "ca/marginal_cpp_maximum_pensionable_earnings",
            "ca/marginal_cpp_line_5",
            "ca/marginal_cpp_line_5_room",
        ),
        _subtract(
            "ca/marginal_cpp_additional_maximum_pensionable_earnings",
            "ca/marginal_cpp_line_2",
            "ca/marginal_cpp_line_2_room",
        ),
        _band(GATE, "ca/marginal_cpp_line_5_room", "ca/marginal_cpp_line_5_room_gate"),
        _band(GATE, "ca/marginal_cpp_line_2_room", "ca/marginal_cpp_line_2_room_gate"),
        _tier_rate(
            "ca/cpp_line_11_base_contribution",
            "ca/marginal_cpp_line_7_signed",
            "ca/marginal_cpp_base_tier_rate",
        ),
        _multiply(
            "ca/marginal_cpp_base_tier_rate",
            "ca/marginal_cpp_line_5_room_gate",
            "ca/marginal_cpp_base_rate",
        ),
        _tier_rate(
            "ca/cpp_line_12_first_additional_contribution",
            "ca/marginal_cpp_line_7_signed",
            "ca/marginal_cpp_first_additional_tier_rate",
        ),
        _multiply(
            "ca/marginal_cpp_first_additional_tier_rate",
            "ca/marginal_cpp_line_5_room_gate",
            "ca/marginal_cpp_first_additional_rate",
        ),
        _tier_rate(
            "ca/cpp_line_22_second_additional_contribution",
            "ca/marginal_cpp_line_4_signed",
            "ca/marginal_cpp_second_additional_tier_rate",
        ),
        _multiply(
            "ca/marginal_cpp_second_additional_tier_rate",
            "ca/marginal_cpp_line_2_room_gate",
            "ca/marginal_cpp_second_additional_rate",
        ),
    ]


def _cpp_rates(year: int, salary: str) -> tuple[Decimal, Decimal]:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), year, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[FORM]
    kinds = bundled_kinds()
    base = sheet.get(kinds.kind("ca/marginal_cpp_base_rate")).value
    second = sheet.get(kinds.kind("ca/marginal_cpp_second_additional_rate")).value
    assert isinstance(base, Decimal)
    assert isinstance(second, Decimal)
    return base, second


@pytest.mark.parametrize(
    ("salary", "base"),
    [("3000", "0"), ("3499.99", "0"), ("3500", "0.0495")],
)
def test_the_cpp_base_rate_starts_at_the_basic_exemption(salary: str, base: str) -> None:
    assert _cpp_rates(2026, salary)[0] == D(base)


@pytest.mark.parametrize(
    ("salary", "second"),
    [("74000", "0"), ("74600", "0.04"), ("85000", "0")],
)
def test_the_second_additional_rate_starts_at_the_first_ceiling_and_stops_at_the_second(
    salary: str, second: str
) -> None:
    assert _cpp_rates(2026, salary)[1] == D(second)


def test_the_exports_are_amount_kinds_that_cannot_be_negative() -> None:
    kinds = bundled_kinds()

    for name in _form().exports:
        kind = kinds.kind(name)
        assert kind.value_type is Decimal
        assert getattr(kind, "non_negative", False)


def test_the_form_names_no_province() -> None:
    # The federal package holds federal facts only; a province reads the form, never the reverse.
    texts = [path.read_text(encoding="utf-8") for path in sorted(FOLDER.glob("*.yaml"))]
    ca = Path(FEDERAL_FORMS).parent / "parameters"
    for family in ("marginal_rate_rounding", "marginal_rate_gate"):
        texts.extend(path.read_text(encoding="utf-8") for path in (ca / family).glob("*.yaml"))

    assert texts
    assert not [text for text in texts if re.search(r"\bca-[a-z]{2}\b", text)]


@pytest.mark.parametrize(
    ("year", "salary", "net", "credit", "federal", "contribution"),
    [
        (2025, "2020", "1", "1", "0", "1"),
        (2025, "10000", "0.99", "0.0659", "0", "0.0759"),
        (2025, "70000", "0.99", "0.0495", "0.1957725", "0.0595"),
        (2025, "75000", "0.96", "0", "0.1968", "0.04"),
        (2025, "200000", "1", "0", "0.2930542655", "0"),
        (2026, "70000", "0.99", "0.0495", "0.19602", "0.0595"),
    ],
)
def test_the_exports_at_a_few_salaries(
    year: int, salary: str, net: str, credit: str, federal: str, contribution: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), year, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[FORM]
    kinds = bundled_kinds()

    def value(name: str) -> Decimal:
        figure = sheet.get(kinds.kind(name)).value
        assert isinstance(figure, Decimal)
        return figure

    assert value("ca/marginal_net_income_rate") == D(net)
    assert value("ca/marginal_credit_contribution_rate") == D(credit)
    assert value("ca/marginal_federal_rate") == D(federal)
    assert value("ca/marginal_contribution_rate") == D(contribution)


def test_the_federal_rate_is_zero_where_no_federal_tax_is_paid_and_opens_with_the_tax() -> None:
    # T1 line 42900 is first positive at a salary of 18,820.27 (2025): the gate follows it.
    def federal(salary: str) -> Decimal:
        worksheets = build_tax_computation().compute(
            TaxCalculationRequest(
                JurisdictionCode("CA-ON"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
            )
        )
        (sheet,) = worksheets[FORM]
        figure = sheet.get(bundled_kinds().kind("ca/marginal_federal_rate")).value
        assert isinstance(figure, Decimal)
        return figure

    assert federal("18820.26") == D("0")
    assert federal("18820.27") == D("0.1339945")


def _ei_rates(year: int, salary: str) -> tuple[Decimal, Decimal]:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), year, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[FORM]
    kinds = bundled_kinds()
    line_7 = sheet.get(kinds.kind("ca/marginal_ei_line_7_rate")).value
    ei = sheet.get(kinds.kind("ca/marginal_ei_rate")).value
    assert isinstance(line_7, Decimal)
    assert isinstance(ei, Decimal)
    return line_7, ei


def test_the_ei_line_7_rate_reads_the_line_7_band_on_line_1() -> None:
    steps = [step for step in _steps() if step[3]["output"] == "ca/marginal_ei_line_7_rate"]

    assert steps == [
        _tier_rate(
            "ca/marginal_ei_line_7_tier", "ca/marginal_ei_line_1", "ca/marginal_ei_line_7_rate"
        )
    ]


@pytest.mark.parametrize(
    ("year", "salary", "line_7", "ei"),
    [
        (2025, "1999.99", "0", "0"),
        (2025, "2000", "1", "1"),
        (2025, "2000.01", "1", "1"),
        (2025, "65699.99", "1", "0.0164"),
        (2025, "65700", "0", "0"),
        (2026, "1999.99", "0", "0"),
        (2026, "2000", "1", "1"),
        (2026, "2000.01", "1", "1"),
        (2026, "68900", "0", "0"),
    ],
)
def test_the_ei_rate_starts_at_the_line_7_exemption_and_the_premium_takes_over_later(
    year: int, salary: str, line_7: str, ei: str
) -> None:
    assert _ei_rates(year, salary) == (D(line_7), D(ei))


def _contribution_rate(
    code: str, birth_year: int, salary: str, months: int | None = None
) -> Decimal:
    given: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(BIRTH_YEAR, birth_year),
    ]
    if months is not None:
        given.append(Artifact(CPP_MONTHS, months))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(JurisdictionCode(code), 2026, tuple(given))
    )
    (sheet,) = worksheets[FORM]
    figure = sheet.get(bundled_kinds().kind("ca/marginal_contribution_rate")).value
    assert isinstance(figure, Decimal)
    return figure


@pytest.mark.parametrize("birth_year", [1955, 2010])
@pytest.mark.parametrize("salary", ["0", "2000", "2033", "20000", "70000"])
def test_a_filer_with_no_cpp_months_is_charged_no_cpp_on_a_further_dollar(
    birth_year: int, salary: str
) -> None:
    # Schedule 8 line A is 0 (70 or older all of 2026; not yet 18 in any month of 2026), so the
    # contribution is 0 and a further dollar of salary adds no CPP: only the EI rate of T2204
    # line 16 is left (1 for the $2,000 exemption band, 1.63% to the maximum, then 0), and the
    # form no longer raises a negative rate at $0 and $2,000.
    ei_rate = {"0": "0", "2000": "1", "2033": "1", "20000": "0.0163", "70000": "0"}[salary]

    assert _contribution_rate("CA-ON", birth_year, salary) == D(ei_rate)


@pytest.mark.parametrize("salary", ["0", "2000", "2033", "20000", "70000"])
def test_a_quebec_filer_born_in_2010_is_charged_no_pension_plan_on_a_further_dollar(
    salary: str,
) -> None:
    # Not yet 18 in any month of 2026: no QPP months. The Quebec EI rate is 1.30%; the form's
    # CPP rates are 0 in the same way.
    ei_rate = {"0": "0", "2000": "1", "2033": "0.013", "20000": "0.013", "70000": "0"}[salary]

    assert _contribution_rate("CA-QC", 2010, salary) == D(ei_rate)


def test_a_filer_with_cpp_months_is_still_charged_cpp() -> None:
    assert _contribution_rate("CA-ON", 1980, "20000") == D("0.0759") - D("0.0164") + D("0.0163")


@pytest.mark.parametrize(
    ("months", "salary", "rate"),
    [
        # Line A = 6: line E 1,750, line B 37,300, line D 42,500 (the proration table, 2026). Below
        # line B the base 4.95% and first additional 1% are charged with the EI 1.63%.
        (6, "20000", "0.0758"),
        # Between line B and line D only the second additional 4% (and no EI over $68,900 yet).
        (6, "40000", "0.0563"),
        # Over line D no CPP is charged any more; only the EI is left.
        (6, "50000", "0.0163"),
        (6, "90000", "0"),
        # Line A = 1: line B 6,216.67, line D 7,083.33.
        (1, "20000", "0.0163"),
    ],
)
def test_a_part_year_filer_is_charged_no_cpp_over_the_prorated_maximums(
    months: int, salary: str, rate: str
) -> None:
    assert _contribution_rate("CA-ON", 1980, salary, months) == D(rate)
