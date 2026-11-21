"""BC479 (2025) line 6, adjusted family net income, from the salary alone, real parts.

Form text (Form BC479, CRA 5010-TC, as recorded on the ticket): "Line 6: Add the amounts from line
5 of columns 1 and 2." with the printed label "Adjusted family net income". The spouse column
(column 2) is not built: a single filer has column 1 only. So line 6 is one calculation, a sum of
the single part, line 5 (`ca-bc/bc479_adjusted_net_income_line_5`), read through core/sum in
`bc479_line_6.yaml` (title "Adjusted family net income", reference "6", rounded through
`ca-bc/cent_rounding`). The output is `ca-bc/bc479_adjusted_family_net_income_line_6`, a
non-negative kind.

The test composes the real British Columbia salary part, the real Schedule 8 parts, the real T1
taxable income parts, the real line 1 to line 5 parts and the new line 6 part, and types in only
the salary (and, in other tests, line 4). The form declaration is made up here, exporting only
line 6.

Figures (hand-computed from the printed forms, not a CRA example): line 6 is line 5, which is
16,865.00 / 198,926.00 at 17,000 / 200,000. With line 4 of 1,000.00 at 17,000, line 6 is 15,865.00.
With line 4 above line 3, line 6 is 0.00.
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
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC479_ADJUSTED_FAMILY_NET_INCOME_LINE_6,
    BC479_UCCB_RDSP_INCOME_LINE_4,
)
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc479"
LINE_5 = "ca-bc/bc479_adjusted_net_income_line_5"
LINE_6 = "ca-bc/bc479_adjusted_family_net_income_line_6"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc479_line_6.yaml"
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_6}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield _federal(name)
    yield BC_PARTS / "bc479_line_1.yaml"
    yield BC_PARTS / "bc479_line_2_input.yaml"
    yield BC_PARTS / "bc479_line_3.yaml"
    yield BC_PARTS / "bc479_line_4_input.yaml"
    yield BC_PARTS / "bc479_line_5.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{part.name}").write_text(text, encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(CODE, 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def _rounding() -> Any:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


# salary, line 6 (column 1 only, so line 6 is line 5 of the same salary).
CASES = [
    ("17000", "16865.00"),
    ("200000", "198926.00"),
]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_6_is_line_5_for_a_single_filer(tmp_path: Path, salary: str, expected: str) -> None:
    line_6 = _sheet(tmp_path, salary).get(BC479_ADJUSTED_FAMILY_NET_INCOME_LINE_6).value

    assert line_6 == D(expected)
    assert str(line_6) == expected
    assert line_6.as_tuple().exponent == -2
    assert not line_6.is_signed()


def test_line_6_follows_line_5_when_line_4_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(BC479_UCCB_RDSP_INCOME_LINE_4, D("1000.00")))

    line_6 = sheet.get(BC479_ADJUSTED_FAMILY_NET_INCOME_LINE_6).value
    assert line_6 == D("15865.00")
    assert str(line_6) == "15865.00"


def test_line_6_is_0_when_line_4_is_above_line_3(tmp_path: Path) -> None:
    # Line 3 is 16,865.00 at 17,000 and line 4 is 20,000.00: line 5 is floored, so line 6 is 0.00.
    sheet = _sheet(tmp_path, "17000", Artifact(BC479_UCCB_RDSP_INCOME_LINE_4, D("20000.00")))

    line_6 = sheet.get(BC479_ADJUSTED_FAMILY_NET_INCOME_LINE_6).value
    assert line_6 == D("0.00")
    assert str(line_6) == "0.00"
    assert not line_6.is_signed()


def test_the_step_traces_one_sum_line_over_line_5_with_the_cent_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(BC479_UCCB_RDSP_INCOME_LINE_4, D("1000.00")))
    kinds = british_columbia_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(LINE_6)]
    assert line == SumLine(
        output=kinds.kind(LINE_6),
        parts=((kinds.kind(LINE_5), D("15865.00")),),
        rounding=_rounding().rounding,
        total=D("15865.00"),
    )


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_titled_adjusted_family_net_income() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": "Adjusted family net income",
        "reference": "6",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_5]},
        "produces": {"output": LINE_6},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_6)

    assert kind is BC479_ADJUSTED_FAMILY_NET_INCOME_LINE_6
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
