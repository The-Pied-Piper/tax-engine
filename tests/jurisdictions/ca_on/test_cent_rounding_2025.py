"""The 2025 `ca-on/cent_rounding` dataset: the one rule shared by the Ontario floor steps
(`core/subtract_not_below_zero`) and the ON428 line 6 product (`core/multiply_by_rate`), that is,
ON428 lines 4, 6, 53, 61, 65, 71, 80, 81, 83, 86 and 88 and ON428-A lines 17 and 20. It carries
nothing but its rule, half-up to the cent, the rule of the dollars-and-cents boxes. It cites the
ON428 and ON428-A text."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_on
import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/cent_rounding"
FORMS = ("ca-on/on428", "ca-on/on428_a")


def test_2025_cent_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_cent_rounding_cites_the_on428_and_on428_a_text() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-a/5006-a-25e.txt",
    )


TAKE_HOME = Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "take_home"
SHARED_STEPS = ("core/sum", "core/times_count")


def shared_steps(form: str) -> list[tuple[str, Any]]:
    """Each `core/sum` and `core/times_count` step in the take-home manifest parts of `form`, as
    (file name, step), in file order."""
    steps: list[tuple[str, Any]] = []
    for path in sorted(TAKE_HOME.rglob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or (document.get("form") or {}).get("name") != form:
            continue
        for step in document.get("capabilities") or []:
            if step.get("name") in SHARED_STEPS:
                steps.append((path.name, step))
    return steps


def rounding_named_by(steps: list[tuple[str, Any]]) -> list[tuple[str, object]]:
    """Each step's file name with the rounding dataset its params name, or `None`."""
    return [(name, (step.get("params") or {}).get("rounding")) for name, step in steps]


@pytest.mark.parametrize("form", FORMS)
def test_every_sum_and_times_count_step_names_the_rounding_dataset(form: str) -> None:
    # A step that adds or multiplies a line names the shared rule, so its cents print at every
    # salary, including a count of 0.
    steps = shared_steps(form)

    assert steps, f"no core/sum or core/times_count step found for {form}"
    assert rounding_named_by(steps) == [(name, FAMILY) for name, _step in steps]
