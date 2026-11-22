"""T691 Part 7 lines 1, 2 and 13 are asked once, by the T691, and imported from its exports.

AB428 line 67, MB428 line 66 and SK428 line 68 print "Form T691: line 1 minus line 2 of Part 7"
multiplied by the province's rate; BC428 line 69 and NL428 line 71 print "Amount from line 14 of
Part 7 of Form T691" multiplied by the rate, and line 14 is line 1 minus line 13 (not below 0).
Each of those is a total of a T691 export and none has an input of its own. A caller who gives
lines 1, 2 and 13 once reaches all five forms; a caller who gives none reads each as 0.00.

The real registered engine is run end to end over each province's real 2025 manifest, as the T1
line 40427 test does. With line 1 of $5,000.00, line 2 of $1,200.00 and line 13 of $1,500.00, the
results are hand-computed from the printed rates: 35% (AB), 50% (MB and SK) of 3,800.00, and 34.9%
(BC) and 60% (NL) of 3,500.00.
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
LINE_1 = "ca/t691_minimum_amount"
LINE_2 = "ca/t691_basic_federal_tax"
LINE_13 = "ca/t691_line_8_plus_line_12"
GIVEN = {LINE_1: "5000.00", LINE_2: "1200.00", LINE_13: "1500.00"}
# Province code, then its form, its line's figure, the printed rate, and the base: line 1 minus
# line 2 (3,800.00) for AB, MB and SK, line 14 (3,500.00) for BC and NL.
FIGURES = {
    "CA-AB": ("ca-ab/ab428", "ca-ab/ab428_additional_minimum_tax_line_67", D("0.35"), D("3800.00")),
    "CA-BC": (
        "ca-bc/bc428",
        "ca-bc/bc428_additional_minimum_tax_line_69",
        D("0.349"),
        D("3500.00"),
    ),
    "CA-MB": (
        "ca-mb/mb428",
        "ca-mb/mb428_additional_tax_minimum_tax_line_66",
        D("0.5"),
        D("3800.00"),
    ),
    "CA-NL": (
        "ca-nl/nl428",
        "ca-nl/nl428_additional_tax_minimum_tax_line_71",
        D("0.6"),
        D("3500.00"),
    ),
    "CA-SK": ("ca-sk/sk428", "ca-sk/sk428_minimum_tax_additional_line_68", D("0.5"), D("3800.00")),
}
OLD_INPUTS = (
    "ca-ab/ab428_minimum_tax_t691_amount_line_67",
    "ca-bc/bc428_additional_minimum_tax_amount_line_69",
    "ca-mb/mb428_t691_amount_line_66",
    "ca-nl/nl428_t691_amount_line_71",
    "ca-sk/sk428_minimum_tax_t691_amount_line_68",
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


@pytest.mark.parametrize("code", FIGURES)
def test_t691_given_once_reaches_the_province_with_its_printed_rate(code: str) -> None:
    form, name, rate, base = FIGURES[code]

    worksheets = _compute(code, GIVEN)

    assert _figure(worksheets, form, name) == D(base) * rate


@pytest.mark.parametrize("code", FIGURES)
def test_a_caller_who_gives_none_reads_the_t691_amount_as_zero(code: str) -> None:
    form, name, *_ = FIGURES[code]

    assert _figure(_compute(code, {}), form, name) == D("0.00")


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
def test_no_provincial_form_declares_a_t691_amount_as_an_input(code: str, package: object) -> None:
    folder = Path(package.__path__[0]) / "manifests" / "2025"  # type: ignore[attr-defined]
    manifest = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)

    assert not set(OLD_INPUTS) & set(inputs_of(manifest))
    assert {LINE_1, LINE_2, LINE_13} <= set(inputs_of(manifest))
