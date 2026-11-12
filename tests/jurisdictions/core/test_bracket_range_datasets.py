"""Tests for the optional top-level key `up_to` of a `brackets` dataset, and a first bracket that
starts above 0 with a printed `tax_at_start`, read through the real YAML source (made-up `ex/`
datasets, figures as quoted strings)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import InvalidParameterDataError
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rate import RATE
from tests.parameter_source_support import BRACKETS_2025, RATE_2025, D, roots, write
from tests.parameter_source_support import core_parsers as built_in_parsers

# "More than 100": the first bracket starts at 100 on a printed 25.00; the second at 200.
UPPER_TABLE = BRACKETS_2025.replace(
    '{from: "0", rate: "0.10"}', '{from: "100", rate: "0.10", tax_at_start: "25.00"}'
).replace('{from: "100", rate: "0.20"}', '{from: "200", rate: "0.20", tax_at_start: "35.00"}')


def source(directory: Path) -> YamlParameterSource:
    return YamlParameterSource(roots(directory), parsers=built_in_parsers())


def test_a_dataset_without_up_to_has_no_upper_end(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", BRACKETS_2025)

    assert source(tmp_path).get("ex/brackets", 2025, BRACKETS).values.up_to is None


def test_reads_up_to_as_an_exact_decimal(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", BRACKETS_2025 + 'up_to: "300.50"\n')

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert schedule.up_to == D("300.50")
    assert schedule.covers(D("300.50"))
    assert not schedule.covers(D("300.51"))


def test_reads_a_first_bracket_above_zero_with_its_printed_tax_at_start(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", UPPER_TABLE)

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert schedule.brackets[0].lower == D("100")
    assert schedule.brackets[0].tax_at_start == D("25.00")
    assert not schedule.covers(D("100"))
    assert schedule.column_for(D("150")).tax_at_start == D("25.00")


def test_reads_a_range_with_both_a_start_above_zero_and_an_up_to(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", UPPER_TABLE + 'up_to: "400"\n')

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert (schedule.covers(D("100")), schedule.covers(D("400")), schedule.covers(D("401"))) == (
        False,
        True,
        False,
    )


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            BRACKETS_2025 + "up_to: 300\n",
            "up_to must be a string, got int",
            id="up-to-as-yaml-number",
        ),
        pytest.param(
            BRACKETS_2025 + 'up_to: "three hundred"\n',
            "up_to is not a decimal: 'three hundred'",
            id="up-to-not-decimal",
        ),
        pytest.param(BRACKETS_2025 + 'up_to: "100"\n', "up_to", id="up-to-equals-last-from"),
        pytest.param(BRACKETS_2025 + 'up_to: "50"\n', "up_to", id="up-to-below-last-from"),
        pytest.param(
            BRACKETS_2025.replace('{from: "0", rate: "0.10"}', '{from: "50", rate: "0.10"}'),
            "tax_at_start",
            id="first-bracket-above-zero-without-a-printed-tax-at-start",
        ),
    ],
)
def test_rejects_a_malformed_range(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/brackets", 2025, BRACKETS)

    assert "2025.yaml" in str(excinfo.value)
    assert "unknown keys" not in str(excinfo.value)  # `up_to` is a known key


def test_up_to_belongs_to_brackets_datasets_only(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/rate/2025.yaml", RATE_2025 + 'up_to: "300"\n')

    with pytest.raises(InvalidParameterDataError, match=r"unknown keys \['up_to'\]"):
        source(tmp_path).get("ex/rate", 2025, RATE)
