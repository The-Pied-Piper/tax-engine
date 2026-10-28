"""The percentage of Form T2203 Part 1 line 52220 column 5 in the CA-ON manifest: checked, read.

The percentage is the caller's input `ca/amt_t2203_column_5_percentage` (50 for 50%). The first
two steps of `08l_t2203_federal_surtax.yaml` check it against
`ca/amt_t2203_column_5_percentage_maximum`, a credit dataset of 100 (`core/credit_amount`, then
`core/at_most`), and produce `ca/amt_t2203_column_5_percentage_checked`. The three readers of the
percentage read the checked kind: `ca/apply_percentage` in 08l (Form T2203 Part 2 line 8), in
`20_alternative_minimum_tax.yaml` (Form T691 Part 3 line 3) and in
`20b_alternative_minimum_tax_part_6.yaml` (Form T691 Part 6 line 10). The form prints no maximum,
so the refusal above 100 is a choice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_calculator.jurisdictions.ca_on

MANIFESTS = Path(tax_calculator.jurisdictions.ca_on.__file__).parent / "manifests" / "v1"
SURTAX_PART = MANIFESTS / "08l_t2203_federal_surtax.yaml"
AMT_PART = MANIFESTS / "20_alternative_minimum_tax.yaml"
AMT_PART_6 = MANIFESTS / "20b_alternative_minimum_tax_part_6.yaml"
UNCHECKED = "ca/amt_t2203_column_5_percentage"
MAXIMUM = "ca/amt_t2203_column_5_percentage_maximum"
CHECKED = "ca/amt_t2203_column_5_percentage_checked"
READERS = (SURTAX_PART, AMT_PART, AMT_PART_6)


def steps(part: Path) -> list[dict[str, Any]]:
    capabilities: list[dict[str, Any]] = yaml.safe_load(part.read_text()).get("capabilities", [])
    return capabilities


def reading(part: Path, kind: str) -> list[dict[str, Any]]:
    """The steps of `part` that consume `kind`, alone or among a list of amounts."""
    return [
        step
        for step in steps(part)
        if any(
            value == kind or (isinstance(value, list) and kind in value)
            for value in step.get("consumes", {}).values()
        )
    ]


def test_the_first_two_steps_of_the_surtax_part_check_the_percentage_against_its_maximum() -> None:
    assert steps(SURTAX_PART)[:2] == [
        {
            "name": "core/credit_amount",
            "params": {"amount": MAXIMUM},
            "produces": {"output": MAXIMUM},
        },
        {
            "name": "core/at_most",
            "consumes": {"amount": UNCHECKED, "bound": MAXIMUM},
            "produces": {"output": CHECKED},
        },
    ]


def test_the_surtax_part_applies_the_checked_percentage_to_line_6() -> None:
    (apply,) = [step for step in steps(SURTAX_PART) if step["name"] == "ca/apply_percentage"]

    assert apply["consumes"] == {"amount": "ca/t2203_line_6", "percentage": CHECKED}
    assert apply["produces"] == {"output": "ca/t2203_line_8"}


@pytest.mark.parametrize("part", READERS, ids=[part.name for part in READERS])
def test_each_reader_of_the_percentage_reads_the_checked_kind(part: Path) -> None:
    readers = reading(part, CHECKED)

    assert [step["name"] for step in readers] == ["ca/apply_percentage"]
    assert readers[0]["consumes"]["percentage"] == CHECKED


def test_only_the_check_reads_the_percentage_as_entered() -> None:
    readers = [
        step["name"]
        for part in sorted(MANIFESTS.glob("*.yaml"))
        for step in reading(part, UNCHECKED)
    ]

    assert readers == ["core/at_most"]
