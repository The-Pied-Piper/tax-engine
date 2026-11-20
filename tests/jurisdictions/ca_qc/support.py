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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact, ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.unit import UnitRegistry
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import T2204_PREMIUMS_DEDUCTED_GIVEN


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
T2204_FORM = "capabilities: []\n"


def real_import(form: str) -> str:
    """The real Quebec manifest's `imports` entry for `form`, as indented YAML for a test header."""
    entries: list[Any] = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["imports"]
    (entry,) = [e for e in entries if e == form or (isinstance(e, dict) and e["form"] == form)]
    return "".join(f"  {line}\n" for line in yaml.safe_dump([entry]).splitlines())


def t2204_worksheet(
    take_home_service: Callable[[str, str], TaxComputationService],
    salary: str,
    given: str | None = None,
) -> Worksheet:
    """The Quebec T2204 worksheet for a salary, over a temporary manifest that takes the salary and
    imports the shared T2204 exactly as the real Quebec manifest does, with its dataset swap. Line
    4 is left blank unless `given` is passed."""
    service = take_home_service(T2204_HEADER + real_import("ca/t2204"), T2204_FORM)
    starting = [Artifact(EMPLOYMENT_INCOME, Decimal(salary))]
    if given is not None:
        starting.append(Artifact(T2204_PREMIUMS_DEDUCTED_GIVEN, Decimal(given)))
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca/t2204"]
    return sheet
