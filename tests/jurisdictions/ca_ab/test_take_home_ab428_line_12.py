"""AB428 (2025) line 12, the bracket column rate of lines 9 to 15, from the real part file through
the real engine.

Form text (Form AB428, CRA 5009-c-25e.txt, repo copy docs/cra-forms-2025/5009-c-25e.txt, read
2026-11-12): the three columns of lines 9 to 15 print "Line 12: Rate 13%", "Line 12: Rate 14%" and
"Line 12: Rate 15%". Column 1 is used if line 1 is "more than $181,481 but not more than
$241,974", column 2 if it is more than $241,974 but not more than $362,961, column 3 if it is
more than $362,961. Below that the lines 2 to 8 columns apply and lines 9 to 15 are left blank.

Line 1 is the taxable income, taken as given: declared as a required input of the test header and
given directly as an Artifact. Line 12 is one `core/bracket_column_rate` over line 1 with the
`ca-ab/brackets_lines_9_to_15` schedule, in the one part `ab428_line_12.yaml`. A line 1 outside the
schedule's range leaves the output blank. The form declaration is test-local: it exports line 12.

Figures: the taxable income at a $20,000 salary is 19,835.00, at $70,000 is 69,335.00 and at
$200,000 is 198,926.00 (hand-computed, not a CRA example), so line 12 is blank, blank and 13%.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK, Blank
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_BRACKET_RATE_LINE_12,
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
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
LINE_PART = ALBERTA_PARTS / "ab428_line_12.yaml"
LINE_1 = "ca-ab/ab428_taxable_income_line_1"
LINE_12 = "ca-ab/ab428_bracket_rate_line_12"
FORM_NAME = "ca-ab/ab428_credits"

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
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_12}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, a form declaration and the
    real line 12 part, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / f"02_{LINE_PART.name}").write_text(
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


def _line_12(tmp_path: Path, taxable_income: str) -> Decimal | Blank:
    kinds = alberta_kinds()
    given = Artifact(kinds.kind(LINE_1), D(taxable_income))
    (sheet,) = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, given)[FORM_NAME]
    value = sheet.get(kinds.kind(LINE_12)).value
    assert value is BLANK or isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # The worked figures: 19,835.00 and 69,335.00 are below the table, so line 12 is blank.
        ("19835.00", None),
        ("69335.00", None),
        # 198,926.00 is in column 1, rate 13%.
        ("198926.00", "0.13"),
    ],
)
def test_line_12_is_the_rate_of_the_column_line_1_falls_in_or_blank(
    tmp_path: Path, taxable_income: str, expected: str | None
) -> None:
    result = _line_12(tmp_path, taxable_income)

    if expected is None:
        assert result is BLANK
    else:
        assert result == D(expected)


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # 181,481.00 is not more than the first threshold: outside the table, blank.
        ("181481.00", None),
        ("181481.01", "0.13"),
        # A threshold falls in the lower column; a cent above it is in the next.
        ("241974.00", "0.13"),
        ("241974.01", "0.14"),
        ("362961.00", "0.14"),
        ("362961.01", "0.15"),
    ],
)
def test_line_12_at_and_one_cent_above_each_threshold(
    tmp_path: Path, taxable_income: str, expected: str | None
) -> None:
    result = _line_12(tmp_path, taxable_income)

    if expected is None:
        assert result is BLANK
    else:
        assert result == D(expected)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_bracket_column_rate_step_like_ontario_line_5() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_rate",
        "title": "Rate",
        "reference": "12",
        "params": {"schedule": "ca-ab/brackets_lines_9_to_15"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_12},
    }


@pytest.mark.parametrize(
    ("identifier", "kind"),
    [(LINE_12, AB428_BRACKET_RATE_LINE_12), (LINE_1, AB428_TAXABLE_INCOME_LINE_1)],
)
def test_the_kinds_are_registered_non_negative_decimal_amount_kinds(
    identifier: str, kind: AmountKind
) -> None:
    registered = alberta_kinds().kind(identifier)

    assert registered is kind
    assert isinstance(registered, AmountKind)
    assert registered.value_type is Decimal
    assert non_negative(registered)
