"""NL428 (2025) line 55, line 53 plus line 54, from the salary, real parts.

Form text (Form NL428, CRA 5001-C, confirmed 2026-11-18): "Line 55 and line 58769: Line 53 plus
line 54 =". Line 55 is one core/sum step over line 53 (`nl428_credits_line_53.yaml`) and line 54,
the optional allowable amount of medical expenses for other dependants
(`nl428_credits_line_54_input.yaml`), in line order. A request that leaves line 54 blank is read as
0 and the step prints its own "left blank, taken as" row. The form prints no label for the line, so
the step has no title.

The test composes the real Schedule 8 parts, the real T1 taxable income parts and the real lines 48,
49, 51, 52, 53, 54 and 55 parts, and types in the salary and, where a case gives them, lines 48 and
54. The header, the salary input and the form declaration are made up here, the form exporting
line 55.

The hand figures are asserted (not a CRA example): net income is the salary less the enhanced CPP
deduction, line 52 is the lesser of 3% of it and 2,410.00, line 53 is line 48 less line 52, not
below 0, and line 55 is line 53 plus line 54.
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
import tax_engine.jurisdictions.ca_nl.catalog as nl_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_49_PART = NL_PARTS / "nl428_credits_line_49.yaml"
LINE_51_PART = NL_PARTS / "nl428_credits_line_51.yaml"
LINE_52_PART = NL_PARTS / "nl428_credits_line_52.yaml"
LINE_48_PART = NL_PARTS / "nl428_credits_line_48_input.yaml"
LINE_53_PART = NL_PARTS / "nl428_credits_line_53.yaml"
LINE_54_PART = NL_PARTS / "nl428_credits_line_54_input.yaml"
LINE_PART = NL_PARTS / "nl428_credits_line_55.yaml"
FORM_NAME = "ca-nl/nl428_credits"
LINE_53 = "ca-nl/nl428_medical_expenses_over_limit_line_53"
LINE_54 = "ca-nl/nl428_allowable_medical_expenses_for_other_dependants_line_54"
KIND = "ca-nl/nl428_medical_expenses_allowable_line_55"
# The real federal parts the T1 taxable-income form needs, beside the salary and lines 49 to 52.
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_medical_expenses_allowable_line_55
    capabilities: []
    """)

# salary, line 48, line 54, line 53, line 55. Net income is 19,835.00 / 69,335.00 / 198,926.00;
# line 52 is the lesser of 3% of it and 2,410.00, which is 595.05 / 2,080.05 / 2,410.00.
CASES = [
    ("20000", None, None, "0.00", "0.00"),
    ("20000", "3000", "150.25", "2404.95", "2555.20"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_49_PART
    yield LINE_51_PART
    yield LINE_52_PART
    yield LINE_48_PART
    yield LINE_53_PART
    yield LINE_54_PART
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(
    tmp_path: Path, salary: str, line_48: str | None = None, line_54: str | None = None
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_48 is not None:
        given.append(Artifact(nl_catalog.NL428_MEDICAL_EXPENSES_LINE_48, D(line_48)))
    if line_54 is not None:
        given.append(
            Artifact(
                nl_catalog.NL428_ALLOWABLE_MEDICAL_EXPENSES_FOR_OTHER_DEPENDANTS_LINE_54,
                D(line_54),
            )
        )
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "line_48", "line_54", "line_53", "expected"), CASES)
def test_line_55_is_line_53_plus_line_54(
    tmp_path: Path,
    salary: str,
    line_48: str | None,
    line_54: str | None,
    line_53: str,
    expected: str,
) -> None:
    sheet = _sheet(tmp_path, salary, line_48, line_54)

    assert _value(sheet, LINE_53) == D(line_53)
    assert _value(sheet, KIND) == D(expected)


def test_a_blank_line_54_is_read_as_zero_and_prints_its_own_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "3000")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert any("left blank, taken as" in row.lower() for row in rows)
    assert _value(sheet, KIND) == D("919.95")


def test_a_given_line_54_prints_no_left_blank_row_for_it(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "3000", "150.25")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert any("919.95" in row and "150.25" in row and "1070.20" in row for row in rows)
    assert not any("left blank, taken as" in row.lower() for row in rows if "150.25" in row)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_sum_step_over_lines_53_and_54() -> None:
    assert _step() == {
        "name": "core/sum",
        "reference": "55",
        "unit": "ca/cad",
        "params": {"rounding": "ca-nl/cent_rounding"},
        "consumes": {"parts": [LINE_53, LINE_54]},
        "blank": {LINE_54: "0"},
        "produces": {"output": KIND},
    }


def test_line_55_is_a_registered_non_negative_amount_kind() -> None:
    kinds = newfoundland_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is nl_catalog.NL428_MEDICAL_EXPENSES_ALLOWABLE_LINE_55
