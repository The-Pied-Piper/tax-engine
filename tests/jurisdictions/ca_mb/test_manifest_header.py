"""The header of the Manitoba 2025 manifest: the return's identity, its outputs and its federal
imports. It declares no inputs yet and swaps no dataset on the federal Schedule 6, because the
general Schedule 6 applies to Manitoba."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_mb

MANIFEST = (
    Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025" / "manifest.yaml"
)


def _header() -> dict[str, Any]:
    header = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(header, dict)
    return header


def test_the_return_identity() -> None:
    header = _header()

    assert header["jurisdiction"] == "CA-MB"
    assert header["version"] == 1
    assert header["valid_from_tax_year"] == 2025
    assert header["title"] == "Return summary"


def test_the_return_exports_the_refund_and_no_capabilities() -> None:
    header = _header()

    assert header["outputs"] == ["ca/refund_or_balance_owing"]
    assert header["capabilities"] == []


def test_the_federal_forms_are_imported_in_order() -> None:
    assert _header()["imports"] == [
        "ca/t1_taxable_income",
        "ca/t1_tax_and_credits",
        "ca/schedule_6",
        "ca/schedule_8",
        "ca/t2204",
    ]


def test_schedule_6_is_imported_without_a_dataset_swap() -> None:
    imports = _header()["imports"]

    assert all(isinstance(entry, str) for entry in imports)


def test_the_header_declares_no_inputs() -> None:
    assert "inputs" not in _header()
