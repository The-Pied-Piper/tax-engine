"""The T1 lines a provincial form copies are asked once, by the T1, and imported from its export.

Four T1 lines are the inputs: line 31000 (line 87, base CPP or QPP contributions on self-employment
income and other earnings), line 31900 (line 102, student loan interest), line 33099 (line 107,
medical expenses) and line 40427 (line 124, minimum tax carryover). AB428 line 64, BC428 line 66,
MB428 line 63, NL428 line 68 and SK428 line 65 print "amount from line 40427 of your return", and
NL428 lines 28, 43 and 48 print the amounts from lines 31000, 31900 and 33099, so each of those is
a total of the T1 export and none of them has an input of its own. A caller who gives line 40427
once reaches every one of those forms; a caller who gives none reads each as 0.00.

The real registered engine is run end to end over each province's real 2025 manifest, as the
provincial end-to-end tests do, with the T1 amounts as inputs. The results are hand-computed from
the printed rates: 35% (AB), 34.9% (BC), 50% (MB and SK) and 60% (NL) of the amount.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_sk
from tax_engine import build_tax_computation
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.manifest_support import inputs_of

D = Decimal
MINIMUM_TAX_CARRYOVER = "ca/minimum_tax_carryover"
CPP_QPP = "ca/self_employment_cpp_qpp_contributions"
STUDENT_LOAN_INTEREST = "ca/student_loan_interest"
MEDICAL_EXPENSES = "ca/medical_expenses"
T1_INPUTS = {MINIMUM_TAX_CARRYOVER, CPP_QPP, STUDENT_LOAN_INTEREST, MEDICAL_EXPENSES}
# Province code, then each form that prints a copy: its form, the figure, and what it is of the
# $1,000.00 given on line 40427 (the printed rate) or of the amount given on line 31000, 31900 or
# 33099 (the amount itself, "1"), as a fraction of the amount.
CARRYOVER = {
    "CA-AB": ("ca-ab/ab428", "ca-ab/ab428_minimum_tax_carryover_line_64", D("0.35")),
    "CA-BC": ("ca-bc/bc428", "ca-bc/bc428_minimum_tax_carryover_line_66", D("0.349")),
    "CA-MB": ("ca-mb/mb428", "ca-mb/mb428_minimum_tax_carryover_line_63", D("0.5")),
    "CA-NL": ("ca-nl/nl428", "ca-nl/nl428_minimum_tax_carryover_line_68", D("0.6")),
    "CA-SK": ("ca-sk/sk428", "ca-sk/sk428_minimum_tax_carryover_line_65", D("0.5")),
}
NL_COPIES = {
    CPP_QPP: "ca-nl/nl428_qpp_contributions_line_28",
    STUDENT_LOAN_INTEREST: "ca-nl/nl428_student_loan_interest_line_43",
    MEDICAL_EXPENSES: "ca-nl/nl428_medical_expenses_line_48",
}
OLD_INPUTS = (
    "ca-ab/ab428_minimum_tax_carryover_amount_line_64",
    "ca-bc/bc428_minimum_tax_carryover_amount",
    "ca-mb/mb428_minimum_tax_carryover_amount_line_63",
    "ca-nl/nl428_minimum_tax_carryover_amount_line_68",
    "ca-sk/sk428_minimum_tax_carryover_amount_line_65",
    *NL_COPIES.values(),
)


def _compute(code: str, amounts: dict[str, str]) -> dict[str, tuple[Worksheet, ...]]:
    kinds = artifact_kinds()
    starting = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    starting += [Artifact(kinds.kind(name), D(value)) for name, value in amounts.items()]
    return build_tax_computation().compute(JurisdictionCode(code), 2025, *starting)


def _figure(worksheets: dict[str, tuple[Worksheet, ...]], form: str, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    (sheet,) = worksheets[form]
    return sheet.get(kind).value


@pytest.mark.parametrize("code", CARRYOVER)
def test_line_40427_given_once_reaches_the_province_with_its_printed_rate(code: str) -> None:
    form, name, rate = CARRYOVER[code]

    worksheets = _compute(code, {MINIMUM_TAX_CARRYOVER: "1000.00"})

    assert _figure(worksheets, form, name) == D("1000.00") * rate


@pytest.mark.parametrize("code", CARRYOVER)
def test_a_caller_who_gives_none_reads_the_carryover_as_zero(code: str) -> None:
    form, name, _ = CARRYOVER[code]

    assert _figure(_compute(code, {}), form, name) == D("0.00")


def test_nl428_lines_28_43_and_48_are_the_amounts_given_on_the_t1_lines() -> None:
    given = {CPP_QPP: "111.11", STUDENT_LOAN_INTEREST: "222.22", MEDICAL_EXPENSES: "333.33"}

    worksheets = _compute("CA-NL", given)

    for t1_name, name in NL_COPIES.items():
        assert _figure(worksheets, "ca-nl/nl428_credits", name) == D(given[t1_name]), name


def test_a_caller_who_gives_none_reads_nl428_lines_28_43_and_48_as_zero() -> None:
    worksheets = _compute("CA-NL", {})

    for name in NL_COPIES.values():
        assert _figure(worksheets, "ca-nl/nl428_credits", name) == D("0.00"), name


@pytest.mark.parametrize(
    ("code", "package"),
    [
        ("CA-AB", tax_engine.jurisdictions.ca_ab),
        ("CA-BC", tax_engine.jurisdictions.ca_bc),
        ("CA-MB", tax_engine.jurisdictions.ca_mb),
        ("CA-NL", tax_engine.jurisdictions.ca_nl),
        ("CA-SK", tax_engine.jurisdictions.ca_sk),
    ],
)
def test_no_provincial_form_declares_a_copy_of_a_t1_line_as_an_input(
    code: str, package: object
) -> None:
    folder = Path(package.__path__[0]) / "manifests" / "2025"  # type: ignore[attr-defined]
    manifest = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)

    assert not set(OLD_INPUTS) & set(inputs_of(manifest))
    assert T1_INPUTS <= set(inputs_of(manifest))
