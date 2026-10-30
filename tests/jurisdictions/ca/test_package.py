"""The federal Canada package: its namespace and where its data lives."""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca.NAMESPACE == "ca"


def test_holds_its_parameter_data() -> None:
    parameters = Path(tax_engine.jurisdictions.ca.__file__).parent / "parameters"

    assert (parameters / "brackets" / "2025.yaml").is_file()
    assert (parameters / "basic_personal_amount" / "2025.yaml").is_file()
    assert (parameters / "credit_rate" / "2025.yaml").is_file()
