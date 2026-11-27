"""Fixtures for the Prince Edward Island tests."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

import pytest

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_pe
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.registry import Namespace
from tests.federal_forms import FEDERAL_FORMS
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_capabilities,
    prince_edward_island_kinds,
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
    prince_edward_island_units,
)

PRINCE_EDWARD_ISLAND_PARTS = (
    Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
)


class TakeHomeFolders:
    """The part files of the Prince Edward Island take-home return: Prince Edward Island's own,
    and the federal forms it imports from the `ca` package. `rglob` searches both."""

    def rglob(self, pattern: str) -> Iterator[Path]:
        yield from PRINCE_EDWARD_ISLAND_PARTS.rglob(pattern)
        yield from FEDERAL_FORMS.rglob(pattern)


TAKE_HOME = TakeHomeFolders()


class TakeHomeService(Protocol):
    """Builds the engine over a temporary Prince Edward Island manifest made of a test header, a
    form declaration and real part files of the take-home folder."""

    def __call__(self, header: str, form: str, *parts: str) -> TaxComputationService: ...


@pytest.fixture
def take_home_service(tmp_path: Path) -> TakeHomeService:
    """A builder of services over a temporary Prince Edward Island take-home manifest.

    The builder writes `header` and `form` to the temporary folder, copies each named part file
    (for example "pe428_line_9.yaml") from the package's manifest folder, or from the
    federal forms, beside them, and points the Prince Edward Island namespace at that folder. The
    two texts sort ahead of the parts, because the folder is composed in file-name order.
    The service is built over the Prince Edward Island package list of `support.py`, not the
    registered engine.
    """

    def build(header: str, form: str, *parts: str) -> TaxComputationService:
        folder = tmp_path / "manifests" / "2025"
        folder.mkdir(parents=True)
        (folder / "00_header.yaml").write_text(header, encoding="utf-8")
        (folder / "01_form.yaml").write_text(form, encoding="utf-8")
        for number, part in enumerate(dict.fromkeys(parts), start=2):
            found = next(TAKE_HOME.rglob(part))
            (folder / f"{number:02d}_{part}").write_text(
                found.read_text(encoding="utf-8"), encoding="utf-8"
            )
        roots = {**prince_edward_island_packages().roots(), Namespace("ca-pe"): tmp_path}
        return TaxComputationService(
            YamlJurisdictionSource(
                roots, prince_edward_island_kinds(), prince_edward_island_units()
            ),
            YamlParameterSource(
                prince_edward_island_packages().roots(),
                prince_edward_island_parameter_parsers(),
                prince_edward_island_units(),
            ),
            prince_edward_island_capabilities(),
        )

    return build
