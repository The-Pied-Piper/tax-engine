"""The MB428 (2025) donations and gifts part files, lines 54 to 56: each part's shape.

Form text (Form MB428, CRA 5007-c-25e.txt): line 54 "Amount from line 13 of your federal
Schedule 9 multiplied by 10.8% =", line 55 "Amount from line 14 of your federal Schedule 9
multiplied by 17.4% =" and line 56 "Line 54 plus line 55 =". See
`end_to_end/test_mb428_donations.py` for the figures through the engine. Each calculated line is
one line = one capability. Lines 54 and 55 first total the Schedule 9 export (lines 13 and 14) into
the amount, which is no longer an optional input of the form.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_mb.support import manitoba_kinds
from tests.kinds import non_negative

MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FORM = {"name": "ca-mb/mb428_credits"}


def _amount_step(line: str) -> dict[str, Any]:
    # The Schedule 9 amount: line 54 reads line 13 and line 55 reads line 14, as the form prints.
    source = {"54": "13", "55": "14"}[line]
    return {
        "name": "core/record_total",
        "title": f"Amount from line {source} of your federal Schedule 9",
        "reference": f"{line} box A",
        "unit": "ca/cad",
        "consumes": {"records": f"ca/schedule_9.donations_and_gifts_line_{source}"},
        "produces": {"output": f"ca-mb/mb428_donations_amount_line_{line}"},
    }


def _rate_step(line: str) -> dict[str, Any]:
    return {
        "name": "core/apply_rate",
        "reference": f"{line} box B",
        "unit": "ca/cad",
        "params": {"rate": f"ca-mb/donations_credit_rate_line_{line}"},
        "consumes": {"base": f"ca-mb/mb428_donations_amount_line_{line}"},
        "blank": {"base": "0"},
        "produces": {"output": f"ca-mb/mb428_donations_credit_at_rate_line_{line}"},
    }


STEPS = {
    "mb428_credits_line_54.yaml": [_amount_step("54"), _rate_step("54")],
    "mb428_credits_line_55.yaml": [_amount_step("55"), _rate_step("55")],
    "mb428_credits_line_56.yaml": [
        {
            "name": "core/sum",
            "title": "Donations and gifts",
            "reference": "56",
            "unit": "ca/cad",
            "params": {"rounding": "ca-mb/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-mb/mb428_donations_credit_at_rate_line_54",
                    "ca-mb/mb428_donations_credit_at_rate_line_55",
                ]
            },
            "produces": {"output": "ca-mb/mb428_donations_credit_line_56"},
        }
    ],
}


def _load(name: str) -> dict[str, Any]:
    part = yaml.safe_load((MB_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


@pytest.mark.parametrize(("name", "steps"), STEPS.items())
def test_each_calculated_line_is_its_steps_on_the_credits_form(
    name: str, steps: list[dict[str, Any]]
) -> None:
    part = _load(name)

    assert part == {"form": FORM, "capabilities": steps}


def test_the_two_input_parts_are_gone_because_schedule_9_owns_the_amount() -> None:
    assert not (MB_PARTS / "mb428_credits_line_54_inputs.yaml").exists()
    assert not (MB_PARTS / "mb428_credits_line_55_inputs.yaml").exists()


def test_the_old_line_56_input_part_is_gone() -> None:
    assert not (MB_PARTS / "mb428_credits_line_56_input.yaml").exists()


@pytest.mark.parametrize(
    ("identifier", "declared"),
    [
        ("ca-mb/mb428_donations_amount_line_54", mb_catalog.MB428_DONATIONS_AMOUNT_LINE_54),
        (
            "ca-mb/mb428_donations_credit_at_rate_line_54",
            mb_catalog.MB428_DONATIONS_CREDIT_AT_RATE_LINE_54,
        ),
        ("ca-mb/mb428_donations_amount_line_55", mb_catalog.MB428_DONATIONS_AMOUNT_LINE_55),
        (
            "ca-mb/mb428_donations_credit_at_rate_line_55",
            mb_catalog.MB428_DONATIONS_CREDIT_AT_RATE_LINE_55,
        ),
        ("ca-mb/mb428_donations_credit_line_56", mb_catalog.MB428_DONATIONS_CREDIT_LINE_56),
    ],
)
def test_each_line_is_a_registered_non_negative_decimal_amount_kind(
    identifier: str, declared: AmountKind
) -> None:
    kind = manitoba_kinds().kind(identifier)

    assert kind is declared
    assert isinstance(kind, AmountKind)
    assert kind.value_type.__name__ == "Decimal"
    assert non_negative(kind)
