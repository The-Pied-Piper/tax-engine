"""T1 lines 12000 and 12010 are asked once, by the T1, and read by the five dividend worksheets.

T1 lines 12000 and 12010 are inputs of `ca/t1_taxable_income` (line 12000 is also an addend of total
income, line 15000); the split form `ca/t1_lines_copied_by_provinces` does not own them.

T1 General 2025 (5006-R) prints line 12000 ("Line 9 and line 12000: Amount of dividends (eligible
and other than eligible)") and line 12010 ("Line 12010: Amount of dividends (other than
eligible)").
The provincial worksheets (AB428 line 63, BC428 line 65, MB428 line 62, ON428 line 57 and SK428
line 64, each "Amount from line 12000 of your return" and "Amount from line 12010 of your return")
read them, so each province's dividend tax credit is computed from the T1 export and none of them
has an input of its own. No NL worksheet is in the forms folder, so NL428 line 67 stays typed.

The real registered engine is run end to end over each province's real 2025 manifest with line
12000 of $1,000.00 and line 12010 of $400.00, so the worksheet's line 1 is 400.00 at the printed
rate and line 2 is 600.00 at the other. The results are hand-computed from the printed rates.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_on
import tax_engine.jurisdictions.ca_sk
from tax_engine import build_tax_computation
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import CapabilityContractError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.manifest_support import inputs_of

D = Decimal
DIVIDENDS = "ca/taxable_dividends"
OTHER_THAN_ELIGIBLE = "ca/taxable_dividends_other_than_eligible"
T1_INPUTS = {DIVIDENDS, OTHER_THAN_ELIGIBLE}
# Province code, then its form, its dividend tax credit, and that credit for line 12000 of 1,000.00
# and line 12010 of 400.00 (line 1 plus line 2 of the worksheet).
CREDIT = {
    "CA-AB": ("ca-ab/ab428", "ca-ab/ab428_dividend_tax_credit_line_63", D("57.44")),
    "CA-BC": ("ca-bc/bc428", "ca-bc/bc428_dividend_tax_credit_line_65", D("79.84")),
    "CA-MB": ("ca-mb/mb428", "ca-mb/mb428_dividend_tax_credit_line_62", D("51.13")),
    "CA-ON": ("ca-on/on428", "ca-on/on428_dividend_tax_credit_line_57", D("71.95")),
    "CA-SK": ("ca-sk/sk428", "ca-sk/sk428_dividend_tax_credit_line_64", D("76.08")),
}
OLD_INPUTS = tuple(name for _, name, _ in CREDIT.values())


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


@pytest.mark.parametrize("code", CREDIT)
def test_lines_12000_and_12010_given_once_reach_the_province_with_its_printed_rates(
    code: str,
) -> None:
    form, name, expected = CREDIT[code]

    worksheets = _compute(code, {DIVIDENDS: "1000.00", OTHER_THAN_ELIGIBLE: "400.00"})

    assert _figure(worksheets, form, name) == expected


@pytest.mark.parametrize("code", CREDIT)
def test_a_caller_who_gives_none_has_a_dividend_tax_credit_of_zero(code: str) -> None:
    form, name, _ = CREDIT[code]

    assert _figure(_compute(code, {}), form, name) == D("0.00")


@pytest.mark.parametrize(
    ("code", "package"),
    [
        ("CA-AB", tax_engine.jurisdictions.ca_ab),
        ("CA-BC", tax_engine.jurisdictions.ca_bc),
        ("CA-MB", tax_engine.jurisdictions.ca_mb),
        ("CA-ON", tax_engine.jurisdictions.ca_on),
        ("CA-SK", tax_engine.jurisdictions.ca_sk),
    ],
)
def test_no_provincial_form_declares_its_dividend_tax_credit_as_an_input(
    code: str, package: object
) -> None:
    folder = Path(package.__path__[0]) / "manifests" / "2025"  # type: ignore[attr-defined]
    manifest = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)

    assert not set(OLD_INPUTS) & set(inputs_of(manifest))
    assert T1_INPUTS <= set(inputs_of(manifest))


def test_line_12000_is_an_addend_of_total_income() -> None:
    plain = _compute("CA-AB", {})["ca/t1_taxable_income"]
    given = _compute("CA-AB", {DIVIDENDS: "10000.00", OTHER_THAN_ELIGIBLE: "2000.00"})
    total = artifact_kinds().kind("ca/total_income")
    assert isinstance(total, AmountKind)

    (before,) = plain
    (after,) = given["ca/t1_taxable_income"]
    assert after.get(total).value - before.get(total).value == D("10000.00")


def test_line_12010_above_line_12000_is_refused() -> None:
    with pytest.raises(CapabilityContractError):
        _compute("CA-AB", {DIVIDENDS: "400.00", OTHER_THAN_ELIGIBLE: "1000.00"})
