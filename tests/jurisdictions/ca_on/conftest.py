"""Fixtures for the Ontario tests."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pytest

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.registry import Namespace
from tax_engine.registrations import JURISDICTIONS, parameter_parsers
from tests.capabilities import bundled_capabilities
from tests.kinds import bundled_kinds

TAKE_HOME = Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "take_home"


class TakeHomeService(Protocol):
    """Builds the engine over a temporary Ontario manifest made of a test header, a form
    declaration and real part files of the take-home folder."""

    def __call__(self, header: str, form: str, *parts: str) -> TaxComputationService: ...


@pytest.fixture
def take_home_service(tmp_path: Path) -> TakeHomeService:
    """A builder of services over a temporary Ontario take-home manifest.

    The builder writes `header` and `form` to the temporary folder, copies each named part file
    (for example "schedule_8_line_1.yaml") from the package's take-home folder beside them, and
    points the Ontario namespace at that folder. The two texts sort ahead of the parts, because
    the folder is composed in file-name order. Every other namespace is the bundled one.
    """

    def build(header: str, form: str, *parts: str) -> TaxComputationService:
        folder = tmp_path / "manifests" / "take_home"
        folder.mkdir(parents=True)
        (folder / "00_header.yaml").write_text(header, encoding="utf-8")
        (folder / "01_form.yaml").write_text(form, encoding="utf-8")
        for number, part in enumerate(parts, start=2):
            (folder / f"{number:02d}_{part}").write_bytes(next(TAKE_HOME.rglob(part)).read_bytes())
        roots = {**JURISDICTIONS.roots(), Namespace("ca-on"): tmp_path}
        return TaxComputationService(
            YamlJurisdictionSource(roots, bundled_kinds()),
            YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
            bundled_capabilities(),
        )

    return build
