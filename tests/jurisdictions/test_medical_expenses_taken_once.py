"""The medical expenses are asked once, by T1 line 33099, and every provincial form that prints the
amount again imports it from the T1 form's export.

T1 line 33099 is the optional input `ca/medical_expenses` of the `ca/t1_medical_expenses` form,
read as 0 when blank and exported cent-rounded as `ca/medical_expenses_line_33099`. AB428 line 44,
BC428 line 46, MB428 line 43, SK428 line 43 and NL428 line 48 ("Amount from line 33099 of your
return") are each a record total of that export and none has an input of its own. A caller who
gives the amount once reaches every one of those lines; a caller who gives none reads each as 0.00.

The real registered engine is run end to end over each province's real 2025 manifest, as the
provincial end-to-end tests do, with a $70,000 salary (net income 69,335.00, so the 3% line is
2,080.05, under every province's dollar cap). The figures are hand-computed from the amounts given.
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
from tests.medical_support import (
    MEDICAL_EXPENSES,
    medical_expenses,
    other_dependants_medical_expenses,
)

D = Decimal
T1_FORM = "ca/t1_medical_expenses"
T1_EXPORT = "ca/medical_expenses_line_33099"
# Province code, its package, the form that prints the line, the line itself (what the typed input
# was called, now the record total), then the line that is the amount over the 3% limit.
PROVINCES = {
    "CA-AB": (
        tax_engine.jurisdictions.ca_ab,
        "ca-ab/ab428_credits",
        "ca-ab/ab428_medical_expenses_line_44",
        "ca-ab/ab428_medical_expenses_over_limit_line_49",
    ),
    "CA-BC": (
        tax_engine.jurisdictions.ca_bc,
        "ca-bc/bc428",
        "ca-bc/bc428_medical_expenses_line_46",
        "ca-bc/bc428_medical_expenses_over_limit_line_51",
    ),
    "CA-MB": (
        tax_engine.jurisdictions.ca_mb,
        "ca-mb/mb428_credits",
        "ca-mb/mb428_medical_expenses_line_43",
        "ca-mb/mb428_medical_expenses_over_limit_line_48",
    ),
    "CA-SK": (
        tax_engine.jurisdictions.ca_sk,
        "ca-sk/sk428_credits",
        "ca-sk/sk428_medical_expenses_line_43",
        "ca-sk/sk428_medical_expenses_over_limit_line_48",
    ),
    "CA-NL": (
        tax_engine.jurisdictions.ca_nl,
        "ca-nl/nl428_credits",
        "ca-nl/nl428_medical_expenses_line_48",
        "ca-nl/nl428_medical_expenses_over_limit_line_53",
    ),
}
OLD_TYPED_INPUTS = (
    "ca-ab/ab428_medical_expenses_line_44",
    "ca-bc/bc428_medical_expenses_line_46",
    "ca-mb/mb428_medical_expenses_line_43",
    "ca-sk/sk428_medical_expenses_line_43",
    "ca-nl/nl428_medical_expenses_line_48",
)
# 3% of 69,335.00 is 2,080.05 (Manitoba's own cap is 1,728.00), so an amount of 5,000.00 is
# over the limit by 5,000.00 less that.
OVER_LIMIT = {"CA-MB": D("3272.00")}
OVER_LIMIT_DEFAULT = D("2919.95")


def _compute(code: str, amount: str | None) -> dict[str, tuple[Worksheet, ...]]:
    starting = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if amount is not None:
        starting.append(medical_expenses(amount))
    return build_tax_computation().compute(JurisdictionCode(code), 2025, *starting)


def _figure(worksheets: dict[str, tuple[Worksheet, ...]], form: str, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    (sheet,) = worksheets[form]
    return sheet.get(kind).value


@pytest.mark.parametrize("code", PROVINCES)
def test_the_amount_given_once_is_exported_by_t1_and_reaches_the_provincial_line(
    code: str,
) -> None:
    _, form, line, _ = PROVINCES[code]

    worksheets = _compute(code, "1000.005")

    # The T1 export is cent-rounded (half up), and the provincial line is that figure.
    assert _figure(worksheets, T1_FORM, T1_EXPORT) == D("1000.01")
    assert _figure(worksheets, form, line) == D("1000.01")


@pytest.mark.parametrize("code", PROVINCES)
def test_a_caller_who_gives_none_reads_the_export_and_the_line_as_zero(code: str) -> None:
    _, form, line, over_limit = PROVINCES[code]

    worksheets = _compute(code, None)

    assert _figure(worksheets, T1_FORM, T1_EXPORT) == D("0.00")
    assert _figure(worksheets, form, line) == D("0.00")
    assert _figure(worksheets, form, over_limit) == D("0.00")


@pytest.mark.parametrize("code", PROVINCES)
def test_the_line_after_it_is_unchanged_for_the_same_amount(code: str) -> None:
    _, form, _, over_limit = PROVINCES[code]

    worksheets = _compute(code, "5000")

    assert _figure(worksheets, form, over_limit) == OVER_LIMIT.get(code, OVER_LIMIT_DEFAULT)


@pytest.mark.parametrize("code", PROVINCES)
def test_the_manifest_asks_for_the_amount_once_and_no_form_types_a_provincial_one(
    code: str,
) -> None:
    package = PROVINCES[code][0]
    manifest = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(
        Path(package.__path__[0]) / "manifests" / "2025"
    )

    declared = set(inputs_of(manifest))
    assert MEDICAL_EXPENSES in declared
    assert not set(OLD_TYPED_INPUTS) & declared


def test_sk428_line_49_reads_the_t1_line_33199_export_and_has_no_input_of_its_own() -> None:
    line_49 = "ca-sk/sk428_other_dependants_medical_expenses_line_49"
    starting = [
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        other_dependants_medical_expenses("250.555"),
    ]
    given = build_tax_computation().compute(JurisdictionCode("CA-SK"), 2025, *starting)
    none = _compute("CA-SK", None)

    assert _figure(given, T1_FORM, "ca/other_dependants_medical_expenses_line_33199") == D("250.56")
    assert _figure(given, "ca-sk/sk428_credits", line_49) == D("250.56")
    assert _figure(none, T1_FORM, "ca/other_dependants_medical_expenses_line_33199") == D("0.00")
    assert _figure(none, "ca-sk/sk428_credits", line_49) == D("0.00")
    # Line 50 adds line 49 to line 48, so with no line 33099 it is the 250.56 given.
    assert _figure(given, "ca-sk/sk428_credits", "ca-sk/sk428_medical_expenses_line_50") == D(
        "250.56"
    )
    manifest = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(
        Path(tax_engine.jurisdictions.ca_sk.__path__[0]) / "manifests" / "2025"
    )
    declared = set(inputs_of(manifest))
    assert "ca/other_dependants_medical_expenses" in declared
    assert line_49 not in declared
