"""5005-R (2025) line 91, the PPIP premiums paid, from the salary alone, real parts.

Form text (CRA 5005-R, 5005-r-25e.txt, page 6): "Line 91 and line 31205: Provincial parental
insurance plan (PPIP) premiums paid (box 55 of all T4 slips) (maximum $484.12)". The take-home
caller has no T4 slip, so the input `ca-qc/ppip_premiums_given` is optional: a request that gives it
has that figure as line 91, unchanged; a request that leaves it out has line 91 computed by
`ca/given_or_contribution_tier` from the employment income with the `ca-qc/ppip_premium` dataset
(0.494% of the earnings to $98,000, at most $484.12), as T2204 line 4 is. RL-1 box H (TP-1 line 97)
is the same figure. The figures are hand-computed from the printed forms, not a CRA example:
20,000 x 0.494% = 98.80, 70,000 x 0.494% = 345.80, and 200,000 is above the $98,000 maximum, so the
printed maximum 484.12.

The test composes the real input part and the real line 91 part under a made-up header, the real
Quebec T1 employment income parts that declare the salary, and the real form declaration, on the
shared Quebec `take_home_service` fixture.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import PPIP_PREMIUMS_GIVEN, PPIP_PREMIUMS_PAID
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import T1_SALARY_PARTS, quebec_kinds
from tests.kinds import non_negative

D = Decimal
FORM_PART = QUEBEC_PARTS / "ppip_premium.yaml"
INPUTS_PART = "ppip_premium_inputs.yaml"
LINE_PART = QUEBEC_PARTS / "ppip_premium_line_91.yaml"
IDENTIFIER = "ca-qc/ppip_premiums_paid"

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)


def _line_91(take_home_service: TakeHomeService, salary: str, given: str | None = None) -> Decimal:
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if given is not None:
        starting.append(Artifact(PPIP_PREMIUMS_GIVEN, D(given)))
    service = take_home_service(
        HEADER,
        FORM_PART.read_text(encoding="utf-8"),
        *T1_SALARY_PARTS,
        INPUTS_PART,
        LINE_PART.name,
    )
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca-qc/ppip_premium"]
    return sheet.get(PPIP_PREMIUMS_PAID).value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-qc/ppip_premium"}
    record_total, step = part["capabilities"]
    assert record_total == {
        "name": "core/record_total",
        "title": "Employment income, T1 line 10100",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/t1_employment_income.employment_income_line_10100"},
        "produces": {"output": "ca-qc/ppip_premium_employment_income"},
    }
    assert isinstance(step, dict)
    return step


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 0.494% of 20,000 and of 70,000.
        ("20000", "98.80"),
        ("70000", "345.80"),
        # Above the $98,000 maximum insurable income: earnings above it add nothing.
        ("200000", "484.12"),
        ("98000", "484.12"),
    ],
)
def test_a_blank_line_91_is_the_ppip_premium_on_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert _line_91(take_home_service, salary) == D(expected)


def test_a_blank_line_91_is_computed_to_the_cent(take_home_service: TakeHomeService) -> None:
    assert str(_line_91(take_home_service, "70000")) == "345.80"


@pytest.mark.parametrize("given", ["400.00", "0"])
def test_a_given_line_91_is_the_output_unchanged(
    take_home_service: TakeHomeService, given: str
) -> None:
    assert str(_line_91(take_home_service, "70000", given)) == given


def test_a_given_line_91_is_not_computed_from_the_salary(
    take_home_service: TakeHomeService,
) -> None:
    # 20,000 would give 98.80; the figure typed from the T4 is line 91 as it is.
    assert str(_line_91(take_home_service, "20000", "400.00")) == "400.00"


def test_the_part_is_a_record_total_of_line_10100_then_one_given_or_contribution_tier_step() -> (
    None
):
    assert _step() == {
        "name": "ca/given_or_contribution_tier",
        "title": "Provincial parental insurance plan (PPIP) premiums paid",
        "reference": "91",
        "unit": "ca/cad",
        "params": {"tier": "ca-qc/ppip_premium"},
        "consumes": {
            "given": "ca-qc/ppip_premiums_given",
            "earnings": "ca-qc/ppip_premium_employment_income",
        },
        "blank": {"given": "compute"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is PPIP_PREMIUMS_PAID
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
