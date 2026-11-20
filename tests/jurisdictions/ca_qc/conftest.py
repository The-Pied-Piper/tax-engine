"""Fixtures of the Quebec tests."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pytest

import tax_engine.jurisdictions.ca_qc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_qc.support import (
    quebec_capabilities,
    quebec_kinds,
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

QUEBEC_PARTS = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025"


class TakeHomeService(Protocol):
    """Builds the engine over a temporary Quebec manifest made of a test header, a form
    declaration and real part files of the Quebec take-home folder."""

    def __call__(self, header: str, form: str, *parts: str) -> TaxComputationService: ...


@pytest.fixture
def take_home_service(tmp_path: Path) -> TakeHomeService:
    """A builder of services over a temporary Quebec take-home manifest.

    The builder writes `header` and `form` to the temporary folder, copies each named part file
    (for example "solidarity_credit_amounts.yaml") from the package's manifest folder beside them,
    and points the Quebec namespace at that folder. The two texts sort ahead of the parts, because
    the folder is composed in file-name order. Quebec is not yet in the registered engine, so the
    service is built over the Quebec package list of `support.py`.
    """

    def build(header: str, form: str, *parts: str) -> TaxComputationService:
        folder = tmp_path / "manifests" / "2025"
        folder.mkdir(parents=True)
        (folder / "00_header.yaml").write_text(header, encoding="utf-8")
        (folder / "01_form.yaml").write_text(form, encoding="utf-8")
        for number, part in enumerate(parts, start=2):
            (folder / f"{number:02d}_{part}").write_text(
                (QUEBEC_PARTS / part).read_text(encoding="utf-8"), encoding="utf-8"
            )
        roots = {**quebec_packages().roots(), Namespace("ca-qc"): tmp_path}
        return TaxComputationService(
            YamlJurisdictionSource(roots, quebec_kinds(), quebec_units()),
            YamlParameterSource(
                quebec_packages().roots(), quebec_parameter_parsers(), quebec_units()
            ),
            quebec_capabilities(),
        )

    return build
