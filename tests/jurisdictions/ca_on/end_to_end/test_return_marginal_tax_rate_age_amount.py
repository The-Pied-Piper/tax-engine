"""The fall of the Ontario age amount in the Ontario marginal rate, worked by hand, 2025 and 2026.

For a filer born 1960 or earlier the age amount (ON428 line 10) is the printed maximum less 15% of
the net income over the threshold (Worksheet ON428 "Line 58080 - Age amount": line 1 maximum, line
3 threshold, line 5 "Applicable rate 15%"), until it is 0. Each dollar of that fall is Ontario tax
at the credit rate of ON428 line 45 (5.05%), so a further dollar of net income over the threshold
adds 0.15 x 5.05% = 0.007575 of Ontario tax while an age amount is still claimed. The credit sits
beside the credit on the contributions: before the surtax factor, the reduction gate, the LIFT
phase-out and the Ontario gate. A further dollar of salary is N dollars of net income, where N is 1
less the CPP first and second additional rates (T1 line 22215 takes them off the income), so

    age term = 0.15 x N x 5.05%            (0 at or under the threshold, 0 once the amount is 0)
    Ontario  = (bracket rate x N + age term - 5.05% x (CPP base + EI)) x surtax factor,
               + the LIFT reduction rate 5% x N where the LIFT credit (Schedule ON428-A) is still
               being reduced, that is net income from $32,500 to $50,000, all after the surtax,
               where the Ontario tax after the LIFT credit is above 0 (the surtax factor is 1 and
               the tax reduction is 0 at every salary below)

The datasets:

- 2025: threshold 46,330, maximum 6,223 (zero at net income 46,330 + 6,223 / 0.15 = 87,816.67);
  CPP 4.95% base and 1% first additional up to the $71,300 maximum, 4% second additional from
  $71,300 to $81,200; EI 1.64% up to $65,700; brackets 5.05% to $52,886, then 9.15%.
- 2026: threshold 47,210, maximum 6,341 (zero at net income 47,210 + 6,341 / 0.15 = 89,483.33);
  EI 1.63% up to $68,900; brackets 5.05% to $53,891, then 9.15%. A filer born 1955 has no CPP in
  2026 (past 70 all year), so N is 1.

Each worksheet line rounds half-up to the cent, so the last salary with an age amount left is
where line 7 is still 0.01 or more: 2025 salary $88,890 is net income $87,816 (the first and the
second additional CPP, $678 + $396, come off a salary over $81,200): line 4 is 41,486, line 6 is
6,222.90, line 7 is 0.10; one more dollar gives line 4 41,487, line 6 6,223.05 and line 7 0. 2026
salary $89,483 is net income $89,483: line 4 is 42,273, line 6 is 6,340.95, line 7 is 0.05; one
more dollar gives line 4 42,274, line 6 6,341.10 and line 7 0. The first dollar over the threshold:
2025 salary $46,763 has the first additional CPP 0.01 x (46,763 - 3,500) = 432.63 off it, net
income 46,330.37, line 4 0.37; salary $46,762 gives net income 46,329.38 and line 4 0. 2026 salary
$47,210 is net income 47,210 (line 4 0) and $47,211 is line 4 1.

A filer born in 1980 and a filer with no birth year have no age amount claimed (the worksheet's
count of aged 65 or older is 0 or blank), so their age term is 0 at every salary.
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
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"

CREDIT_RATE = D("0.0505")
LIFT_RATE = D("0.05")
AGE_RATE = D("0.15")
AGE_TERM = "ca-on/marginal_ontario_age_credit_rate"
ONTARIO_RATE = "ca-on/ontario_marginal_rate"
SURTAX_FACTOR = "ca-on/ontario_surtax_factor"
LINE_4 = "ca-on/marginal_age_income_over_threshold"
CLAIMED = "ca-on/marginal_age_amount_claimed"

# (year, salary): N, the CPP base plus EI rate of a filer who pays CPP, the bracket rate of ON428
# line 5. At salary 0 the Ontario tax after the LIFT credit is 0, so the Ontario rate is 0.
CPP_FILER = {
    (2025, "0"): ("0", "0", "0.0505"),
    (2025, "46762"): ("0.99", "0.0659", "0.0505"),
    (2025, "46763"): ("0.99", "0.0659", "0.0505"),
    (2025, "60000"): ("0.99", "0.0659", "0.0915"),
    (2025, "88890"): ("1", "0", "0.0915"),
    (2025, "88891"): ("1", "0", "0.0915"),
    (2026, "0"): ("0", "0", "0.0505"),
    (2026, "47210"): ("0.99", "0.0658", "0.0505"),
    (2026, "47211"): ("0.99", "0.0658", "0.0505"),
    (2026, "60000"): ("0.99", "0.0658", "0.0915"),
    (2026, "89483"): ("1", "0", "0.0915"),
    (2026, "89484"): ("1", "0", "0.0915"),
}
# The 2026 filer born 1955 pays no CPP: N is 1 and only the EI (to $68,900) earns a credit.
NO_CPP_2026 = {
    (2026, "0"): ("0", "0", "0.0505"),
    (2026, "47210"): ("1", "0.0163", "0.0505"),
    (2026, "47211"): ("1", "0.0163", "0.0505"),
    (2026, "60000"): ("1", "0.0163", "0.0915"),
    (2026, "89483"): ("1", "0", "0.0915"),
    (2026, "89484"): ("1", "0", "0.0915"),
}
# The salaries whose net income is in the LIFT credit's phase-out ($32,500 to $50,000).
IN_LIFT_PHASE_OUT = {"46762", "46763", "47210", "47211"}
# Born 1955: the age amount is still falling (net income over the threshold, amount left).
FALLING = {
    (2025, "46763"),
    (2025, "60000"),
    (2025, "88890"),
    (2026, "47211"),
    (2026, "60000"),
    (2026, "89483"),
}
# Net income over the threshold (worksheet line 4) of the born 1955 filer, and the age amount
# claimed before the printed maximum (line 7).
LINE_4_1955 = {
    (2025, "0"): ("0.00", "6223.00"),
    (2025, "46762"): ("0.00", "6223.00"),
    (2025, "46763"): ("0.37", "6222.94"),
    (2025, "60000"): ("13105.00", "4257.25"),
    (2025, "88890"): ("41486.00", "0.10"),
    (2025, "88891"): ("41487.00", "0.00"),
    (2026, "0"): ("0.00", "6341.00"),
    (2026, "47210"): ("0.00", "6341.00"),
    (2026, "47211"): ("1.00", "6340.85"),
    (2026, "60000"): ("12790.00", "4422.50"),
    (2026, "89483"): ("42273.00", "0.05"),
    (2026, "89484"): ("42274.00", "0.00"),
}


def _summary(year: int, salary: str, birth_year: int | None) -> Worksheet:
    given: list[Artifact[Decimal] | Artifact[int]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if birth_year is not None:
        given.append(Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(TaxCalculationRequest(ONTARIO, year, tuple(given)))
    (summary,) = worksheets[RETURN]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


def _expected_ontario_rate(parts: tuple[str, str, str], age_term: Decimal, salary: str) -> Decimal:
    net_income_rate, contribution_rate, bracket = (D(part) for part in parts)
    if salary == "0":
        return D("0")
    lift = LIFT_RATE * net_income_rate if salary in IN_LIFT_PHASE_OUT else D("0")
    return bracket * net_income_rate + age_term - CREDIT_RATE * contribution_rate + lift


def _cases() -> list[pytest.ParameterSet]:
    cases = []
    for birth_year in (1955, 1980, None):
        for (year, salary), parts in CPP_FILER.items():
            if birth_year == 1955 and (year, salary) in NO_CPP_2026:
                parts = NO_CPP_2026[(year, salary)]
            falling = birth_year == 1955 and (year, salary) in FALLING
            age_term = AGE_RATE * D(parts[0]) * CREDIT_RATE if falling else D("0")
            cases.append(
                pytest.param(
                    year,
                    salary,
                    birth_year,
                    age_term,
                    _expected_ontario_rate(parts, age_term, salary),
                    id=f"{year}-{salary}-{birth_year or 'blank'}",
                )
            )
    return cases


@pytest.mark.parametrize(("year", "salary", "birth_year", "age_term", "ontario_rate"), _cases())
def test_the_age_amount_fall_adds_its_credit_rate_to_the_ontario_marginal_rate(
    year: int, salary: str, birth_year: int | None, age_term: Decimal, ontario_rate: Decimal
) -> None:
    summary = _summary(year, salary, birth_year)

    assert _value(summary, SURTAX_FACTOR) == D("1")
    assert _value(summary, AGE_TERM) == age_term
    assert _value(summary, ONTARIO_RATE) == ontario_rate


@pytest.mark.parametrize(("key", "figures"), list(LINE_4_1955.items()))
def test_the_worksheet_figures_the_age_term_is_gated_by_are_those_of_the_printed_worksheet(
    key: tuple[int, str], figures: tuple[str, str]
) -> None:
    year, salary = key
    summary = _summary(year, salary, 1955)

    assert _value(summary, LINE_4) == D(figures[0])
    assert _value(summary, CLAIMED) == D(figures[1])


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("birth_year", [1980, None])
def test_a_filer_with_no_age_amount_has_no_age_term_at_any_salary(
    year: int, birth_year: int | None
) -> None:
    for salary in ("0", "50000", "60000", "75000", "100000"):
        assert _value(_summary(year, salary, birth_year), CLAIMED) == D("0")
        assert _value(_summary(year, salary, birth_year), AGE_TERM) == D("0")
