"""AB428 (2025) line 67, the Alberta additional tax for minimum tax purposes, computed from the real
part files through the real engine.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 67: Form T691: line 1 minus line 2 of Part 7 ^ /
multiplied by 35% = ^". The input is the T691 amount
(`ca-ab/ab428_minimum_tax_t691_amount_line_67`), which the inputs part declares as optional, read
as 0 when left out. Line 67 is one calculation: 35% of that amount, a printed rate held in
the `ca-ab/minimum_tax_rate` dataset, rounded half-up to the cent. The output is
`ca-ab/ab428_additional_minimum_tax_line_67`.

The inputs part and the line 67 part are both loaded from the package beside a header and a form of
their own. Alberta is not yet listed in the registrations, so the service is built over the Alberta
package list of `support.py`.
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
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)

D = Decimal
CODE = JurisdictionCode("CA-AB")
T691_AMOUNT = "ca-ab/ab428_minimum_tax_t691_amount_line_67"
LINE_67 = "ca-ab/ab428_additional_minimum_tax_line_67"
MANIFESTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
INPUTS_PART = "ab428_line_67_inputs.yaml"
PART = "ab428_line_67.yaml"

HEADER = dedent(f"""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs: [{T691_AMOUNT}]
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: ca-ab/ab428
      required: true
      exports:
        - {LINE_67}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for position, name in ((2, INPUTS_PART), (3, PART)):
        (folder / f"{position:02d}_{name}").write_text(
            (MANIFESTS / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _worksheet(tmp_path: Path, amount: str | None) -> Worksheet:
    kinds = alberta_kinds()
    given = [] if amount is None else [Artifact(kinds.kind(T691_AMOUNT), D(amount))]
    return _service(tmp_path).compute(CODE, 2025, *given)["ca-ab/ab428"][0]


def _line_67(tmp_path: Path, amount: str | None) -> Decimal:
    value = _worksheet(tmp_path, amount).get(alberta_kinds().kind(LINE_67)).value
    assert isinstance(value, Decimal)
    return value


def test_the_part_declares_the_one_calculation_as_the_form_prints_it() -> None:
    part: Any = yaml.safe_load((MANIFESTS / PART).read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca-ab/ab428"}
    assert part["capabilities"] == [
        {
            "name": "core/apply_rate",
            "title": "Alberta additional tax for minimum tax purposes",
            "reference": "67 box B",
            "unit": "ca/cad",
            "params": {"rate": "ca-ab/minimum_tax_rate"},
            "consumes": {"base": T691_AMOUNT},
            "produces": {"output": LINE_67},
        }
    ]


def test_the_output_kind_is_in_the_alberta_catalog() -> None:
    from tax_engine.jurisdictions.ca_ab.catalog import AB428_ADDITIONAL_MINIMUM_TAX_LINE_67

    assert AB428_ADDITIONAL_MINIMUM_TAX_LINE_67.identifier == LINE_67
    assert alberta_kinds().kind(LINE_67) is AB428_ADDITIONAL_MINIMUM_TAX_LINE_67


@pytest.mark.parametrize(
    ("amount", "tax"),
    [
        # A T691 amount of 1,000.00: 35% of 1,000.00 is 350.00.
        ("1000.00", "350.00"),
        # No amount (0): the line is 0.
        ("0", "0.00"),
        # 1,000.01 x 35% = 350.0035, rounded half-up to 350.00.
        ("1000.01", "350.00"),
        # 0.03 x 35% = 0.0105, rounded half-up to 0.01.
        ("0.03", "0.01"),
        # 0.01 x 35% = 0.0035, rounded half-up to 0.00.
        ("0.01", "0.00"),
        # 0.10 x 35% = 0.035, a tie, rounded half-up to 0.04.
        ("0.10", "0.04"),
    ],
)
def test_line_67_is_35_percent_of_the_t691_amount_rounded_half_up(
    tmp_path: Path, amount: str, tax: str
) -> None:
    assert _line_67(tmp_path, amount) == D(tax)


def test_a_caller_who_leaves_out_the_t691_amount_gets_0(tmp_path: Path) -> None:
    # The amount is left out, so it is read as 0, and the line is 0.00: the ticket's figure at
    # $20,000, $70,000 and $200,000 (salary only, no minimum tax to report).
    assert _line_67(tmp_path, None) == D("0.00")
