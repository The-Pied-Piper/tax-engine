"""The CA-ON package: its namespace and where its data and manifest live."""

from __future__ import annotations

import re
from pathlib import Path

import tax_calculator.jurisdictions.ca_on


def test_declares_its_namespace() -> None:
    assert tax_calculator.jurisdictions.ca_on.NAMESPACE == "ca-on"


def test_holds_its_manifest_and_parameter_data() -> None:
    directory = Path(tax_calculator.jurisdictions.ca_on.__file__).parent

    assert (directory / "manifests" / "v1").is_dir()
    assert not (directory / "manifests" / "v1.yaml").exists()
    assert (directory / "parameters" / "brackets" / "2025.yaml").is_file()
    assert (directory / "parameters" / "basic_personal_amount" / "2025.yaml").is_file()
    assert (directory / "parameters" / "credit_rate" / "2025.yaml").is_file()


def test_no_manifest_part_is_over_30_kb() -> None:
    manifests = Path(tax_calculator.jurisdictions.ca_on.__file__).parent / "manifests"

    parts = [p for p in manifests.rglob("*") if p.is_file()]

    assert parts
    assert [(p.name, p.stat().st_size) for p in parts if p.stat().st_size > 30 * 1024] == []


def test_manifest_parts_are_named_by_number_letter_and_topic() -> None:
    manifests = Path(tax_calculator.jurisdictions.ca_on.__file__).parent / "manifests"
    names = [p.name for p in manifests.rglob("*.yaml")]
    pattern = re.compile(r"^(\d\d)([a-z]?)_[a-z0-9_]+\.yaml$")

    matches = [pattern.match(name) for name in names]

    assert all(matches)
    numbers = [m.group(1) for m in matches if m and not m.group(2)]
    assert len(numbers) == len(set(numbers))
