"""Schedule MB428-A (2025) line 11, net income multiplied by 9%, from the salary alone.

Form text (Schedule MB428-A, CRA 5007-A): "Line 11: Net income from line 23600 of your return
multiplied by 9% = ". The 9% is a printed rate, so it is the `ca-mb/family_tax_benefit_rate` dataset
figure and has no step of its own; the line is one core/apply_rate step over the net income of the
first box, rounded half-up to the cent by the dataset's own rule, as Alberta line 54 is over
line 52. The form names no label for the line, so the step has no title.

The test composes the T1 employment income form, the real federal parts the T1 taxable income form
needs (the same as the net income box's test), the real `mb428_a_line_11.yaml` and the new
`mb428_a_line_11_product.yaml`, and types in only the salary. The Schedule MB428-A form declaration
is made up here, exporting only the product. The service is built over the Manitoba package list of
`support.py`.

The figures are hand-computed from the printed form (not a CRA example): net income is 9,935.00
and 198,926.00 at the two salaries, times 0.09, half-up to the cent.
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
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
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
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
NET_INCOME_PART = MB_PARTS / "mb428_a_line_11.yaml"
PART = MB_PARTS / "mb428_a_line_11_product.yaml"
IDENTIFIER = "ca-mb/mb428_a_line_11"
FORM_NAME = "ca-mb/mb428_a"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 11.
FEDERAL_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb428_a
      required: true
      exports:
        - ca-mb/mb428_a_line_11
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield NET_INCOME_PART
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(dict.fromkeys(_part_files()), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-MB"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line_11(tmp_path: Path, salary: str) -> Decimal:
    return D(_sheet(tmp_path, salary).get(manitoba_kinds().kind(IDENTIFIER)).value)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


# salary, line 11: net income (9,935.00 and 198,926.00, as the net income box's test pins) times
# 0.09, half-up to the cent: 894.15 (894.1500) and 17,903.34 (17,903.3400).
CASES = [
    ("10000", "894.15"),
    ("200000", "17903.34"),
]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_11_is_net_income_times_9_percent(tmp_path: Path, salary: str, expected: str) -> None:
    assert _line_11(tmp_path, salary) == D(expected)


def test_the_part_is_one_untitled_apply_rate_step_over_the_net_income_box() -> None:
    assert _step() == {
        "name": "core/apply_rate",
        "reference": "11",
        "unit": "ca/cad",
        "params": {"rate": "ca-mb/family_tax_benefit_rate"},
        "consumes": {"base": "ca-mb/mb428_a_net_income_line_11"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB428_A_LINE_11
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
