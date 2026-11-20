"""Fixtures for the Quebec tests."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.application.services.tax_computation import TaxComputationService
from tests.jurisdictions.ca_qc.support import quebec_service

MANIFEST = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025" / "manifest.yaml"
)
HEADER = dedent("""\
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


def _real_import(form: str) -> str:
    """The real Quebec manifest's `imports` entry for `form`, as YAML text for a test manifest."""
    header = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    entries: list[Any] = header["imports"]
    (entry,) = [e for e in entries if e == form or (isinstance(e, dict) and e["form"] == form)]
    return yaml.safe_dump([entry])


@pytest.fixture
def take_home_service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Quebec 2025 manifest that takes the salary and imports the shared
    T2204 exactly as the real Quebec manifest does, with its dataset swap.

    The real manifest declares no inputs or outputs yet, so the test header declares the salary;
    the import entry is read from the real manifest, so a change to the swap there is tested here.
    """
    imports = "".join(f"  {line}\n" for line in _real_import("ca/t2204").splitlines())
    return quebec_service(tmp_path, HEADER + imports)
