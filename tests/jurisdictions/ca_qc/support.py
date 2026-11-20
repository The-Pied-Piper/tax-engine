"""The Quebec package list and the registries built over it.

Quebec is not yet listed in `tax_engine.registrations.JURISDICTIONS`, so the
tests of this package build their own package list (core, federal, Quebec)
here and take their kinds and capabilities from it. Each registry is built once per test process;
never register into one.
"""

from collections.abc import Callable
from decimal import Decimal
from functools import cache
from pathlib import Path
from textwrap import dedent
from typing import Any

import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_qc
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import InputDeclaration
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import UnitRegistry
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import T2204_PREMIUMS_DEDUCTED_GIVEN
from tests.manifest_support import inputs_without_form


@cache
def quebec_packages() -> JurisdictionPackages:
    """The packages a Quebec return needs: core, federal and ca-qc."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_qc,
        )
    )


@cache
def quebec_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Quebec package list; never register into it."""
    kinds = ArtifactRegistry()
    quebec_packages().register(kinds)
    return kinds


@cache
def quebec_units() -> UnitRegistry:
    """The units of the Quebec package list; never register into it."""
    registry = UnitRegistry()
    quebec_packages().register_units(registry)
    return registry


@cache
def quebec_capabilities() -> CapabilityRegistry:
    """The capabilities of the Quebec package list; never register into it."""
    registry = CapabilityRegistry()
    quebec_packages().register_capabilities(registry)
    return registry


@cache
def quebec_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the Quebec list; never register into it."""
    registry = ParameterParserRegistry()
    quebec_packages().register_parameter_parsers(registry)
    return registry


MANIFEST = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025" / "manifest.yaml"
)
T2204_HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    imports:
    """)
# The T2204 reads T1 line 10100 from the Quebec T1, so the test declares that form, exporting line
# 10100 alone under the neutral name the shared form reads, and composes the real line 10100 part.
T2204_FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca-qc/employment_income_line_10100
      supplies:
        ca/t1_taxable_income.employment_income_line_10100: ca-qc/employment_income_line_10100
    capabilities: []
    """)
T2204_T1_PART = "t1_taxable_income_line_10100.yaml"


def real_import(form: str) -> str:
    """The real Quebec manifest's `imports` entry for `form`, as indented YAML for a test header."""
    entries: list[Any] = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["imports"]
    (entry,) = [e for e in entries if e == form or (isinstance(e, dict) and e["form"] == form)]
    return "".join(f"  {line}\n" for line in yaml.safe_dump([entry]).splitlines())


def t2204_worksheet(
    take_home_service: Callable[..., TaxComputationService],
    salary: str,
    given: str | None = None,
) -> Worksheet:
    """The Quebec T2204 worksheet for a salary, over a temporary manifest that takes the salary and
    imports the shared T2204 exactly as the real Quebec manifest does, with its dataset swap. Line
    4 is left blank unless `given` is passed."""
    service = take_home_service(T2204_HEADER + real_import("ca/t2204"), T2204_FORM, T2204_T1_PART)
    starting = [Artifact(EMPLOYMENT_INCOME, Decimal(salary))]
    if given is not None:
        starting.append(Artifact(T2204_PREMIUMS_DEDUCTED_GIVEN, Decimal(given)))
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca/t2204"]
    return sheet


SCHEDULE_P_HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
TP1_PARTS = (
    "salary.yaml",
    "tp1_income.yaml",
    "tp1_income_line_97_input.yaml",
    "tp1_income_line_97.yaml",
    "tp1_income_line_98_input.yaml",
    "tp1_income_line_98.yaml",
    "tp1_income_line_98_1_input.yaml",
    "tp1_income_line_98_1.yaml",
    "tp1_income_line_98_2_input.yaml",
    "tp1_income_line_98_2.yaml",
    "tp1_income_line_199_input.yaml",
    "tp1_income_line_199.yaml",
)
WORK_CHART_201_PARTS = (
    "work_chart_201.yaml",
    "work_chart_201_line_1_input_105.yaml",
    "work_chart_201_line_1_input_107.yaml",
    "work_chart_201_line_1_input_box_211.yaml",
    "work_chart_201_line_1.yaml",
    "work_chart_201_line_2_input.yaml",
    "work_chart_201_line_3_input.yaml",
    "work_chart_201_line_4_input.yaml",
    "work_chart_201_line_5_input.yaml",
    "work_chart_201_line_6.yaml",
    "work_chart_201_line_7_input.yaml",
    "work_chart_201_line_8.yaml",
    "work_chart_201_line_9.yaml",
)
SCHEDULE_P_FIRST_PARTS = (
    *TP1_PARTS,
    *WORK_CHART_201_PARTS,
    "schedule_p_line_10.yaml",
)
SCHEDULE_P_WORK_INCOME_PARTS = (
    *SCHEDULE_P_FIRST_PARTS,
    "schedule_p_line_13_inputs.yaml",
    "schedule_p_line_14_inputs.yaml",
    "schedule_p_line_15_inputs.yaml",
    "schedule_p_line_18.yaml",
    "schedule_p_line_22_inputs.yaml",
    "schedule_p_line_29.yaml",
)


def schedule_p_form(*exports: str) -> str:
    """A Schedule P form declaration that exports only the lines a test builds."""
    lines = "".join(f"    - {export}\n" for export in exports)
    return f"form:\n  name: ca-qc/schedule_p\n  required: true\n  exports:\n{lines}"


def schedule_p_worksheet(
    take_home_service: Callable[..., TaxComputationService],
    form: str,
    parts: tuple[str, ...],
    salary: str,
    *given: tuple[ArtifactKind[Any], str],
) -> Worksheet:
    """The Schedule P worksheet of a salary, over the real TP-1 income parts and the Schedule P
    `parts` of a test; `given` are the optional answers the test passes."""
    starting = [Artifact(EMPLOYMENT_INCOME, Decimal(salary))]
    starting += [Artifact(kind, kind.value_type(value)) for kind, value in given]
    (sheet,) = take_home_service(SCHEDULE_P_HEADER, form, *parts).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/schedule_p"]
    return sheet


def schedule_p_input(tmp_path: Path, part: str, name: str) -> InputDeclaration:
    """The declaration of input `name` in the Schedule P inputs `part`, loaded through the Quebec
    manifest source under a test header (the part's `form:` header is left out, as the inputs of a
    part joined to the default form are the caller's own)."""
    folder = tmp_path / "manifest"
    folder.mkdir(parents=True)
    (folder / "header.yaml").write_text(SCHEDULE_P_HEADER + "capabilities: []\n", encoding="utf-8")
    (folder / part).write_text(inputs_without_form(MANIFEST.parent / part), encoding="utf-8")
    roots = {**quebec_packages().roots(), Namespace("ca-qc"): tmp_path}
    return YamlJurisdictionSource(roots, quebec_kinds(), quebec_units()).load(folder).inputs[name]
