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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
        "ca/marginal_basic_federal_tax",
        "ca/marginal_cpp_line_7_difference",
        "ca/marginal_cpp_line_4",
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


@pytest.mark.parametrize("code", ["CA-AB", "CA-BC", "CA-NL"])
def test_a_province_can_import_the_form_alone(code: str) -> None:
    # Everything the form reads is an export of a T1 form that each province imports, and none of
    # the artifacts it produces is produced by the province's own return, so an `imports` line
    # is all a province needs.
    manifest = real_manifest(code)
    names = {form.name for form in manifest.forms}
    produced = {
        output
        for form in manifest.forms
        for step in form.capabilities
        for output in step.produces.values()
    }
    own = {output for step in _form().capabilities for output in step.produces.values()}

    assert {
        "ca/t1_employment_income",
        "ca/t1_taxable_income",
        "ca/t1_tax_and_credits",
    } <= names
    assert not own & produced


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
