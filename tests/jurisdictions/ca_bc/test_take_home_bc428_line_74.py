"""BC428 (2025) line 74, the net income, from the salary alone, real parts.

Form text (Form BC428, CRA 5010-c-25e.txt): "Line 74: Enter your net income from line 23600 of
your return." The form names no label for the line, so the step has no title. Line 23600 is read
as the T1 form exports it, floored, `ca/t1_taxable_income.net_income`, which reaches this form only
as a record list: line 74 is a core/record_total over it, as ON428-A line 6 is. The kind is
non-negative.

The test composes the T1 employment income form, the real federal parts the T1 taxable
income form needs (Schedule 8 for line 23300, and the T1 lines 15000, 23300, 23400, 23600, 23600
signed and 26000 with their inputs) and the real `bc428_line_74.yaml`, and types in only the salary.
The BC428 form declaration is made up here, exporting only line 74, because the real header is owned
by another change. The service is built over the British Columbia package list of `support.py`.
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
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC428_NET_INCOME_LINE_74
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
PART = BC_PARTS / "bc428_line_74.yaml"
IDENTIFIER = "ca-bc/bc428_net_income_line_74"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 74.
FEDERAL_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_net_income_line_74
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _line_74(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-BC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet.get(BC428_NET_INCOME_LINE_74).value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


# Taxable income is the salary less the CPP enhanced and second-ceiling amounts (T1 line 23600).
@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("17000", "16865.00"),
        ("200000", "198926.00"),
    ],
)
def test_line_74_is_the_t1_net_income(tmp_path: Path, salary: str, expected: str) -> None:
    assert _line_74(tmp_path, salary) == D(expected)


def test_the_part_is_one_untitled_record_total_step_over_the_t1_net_income() -> None:
    assert _step() == {
        "name": "core/record_total",
        "reference": "74",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.net_income"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert kind is BC428_NET_INCOME_LINE_74
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
