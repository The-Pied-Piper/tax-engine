"""Schedule 9 line 12 is asked once, by Schedule 9, and each province reads lines 13 and 14 from it.

Schedule 9 (5000-S9, 2025): "Line 12: Line 10 plus line 11 =", "Line 13: Enter whichever is less:
amount from line 12 or $200." and "Line 14: Line 12 minus line 13 =". Each provincial form prints
"Amount from line 13 of your federal Schedule 9" and "Amount from line 14 of your federal Schedule
9": AB428 lines 55 and 56, MB428 lines 54 and 55, NL428 lines 59 and 60, ON428 lines 47 and 48 and
SK428 lines 54 and 55. Each of those is a total of the Schedule 9 export and none has an input of
its own, so one line 12 amount reaches every province: the first $200 as line 13 and the rest as
line 14.

The real registered engine is run end to end over each province's real 2025 manifest, as the
provincial end-to-end tests do. The figures are hand-computed from the printed $200: a line 12 of
150 is 150 on line 13 and 0 on line 14, and one of 1,000 is 200 and 800.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_on
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
LINE_12 = "ca/donations_and_gifts_line_12"
# Province code, the form that prints the two copies, and the figure of each (line 13 then 14).
COPIES = {
    "CA-AB": (
        "ca-ab/ab428_credits",
        "ca-ab/ab428_donations_amount_line_55",
        "ca-ab/ab428_donations_amount_line_56",
    ),
    "CA-MB": (
        "ca-mb/mb428_credits",
        "ca-mb/mb428_donations_amount_line_54",
        "ca-mb/mb428_donations_amount_line_55",
    ),
    "CA-NL": (
        "ca-nl/nl428_credits",
        "ca-nl/nl428_donations_amount_line_59",
        "ca-nl/nl428_donations_amount_line_60",
    ),
    "CA-ON": (
        "ca-on/on428",
        "ca-on/on428_donations_amount_line_47",
        "ca-on/on428_donations_amount_line_48",
    ),
    "CA-SK": (
        "ca-sk/sk428_credits",
        "ca-sk/sk428_donations_amount_line_54",
        "ca-sk/sk428_donations_amount_line_55",
    ),
}
PACKAGES = {
    "CA-AB": tax_engine.jurisdictions.ca_ab,
    "CA-MB": tax_engine.jurisdictions.ca_mb,
    "CA-NL": tax_engine.jurisdictions.ca_nl,
    "CA-ON": tax_engine.jurisdictions.ca_on,
    "CA-SK": tax_engine.jurisdictions.ca_sk,
}


def _compute(code: str, line_12: str | None) -> dict[str, tuple[Worksheet, ...]]:
    starting = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if line_12 is not None:
        starting.append(Artifact(artifact_kinds().kind(LINE_12), D(line_12)))
    return build_tax_computation().compute(JurisdictionCode(code), 2025, *starting)


def _figure(worksheets: dict[str, tuple[Worksheet, ...]], form: str, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    (sheet,) = worksheets[form]
    return sheet.get(kind).value


@pytest.mark.parametrize("code", COPIES)
@pytest.mark.parametrize(
    ("line_12", "line_13", "line_14"), [("150", "150.00", "0.00"), ("1000", "200.00", "800.00")]
)
def test_one_line_12_gives_each_province_the_first_200_then_the_rest(
    code: str, line_12: str, line_13: str, line_14: str
) -> None:
    form, first, second = COPIES[code]

    worksheets = _compute(code, line_12)

    assert _figure(worksheets, form, first) == D(line_13)
    assert _figure(worksheets, form, second) == D(line_14)


def test_schedule_9_exports_lines_13_and_14_of_the_same_line_12() -> None:
    worksheets = _compute("CA-ON", "1000")

    assert _figure(worksheets, "ca/schedule_9", "ca/donations_and_gifts_line_13") == D("200.00")
    assert _figure(worksheets, "ca/schedule_9", "ca/donations_and_gifts_line_14") == D("800.00")


@pytest.mark.parametrize("code", COPIES)
def test_a_caller_who_gives_no_line_12_reads_both_lines_as_zero(code: str) -> None:
    form, first, second = COPIES[code]

    worksheets = _compute(code, None)

    assert _figure(worksheets, form, first) == D("0.00")
    assert _figure(worksheets, form, second) == D("0.00")


@pytest.mark.parametrize("code", COPIES)
def test_no_province_declares_the_copies_as_inputs_and_line_12_is_the_one_input(code: str) -> None:
    _, first, second = COPIES[code]
    folder = Path(PACKAGES[code].__path__[0]) / "manifests" / "2025"
    manifest = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)

    assert not {first, second} & set(inputs_of(manifest))
    assert LINE_12 in inputs_of(manifest)
