"""Test support for the T691 tests: the real T691 form run on its own through the real engine."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.registrations import JURISDICTIONS, parameter_parsers, units
from tests.capabilities import bundled_capabilities
from tests.federal_forms import form_parts
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
LINE_1 = "ca/t691_minimum_amount"
LINE_2 = "ca/t691_basic_federal_tax"
LINE_13 = "ca/t691_line_8_plus_line_12"
INPUTS = {"line_1": LINE_1, "line_2": LINE_2, "line_13": LINE_13}
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""


def t691_figure(tmp_path: Path, output: str, **given: str) -> Decimal:
    """The T691 form's figure `output`, with the named lines (`line_1`, `line_2`, `line_13`) given
    and the others left blank, over a temporary manifest of a test header and the real T691 parts.
    """
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text("{}\n", encoding="utf-8")
    for number, part in enumerate(form_parts("t691"), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**JURISDICTIONS.roots(), Namespace("ca-on"): tmp_path}
    service = TaxComputationService(
        YamlJurisdictionSource(roots, bundled_kinds(), units()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), units()),
        bundled_capabilities(),
    )
    kinds = bundled_kinds()
    starting = [Artifact(kinds.kind(INPUTS[key]), D(value)) for key, value in given.items()]
    (sheet,) = service.compute(CODE, 2025, *starting)["ca/t691"]
    value = sheet.get(kinds.kind(output)).value
    assert isinstance(value, Decimal)
    return value
