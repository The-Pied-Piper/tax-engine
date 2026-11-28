"""Form MB479 (2025 and 2026) line 7, the basic credit, over the optional year of birth.

Form text (CRA 5007-tc-25e.txt): "Line 7: Basic credit 195.00". The amount is the
`ca-mb/personal_tax_credit_basic` dataset, claimed through core/credit_amount.

The form prints no age condition. The Manitoba guide, CRA 5007-PC (Form MB479, Personal tax
credit): "If you were under 19 years of age at the end of the year, you can only claim this credit
if one of the following applies to you: You had a spouse or common-law partner / You were a parent
/ You can claim the Manitoba homeowners affordability tax credit on your 2025 return". The engine
models a filer with no spouse, child or property, so a filer under 19 at the end of the year has no
credit: line 7 is 0.00. The year of birth is the T1's optional `ca/birth_year`; a request that
leaves it out claims the credit in full. The cutoff year is 2006 for 2025 and 2007 for 2026 (age 19
on 31 December; 2026 is provisional).

The manifest part is loaded from the package, beside the T1's copied-lines form. The header and the
form's export are made up here, because the shared scaffold owns them. Manitoba is not yet listed in
the registrations, so the service is built here over the Manitoba package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.jurisdictions.ca_mb.catalog import MB479_BASIC_CREDIT_LINE_7
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_mb.__file__).parent
    / "manifests"
    / "2025"
    / "mb479_line_7.yaml"
)
PARTS = (*form_parts("t1_lines_copied_by_provinces"), PART_PATH)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb479
      required: true
      exports:
        - ca-mb/mb479_basic_credit_line_7
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(PARTS, start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def line_7(tmp_path: Path, year: int, birth_year: int | None) -> Decimal:
    given = () if birth_year is None else (Artifact(BIRTH_YEAR, birth_year),)
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-MB"), year, given)
    )
    (sheet,) = worksheets["ca-mb/mb479"]
    return sheet.get(MB479_BASIC_CREDIT_LINE_7).value


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("birth_year", [None, 1980, 1955, 1990])
def test_line_7_is_the_printed_claim_when_19_or_older_or_the_year_is_left_out(
    tmp_path: Path, year: int, birth_year: int | None
) -> None:
    assert line_7(tmp_path, year, birth_year) == D("195.00")


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("age", [0, 5, 16, 17, 18])
def test_line_7_is_zero_when_under_19_at_the_end_of_the_year(
    tmp_path: Path, year: int, age: int
) -> None:
    assert line_7(tmp_path, year, year - age) == D("0.00")


@pytest.mark.parametrize(
    ("year", "birth_year", "expected"),
    [
        (2025, 2006, "195.00"),
        (2025, 2007, "0.00"),
        (2026, 2007, "195.00"),
        (2026, 2008, "0.00"),
    ],
)
def test_the_cutoff_year_moves_with_the_tax_year(
    tmp_path: Path, year: int, birth_year: int, expected: str
) -> None:
    assert line_7(tmp_path, year, birth_year) == D(expected)


def test_the_part_reads_the_flag_claims_the_dataset_figure_and_multiplies_them() -> None:
    part = yaml.safe_load(PART_PATH.read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca-mb/mb479"}
    flag, claim, line = part["capabilities"]
    assert flag["name"] == "core/first_record_count"
    assert flag["consumes"] == {"records": "ca/t1_lines_copied_by_provinces.age_19_or_older"}
    assert flag["produces"] == {"output": "ca-mb/mb479_age_19_or_older"}
    assert claim["name"] == "core/credit_amount"
    assert claim["params"] == {"amount": "ca-mb/personal_tax_credit_basic"}
    assert claim["produces"] == {"output": "ca-mb/mb479_basic_credit_claim_line_7"}
    assert line["name"] == "core/times_count"
    assert line["title"] == "Basic credit"
    assert line["reference"] == "7"
    assert line["unit"] == "ca/cad"
    assert line["blank"] == {"count": "1"}
    assert line["produces"] == {"output": "ca-mb/mb479_basic_credit_line_7"}


def test_the_basic_credit_is_a_non_negative_amount_kind() -> None:
    kind = manitoba_kinds().kind("ca-mb/mb479_basic_credit_line_7")

    assert kind is MB479_BASIC_CREDIT_LINE_7
    assert non_negative(kind)
