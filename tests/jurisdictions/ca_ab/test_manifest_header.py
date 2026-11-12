"""The header of the Alberta 2025 manifest: the return's identity, its output and its federal
imports. It declares no inputs yet; the salary input is ticket #662."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca_ab
import yaml

MANIFEST = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025" / "manifest.yaml"
)


def _header() -> dict[str, Any]:
    header = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(header, dict)
    return header


def test_the_return_identity() -> None:
    header = _header()

    assert header["jurisdiction"] == "CA-AB"
    assert header["version"] == 1
    assert header["valid_from_tax_year"] == 2025
    assert header["title"] == "Return summary"


def test_the_return_exports_the_refund_or_balance_owing_and_declares_no_capabilities() -> None:
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


def test_the_header_declares_no_inputs() -> None:
    assert "inputs" not in _header()
