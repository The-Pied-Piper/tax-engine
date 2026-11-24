"""Where each part of the British Columbia marginal rate switches on, through the real engine, 2025.

Each income tax part counts only where its own tax is above zero, and the tax reduction's slope
only inside the reduction's range, so the rate steps at the salaries below (found cent by cent from
the forms' own lines; the extra-run check in `test_return_marginal_tax_rate_extra_run.py` shows the
rate agrees with the engine on each side). The federal part reads T1 line 42900 "Basic federal
tax", which is 0.00 at 18,820.26 and 0.01 at 18,820.27. The British Columbia part reads BC428 line
80, which is 0.00 at 25,551.24 and 0.01 at 25,551.25, inside the tax reduction's range (BC428
lines 73 to 79: 562.00 falling by 3.56% of the net income over 25,020.00). The reduction's slope
ends where line 79 reaches 0.00, at a salary of 41,183.21 (net income 40,806.38, line 78 is then
562.00). The 2026 thresholds are in `test_return_marginal_tax_rate_gates_2026.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
RETURN = "ca-bc/return"
BC428_FORM = "ca-bc/bc428"

TAX_AFTER_REDUCTION = "ca-bc/british_columbia_tax_after_reduction_return"
TAX_REDUCTION = "ca-bc/british_columbia_tax_reduction_return"
BC_GATE = "ca-bc/british_columbia_rate_gate"
REDUCTION_GATE = "ca-bc/british_columbia_reduction_gate"
PHASE_OUT = "ca-bc/british_columbia_reduction_phase_out_rate"
BRACKET = "ca-bc/british_columbia_bracket_rate_return"
FEDERAL = "ca-bc/marginal_federal_rate"
BC_RATE = "ca-bc/british_columbia_marginal_rate"
CONTRIBUTION = "ca-bc/marginal_contribution_rate"
MARGINAL = "ca-bc/marginal_tax_rate"
LINE_80 = "ca-bc/bc428_tax_after_reduction_line_80"


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled British Columbia manifest, as the calculator loads it, salary the
    # only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


# Salary, then the federal marginal rate, the British Columbia marginal rate, the contribution rate
# and the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # No tax and no contribution: every part is 0 although the bracket rates are 14.5% and 5.06%.
    ("100", "0", "0", "0", "0"),
    # T2204 line 16 rises 1 for 1 between 2,000 and 2,033: the EI rate is 1.
    ("2001", "0", "0", "1", "1"),
    # Contributions only: CPP 4.95% + 1% and EI 1.64%, no basic federal tax yet.
    ("18820.26", "0", "0", "0.0759", "0.0759"),
    # Basic federal tax is first positive: the federal part opens.
    ("18820.27", "0.1339945", "0", "0.0759", "0.2098945"),
    # The tax reduction (562.00) takes all the British Columbia tax at 20,000 and up to 25,551.24.
    ("20000", "0.1339945", "0", "0.0759", "0.2098945"),
    ("25551.24", "0.1339945", "0", "0.0759", "0.2098945"),
    # BC428 line 80 is first positive, inside the reduction's range: 5.06% x 0.9241 + 3.56% x 0.99.
    ("25551.25", "0.1339945", "0.08200346", "0.0759", "0.29189796"),
    ("41183.20", "0.1339945", "0.08200346", "0.0759", "0.29189796"),
    # The reduction has run out: 5.06% x 0.9241 only.
    ("41183.21", "0.1339945", "0.04675946", "0.0759", "0.25665396"),
    # Above the EI maximum of 65,700: CPP 4.95% + 1% only.
    ("70000", "0.1957725", "0.0737253", "0.0595", "0.3289978"),
    ("120000", "0.26", "0.1229", "0", "0.3829"),
    ("200000", "0.2930542655", "0.168", "0", "0.4610542655"),
]


@pytest.mark.parametrize(
    ("salary", "federal", "british_columbia", "contribution", "marginal"), PARTS
)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, british_columbia: str, contribution: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, BC_RATE) == D(british_columbia)
    assert _value(summary, CONTRIBUTION) == D(contribution)
    assert _value(summary, MARGINAL) == D(marginal)
    assert D(federal) + D(british_columbia) + D(contribution) == D(marginal)


@pytest.mark.parametrize(
    ("salary", "federal_part_is_open", "british_columbia_tax_is_positive"),
    [
        ("100", False, False),
        ("18820.26", False, False),
        ("18820.27", True, False),
        ("25551.24", True, False),
        ("25551.25", True, True),
        ("70000", True, True),
    ],
)
def test_the_gates_open_with_the_taxes_they_read(
    salary: str, federal_part_is_open: bool, british_columbia_tax_is_positive: bool
) -> None:
    summary = _summary(salary)

    assert (_value(summary, FEDERAL) > 0) is federal_part_is_open
    assert (_value(summary, TAX_AFTER_REDUCTION) > 0) is british_columbia_tax_is_positive
    assert _value(summary, BC_GATE) == D(int(british_columbia_tax_is_positive))


@pytest.mark.parametrize("salary", ["100", "18820.26", "25551.24", "25551.25"])
def test_the_bracket_rate_read_by_the_gate_is_ungated(salary: str) -> None:
    # The gate changes the part, not the bracket rate it multiplies: 5.06% at every one of these
    # salaries.
    assert _value(_summary(salary), BRACKET) == D("0.0506")


def test_the_british_columbia_gate_follows_line_80_and_not_the_reduction() -> None:
    # At 20,000 the reduction is positive (562.00) while BC428 line 80 is 0.00, and the gate follows
    # line 80, so the British Columbia part is absent although the reduction is in the rate.
    kinds = bundled_kinds()
    summary = _summary("20000")
    (bc428,) = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, 2025, (Artifact(EMPLOYMENT_INCOME, D("20000")),))
    )[BC428_FORM]

    assert _value(summary, TAX_REDUCTION) > 0
    assert bc428.get(kinds.kind(LINE_80)).value == D("0")
    assert _value(summary, BC_GATE) == D("0")
    assert _value(summary, BC_RATE) == D("0")


@pytest.mark.parametrize(
    ("salary", "reduction_is_positive"),
    [
        ("20000", True),
        ("30000", True),
        ("41183.20", True),
        ("41183.21", False),
        ("45000", False),
        ("70000", False),
    ],
)
def test_the_reduction_gate_follows_the_british_columbia_tax_reduction(
    salary: str, reduction_is_positive: bool
) -> None:
    # BC428 line 79 is 0.01 at 41,183.20 and 0.00 at 41,183.21.
    summary = _summary(salary)

    assert (_value(summary, TAX_REDUCTION) > 0) is reduction_is_positive
    assert _value(summary, REDUCTION_GATE) == D(int(reduction_is_positive))


@pytest.mark.parametrize(
    ("salary", "phase_out"),
    [
        # 3.56% from a net income of 25,020.15 (a salary of 25,237.53) to just under 40,807.
        ("25237.52", "0"),
        ("25237.53", "0.0356"),
        ("30000", "0.0356"),
        ("41183.20", "0.0356"),
        ("41183.21", "0"),
        ("70000", "0"),
    ],
)
def test_the_reduction_adds_its_slope_while_line_78_and_line_79_are_positive(
    salary: str, phase_out: str
) -> None:
    assert _value(_summary(salary), PHASE_OUT) == D(phase_out)
