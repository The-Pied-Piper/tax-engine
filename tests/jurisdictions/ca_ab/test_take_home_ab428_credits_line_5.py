"""AB428 (2025) line 5, the bracket column rate, computed from the real part file through the real
engine.

Form text (Form AB428, CRA 5009-c-25e.txt, cra-docs copy
cra-docs/docs/cra-forms-2025/5009-c-25e.txt): each of
the three columns of lines 2 to 8 prints its rate on "Line 5": "Line 5: Rate 8%", "Line 5: Rate 10%"
and "Line 5: Rate 12%". Line 5 is the printed rate of the column that taxable income falls in, and a
taxable income exactly at a column's upper bound falls in that lower column. A taxable income above
the table's range (181,481) is left blank on this line.

Line 1 is the taxable income (line 26000), taken as given: it is declared as a required input of
the test header and given directly as an Artifact, so this test does not compose the T1 lines.
Line 5 is one `core/bracket_column_rate` over line 1 with the `ca-ab/brackets_lines_2_to_8`
schedule, output `ca-ab/ab428_bracket_rate_line_5`, in the one part `ab428_credits_line_5.yaml`. The
output is a rate held in a Decimal artifact, not rounded. The form declaration is test-local: it
exports line 5.

Figures: the taxable income at a $20,000 salary is 19,835.00, at $70,000 is 69,335.00 and at
$200,000 is 198,926.00 (hand-computed, not a CRA example), so line 5 is 8%, 10% and blank.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_BRACKET_RATE_LINE_5,
    AB428_TAXABLE_INCOME_LINE_1,
)
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative

D = Decimal
LINE_PART = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent
    / "manifests"
    / "2025"
    / "ab428_credits_line_5.yaml"
)
LINE_1 = "ca-ab/ab428_taxable_income_line_1"
LINE_5 = "ca-ab/ab428_bracket_rate_line_5"

HEADER = dedent(f"""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: {LINE_1}
        required: true
    outputs:
      - {LINE_1}
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - {LINE_5}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_ab428_credits_line_5.yaml").write_text(
        LINE_PART.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _line_5(tmp_path: Path, taxable_income: str) -> Artifact[Decimal]:
    given = Artifact(AB428_TAXABLE_INCOME_LINE_1, D(taxable_income))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, given)
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    return sheet.get(AB428_BRACKET_RATE_LINE_5)


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # The worked figure for a $20,000 salary: 19,835.00 is in column 1, rate 8%.
        ("19835.00", "0.08"),
        # The worked figure for a $70,000 salary: 69,335.00 is in column 2, rate 10%.
        ("69335.00", "0.10"),
    ],
)
def test_line_5_is_the_rate_of_the_column_line_1_falls_in(
    tmp_path: Path, taxable_income: str, expected: str
) -> None:
    assert _line_5(tmp_path, taxable_income).value == D(expected)


def test_line_5_is_blank_when_line_1_is_above_the_table_at_a_200000_salary(
    tmp_path: Path,
) -> None:
    # The worked figure for a $200,000 salary: 198,926.00 is above 181,481, so the line is blank.
    assert _line_5(tmp_path, "198926.00").is_blank


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # 0 is the lower bound of column 1, so it takes column 1's rate.
        ("0.00", "0.08"),
        # Each threshold falls in the lower column, so it takes that column's rate.
        ("60000.00", "0.08"),
        ("151234.00", "0.10"),
        ("181481.00", "0.12"),
        # One cent above a threshold is in the next column.
        ("60000.01", "0.10"),
        ("151234.01", "0.12"),
    ],
)
def test_line_5_at_and_just_above_a_threshold(
    tmp_path: Path, taxable_income: str, expected: str
) -> None:
    assert _line_5(tmp_path, taxable_income).value == D(expected)


def test_line_5_one_cent_above_the_table_is_blank(tmp_path: Path) -> None:
    assert _line_5(tmp_path, "181481.01").is_blank


def test_the_part_names_the_form_and_has_one_bracket_column_rate_step() -> None:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428_credits"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "params", "consumes", "produces"]
    assert step["name"] == "core/bracket_column_rate"
    assert step["title"] == "Rate"
    assert step["reference"] == "5"
    assert step["params"] == {"schedule": "ca-ab/brackets_lines_2_to_8"}
    assert step["consumes"] == {"base": LINE_1}
    assert step["produces"] == {"output": LINE_5}


def test_line_5_is_a_registered_non_negative_amount_kind() -> None:
    kinds = alberta_kinds()

    assert LINE_5 in kinds.identifiers()
    kind = kinds.kind(LINE_5)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is AB428_BRACKET_RATE_LINE_5
