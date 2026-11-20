"""The header of the Quebec 2025 manifest: the return's identity and its federal imports (Schedules
8 and 6 and T2204; T2204 reads the Quebec EI premium dataset, 5005-S10). It declares no inputs or
outputs yet; later tickets add them."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc

MANIFEST = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025" / "manifest.yaml"
)


def _header() -> dict[str, Any]:
    header = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(header, dict)
    return header


def test_the_return_identity() -> None:
    header = _header()

    assert header["jurisdiction"] == "CA-QC"
    assert header["version"] == 1
    assert header["valid_from_tax_year"] == 2025
    assert header["title"] == "Return summary"


def test_the_return_declares_no_capabilities_and_no_outputs_yet() -> None:
    header = _header()

    assert header["capabilities"] == []
    assert "outputs" not in header


def test_the_federal_forms_are_imported_in_order_and_read_the_quebec_datasets() -> None:
    assert _header()["imports"] == [
        {
            "form": "ca/schedule_8",
            "datasets": {
                "ca/cpp_line_11_base_contribution": "ca-qc/qpp_line_11_base_contribution",
            },
        },
        {
            "form": "ca/schedule_6",
            "datasets": {
                "ca/cwb_base_amount": "ca-qc/cwb_base_amount",
                "ca/cwb_rate": "ca-qc/cwb_rate",
            },
        },
        {"form": "ca/t2204", "datasets": {"ca/ei_premium": "ca-qc/ei_premium"}},
    ]


def test_the_quebec_return_does_not_import_the_federal_t1_forms() -> None:
    imports = _header()["imports"]

    assert "ca/t1_taxable_income" not in imports
    assert "ca/t1_tax_and_credits" not in imports


def test_the_header_declares_no_inputs() -> None:
    assert "inputs" not in _header()


def test_every_manifest_part_file_loads() -> None:
    parts = sorted(MANIFEST.parent.glob("*.yaml"))

    assert MANIFEST in parts
    for part in parts:
        assert isinstance(yaml.safe_load(part.read_text(encoding="utf-8")), dict)
