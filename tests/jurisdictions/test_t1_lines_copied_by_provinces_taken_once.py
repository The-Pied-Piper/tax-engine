"""The T1 lines a provincial form copies are asked once, by the T1, and imported from its export.

Six T1 lines are the inputs: line 31000 (line 87, base CPP or QPP contributions on self-employment
income and other earnings), line 31217 (line 89, EI premiums on self-employment and other eligible
earnings), line 31900 (line 102, student loan interest), line 33099 (line 107,
medical expenses), line 33199 (line 111, allowable medical expenses for other dependants) and line
40427 (line 124, minimum tax carryover). AB428 line 64, BC428 line 66, MB428 line 63, NL428 line 68
and SK428 line 65 print "amount from line 40427 of your return", as does ON428 line 59 (whose line
60 is the lesser of line 58 and that amount at 24.63%), NL428 lines 28, 30, 43 and 48 print the
amounts from lines 31000, 31217, 31900 and 33099, AB428 line 44, BC428 line 46, MB428 line 43 and
SK428 line 43 print "amount from line 33099 of your return", and SK428 line 49 prints the amount
from line 33199, so each of those is a total of the T1 export and none of them has an input of its
own. A caller who
gives a T1 line once reaches every one of those forms; a caller who gives none reads each as 0.00.
AB428 line 50, BC428 line 52 and ON428 line 42 (other dependants) and ON428 line 36 are not copies
of the T1 and keep their own inputs.

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
import tax_engine.jurisdictions.ca_on
import tax_engine.jurisdictions.ca_sk
from tax_engine import build_tax_computation
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
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
EI_SELF_EMPLOYMENT = "ca/ei_premiums_on_self_employment"
STUDENT_LOAN_INTEREST = "ca/student_loan_interest"
MEDICAL_EXPENSES = "ca/medical_expenses"
OTHER_DEPENDANTS = "ca/other_dependants_medical_expenses"
T1_INPUTS = {
    MINIMUM_TAX_CARRYOVER,
    CPP_QPP,
    EI_SELF_EMPLOYMENT,
    STUDENT_LOAN_INTEREST,
    MEDICAL_EXPENSES,
    OTHER_DEPENDANTS,
}
# Province code, then each form that prints a copy: its form, the figure, and what it is of the
# $1,000.00 given on line 40427 (the printed rate) or of the amount given on line 31000, 31900 or
# 33099 (the amount itself, "1"), as a fraction of the amount.
CARRYOVER = {
    "CA-AB": ("ca-ab/ab428", "ca-ab/ab428_minimum_tax_carryover_line_64", D("0.35")),
    "CA-BC": ("ca-bc/bc428", "ca-bc/bc428_minimum_tax_carryover_line_66", D("0.349")),
    "CA-MB": ("ca-mb/mb428", "ca-mb/mb428_minimum_tax_carryover_line_63", D("0.5")),
    "CA-NL": ("ca-nl/nl428", "ca-nl/nl428_minimum_tax_carryover_line_68", D("0.6")),
    "CA-ON": ("ca-on/on428", "ca-on/on428_minimum_tax_carryover_line_60", D("0.2463")),
    "CA-SK": ("ca-sk/sk428", "ca-sk/sk428_minimum_tax_carryover_line_65", D("0.5")),
}
NL_COPIES = {
    CPP_QPP: "ca-nl/nl428_qpp_contributions_line_28",
    EI_SELF_EMPLOYMENT: "ca-nl/nl428_ei_premiums_line_30",
    STUDENT_LOAN_INTEREST: "ca-nl/nl428_student_loan_interest_line_43",
    MEDICAL_EXPENSES: "ca-nl/nl428_medical_expenses_line_48",
}
# Province code, then the form and figure of its line that prints "amount from line 33099", and the
# line after it (over the limit) that reads it, with that line's value for 5,000.005 given at a
# $70,000 salary: the T1 export is 5,000.01, net income is 69,335.00 and 3% of it is 2,080.05, so
# the line is 2,919.96 (Manitoba's own cap is 1,728.00, so 3,272.01).
MEDICAL = {
    "CA-AB": (
        "ca-ab/ab428_credits",
        "ca-ab/ab428_medical_expenses_line_44",
        "ca-ab/ab428_medical_expenses_over_limit_line_49",
        D("2919.96"),
    ),
    "CA-BC": (
        "ca-bc/bc428",
        "ca-bc/bc428_medical_expenses_line_46",
        "ca-bc/bc428_medical_expenses_over_limit_line_51",
        D("2919.96"),
    ),
    "CA-MB": (
        "ca-mb/mb428_credits",
        "ca-mb/mb428_medical_expenses_line_43",
        "ca-mb/mb428_medical_expenses_over_limit_line_48",
        D("3272.01"),
    ),
    "CA-SK": (
        "ca-sk/sk428_credits",
        "ca-sk/sk428_medical_expenses_line_43",
        "ca-sk/sk428_medical_expenses_over_limit_line_48",
        D("2919.96"),
    ),
}
NL_LINE_35 = "ca-nl/nl428_cpp_ei_and_other_line_35"
T1_LINE_96 = "ca/credits_subtotal_line_96"
SK_LINE_49 = "ca-sk/sk428_other_dependants_medical_expenses_line_49"
SK_LINE_50 = "ca-sk/sk428_medical_expenses_line_50"
OLD_INPUTS = (
    "ca-ab/ab428_medical_expenses_line_44",
    "ca-bc/bc428_medical_expenses_line_46",
    "ca-mb/mb428_medical_expenses_line_43",
    "ca-sk/sk428_medical_expenses_line_43",
    SK_LINE_49,
    "ca-ab/ab428_minimum_tax_carryover_amount_line_64",
    "ca-bc/bc428_minimum_tax_carryover_amount",
    "ca-mb/mb428_minimum_tax_carryover_amount_line_63",
    "ca-nl/nl428_minimum_tax_carryover_amount_line_68",
    "ca-sk/sk428_minimum_tax_carryover_amount_line_65",
    "ca-on/on428_minimum_tax_carryover_line_60",
    *NL_COPIES.values(),
)


def _compute(code: str, amounts: dict[str, str]) -> dict[str, tuple[Worksheet, ...]]:
    kinds = artifact_kinds()
    starting = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    starting += [Artifact(kinds.kind(name), D(value)) for name, value in amounts.items()]
    return build_tax_computation().compute(
        TaxCalculationRequest(JurisdictionCode(code), 2025, tuple(starting))
    )


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


def test_nl428_lines_28_30_43_and_48_are_the_amounts_given_on_the_t1_lines() -> None:
    given = {
        CPP_QPP: "111.11",
        EI_SELF_EMPLOYMENT: "444.44",
        STUDENT_LOAN_INTEREST: "222.22",
        MEDICAL_EXPENSES: "333.33",
    }

    worksheets = _compute("CA-NL", given)

    for t1_name, name in NL_COPIES.items():
        assert _figure(worksheets, "ca-nl/nl428_credits", name) == D(given[t1_name]), name


def test_line_31217_given_once_raises_nl428_line_35_and_t1_line_96_by_that_amount() -> None:
    # $70,000, 400.00 on line 31217. NL428 line 35 is line 27 (3,291.75) plus line 29 (1,077.48) =
    # 4,369.23 without it, 4,769.23 with it; T1 line 96 is 5,840.23 without it (3,291.75 + 1,077.48
    # + 1,471.00), 6,240.23 with it. Both read the one figure the T1 form exports.
    for given, nl_35, t1_96 in (
        ({}, "4369.23", "5840.23"),
        ({EI_SELF_EMPLOYMENT: "400"}, "4769.23", "6240.23"),
    ):
        nl = _figure(_compute("CA-NL", given), "ca-nl/nl428_credits", NL_LINE_35)
        t1 = _figure(_compute("CA-NL", given), "ca/t1_tax_and_credits", T1_LINE_96)
        assert (nl, t1) == (D(nl_35), D(t1_96))


def test_a_caller_who_gives_none_reads_nl428_lines_28_30_43_and_48_as_zero() -> None:
    worksheets = _compute("CA-NL", {})

    for name in NL_COPIES.values():
        assert _figure(worksheets, "ca-nl/nl428_credits", name) == D("0.00"), name


@pytest.mark.parametrize("code", MEDICAL)
def test_line_33099_given_once_reaches_the_province_and_the_line_after_it(code: str) -> None:
    form, line, over_limit, expected = MEDICAL[code]

    worksheets = _compute(code, {MEDICAL_EXPENSES: "5000.005"})

    # The T1 export is cent-rounded, half up, and the provincial line is that figure.
    assert _figure(worksheets, form, line) == D("5000.01")
    assert _figure(worksheets, form, over_limit) == expected


@pytest.mark.parametrize("code", MEDICAL)
def test_a_caller_who_gives_none_reads_the_medical_line_as_zero(code: str) -> None:
    form, line, _, _ = MEDICAL[code]

    assert _figure(_compute(code, {}), form, line) == D("0.00")


def test_sk428_line_49_is_the_amount_given_on_t1_line_33199() -> None:
    worksheets = _compute("CA-SK", {OTHER_DEPENDANTS: "250.555"})

    # The T1 export is cent-rounded, half up, and line 49 is that figure; with no line 33099 the
    # line 48 is 0.00, so line 50 (line 48 plus line 49) is the same 250.56.
    assert _figure(worksheets, "ca-sk/sk428_credits", SK_LINE_49) == D("250.56")
    assert _figure(worksheets, "ca-sk/sk428_credits", SK_LINE_50) == D("250.56")
    assert _figure(_compute("CA-SK", {}), "ca-sk/sk428_credits", SK_LINE_49) == D("0.00")


@pytest.mark.parametrize(
    ("code", "package"),
    [
        ("CA-AB", tax_engine.jurisdictions.ca_ab),
        ("CA-BC", tax_engine.jurisdictions.ca_bc),
        ("CA-MB", tax_engine.jurisdictions.ca_mb),
        ("CA-NL", tax_engine.jurisdictions.ca_nl),
        ("CA-ON", tax_engine.jurisdictions.ca_on),
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
