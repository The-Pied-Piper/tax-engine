"""NL428 (2025) line 63, tax on taxable income from line 8 or 15, real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 63: Newfoundland and Labrador tax on
taxable income from line 8 or 15 ^". Under line 8: "If you completed lines 2 to 8 for a column
above, enter the amount from line 8 on line 63 and continue at line 16." Under line 15: "If you
completed lines 9 to 15 for a column above, enter the amount from line 15 on line 63 and continue at
line 16."

Line 63 is one step, the capability `ca-nl/tax_on_taxable_income` (`nl428_line_63.yaml`), reading
the line 8 and line 15 exports of `ca-nl/nl428_credits` as record lists and giving the one that has
a figure; the other is blank. Its output is
`ca-nl/nl428_newfoundland_and_labrador_tax_on_taxable_income_line_63`, on the form `ca-nl/nl428`.

Figures (hand-computed, not a CRA example): salary 20,000 gives line 8 of 1,725.65
(line 1 at or below 220,910); 250,000 gives line 15 of 38,001.21.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.trace import TaxOnTaxableIncomeLine
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
CODE = JurisdictionCode("CA-NL")
CREDITS = "ca-nl/nl428_credits"
TAX = "ca-nl/nl428"
LINE_8 = "ca-nl/nl428_tax_on_taxable_income_line_8"
LINE_15 = "ca-nl/nl428_tax_on_taxable_income_line_15"
LINE_63 = "ca-nl/nl428_newfoundland_and_labrador_tax_on_taxable_income_line_63"
TITLE = "Newfoundland and Labrador tax on taxable income from line 8 or 15"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART = NL_PARTS / "nl428_line_63.yaml"
# The real parts, in composition order: lines 1 and 3 to 8, lines 10 to 15, line 63.
NL_LINE_PARTS = (
    *(
        NL_PARTS / f"nl428_credits_line_{number}.yaml"
        for number in (1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15)
    ),
    PART,
)
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The two form declarations, test-local: the credits form exports lines 8 and 15, the tax form
# line 63.
FORM_TEXT = dedent(f"""\
    form:
      name: {CREDITS}
      required: true
      exports:
        - {LINE_8}
        - {LINE_15}
    capabilities: []
    """)
TAX_FORM_TEXT = dedent(f"""\
    form:
      name: {TAX}
      required: true
      exports:
        - {LINE_63}
    capabilities: []
    """)


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    for found in form_parts("schedule_8"):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = next(FEDERAL_FORMS.rglob(name))
        yield (
            name,
            found.read_text("utf-8"),
        )
    for part in NL_LINE_PARTS:
        yield part.name, part.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    (folder / "02_tax_form.yaml").write_text(TAX_FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=3):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(CODE, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (sheet,) = worksheets[TAX]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = newfoundland_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(
    ("salary", "used", "expected"),
    [
        ("20000", LINE_8, "1725.65"),
        ("250000", LINE_15, "38001.21"),
    ],
)
def test_line_63_is_the_line_that_has_a_figure(
    tmp_path: Path, salary: str, used: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_63)).value == D(expected)
    (line,) = [t for t in sheet.trace if isinstance(t, TaxOnTaxableIncomeLine)]
    assert line.used == _kind(used)
    assert line.left_blank == _kind(LINE_15 if used == LINE_8 else LINE_8)


def test_the_part_is_one_step_that_reads_the_two_exports_across_the_form_boundary() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": TAX},
        "capabilities": [
            {
                "name": "ca-nl/tax_on_taxable_income",
                "title": TITLE,
                "reference": "63",
                "unit": "ca/cad",
                "consumes": {
                    "line_8": f"{CREDITS}.nl428_tax_on_taxable_income_line_8",
                    "line_15": f"{CREDITS}.nl428_tax_on_taxable_income_line_15",
                },
                "blank": {"line_8": {LINE_8: "compute"}, "line_15": {LINE_15: "compute"}},
                "produces": {"output": LINE_63},
            }
        ],
    }
