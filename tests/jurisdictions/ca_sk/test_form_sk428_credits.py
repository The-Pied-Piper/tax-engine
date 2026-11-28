"""The Saskatchewan form `ca-sk/sk428_credits` (Form SK428, lines 1 to 57) and the five kinds it
exports: line 5, the bracket rate (the figure the return summary reads for the marginal tax rate),
line 8, Saskatchewan tax on taxable income, line 57, Saskatchewan non-refundable tax credits, and
the age amount worksheet's line 4 and the age amount claimed (read for the age amount's fall in
the marginal tax rate).

The part file names the form and its exports; line parts carry the capabilities. The Saskatchewan
package is not yet listed, so the part is read as YAML and the kinds are taken from the
Saskatchewan package list in `support.py`, not from the engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_sk
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_sk.support import saskatchewan_kinds
from tests.kinds import non_negative

PART = (
    Path(tax_engine.jurisdictions.ca_sk.__file__).parent
    / "manifests"
    / "2025"
    / "sk428_credits.yaml"
)

EXPORTS = [
    "ca-sk/sk428_bracket_rate_line_5",
    "ca-sk/sk428_tax_on_taxable_income_line_8",
    "ca-sk/sk428_non_refundable_credits_line_57",
    "ca-sk/worksheet_sk428_age_amount_line_4",
    "ca-sk/sk428_age_amount_claimed_line_10",
]


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == "ca-sk/sk428_credits"
    assert form["title"] == "Form SK428: Saskatchewan Tax"
    assert form["required"] is True


def test_the_form_exports_line_5_the_two_tax_form_lines_and_the_two_age_figures_in_order() -> None:
    assert _part()["form"]["exports"] == EXPORTS


def test_the_form_supplies_nothing_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert "supplies" not in part["form"]
    assert "supplies" not in part
    assert part["capabilities"] == []


def test_the_part_keys_mirror_the_alberta_ab428_part() -> None:
    part = _part()

    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert list(part) == ["form", "capabilities"]


@pytest.mark.parametrize("identifier", EXPORTS)
def test_each_export_is_a_registered_non_negative_amount_kind(identifier: str) -> None:
    kinds = saskatchewan_kinds()

    assert identifier in kinds.identifiers()
    kind = kinds.kind(identifier)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
