"""TaxComputationService carries a manifest's `unit:` from the YAML to the worksheet it computes.

The service hands the manifest's resolved units (`Manifest.units_by_name`) to each form it
composes, so a computed worksheet's artifacts carry the unit (`artifact.unit`) and its trace prints
it. Made-up packages: `ex-on` (a province) names units of `ex` (ex/crowns), of itself (ex-on/ducats)
and of core (core/moons), by their full identifiers.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any, ClassVar

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.unit_text import (
    EnglishUnitText,
    EnglishUnitTextRegistry,
)
from tax_engine.adapters.inbound.unit_text import Placement
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityRegistry, CapabilityResult
from tax_engine.domain.errors import NotFoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.unit import UnitCatalog, UnitRegistry
from tests.kinds import AutoKinds

D = Decimal
EX_ON = JurisdictionCode("EX-ON")
GROSS = AmountKind("ex/gross_pay")
LESS = AmountKind("ex/allowance")
NET = AmountKind("ex/net_pay")


class Net(Capability):
    """Produces `net` as `gross` less `allowance`, not below 0, with its trace line."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"gross": Decimal, "allowance": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"net": Decimal}

    def __init__(
        self,
        gross: ArtifactKind[Decimal],
        allowance: ArtifactKind[Decimal],
        net: ArtifactKind[Decimal],
    ) -> None:
        super().__init__(gross=gross, allowance=allowance, net=net)
        self._gross, self._allowance, self._net = gross, allowance, net

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        gross = self._input(inputs, self._gross).value
        allowance = self._input(inputs, self._allowance).value
        result = max(gross - allowance, D("0"))
        line = SubtractedNotBelowZeroLine(
            output=self._net,
            minuend=self._gross,
            minuend_amount=gross,
            subtrahend=self._allowance,
            subtrahend_amount=allowance,
            result=result,
            rounding=NO_ROUNDING,
        )
        return CapabilityResult(outputs=(Artifact(self._net, result),), trace=(line,))


class NoParameters:
    def get[T](self, family: str, tax_year: int, kind: ParameterKind[T]) -> ParameterDataset[T]:
        raise NotFoundError(f"no {family} dataset for tax year {tax_year}")


def registry() -> UnitRegistry:
    units = UnitRegistry()
    for namespace, name in (("core", "moons"), ("ex", "crowns"), ("ex-on", "ducats")):
        catalog = UnitCatalog(Namespace(namespace))
        catalog.declare(name)
        units.register_catalog(catalog)
    return units


def texts() -> EnglishUnitTextRegistry:
    registry = EnglishUnitTextRegistry()
    registry.register_text(
        EnglishUnitText("ex/crowns", "EX$", "EX$", Placement.BEFORE, spaced=False)
    )
    registry.register_text(
        EnglishUnitText("ex-on/ducats", "ON$", "ON$", Placement.BEFORE, spaced=False)
    )
    registry.register_text(
        EnglishUnitText("core/moons", "moon", "moons", Placement.AFTER, spaced=True)
    )
    return registry


def service(directory: Path, manifest: str) -> TaxComputationService:
    path = directory / "ex-on" / "manifests" / "v1.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "jurisdiction: EX-ON\nversion: 1\nvalid_from_tax_year: 2025\noutputs: [ex/net_pay]\n"
        + dedent(manifest),
        encoding="utf-8",
    )
    capabilities = CapabilityRegistry()
    capabilities.register("ex/net", Net)
    return TaxComputationService(
        YamlJurisdictionSource({Namespace("ex-on"): directory / "ex-on"}, AutoKinds(), registry()),
        NoParameters(),
        capabilities,
    )


WITH_UNITS = """\
inputs:
  - {name: ex/gross_pay, required: true, unit: ex/crowns}
  - {name: ex/allowance, required: true, unit: ex/crowns}
capabilities:
  - name: ex/net
    unit: ex-on/ducats
    consumes: {gross: ex/gross_pay, allowance: ex/allowance}
    produces: {net: ex/net_pay}
"""

WITHOUT_UNITS = """\
inputs:
  - {name: ex/gross_pay, required: true}
  - {name: ex/allowance, required: true}
capabilities:
  - name: ex/net
    consumes: {gross: ex/gross_pay, allowance: ex/allowance}
    produces: {net: ex/net_pay}
"""


def computed(directory: Path, manifest: str, *given: Artifact[Any]) -> Any:
    worksheets = service(directory, manifest).compute(EX_ON, 2025, *given)
    (sheet,) = worksheets["ex-on/return"]
    return sheet


def test_a_computed_worksheets_artifacts_carry_the_manifests_units(tmp_path: Path) -> None:
    sheet = computed(tmp_path, WITH_UNITS, Artifact(GROSS, D("70000")), Artifact(LESS, D("1300")))

    assert sheet.get(GROSS).unit == registry().get("ex/crowns")
    assert sheet.get(LESS).unit == registry().get("ex/crowns")
    assert sheet.get(NET).unit == registry().get("ex-on/ducats")
    assert sheet.get(NET).value == D("68700")


def test_the_unit_is_readable_on_the_worksheet_by_label_and_by_trace_line(tmp_path: Path) -> None:
    sheet = computed(tmp_path, WITH_UNITS, Artifact(GROSS, D("70000")), Artifact(LESS, D("1300")))
    (line,) = sheet.trace

    assert sheet.unit("net_pay") == registry().get("ex-on/ducats")
    assert sheet.unit_of(line) == registry().get("ex-on/ducats")


def test_the_rendered_trace_prints_the_units(tmp_path: Path) -> None:
    sheet = computed(tmp_path, WITH_UNITS, Artifact(GROSS, D("70000")), Artifact(LESS, D("1300")))

    assert EnglishTraceRenderer(unit_texts=texts()).render_all(sheet.trace, sheet) == (
        "Gross pay (EX$70000.00) less allowance (EX$1300.00), not below 0, "
        "gives ON$68700.00 (not rounded).",
    )


def test_a_manifest_naming_no_unit_gives_artifacts_without_one_and_the_old_text(
    tmp_path: Path,
) -> None:
    sheet = computed(
        tmp_path, WITHOUT_UNITS, Artifact(GROSS, D("70000")), Artifact(LESS, D("1300"))
    )

    assert (sheet.get(GROSS).unit, sheet.get(NET).unit) == (None, None)
    assert EnglishTraceRenderer().render_all(sheet.trace, sheet) == (
        "Gross pay (70000.00) less allowance (1300.00), not below 0, gives 68700.00 (not rounded).",
    )


def test_the_manifest_decides_a_unit_the_caller_gave_an_artifact_is_dropped(
    tmp_path: Path,
) -> None:
    unit = registry().get("ex/crowns")
    sheet = computed(
        tmp_path,
        WITHOUT_UNITS,
        Artifact(GROSS, D("70000"), unit=unit),
        Artifact(LESS, D("1300"), unit=unit),
    )

    assert sheet.get(GROSS).unit is None
    assert sheet.get(LESS).unit is None
