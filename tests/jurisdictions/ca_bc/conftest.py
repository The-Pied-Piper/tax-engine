"""Fixtures for the British Columbia tests."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pytest

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.registry import Namespace
from tax_engine.registrations import JURISDICTIONS, parameter_parsers, units
from tests.capabilities import bundled_capabilities
from tests.kinds import bundled_kinds

BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"


class TakeHomeService(Protocol):
    """Builds the engine over a temporary British Columbia manifest made of a test header, a form
    declaration and real part files of the British Columbia manifest folder."""

    def __call__(self, header: str, form: str, *parts: str) -> TaxComputationService: ...


@pytest.fixture
def take_home_service(tmp_path: Path) -> TakeHomeService:
    """A builder of services over a temporary British Columbia take-home manifest.

    The builder writes `header` and `form` to the temporary folder, copies each named part file
    (for example "bc428_line_5.yaml") from the package's manifest folder beside them, and points
    the British Columbia namespace at that folder. The two texts sort ahead of the parts, because
    the folder is composed in file-name order. Every other namespace is the registered one.
    """

    def build(header: str, form: str, *parts: str) -> TaxComputationService:
        folder = tmp_path / "manifests" / "2025"
        folder.mkdir(parents=True)
        (folder / "00_header.yaml").write_text(header, encoding="utf-8")
        (folder / "01_form.yaml").write_text(form, encoding="utf-8")
        for number, part in enumerate(parts, start=2):
            text = (BC_PARTS / part).read_text(encoding="utf-8")
            (folder / f"{number:02d}_{part}").write_text(text, encoding="utf-8")
        roots = {**JURISDICTIONS.roots(), Namespace("ca-bc"): tmp_path}
        return TaxComputationService(
            YamlJurisdictionSource(roots, bundled_kinds(), units()),
            YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), units()),
            bundled_capabilities(),
        )

    return build
