"""The UCCB and RDSP amounts are asked once, by the T1 lines they belong to, and every form that
prints them again as a total imports them from the T1 form's export.

Four T1 lines are the inputs: line 11700 (UCCB income), line 12500 (RDSP income), line 21300 (UCCB
repayment) and the RDSP income repayment included on line 23200. Schedule 6 line 11, BC479 lines 2
and 4, MB479 lines 2 and 4 and NL428 lines 89 and 91 (column 1) print a total of two of them, so
each is a sum step over the T1 export and none of them has an input of its own. A caller that gives
line 11700 once reaches every one of those forms; a caller that gives none reads each total as
0.00.

The real registered engine is run end to end over each province's real 2025 manifest, as the
provincial end-to-end tests do, with the starting amounts as inputs. The sums are hand-added from
the amounts given.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_nl
from tax_engine import build_tax_computation
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units

D = Decimal
UCCB_INCOME = "ca/uccb_income"
RDSP_INCOME = "ca/rdsp_income"
UCCB_REPAYMENT = "ca/uccb_repayment"
RDSP_REPAYMENT = "ca/rdsp_income_repayment"
SCHEDULE_6_LINE_11 = ("ca/schedule_6", "ca/uccb_and_rdsp_income")
# Province code, then each form that prints a total: its form, the line 2 / 89 total of the
# repayments and the line 4 / 91 total of the incomes.
PROVINCES = {
    "CA-ON": (SCHEDULE_6_LINE_11,),
    "CA-BC": (
        SCHEDULE_6_LINE_11,
        ("ca-bc/bc479", "ca-bc/bc479_uccb_rdsp_repayments_line_2"),
        ("ca-bc/bc479", "ca-bc/bc479_uccb_rdsp_income_line_4"),
    ),
    "CA-MB": (
        SCHEDULE_6_LINE_11,
        ("ca-mb/mb479", "ca-mb/mb479_uccb_rdsp_repayments_line_2"),
        ("ca-mb/mb479", "ca-mb/mb479_uccb_rdsp_income_line_4"),
    ),
    "CA-NL": (
        SCHEDULE_6_LINE_11,
        ("ca-nl/nl428", "ca-nl/nl428_uccb_rdsp_repayments_line_89"),
        ("ca-nl/nl428", "ca-nl/nl428_uccb_rdsp_income_line_91"),
    ),
}
INCOME_LINES = {
    "ca/uccb_and_rdsp_income",
    "ca-bc/bc479_uccb_rdsp_income_line_4",
    "ca-mb/mb479_uccb_rdsp_income_line_4",
    "ca-nl/nl428_uccb_rdsp_income_line_91",
}
OLD_TOTAL_INPUTS = (
    "ca/uccb_and_rdsp_income",
    "ca-bc/bc479_uccb_rdsp_repayments_line_2",
    "ca-bc/bc479_uccb_rdsp_income_line_4",
    "ca-mb/mb479_uccb_rdsp_repayments_line_2",
    "ca-mb/mb479_uccb_rdsp_income_line_4",
    "ca-nl/nl428_uccb_rdsp_repayments_line_89",
    "ca-nl/nl428_uccb_rdsp_income_line_91",
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


@pytest.mark.parametrize("code", PROVINCES)
def test_line_11700_given_once_reaches_every_form_that_prints_a_total(code: str) -> None:
    worksheets = _compute(code, {UCCB_INCOME: "1200.50"})

    for form, name in PROVINCES[code]:
        expected = D("1200.50") if name in INCOME_LINES else D("0.00")
        assert _figure(worksheets, form, name) == expected, name


@pytest.mark.parametrize("code", PROVINCES)
def test_each_total_adds_its_two_t1_lines(code: str) -> None:
    worksheets = _compute(
        code,
        {
            UCCB_INCOME: "1200.50",
            RDSP_INCOME: "300.25",
            UCCB_REPAYMENT: "40.10",
            RDSP_REPAYMENT: "9.90",
        },
    )

    for form, name in PROVINCES[code]:
        expected = D("1500.75") if name in INCOME_LINES else D("50.00")
        assert _figure(worksheets, form, name) == expected, name


@pytest.mark.parametrize("code", PROVINCES)
def test_a_caller_who_gives_none_reads_every_total_as_zero(code: str) -> None:
    worksheets = _compute(code, {})

    for form, name in PROVINCES[code]:
        assert _figure(worksheets, form, name) == D("0.00"), name


@pytest.mark.parametrize("code", PROVINCES)
def test_the_income_given_once_lowers_the_cwb_net_income_of_schedule_6(code: str) -> None:
    given = _compute(code, {UCCB_INCOME: "1000.00"})
    none = _compute(code, {})

    line_10 = "ca/cwb_net_income_total_line_10"
    line_12 = "ca/cwb_net_income_less_uccb_rdsp_line_12"
    assert _figure(given, "ca/schedule_6", line_10) == _figure(none, "ca/schedule_6", line_10)
    assert _figure(given, "ca/schedule_6", line_12) == (
        _figure(none, "ca/schedule_6", line_12) - D("1000.00")
    )


def _manifest_folder(code: str) -> Path:
    package = {
        "CA-BC": tax_engine.jurisdictions.ca_bc,
        "CA-MB": tax_engine.jurisdictions.ca_mb,
        "CA-NL": tax_engine.jurisdictions.ca_nl,
    }[code]
    return Path(package.__path__[0]) / "manifests" / "2025"


@pytest.mark.parametrize("code", ["CA-BC", "CA-MB", "CA-NL"])
def test_no_form_declares_a_total_of_the_two_lines_as_an_input(code: str) -> None:
    manifest = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(
        _manifest_folder(code)
    )

    assert not set(OLD_TOTAL_INPUTS) & set(manifest.inputs)
    assert {UCCB_INCOME, RDSP_INCOME, UCCB_REPAYMENT, RDSP_REPAYMENT} <= set(manifest.inputs)
