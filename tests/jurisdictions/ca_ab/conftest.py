"""Fixtures for the Alberta tests."""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

import pytest

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.registry import Namespace
from tax_engine.registrations import JURISDICTIONS, parameter_parsers, units
from tests.capabilities import bundled_capabilities
from tests.kinds import bundled_kinds
from tests.manifest_support import inputs_without_form

ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"


class TakeHomeFolders:
    """The part files of the Alberta take-home return: Alberta's own, and the federal forms it
    imports from the `ca` package. `rglob` and `glob` search both; `/` names a file of Alberta's.
    """

    def rglob(self, pattern: str) -> Iterator[Path]:
        yield from ALBERTA_PARTS.rglob(pattern)
        yield from FEDERAL_FORMS.rglob(pattern)

    def glob(self, pattern: str) -> Iterator[Path]:
        yield from ALBERTA_PARTS.glob(pattern)
        yield from FEDERAL_FORMS.glob(pattern)

    def __truediv__(self, name: str) -> Path:
        return ALBERTA_PARTS / name


TAKE_HOME = TakeHomeFolders()


def header_without_imports() -> str:
    """The real Alberta manifest header with its `imports:` list taken out.

    A test that copies the federal parts beside the header as parts of its own manifest cannot also
    import them.
    """
    header = (ALBERTA_PARTS / "manifest.yaml").read_text(encoding="utf-8")
    return re.sub(r"^imports:\n(?:  - .*\n)+", "", header, flags=re.MULTILINE)


class TakeHomeService(Protocol):
    """Builds the engine over a temporary Alberta manifest made of a test header, a form
    declaration and real part files of the take-home folder."""

    def __call__(self, header: str, form: str, *parts: str) -> TaxComputationService: ...


@pytest.fixture
def take_home_service(tmp_path: Path) -> TakeHomeService:
    """A builder of services over a temporary Alberta take-home manifest.

    The builder writes `header` and `form` to the temporary folder, copies each named part file
    (for example "schedule_8_line_1.yaml") from the package's take-home folder beside them, and
    points the Alberta namespace at that folder. The two texts sort ahead of the parts, because
    the folder is composed in file-name order. Every other namespace is the bundled one.
    """

    def build(header: str, form: str, *parts: str) -> TaxComputationService:
        folder = tmp_path / "manifests" / "2025"
        folder.mkdir(parents=True)
        (folder / "00_header.yaml").write_text(header, encoding="utf-8")
        (folder / "01_form.yaml").write_text(form, encoding="utf-8")
        for number, part in enumerate(parts, start=2):
            found = next(TAKE_HOME.rglob(part))
            (folder / f"{number:02d}_{part}").write_text(
                inputs_without_form(found)
                if part.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
                else found.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        roots = {**JURISDICTIONS.roots(), Namespace("ca-ab"): tmp_path}
        return TaxComputationService(
            YamlJurisdictionSource(roots, bundled_kinds(), units()),
            YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), units()),
            bundled_capabilities(),
        )

    return build
