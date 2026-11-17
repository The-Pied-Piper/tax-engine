"""MB428 (2025) line 19, CPP or QPP contributions, from the salary alone, real parts.

Form text (Form MB428, CRA 5007-C, read 2026-11-14): "Line 19 and line 58240: Amount from line 30800
of your return". The line is a copy, so its one step is a core/record_total over the Schedule 8
export that gives T1 line 30800 (Schedule 8 line 25, the CPP base contributions on the return), as
Alberta's line 27 is (`ab428_line_27.yaml`).

The test composes the real Manitoba salary part, the real Schedule 8 parts and the real line part
(`mb428_credits_line_19.yaml`), and types in only the salary. The form declaration is made up here,
exporting the line read, because the real form part exports only the lines already built. The
figures are hand-computed from the printed forms (not a CRA example): 4.95% of the salary above the
$3,500 basic exemption, to the maximum of $3,356.10, rounded half-up to the cent.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_mb.catalog import MB428_CPP_CONTRIBUTIONS_LINE_19
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = MB_PARTS / "mb428_credits_line_19.yaml"
KIND = "ca-mb/mb428_cpp_contributions_line_19"

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_cpp_contributions_line_19
    capabilities: []
    """)

CASES = [
    ("10000", "321.75"),
    ("20000", "816.75"),
    ("70000", "3291.75"),
    ("200000", "3356.10"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(),
            manitoba_parameter_parsers(),
            manitoba_units(),
        ),
        manitoba_capabilities(),
    )


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_19_is_the_schedule_8_cpp_base_contributions(
    tmp_path: Path, salary: str, expected: str
) -> None:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )

    (sheet,) = worksheets["ca-mb/mb428_credits"]
    assert sheet.get(MB428_CPP_CONTRIBUTIONS_LINE_19).value == D(expected)


def _line() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_record_total_step_like_alberta_line_27() -> None:
    part = _line()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-mb/mb428_credits"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["title"] == "CPP or QPP contributions"
    assert step["reference"] == "19"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {
        "records": "ca/schedule_8.schedule_8_cpp_base_contributions_on_return"
    }
    assert step["produces"] == {"output": KIND}


def test_line_19_is_a_registered_non_negative_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is MB428_CPP_CONTRIBUTIONS_LINE_19
