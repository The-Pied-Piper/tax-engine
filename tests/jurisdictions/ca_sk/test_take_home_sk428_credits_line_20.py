"""SK428 (2025) line 20, the credits subtotal, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 20: Add lines 9, 10, 13, and 16 to 19. =". Lines
10, 13 and 16 to 19 are blank for a salary-only single filer, so only line 9, the basic personal
amount (19,491.00), contributes, at every salary. The form prints no label for line 20, so the step
has no title.

The test composes the real Saskatchewan salary part, the real line 9 part
(`sk428_credits_line_9.yaml`) and the real line part (`sk428_credits_line_20.yaml`), and types in
only the salary. The header and the form's exports are made up here, because the shared scaffold
owns them. The expected amount is re-derived from the printed `ca-sk/basic_personal_amount` dataset
(19,491), rounded to the cent through `ca-sk/cent_rounding`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.credit import CREDIT
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_sk.catalog import SK428_CREDITS_SUBTOTAL_LINE_20
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_PART = SK_PARTS / "sk428_credits_line_20.yaml"
KIND = "ca-sk/sk428_credits_subtotal_line_20"

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/basic_personal_amount
        - ca-sk/sk428_credits_subtotal_line_20
    capabilities: []
    """)
PART_NAMES = ["salary.yaml", "sk428_credits_line_9.yaml", "sk428_credits_line_20.yaml"]


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, name in enumerate(PART_NAMES, start=2):
        (folder / f"{number:02d}_{name}").write_text(
            (SK_PARTS / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def line_20(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-SK"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-sk/sk428_credits"]
    return sheet.get(SK428_CREDITS_SUBTOTAL_LINE_20).value


def _basic_personal_amount() -> Decimal:
    source = YamlParameterSource(
        saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
    )
    amount = source.get("ca-sk/basic_personal_amount", 2025, CREDIT).values.amount
    assert isinstance(amount, Decimal)
    return amount


def test_the_dataset_amount_is_the_printed_19491() -> None:
    assert _basic_personal_amount() == D("19491")


@pytest.mark.parametrize("salary", ["0", "20000", "70000", "200000"])
def test_line_20_is_line_9_alone_at_every_salary(tmp_path: Path, salary: str) -> None:
    result = line_20(tmp_path, salary)

    assert result == _basic_personal_amount().quantize(D("0.01"))
    assert result == D("19491.00")


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-sk/sk428_credits"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_sum_step_over_the_basic_personal_amount() -> None:
    assert _step() == {
        "name": "core/sum",
        "reference": "20",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {"parts": ["ca-sk/basic_personal_amount"]},
        "produces": {"output": KIND},
    }


def test_the_step_keys_are_in_order_and_there_is_no_title() -> None:
    assert list(_step()) == ["name", "reference", "unit", "params", "consumes", "produces"]


def test_line_20_is_a_registered_non_negative_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is SK428_CREDITS_SUBTOTAL_LINE_20
