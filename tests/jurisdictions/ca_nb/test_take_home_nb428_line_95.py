"""NB428 (2025) line 95, from the salary alone, real parts.

Form text: Form NB428, CRA 5004-C (on the ticket, read 26 Nov 2026); the part file's comment
quotes it. Figures hand-computed from the printed form: net income is the salary less the
enhanced CPP deduction, plus the optional UCCB and RDSP income lines where given.
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
import tax_engine.jurisdictions.ca_nb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
    new_brunswick_units,
)
from tests.kinds import non_negative

D = Decimal
NB_PARTS = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / "manifests" / "2025"
LINE_PART = NB_PARTS / "nb428_line_95.yaml"
FEDERAL_FORM_NAMES = (
    "schedule_9",
    "schedule_8",
    "t2204",
    "t1_employment_income",
    "t1_taxable_income",
)
NB_PART_NAMES = (
    "nb428_line_1.yaml",
    "nb428_line_3.yaml",
    "nb428_line_4.yaml",
    "nb428_line_5.yaml",
    "nb428_line_6.yaml",
    "nb428_line_7.yaml",
    "nb428_line_8.yaml",
    "nb428_line_55_input.yaml",
    "nb428_line_56.yaml",
    "nb428_line_9.yaml",
    "nb428_line_18.yaml",
    "nb428_line_19.yaml",
    "nb428_line_21.yaml",
    "nb428_line_25.yaml",
    "nb428_line_26.yaml",
    "nb428_line_30.yaml",
    "nb428_line_33.yaml",
    "nb428_line_38.yaml",
    "nb428_line_46_input.yaml",
    "nb428_line_47.yaml",
    "nb428_line_49.yaml",
    "nb428_line_50.yaml",
    "nb428_line_51.yaml",
    "nb428_line_52.yaml",
    "nb428_line_53.yaml",
    "nb428_line_58.yaml",
    "nb428_line_60_input.yaml",
    "nb428_line_61_input.yaml",
    "nb428_line_62.yaml",
    "nb428_line_63.yaml",
    "nb428_line_64_input.yaml",
    "nb428_line_65.yaml",
    "nb428_line_66_input.yaml",
    "nb428_line_67.yaml",
    "nb428_line_70.yaml",
    "nb428_line_71.yaml",
    "nb428_line_72.yaml",
    "nb428_line_73.yaml",
    "nb428_line_74.yaml",
    "nb428_line_77.yaml",
    "nb428_line_80.yaml",
    "nb428_line_82.yaml",
    "nb428_line_83.yaml",
    "nb428_line_85.yaml",
    "nb428_line_86.yaml",
    "nb428_line_87.yaml",
    "nb428_line_92_input.yaml",
    "nb428_line_92.yaml",
    "nb428_line_93.yaml",
    "nb428_line_94_input.yaml",
    "nb428_line_94.yaml",
    "nb428_line_95.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-NB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nb/nb428
      required: true
      exports:
        - ca-nb/nb428_tax_line_67
        - ca-nb/nb428_net_income_line_70
        - ca-nb/nb428_uccb_repayment_line_21300
        - ca-nb/nb428_rdsp_income_repayment_line_23200
        - ca-nb/nb428_uccb_rdsp_repayments_line_71
        - ca-nb/nb428_family_income_line_72
        - ca-nb/nb428_uccb_income_line_11700
        - ca-nb/nb428_rdsp_income_line_12500
        - ca-nb/nb428_uccb_rdsp_income_line_73
        - ca-nb/nb428_adjusted_family_income_line_74
        - ca-nb/low_income_reduction_basic
        - ca-nb/nb428_low_income_reduction_line_80
        - ca-nb/low_income_reduction_base_amount
        - ca-nb/nb428_line_83
        - ca-nb/nb428_line_85
        - ca-nb/nb428_line_86_before_eligibility_test
        - ca-nb/low_income_reduction_single_income_limit
        - ca-nb/nb428_income_under_single_limit
        - ca-nb/nb428_line_86_eligibility_gate
        - ca-nb/nb428_line_86
        - ca-nb/nb428_tax_line_87
        - ca-nb/nb428_tax_line_95
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    for form in FEDERAL_FORM_NAMES:
        yield from form_parts(form)
    for name in NB_PART_NAMES:
        yield NB_PARTS / name


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary New Brunswick manifest of a test header, a form declaration
    and the real part files, every other namespace being the package list's own. The header and
    the form declaration are made up here, because the shared scaffold owns them."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(dict.fromkeys(_part_files()), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**new_brunswick_packages().roots(), Namespace("ca-nb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, new_brunswick_kinds(), new_brunswick_units()),
        YamlParameterSource(
            new_brunswick_packages().roots(),
            new_brunswick_parameter_parsers(),
            new_brunswick_units(),
        ),
        new_brunswick_capabilities(),
    )


def _kind(identifier: str) -> AmountKind:
    kind = new_brunswick_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _values(tmp_path: Path, salary: str, given: dict[str, str]) -> dict[str, Decimal]:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(_kind(name), D(value)) for name, value in given.items()]
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NB"), 2025, tuple(artifacts))
    )
    (sheet,) = worksheets["ca-nb/nb428"]
    return {name: D(sheet.get(_kind(name)).value) for name in ("ca-nb/nb428_tax_line_95",)}


CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-nb/nb428_tax_line_95": "0.00"}),
    ("30000", {}, {"ca-nb/nb428_tax_line_95": "798.76"}),
    ("70000", {}, {"ca-nb/nb428_tax_line_95": "5676.89"}),
    (
        "70000",
        {
            "ca-nb/nb428_political_contribution_credit_line_92": "100.00",
            "ca-nb/nb428_labour_sponsored_credit_line_94": "200.00",
        },
        {"ca-nb/nb428_tax_line_95": "5376.89"},
    ),
    (
        "20000",
        {
            "ca-nb/nb428_political_contribution_credit_line_92": "100.00",
            "ca-nb/nb428_labour_sponsored_credit_line_94": "200.00",
        },
        {"ca-nb/nb428_tax_line_95": "0.00"},
    ),
]


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_line_95_figures(
    tmp_path: Path, salary: str, given: dict[str, str], expected: dict[str, str]
) -> None:
    values = _values(tmp_path, salary, given)

    assert values == {name: D(value) for name, value in expected.items()}


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


@pytest.mark.parametrize("identifier", ("ca-nb/nb428_tax_line_95",))
def test_the_kind_is_a_registered_non_negative_amount_kind(identifier: str) -> None:
    kind = new_brunswick_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_part_names_the_form_and_has_its_steps() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-nb/nb428"}
    assert part["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "95",
            "unit": "ca/cad",
            "params": {"rounding": "ca-nb/cent_rounding"},
            "consumes": {
                "amount": "ca-nb/nb428_tax_line_93",
                "less": "ca-nb/nb428_labour_sponsored_credit_checked_line_94",
            },
            "blank": {"less": "0"},
            "produces": {"output": "ca-nb/nb428_tax_line_95"},
        }
    ]
